from flask import Blueprint

# Import semua blueprint dari modul lain
from .auth import auth_bp
from .bukti import bukti_bp
from .surat_tilang import surat_bp
from .additional import additional_bp

# List semua blueprint untuk didaftarkan di app.py
all_blueprints = [
    auth_bp,
    bukti_bp,
    surat_bp,
    additional_bp
]
