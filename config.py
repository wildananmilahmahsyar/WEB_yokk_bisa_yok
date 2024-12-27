import os


# Memuat environment variables dari file .env jika tersedia


class Config:
    # Secret Key untuk Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "aasc")

    # Konfigurasi Firebase
    FIREBASE_CONFIG = {
        'apiKey': os.getenv("FIREBASE_API_KEY", "AIzaSyD1AEPWzJOPcgoj0cKSW9amRPJUQR2lbb0"),
        'authDomain': os.getenv("FIREBASE_AUTH_DOMAIN", "authentication-f2824.firebaseapp.com"),
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL", "https://authentication-f2824-default-rtdb.firebaseio.com"),
        'projectId': os.getenv("FIREBASE_PROJECT_ID", "authentication-f2824"),
        'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET", "authentication-f2824.appspot.com"),
        'messagingSenderId': os.getenv("FIREBASE_MESSAGING_SENDER_ID", "1021863772561"),
        'appId': os.getenv("FIREBASE_APP_ID", "1:1021863772561:web:c00adbdf7e995e85da5a30"),
        'measurementId': os.getenv("FIREBASE_MEASUREMENT_ID", "G-B28KE6CBSZ")
    }

    # Path kredensial Google Drive API
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

    # Scope Google Drive API
    GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']

    # Konfigurasi Nusa SMS API
    NUSA_SMS_API_KEY = os.getenv("NUSA_SMS_API_KEY", "17DD4AFEE4FA64D462D92FBC82899175")
    NUSA_SMS_BASE_URL = os.getenv("NUSA_SMS_BASE_URL", "https://api.nusasms.com/nusasms_api/1.0/whatsapp/message")

    # Direktori untuk menyimpan file sementara
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/")

    # Debug mode
    DEBUG = os.getenv("DEBUG", True)
