from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
from modules.utils import upload_to_drive
from pyrebase import pyrebase
import os
from config import Config


firebase_config = Config.FIREBASE_CONFIG
firebase = pyrebase.initialize_app(firebase_config)

db = firebase.database()

# Inisialisasi blueprint untuk bukti
bukti_bp = Blueprint('bukti', __name__)

# Route: Menampilkan halaman bukti
@bukti_bp.route("/bukti", methods=["GET"])
def bukti():
    return render_template("bukti.html")

# Route: Upload foto bukti pelanggaran ke Google Drive
@bukti_bp.route("/upload", methods=["POST"])
def upload():
    print("Request received")
    try:
        # Data form
        no_kendaraan = request.form["no_kendaraan"]
        time = request.form["time"]
        location = request.form["location"]
        photo = request.files["photo"]

        # Simpan file sementara di server lokal
        filename = secure_filename(photo.filename)
        file_path = os.path.join("uploads", filename)
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        photo.save(file_path)

        # Upload ke Google Drive
        drive_links = upload_to_drive(file_path, filename)
        if not drive_links:
            return jsonify({"error": "Gagal mengunggah ke Google Drive"}), 500

        # Tambahkan data ke Firebase
        data = {
            "no_kendaraan": no_kendaraan,
            "time": time,
            "location": location,
            "photo_url": drive_links["webViewLink"],  # Simpan tautan langsung
            "photo_id": drive_links["id"],           # ID file untuk thumbnail
            "status": "Menunggu"                     # Status awal
        }
        db.child("BUKTI").push(data)

        # Hapus file sementara dari server
        os.remove(file_path)

        return jsonify({"message": "Data berhasil diunggah!", "data": data}), 200
    except Exception as e:
        print("Error occurred during upload:", e)
        return jsonify({"error": str(e)}), 500

# Route: Mengambil daftar pelanggar
@bukti_bp.route("/get_pelanggar", methods=["GET"])
def get_pelanggar():
    try:
        bukti_data = db.child("BUKTI").get()

        result = []
        if bukti_data.each():
            for item in bukti_data.each():
                record = item.val()
                record["id"] = item.key()
                result.append(record)

        return jsonify({"data": result}), 200
    except Exception as e:
        print("Error occurred while retrieving data:", e)
        return jsonify({"error": "Gagal mengambil data"}), 500

# Route: Menghapus data bukti pelanggaran
@bukti_bp.route("/delete_bukti/<no_kendaraan>", methods=["DELETE"])
def delete_bukti(no_kendaraan):
    try:
        bukti_records = db.child("BUKTI").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()

        if bukti_records.each():
            for record in bukti_records.each():
                db.child("BUKTI").child(record.key()).remove()
                return jsonify({"message": "Data berhasil dihapus"}), 200

        return jsonify({"error": "Data tidak ditemukan"}), 404
    except Exception as e:
        print("Error occurred while deleting data:", e)
        return jsonify({"error": "Terjadi kesalahan saat menghapus data"}), 500


# Route: Mengambil detail bukti berdasarkan nomor kendaraan
@bukti_bp.route("/get_detail/<no_kendaraan>", methods=["GET"])
def get_detail(no_kendaraan):
    try:
        # Ambil data dari Firebase
        records = db.child("data_lengkap").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()
        bukti_records = db.child("BUKTI").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()
        

        if records.each():
            data_lengkap = records.each()[0].val()
            if bukti_records.each():
                data_bukti = bukti_records.each()[0].val()
                photo_url = data_bukti.get("photo_url")

                # Tambahkan ID foto jika ada
                if photo_url:
                    if "/file/d/" in photo_url:
                        file_id = photo_url.split("/file/d/")[1].split("/")[0]
                        data_lengkap["photo_id"] = file_id
                    elif "id=" in photo_url:
                        file_id = photo_url.split("id=")[1].split("&")[0]
                        data_lengkap["photo_id"] = file_id
                    else:
                        data_lengkap["photo_id"] = None
                else:
                    data_lengkap["photo_id"] = None

                # Tambahkan tautan langsung ke data_lengkap
                data_lengkap["photo_url"] = photo_url
                print(f"Data yang dikembalikan Firebase: {data_lengkap}")

            return jsonify(data_lengkap), 200

        return jsonify({"error": "Data tidak ditemukan"}), 404
    except Exception as e:
        print("Error occurred:", e)
        return jsonify({"error": "Terjadi kesalahan pada server"}), 500

# Route: Mengambil data pelanggar secara real-time
@bukti_bp.route("/get_realtime_pelanggar", methods=["GET"])
def get_realtime_pelanggar():
    try:
        bukti_data = db.child("BUKTI").get()

        result = []
        if bukti_data.each():
            for item in bukti_data.each():
                record = item.val()
                record["id"] = item.key()
                result.append(record)

        return jsonify({"data": result}), 200
    except Exception as e:
        print("Error occurred while retrieving real-time data:", e)
        return jsonify({"error": "Gagal mengambil data real-time"}), 500

@bukti_bp.route("/deletearsip/<no_kendaraan>", methods=["DELETE"])
def deletearsip(no_kendaraan):
    try:
        bukti_records = db.child("ARSIP").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()

        if bukti_records.each():
            for record in bukti_records.each():
                db.child("ARSIP").child(record.key()).remove()
                return jsonify({"message": "Data berhasil dihapus"}), 200

        return jsonify({"error": "Data tidak ditemukan"}), 404
    except Exception as e:
        print("Error occurred while deleting data:", e)
        return jsonify({"error": "Terjadi kesalahan saat menghapus data"}), 500

@bukti_bp.route("/get_suggestions", methods=["GET"])
def get_suggestions():
    query = request.args.get("query", "").lower()
    try:
        bukti_data = db.child("data_lengkap").get()
        results = []

        if bukti_data.each():
            for item in bukti_data.each():
                record = item.val()
                if query in record["no_kendaraan"].lower():
                    results.append({"no_kendaraan": record["no_kendaraan"]})

        return jsonify({"results": results[:10]}), 200  # Batasi ke 10 hasil
    except Exception as e:
        print("Error occurred while fetching suggestions:", e)
        return jsonify({"error": "Gagal mengambil saran"}), 500

