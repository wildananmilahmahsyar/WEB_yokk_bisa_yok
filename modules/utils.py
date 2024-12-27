from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import os

# Konfigurasi Google Drive API
GOOGLE_CREDENTIALS_FILE = "credentials.json"  # Path ke file kredensial Google Service Account
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Fungsi: Upload file ke Google Drive
def upload_to_drive(file_path, filename):
    try:
        # Inisialisasi Google Drive API
        creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)

        # Metadata file untuk gambar
        file_metadata = {
            'name': filename,
            'mimeType': 'image/jpeg'
        }

        # Upload file ke Google Drive
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()

        # Set file permissions menjadi publik
        drive_service.permissions().create(
            fileId=uploaded_file['id'],
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        # Kembalikan tautan langsung (webViewLink)
        print("File berhasil diunggah ke Google Drive:", uploaded_file.get('webViewLink'))
        return {
            "webViewLink": uploaded_file.get('webViewLink'),  # Tautan langsung ke gambar
            "id": uploaded_file.get('id')                    # ID file untuk thumbnail
        }
    except Exception as e:
        print("Error saat mengunggah ke Google Drive:", e)
        return None

# Fungsi: Validasi input kosong
def validate_input(data, required_fields):
    """
    Memvalidasi apakah semua field wajib diisi.

    Args:
        data (dict): Data input.
        required_fields (list): List field yang wajib diisi.

    Returns:
        tuple: (bool, str) Status validasi dan pesan error jika ada.
    """
    for field in required_fields:
        if not data.get(field):
            return False, f"Field '{field}' tidak boleh kosong."
    return True, ""

# Fungsi: Membuat folder jika belum ada
def ensure_folder_exists(folder_path):
    """
    Membuat folder jika belum ada.

    Args:
        folder_path (str): Path folder yang ingin dibuat.
    """
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    except Exception as e:
        print("Error saat membuat folder:", e)

# Fungsi: Menghapus file lokal
def delete_local_file(file_path):
    """
    Menghapus file lokal setelah diunggah.

    Args:
        file_path (str): Path file yang akan dihapus.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} berhasil dihapus.")
    except Exception as e:
        print(f"Error saat menghapus file {file_path}:", e)
