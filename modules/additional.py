from flask import Blueprint, jsonify, request, render_template
from pyrebase import pyrebase
from config import Config

firebase_config = Config.FIREBASE_CONFIG
firebase = pyrebase.initialize_app(firebase_config)

db = firebase.database()

# Inisialisasi blueprint untuk additional
additional_bp = Blueprint('additional', __name__)

# Route: Halaman form untuk menyimpan data lengkap
@additional_bp.route("/form_data_lengkap", methods=["GET"])
def form_data_lengkap():
    return render_template("form_data_lengkap.html")

# Route: Menyimpan data lengkap ke Firebase
@additional_bp.route("/save_data", methods=["POST"])
def save_data():
    try:
        # Ambil data dari JSON request
        data = request.get_json()
        no_kendaraan = data.get("no_kendaraan")
        nama = data.get("nama")
        no_sim = data.get("no_sim")
        alamat = data.get("alamat")
        jenis_kendaraan = data.get("jenis_kendaraan")

        if not no_kendaraan or not nama or not no_sim:
            return jsonify({"error": "Data tidak boleh kosong"}), 400

        # Simpan data ke Firebase
        db.child("data_lengkap").push({
            "no_kendaraan": no_kendaraan,
            "nama": nama,
            "no_sim": no_sim,
            "alamat": alamat,
            "jenis_kendaraan": jenis_kendaraan
        })

        return jsonify({"message": "Data berhasil disimpan"}), 200
    except Exception as e:
        print("Error occurred while saving data:", e)
        return jsonify({"error": str(e)}), 500

# Route: Mengarsipkan data pelanggaran berdasarkan nomor kendaraan
@additional_bp.route("/archive_pelanggar/<no_kendaraan>", methods=["POST"])
def archive_pelanggar(no_kendaraan):
    try:
        # Ambil data dari tabel BUKTI berdasarkan no_kendaraan
        bukti_records = db.child("BUKTI").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()

        if not bukti_records.each():
            return jsonify({"error": "Data tidak ditemukan"}), 404

        for record in bukti_records.each():
            # Pindahkan data ke arsip
            data_to_archive = record.val()
            db.child("ARSIP").push(data_to_archive)

            # Hapus data dari BUKTI
            db.child("BUKTI").child(record.key()).remove()

        return jsonify({"message": "Data berhasil diarsipkan"}), 200
    except Exception as e:
        print("Error occurred while archiving data:", e)
        return jsonify({"error": str(e)}), 500

# Route: Mengambil data arsip pelanggaran
@additional_bp.route("/get_pelanggar_arsip", methods=["GET"])
def get_pelanggar_arsip():
    try:
        # Ambil data arsip dari Firebase
        arsip_data = db.child("ARSIP").get()

        result = []
        if arsip_data.each():
            for item in arsip_data.each():
                record = item.val()
                result.append(record)

        return jsonify({"data": result}), 200
    except Exception as e:
        print("Error occurred while retrieving archive data:", e)
        return jsonify({"error": "Gagal mengambil data arsip"}), 500

# Route: Memperbarui status pelanggaran berdasarkan nomor kendaraan
@additional_bp.route("/update_status/<no_kendaraan>/<status>", methods=["POST"])
def update_status(no_kendaraan, status):
    try:
        print(f"Memperbarui status: {no_kendaraan} menjadi {status}")
        
        # Ambil data dari Firebase berdasarkan nomor kendaraan
        records = db.child("BUKTI").order_by_child("no_kendaraan").equal_to(no_kendaraan).get()

        if records.each():
            for record in records.each():
                db.child("BUKTI").child(record.key()).update({"status": status})
            return jsonify({"message": "Status berhasil diperbarui"}), 200

        return jsonify({"error": "Data tidak ditemukan"}), 404
    except Exception as e:
        print("Error occurred while updating status:", e)
        return jsonify({"error": str(e)}), 500
