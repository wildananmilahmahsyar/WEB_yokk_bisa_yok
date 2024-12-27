from flask import Blueprint, request, redirect, url_for, render_template, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from pyrebase import pyrebase
from config import Config
import logging



firebase_config = Config.FIREBASE_CONFIG
# Inisialisasi Firebase
firebase = pyrebase.initialize_app(firebase_config)

db = firebase.database()

# Inisialisasi blueprint untuk auth
auth_bp = Blueprint('auth', __name__)

#LOGGING 
logging.basicConfig(level=logging.DEBUG)
@auth_bp.before_request
def log_request():
    logging.debug(f"Request: {request.method} {request.url} - Data: {request.form}")

# Fungsi cek superadmin
def is_superadmin(username, password):
    return username in ["adminetle", "superadmin"] and password == "superadminpassword"

# Route: Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.clear()
        username = request.form["username"]
        password = request.form["password"]

        # Cek jika superadmin
        if is_superadmin(username, password):
            session['user_role'] = 'superadmin'
            session['user_id'] = 'superadmin'
            flash("Login berhasil sebagai Superadmin.", "success")
            return redirect(url_for('auth.register'))

        # Cek pengguna biasa di Firebase
        users = db.child("users").get()
        for user in users.each():
            user_data = user.val()
            if user_data["nrp"] == username and check_password_hash(user_data["password"], password):
                session['user_id'] = user.key()
                session['user_name'] = user_data["nama"]
                session['user_role'] = 'user'
                flash("Login berhasil!", "success")
                return redirect(f"http://localhost:8000/templates/dashboard.php?user_id={session['user_id']}")

        flash("Login gagal, periksa username dan password Anda.", "error")
    return render_template("login.html")

# Route: Register pengguna baru (hanya untuk superadmin)
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get('user_role') != 'superadmin':
        flash("Anda tidak memiliki akses ke halaman ini.", "error")
        return redirect(url_for('auth.login'))

    users_list = []
    users = db.child("users").get()
    if users.each():
        for user in users.each():
            user_data = user.val()
            user_data["id"] = user.key()
            users_list.append(user_data)

    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        nrp = request.form.get("nrp", "").strip()
        no_hp = request.form.get("no_hp", "").strip()
        email = request.form.get("registrasi_email", "").strip()
        password = request.form.get("password", "").strip()

        # Validasi server-side
        if not (nama and nrp and no_hp and email and password):
            flash("Semua kolom wajib diisi!", "error")
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash("Kata sandi harus minimal 8 karakter.", "error")
            return redirect(url_for('auth.register'))

        if not nrp.isdigit() or len(nrp) > 12:
            flash("NRP harus berupa angka dan maksimal 12 digit.", "error")
            return redirect(url_for('auth.register'))

        if not no_hp.isdigit() or not (10 <= len(no_hp) <= 13):
            flash("Nomor HP tidak valid.", "error")
            return redirect(url_for('auth.register'))

        try:
            hashed_password = generate_password_hash(password)
            new_user = {
                "nama": nama,
                "nrp": nrp,
                "no_hp": no_hp,
                "email": email,
                "password": hashed_password
            }
            db.child("users").push(new_user)
            flash("Pengguna baru berhasil ditambahkan.", "success")
        except Exception as e:
            print("Error saat registrasi:", e)
            flash("Terjadi kesalahan saat menambahkan pengguna.", "error")

        return redirect(url_for('auth.register'))

    return render_template("register.html", users=users_list)


# Route: Edit data pengguna
@auth_bp.route("/edit_user/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if session.get('user_role') != 'superadmin':
        flash("Anda tidak memiliki akses untuk mengedit pengguna.", "error")
        return redirect(url_for('auth.register'))

    if request.method == "GET":
        user = db.child("users").child(user_id).get()
        if user.val():
            user_to_edit = {"id": user.key(), **user.val()}
            return render_template("register.html", user_to_edit=user_to_edit)
        flash("Pengguna tidak ditemukan.", "error")
        return redirect(url_for('auth.register'))

    try:
        nama = request.form["nama"]
        nrp = request.form["nrp"]
        no_hp = request.form["no_hp"]
        email = request.form["email"]

        updated_user = {
            "nama": nama,
            "nrp": nrp,
            "no_hp": no_hp,
            "email": email
        }
        db.child("users").child(user_id).update(updated_user)
        flash("Data pengguna berhasil diperbarui.", "success")
    except Exception as e:
        print("Error saat mengedit pengguna:", e)
        flash("Gagal memperbarui data pengguna.", "error")
    return redirect(url_for('auth.register'))

# Route: Hapus pengguna
@auth_bp.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    if session.get('user_role') != 'superadmin':
        flash("Anda tidak memiliki akses untuk menghapus pengguna.", "error")
        return redirect(url_for('auth.register'))

    try:
        db.child("users").child(user_id).remove()
        flash("Pengguna berhasil dihapus.", "success")
    except Exception as e:
        print("Error saat menghapus pengguna:", e)
        flash("Gagal menghapus pengguna.", "error")
    return redirect(url_for('auth.register'))

# Route: Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Anda telah berhasil keluar.", "success")
    return redirect(url_for('auth.login'))

# Route: Ambil data pengguna
@auth_bp.route("/get_user", methods=["GET"])
def get_user():
    user_id = request.args.get("user_id") or session.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID tidak ditemukan"}), 404

    user = db.child("users").child(user_id).get()
    if user.val():
        user_data = user.val()
        return jsonify({
            "nama": user_data.get("nama"),
            "nrp": user_data.get("nrp"),
            "no_hp": user_data.get("no_hp"),
            "email": user_data.get("email")
        }), 200
    return jsonify({"error": "User tidak ditemukan"}), 404


