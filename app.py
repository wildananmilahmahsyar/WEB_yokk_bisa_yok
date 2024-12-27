from flask import Flask
from config import Config
from modules import all_blueprints

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Memuat konfigurasi dari config.py
app.config.from_object(Config)

# Mendaftarkan semua blueprint dari modules/__init__.py
for blueprint in all_blueprints:
    app.register_blueprint(blueprint)

# Route Index (Opsional)
@app.route("/")
def index():
    return "<h1>Selamat Datang di Aplikasi ETLE</h1><p>Silakan akses endpoint yang tersedia.</p>"

# Menjalankan aplikasi Flask
if __name__ == "__main__":
    print("Aplikasi Flask berjalan di mode debug:", Config.DEBUG)
    app.run(debug=Config.DEBUG)
