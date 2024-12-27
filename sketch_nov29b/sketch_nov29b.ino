#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>

// Konfigurasi Wi-Fi dan Firebase
#define SSID "NURUL NISA" // Nama Wi-Fi
#define PASSWORD "12345678" // Password Wi-Fi
#define API_KEY "AIzaSyB3MdwRKupCRnQn4qFJPmu3UWVcCmp18rc" // API Key Firebase
#define DATABASE_URL "https://authentication-f2824-default-rtdb.firebaseio.com/" // URL Database Firebase

// Definisi Pin untuk Lampu Lalu Lintas Pertama
#define RED_PIN1 18    // Pin LED Merah Pertama
#define YELLOW_PIN1 19 // Pin LED Kuning Pertama
#define GREEN_PIN1 21  // Pin LED Hijau Pertama

// Definisi Pin untuk Lampu Lalu Lintas Kedua
#define RED_PIN2 13    // Pin LED Merah Kedua
#define YELLOW_PIN2 12 // Pin LED Kuning Kedua
#define GREEN_PIN2 14  // Pin LED Hijau Kedua

// Pin Sensor Infrared
#define IR_SENSOR_PIN 32 // Pin Sensor IR

// Variabel Waktu (Milliseconds)
const int redDuration = 10000;    // 10 detik
const int yellowDuration = 2000;  // 2 detik
const int greenDuration = 5000;   // 5 detik

// Variabel Tracking Pelanggaran
int violationCount = 0;
bool isRedLight1On = false;
bool isRedLight2On = false;

// Firebase Variables
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

void setup() {
  // Inisialisasi Serial Monitor
  Serial.begin(115200);
  
  // Setup Pin Mode untuk Lampu Pertama
  pinMode(RED_PIN1, OUTPUT);
  pinMode(YELLOW_PIN1, OUTPUT);
  pinMode(GREEN_PIN1, OUTPUT);

  // Setup Pin Mode untuk Lampu Kedua
  pinMode(RED_PIN2, OUTPUT);
  pinMode(YELLOW_PIN2, OUTPUT);
  pinMode(GREEN_PIN2, OUTPUT);
  
  // Setup Pin Sensor IR
  pinMode(IR_SENSOR_PIN, INPUT);
  
  // Koneksi Wi-Fi
  Serial.println("Memulai koneksi Wi-Fi...");
  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }

  Serial.print("\nTerhubung ke Wi-Fi dengan IP: ");
  Serial.println(WiFi.localIP());

  // Konfigurasi Firebase
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  Serial.println("Menghubungkan ke Firebase...");
  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("SignUp berhasil");
  } else {
    Serial.printf("Error SignUp: %s\n", config.signer.signupError.message.c_str());
  }

  Firebase.begin(&config, &auth);
  Serial.println("Firebase dimulai.");
}

void loop() {
  // Siklus Lampu Pertama (Hijau)
  firstTrafficLightGreenCycle();

  // Siklus Lampu Kedua (Merah)
  secondTrafficLightRedCycle();

  // Siklus Lampu Pertama (Kuning)
  firstTrafficLightYellowCycle();

  // Siklus Lampu Kedua (Hijau)
  secondTrafficLightGreenCycle();

  // Siklus Lampu Pertama (Merah)
  firstTrafficLightRedCycle();

  // Siklus Lampu Kedua (Kuning)
  secondTrafficLightYellowCycle();
}

void firstTrafficLightGreenCycle() {
  Serial.println("Debug: Lampu Pertama Hijau");
  
  // Lampu Pertama Hijau
  digitalWrite(RED_PIN1, LOW);
  digitalWrite(GREEN_PIN1, HIGH);
  digitalWrite(YELLOW_PIN1, LOW);

  // Lampu Kedua Merah
  digitalWrite(RED_PIN2, HIGH);
  digitalWrite(GREEN_PIN2, LOW);
  digitalWrite(YELLOW_PIN2, LOW);

  Serial.println("Status: LAMPU PERTAMA HIJAU, LAMPU KEDUA MERAH");
  delay(greenDuration);
}

