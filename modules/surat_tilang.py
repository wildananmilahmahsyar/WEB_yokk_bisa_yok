from flask import Blueprint, jsonify, request
from modules.utils import upload_to_drive
from docx import Document
import os
import requests
from pyrebase import pyrebase
from config import Config
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# Inisialisasi Firebase
firebase_config = Config.FIREBASE_CONFIG
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# Inisialisasi blueprint untuk surat tilang
surat_bp = Blueprint('surat', __name__)

# Akses API Key dan URL Nusa SMS
NUSA_SMS_API_KEY = Config.NUSA_SMS_API_KEY
NUSA_SMS_BASE_URL = Config.NUSA_SMS_BASE_URL


# Fungsi Upload ke Google Drive
def upload_to_drive(file_path, filename):
    try:
        creds = Credentials.from_service_account_file(Config.GOOGLE_CREDENTIALS_FILE, scopes=Config.GOOGLE_DRIVE_SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': filename,
            'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()

        drive_service.permissions().create(
            fileId=uploaded_file['id'],
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        return uploaded_file.get('webViewLink')
    except Exception as e:
        print("Error saat upload ke Google Drive:", e)
        return None


# Route: Membuat surat tilang otomatis
@surat_bp.route("/generate_surat_tilang/<no_kendaraan>", methods=["POST"])
def generate_surat_tilang(no_kendaraan):
    try:
        # Ambil data dari tabel BUKTI dan data_lengkap berdasarkan no_kendaraan
        bukti_records = db.child("BUKTI").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()
        data_lengkap_records = db.child("data_lengkap").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()

        if not bukti_records.each() or not data_lengkap_records.each():
            return jsonify({"error": "Data tidak ditemukan"}), 404

        bukti_data = bukti_records.each()[0].val()
        data_lengkap = data_lengkap_records.each()[0].val()

        # Debug data untuk memastikan isi data dari Firebase
        print("Bukti Data:", bukti_data)    # Debugging: Cetak data dari Firebase
        print("Data Lengkap:", data_lengkap)  # Debugging: Cetak data dari Firebase


        # Update status menjadi "Tertindak"
        for record in bukti_records.each():
            db.child("BUKTI").child(record.key()).update({"status": "Tertindak"})


        # Isi data untuk template Word
        template_path = "D:\SEMESTER_5\POSLANTAS APP\SURAT TILANG1.docx"  # Sesuaikan path ke template Anda
        output_path = f"surat_tilang_{no_kendaraan}.docx"

        data = {
            "[Nomor Surat Tilang]": bukti_data.get("no_kendaraan", "-"),
            "[Nama Lengkap]": data_lengkap.get("nama", "-"),
            "[Nomor SIM]": data_lengkap.get("no_sim", "-"),
            "[Alamat Lengkap]": data_lengkap.get("alamat", "-"),
            "[Nomor Polisi Kendaraan]": bukti_data.get("no_kendaraan", "-"),
            "[Jenis/Model Kendaraan]": data_lengkap.get("jenis_kendaraan", "-"),
            "[waktu Kejadian]": bukti_data.get("time", "-"),
            "[Tempat]": bukti_data.get("location", "-"),
            "[Foto Pelanggaran]": bukti_data.get("photo_url", "-")
        }

        # Generate Word document
        doc = Document(template_path)
        for paragraph in doc.paragraphs:
            for placeholder, value in data.items():
                if placeholder in paragraph.text:
                    paragraph.text = paragraph.text.replace(placeholder, value)
        doc.save(output_path)

        # Upload surat ke Google Drive
        drive_link = upload_to_drive(output_path, f"Surat_Tilang_{no_kendaraan}.docx")

        # Hapus file lokal setelah upload
        if os.path.exists(output_path):
            os.remove(output_path)

        # Kirim SMS notifikasi ke pelanggar
        try:
            nama_pelanggar = data_lengkap.get("nama", "Pengguna Tidak Diketahui")
            no_hp = data_lengkap.get("no_hp", None)
            time = bukti_data.get("time", "-")
            location = bukti_data.get("location", "-")

            if no_hp:
                sms_message = f"""
INFO PELANGGARAN LALU LINTAS
Kepada Yth. {nama_pelanggar},

Kami mendeteksi pelanggaran lalu lintas atas nama Anda pada {time} di lokasi {location}.
Pelanggaran: Menerobos lampu merah.

Surat tilang Anda dapat diakses di tautan berikut:
{drive_link}

Hormat kami,
Petugas ETLE.
"""
                headers = {"Accept": "application/json", "APIKey": NUSA_SMS_API_KEY}
                payload = {"destination": no_hp, "message": sms_message, "include_unsubscribe": True}
                response = requests.post(NUSA_SMS_BASE_URL, headers=headers, json=payload)

                if response.status_code == 200:
                    print("Pesan berhasil dikirim.")
                else:
                    print("Gagal mengirim pesan:", response.json())
        except Exception as e:
            print("Error while sending SMS:", e)

        return jsonify({"message": "Surat tilang berhasil dibuat dan dikirim", "drive_link": drive_link}), 200
    except Exception as e:
        print("Error occurred while generating surat tilang:", e)
        return jsonify({"error": str(e)}), 500


# Route: Mengirim SMS notifikasi
@surat_bp.route("/send_sms", methods=["POST"])
def send_sms():
    try:
        data = request.get_json()
        destination = data.get("destination")
        message = data.get("message")

        if not destination or not message:
            return jsonify({"error": "Nomor tujuan atau pesan tidak boleh kosong"}), 400

        headers = {"Accept": "application/json", "APIKey": NUSA_SMS_API_KEY}
        payload = {"destination": destination, "message": message, "include_unsubscribe": True}

        response = requests.post(NUSA_SMS_BASE_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify({"message": "Pesan berhasil dikirim"}), 200
        else:
            return jsonify({"error": response.json().get('error', 'Gagal mengirim pesan')}), response.status_code
    except Exception as e:
        print("Error occurred while sending SMS:", e)
        return jsonify({"error": str(e)}), 500
