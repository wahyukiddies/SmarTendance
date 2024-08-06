// KELOMPOK 2 - Smartendance
// Node 1: Registrasi
// WORK ONLY ON ESP8266 !

/* REQUIRED LIBRARIES */
#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <espnow.h>

/* RC522 SENSOR SETUP */
const byte SS_PIN = D8;
const byte RST_PIN = D0;
MFRC522 mfrc522(SS_PIN, RST_PIN);

/* WIFI CREDENTIALS */
const char* WIFI_SSID = "Rahasia"; // Update this to your own WiFi ssid.
const char* WIFI_PASS = "rahasiatuhan";  // Update this to your own WiFi password.
WiFiClient espClient;

/* MQTT BROKER CREDENTIALS */
const char* MQTT_HOST = "192.168.237.252"; // Update this to your PC/device IP address which is the MQTT broker/host.
const int MQTT_PORT = 1883; // Don't change the default mqtt port until you change the `mosquitto.conf` configuration in the source code.
const char* MQTT_USER = ""; // leave blank if no credentials used
const char* MQTT_PASS = ""; // leave blank if no credentials used
const char* CLIENT_NAME = "Node1_Registrasi_ESP8266"; // You can change this client name (optional).
const char* MQTT_PUB_TOPIC = "Smartendance/ESP8266/Register"; // Don't change this publish topic.
PubSubClient mqttClient(espClient);

/* LCD SETUP */
LiquidCrystal_I2C lcd(0x27, 16, 2);

bool cardScanned = false;
unsigned long lastScanTime = 0;
const unsigned long scanBlockDuration = 5000; // 5 seconds

bool isDeactivated = false;

// Variabel RSSI untuk menghitung kekuatan sinyal.
int rssi = 0;
// Variabel sendTime dan receiveTime untuk menghitung latensi.
unsigned long sendTime, receiveTime;

// Timer untuk pengecekan WiFi dan MQTT
unsigned long lastWiFiCheck = 0;
unsigned long lastMqttCheck = 0;

void connectWiFi() {
  Serial.print("Connecting to WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.println();
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  Serial.print("Connected to: ");
  Serial.println(WIFI_SSID);
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
}

String readUID() {
  // If the RFID card is present, then read the UID.
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++)
    uid += String(mfrc522.uid.uidByte[i], HEX);
  
  return uid;
}

void connectMqttBroker() {
  while (!mqttClient.connected()) {
    Serial.println("Connecting to MQTT broker: " + String(MQTT_HOST));

    if (mqttClient.connect(CLIENT_NAME, MQTT_USER, MQTT_PASS)) {
      Serial.println("Connected to MQTT broker: " + String(MQTT_HOST));
    }
    else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(": Connection to MQTT broker failed!");
      Serial.println("Try again in 3 seconds.");
      delay(3000);
    }
  }
}

void publishUID(const char* uid) {
  if (!cardScanned) {
    lcd.clear();

    if (mqttClient.publish(MQTT_PUB_TOPIC, uid)) {
      Serial.print("Message successfully published on topic [");
      Serial.print(MQTT_PUB_TOPIC);
      Serial.println("]");

      lcd.setCursor(0, 0);
      lcd.print(uid);
      lcd.setCursor(0, 1);
      lcd.print("UID Sent");

      // Set the flag and record the last scan time
      cardScanned = true;
      lastScanTime = millis();
    } else {
      Serial.println("Failed to publish success message");
      lcd.setCursor(0, 0);
      lcd.print(uid);
      lcd.setCursor(0, 1);
      lcd.print("UID Not Sent");

      initializeText();
    }
  }
}

void initializeText(){
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("# Smartendance #");
  lcd.setCursor(0, 1);
  lcd.print("Tap your card");
}

void onReceive(uint8_t *macAddr, uint8_t *data, uint8_t dataLen) {
  String message = String((char*)data);
  Serial.print("Received message: ");
  Serial.println(message);

  if (message.equalsIgnoreCase("deactivate")) {
    isDeactivated = true;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("# Deactivated #");
    lcd.setCursor(0, 1);
    lcd.print("Lock Absensi");
  } else if (message.equalsIgnoreCase("activate")) {
    isDeactivated = false;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("# Activated #");
    lcd.setCursor(0, 1);
    lcd.print("Unlock Absensi");
  }

  // Dapatkan RSSI
  rssi = WiFi.RSSI();
  Serial.print("RSSI: ");
  Serial.print(rssi);
  Serial.println(" dBm");

  unsigned long responseTime = millis();
  String callback = "received," + WiFi.macAddress() + "," + message; // Append MAC address to the message
  esp_now_send(macAddr, (uint8_t *)message.c_str(), message.length());
  Serial.print("Sent response to ");
  for (int i = 0; i < 6; i++) {
    Serial.print(macAddr[i], HEX);
    if (i < 5) Serial.print(":");
  }
  Serial.print(". Message: ");
  Serial.println(callback);
}

void setup() {
  Serial.setDebugOutput(true);
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  connectWiFi();

  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  connectMqttBroker();

  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Connected to WiFi");
  lcd.setCursor(0, 1);
  lcd.print("IP: " + WiFi.localIP().toString());
  delay(2000);
  lcd.clear();

  initializeText();

  // Initialize ESPNOW
  if (esp_now_init() != 0) {
    Serial.println("Error initializing ESPNOW");
    return;
  }
  esp_now_set_self_role(ESP_NOW_ROLE_COMBO);
  esp_now_register_recv_cb(onReceive);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastWiFiCheck >= 5000) { // Check WiFi connection every 5 seconds
    lastWiFiCheck = currentMillis;
    if (WiFi.status() != WL_CONNECTED) {
      connectWiFi();
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Connecting to");
      lcd.setCursor(0, 1);
      lcd.print("WiFi............");
      delay(2000);
      lcd.clear();
    }
  }

  if (currentMillis - lastMqttCheck >= 5000) { // Check MQTT connection every 5 seconds
    lastMqttCheck = currentMillis;
    if (!mqttClient.connected()) {
      connectMqttBroker();
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Connecting to");
      lcd.setCursor(0, 1);
      lcd.print("MQTT broker.....");
      delay(2000);
      lcd.clear();
    }
  }
  mqttClient.loop(); // Process MQTT messages.

  if (cardScanned && (currentMillis - lastScanTime >= scanBlockDuration)) {
    cardScanned = false;
    initializeText();
  }

  if (!isDeactivated) {
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      String uid = readUID();
      sendTime = millis(); // Save send time to calculate the latency.
      publishUID(uid.c_str());
    }
  }
}