void secondTrafficLightRedCycle() {
  Serial.println("Debug: Lampu Kedua Tetap Merah");
  
  digitalWrite(RED_PIN2, HIGH);
  digitalWrite(GREEN_PIN2, LOW);
  digitalWrite(YELLOW_PIN2, LOW);

  isRedLight2On = true;
  unsigned long startTime = millis();
  while (millis() - startTime < redDuration) {
    checkForViolation();
  }
  isRedLight2On = false;
}

void firstTrafficLightYellowCycle() {
  Serial.println("Debug: Lampu Pertama Kuning");
  
  // Lampu Pertama Kuning
  digitalWrite(GREEN_PIN1, LOW);
  digitalWrite(YELLOW_PIN1, HIGH);
  digitalWrite(RED_PIN1, LOW);

  // Lampu Kedua Tetap Merah
  digitalWrite(RED_PIN2, HIGH);
  digitalWrite(GREEN_PIN2, LOW);
  digitalWrite(YELLOW_PIN2, LOW);

  Serial.println("Status: LAMPU PERTAMA KUNING, LAMPU KEDUA MERAH");
  delay(yellowDuration);
}

void secondTrafficLightGreenCycle() {
  Serial.println("Debug: Lampu Kedua Hijau");
  
  // Lampu Pertama Merah
  digitalWrite(RED_PIN1, HIGH);
  digitalWrite(GREEN_PIN1, LOW);
  digitalWrite(YELLOW_PIN1, LOW);

  // Lampu Kedua Hijau
  digitalWrite(RED_PIN2, LOW);
  digitalWrite(GREEN_PIN2, HIGH);
  digitalWrite(YELLOW_PIN2, LOW);

  Serial.println("Status: LAMPU PERTAMA MERAH, LAMPU KEDUA HIJAU");
  delay(greenDuration);
}

void firstTrafficLightRedCycle() {
  Serial.println("Debug: Lampu Pertama Merah");
  
  digitalWrite(RED_PIN1, HIGH);
  digitalWrite(GREEN_PIN1, LOW);
  digitalWrite(YELLOW_PIN1, LOW);

  isRedLight1On = true;
  unsigned long startTime = millis();
  while (millis() - startTime < redDuration) {
    checkForViolation();
  }
  isRedLight1On = false;
}

void secondTrafficLightYellowCycle() {
  Serial.println("Debug: Lampu Kedua Kuning");
  
  // Lampu Pertama Tetap Merah
  digitalWrite(RED_PIN1, HIGH);
  digitalWrite(GREEN_PIN1, LOW);
  digitalWrite(YELLOW_PIN1, LOW);

  // Lampu Kedua Kuning
  digitalWrite(GREEN_PIN2, LOW);
  digitalWrite(YELLOW_PIN2, HIGH);
  digitalWrite(RED_PIN2, LOW);

  Serial.println("Status: LAMPU PERTAMA MERAH, LAMPU KEDUA KUNING");
  delay(yellowDuration);
}

void checkForViolation() {
  int irStatus = digitalRead(IR_SENSOR_PIN); // Baca nilai dari sensor inframerah
  
  if ((isRedLight1On || isRedLight2On) && irStatus == LOW) {
    violationCount++;
    Serial.println("!!! PELANGGARAN TERDETEKSI !!!");
    Serial.print("Total Pelanggaran: ");
    Serial.println(violationCount);

    // Kirim data pelanggaran ke Firebase
    if (Firebase.RTDB.setInt(&fbdo, "/PELAGGARAN/COUNT", violationCount)) {
      Serial.println("Data pelanggaran berhasil dikirim ke Firebase");
    } else {
      Serial.print("Gagal mengirim data ke Firebase: ");
      Serial.println(fbdo.errorReason());
    }

    // Kirim status pelanggaran
    if (Firebase.RTDB.setString(&fbdo, "/PELAGGARAN/STATUS", "Pelanggaran Terdeteksi")) {
      Serial.println("Status pelanggaran berhasil dikirim ke Firebase");
    } else {
      Serial.print("Gagal mengirim status ke Firebase: ");
      Serial.println(fbdo.errorReason());
    }

    delay(1000); // Hindari multiple detection
  }
}