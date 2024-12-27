from ultralytics import YOLO
import cv2
import datetime
import time
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import firebase_admin
from firebase_admin import credentials, db
import pytesseract

# Inisialisasi Firebase
firebase_cred = credentials.Certificate("firebase_admin_sdk.json")  # Sesuaikan dengan nama file JSON Anda
firebase_admin.initialize_app(firebase_cred, {
    'databaseURL': 'https://authentication-f2824.firebaseio.com/'  # Ganti dengan URL Firebase Anda
})

# Inisialisasi Google Drive API
drive_creds = Credentials.from_service_account_file("credentials.json")
drive_service = build('drive', 'v3', credentials=drive_creds)

# Inisialisasi YOLOv8 dan direktori
output_dir = "detected_images"
os.makedirs(output_dir, exist_ok=True)
model = YOLO("best.pt")

# Inisialisasi kamera internal
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Kamera tidak dapat dibuka.")
    exit()

# Konfigurasi Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Ubah path sesuai instalasi Anda

# Fungsi untuk mengunggah file ke Google Drive
def upload_to_drive(file_path, filename):
    try:
        file_metadata = {'name': filename, 'mimeType': 'image/jpeg'}
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()

        # Set permissions
        drive_service.permissions().create(fileId=uploaded_file['id'], body={'role': 'reader', 'type': 'anyone'}).execute()
        return uploaded_file.get('webViewLink')
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None

# Fungsi untuk menyimpan data ke Firebase
def save_to_firebase(no_kendaraan, photo_url):
    data = {
        "location": "Jl. Jendral Sudirman",
        "no_kendaraan": no_kendaraan,
        "photo_url": photo_url,
        "status": "Menunggu",
        "time": datetime.datetime.now().isoformat()
    }
    db.reference("BUKTI").push(data)
    print("Data berhasil disimpan ke Firebase.")

# Fungsi untuk mendeteksi nomor kendaraan menggunakan OCR
def detect_license_plate(frame, bbox):
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    cropped_frame = frame[y1:y2, x1:x2]  # Potong area nomor kendaraan
    gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)  # Ubah ke grayscale
    no_kendaraan = pytesseract.image_to_string(gray_frame, config='--psm 8').strip()  # Deteksi teks
    return no_kendaraan

# Variabel kontrol
last_detection_time = 0
confidence_threshold = 0.3
target_classes = [0, 1, 2]

# Deteksi real-time
print("Tekan 'q' untuk keluar...")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Tidak dapat membaca frame.")
        break

    results = model(frame)
    current_time = time.time()

    if current_time - last_detection_time >= 10:
        detected = False

        for detection in results[0].boxes:
            class_id = detection.cls.cpu().item()
            confidence = detection.conf.cpu().item()
            bbox = detection.xyxy.cpu().numpy().tolist()

            if class_id in target_classes and confidence > confidence_threshold:
                detected = True

                # Deteksi nomor kendaraan menggunakan OCR
                no_kendaraan = detect_license_plate(frame, bbox)
                print(f"Nomor Kendaraan Terdeteksi: {no_kendaraan}")

                # Simpan gambar lokal
                filename = f"detected_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                file_path = os.path.join(output_dir, filename)
                cv2.imwrite(file_path, frame)
                print(f"Gambar disimpan: {file_path}")

                # Upload ke Google Drive
                photo_url = upload_to_drive(file_path, filename)
                if photo_url:
                    # Simpan ke Firebase
                    save_to_firebase(no_kendaraan, photo_url)

                last_detection_time = current_time

    # Tampilkan frame dengan anotasi
    annotated_frame = results[0].plot()
    cv2.imshow("YOLOv8 Real-Time Detection", annotated_frame)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan
cap.release()
cv2.destroyAllWindows()
