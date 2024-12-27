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
import re  # Tambahkan impor di bagian atas file, jika belum ada

# Inisialisasi Firebase dengan URL yang benar
firebase_cred = credentials.Certificate("firebase_admin_sdk.json")
firebase_admin.initialize_app(firebase_cred, {
    'databaseURL': 'https://authentication-f2824-default-rtdb.firebaseio.com/'  # Ganti dengan URL Firebase Anda
})

# Inisialisasi Google Drive API
drive_creds = Credentials.from_service_account_file("credentials.json")
drive_service = build('drive', 'v3', credentials=drive_creds)

# Inisialisasi YOLOv8 dan direktori
output_dir = "detected_images"
os.makedirs(output_dir, exist_ok=True)
model = YOLO("best.pt")

# Inisialisasi kamera internal
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Kamera tidak dapat dibuka.")
    exit()

# Konfigurasi Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Ubah path sesuai instalasi Anda
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"  # Sesuaikan path ini

# Fungsi untuk mengunggah file ke Google Drive
def upload_to_drive(file_path, filename):
    try:
        file_metadata = {'name': filename, 'mimeType': 'image/jpeg'}
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()

        # Set permissions
        drive_service.permissions().create(fileId=uploaded_file['id'], body={'role': 'reader', 'type': 'anyone'}).execute()

        # Kembalikan ID file dan tautan langsung
        return {
            "webViewLink": uploaded_file.get('webViewLink'),
            "photo_id": uploaded_file.get('id')
        }
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None

# Fungsi untuk menyimpan data ke Firebase
def save_to_firebase(no_kendaraan, photo_url, photo_id):
    data = {
        "location": "Jl. Jendral Sudirman",
        "no_kendaraan": no_kendaraan,
        "photo_url": photo_url,
        "photo_id": photo_id,  # Tambahkan photo_id
        "status": "Menunggu",
        "time": datetime.datetime.now().isoformat()
    }
    db.reference("BUKTI").push(data)  # Gunakan path yang benar
    print("Data berhasil disimpan ke Firebase.")

# Fungsi untuk mendeteksi nomor kendaraan menggunakan OCR
def detect_license_plate(frame, bbox):
    # Debugging: Print isi bounding box
    print(f"Bounding Box Data: {bbox}")
    print(f"Bounding Box Type: {type(bbox)}, Data: {bbox}")

    # Ambil koordinat bounding box dari nested list
    if isinstance(bbox[0], list) or isinstance(bbox[0], tuple):  # Jika elemen pertama adalah list atau tuple
        bbox = bbox[0]  # Ambil elemen pertama sebagai koordinat

    # Pastikan bbox adalah array numpy dan konversi ke integer
    x1, y1, x2, y2 = map(int, bbox[:4])  # Gunakan map untuk memastikan konversi ke integer

    # Validasi bounding box agar tidak keluar dari dimensi frame
    height, width, _ = frame.shape
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(width, x2), min(height, y2)

    # Potong dan proses area nomor kendaraan
    cropped_frame = frame[y1:y2, x1:x2]  # Potong area nomor kendaraan
    gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)  # Ubah ke grayscale
    no_kendaraan = pytesseract.image_to_string(gray_frame, config='--psm 8').strip()  # Deteksi teks

    # Validasi hasil OCR menggunakan regex
    match = re.search(r'[A-Z]{1,2}\s?\d{1,4}\s?[A-Z]{1,3}', no_kendaraan)  # Regex untuk format plat nomor
    if match:
        no_kendaraan = match.group().replace(" ", "")  # Hapus spasi
    else:
        print("OCR gagal membaca nomor kendaraan.")
        no_kendaraan = input("Masukkan nomor kendaraan secara manual: ")  # Input manual

    return no_kendaraan

# Variabel kontrol
last_detection_time = 0
confidence_threshold = 0.3
target_classes = [0, 1, 2]

# Deteksi real-time
# Proses utama deteksi
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
                drive_response = upload_to_drive(file_path, filename)
                if drive_response:
                    photo_url = drive_response["webViewLink"]
                    photo_id = drive_response["photo_id"]  # Ambil ID file

                    # Simpan ke Firebase
                    save_to_firebase(no_kendaraan, photo_url, photo_id)

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