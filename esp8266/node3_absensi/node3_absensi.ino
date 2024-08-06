// KELOMPOK 2 - Smartendance
// Node3: Absensi
// WORK ONLY ON ESP8266 !

/* REQUIRED LIBRARIES */
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <espnow.h>

/* RC522 SENSOR SETUP */  
const byte SS_PIN = D8; // Update this according to your wiring
const byte RST_PIN = D0; // Update this according to your wiring
MFRC522 mfrc522(SS_PIN, RST_PIN);

/* WIFI CREDENTIALS */
const char* WIFI_SSID = "Rahasia"; // Update this to your own WiFi ssid.
const char* WIFI_PASS = "rahasiatuhan";  // Update this to your own WiFi password.

/* MQTT BROKER CREDENTIALS */
const char* MQTT_HOST = "192.168.237.252"; // Update this to your PC/device IP address which is the MQTT broker/host.
const int MQTT_PORT = 1883; // Don't change the default mqtt port until you change the `mosquitto.conf` configuration in the source code.
const char* MQTT_USER = ""; // leave blank if no credentials used
const char* MQTT_PASS = ""; // leave blank if no credentials used
const char* CLIENT_NAME = "Node3_Absensi_ESP8266"; // You can change this client name (optional).
const char* MQTT_PUB_TOPIC = "Smartendance/ESP8266/AttendanceFinal"; // Don't change this publish topic.
const char* MQTT_SUB_TOPIC = "Smartendance/ESP8266/AttendanceFinal/Response"; // Don't change this subs topic.

const int I2C_SDA = D3;
const int I2C_SCL = D4;

bool messageReceived = false;
bool isDeactivated = false;

/* I2C LCD Setup */
LiquidCrystal_I2C lcd(0x27, 16, 2); // Address 0x27, 16 columns and 2 rows

/* INSTANCE AN OBJECT FROM 'WiFiClient' and 'PubSubClient' CLASSES */
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Variabel RSSI untuk menghitung kekuatan sinyal.
int rssi = 0;
// Variabel sendTime dan receiveTime untuk menghitung latensi.
unsigned long sendTime, receiveTime;
// Variabel untuk mengelola timer non-blocking
unsigned long lastWiFiCheck = 0;
unsigned long lastMqttCheck = 0;
unsigned long lastReadTime = 0;

/* FUNCTION DECLARATIONS */
void connectWiFi();
String readUID();
void connectMqttBroker();
bool publishUID(const char* uid);
void initializeText();
void callback(char* topic, byte* payload, unsigned int length);
void onReceive(uint8_t *macAddr, uint8_t *data, uint8_t dataLen);
void sendMessageBack(uint8_t *address, String message);

void callback(char* topic, byte* payload, unsigned int length) {
  char status[4];
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);

  for (int i = 0; i < 3; i++) {
    status[i] = (char)payload[i];
  }
  status[3] = '\0';
  Serial.print("Message: ");
  Serial.println(status);

  messageReceived = true;

  // Check if status is 100, 101, 102, 103, or 104
  if(strcmp(status, "100") == 0){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Successful!");
    lcd.setCursor(0, 1);
    lcd.print("Attended");
  }
  else if(strcmp(status, "101") == 0){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Failed!");
    lcd.setCursor(0, 1);
    lcd.print("User not found");
  }
  else if(strcmp(status, "102") == 0){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Failed!");
    lcd.setCursor(0, 1);
    lcd.print("Course not found");
  }
  else if(strcmp(status, "103") == 0){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Failed!");
    lcd.setCursor(0, 1);
    lcd.print("Already attended");
  }
  else if(strcmp(status, "104") == 0){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Failed!");
    lcd.setCursor(0, 1);
    lcd.print("Role not found");
  }
}

void connectWiFi() {
  Serial.print("Connecting to WiFi...");
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
  String uid = "";
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    for (byte i = 0; i < mfrc522.uid.size; i++)
      uid += String(mfrc522.uid.uidByte[i], HEX);
    mfrc522.PICC_HaltA();
  }
  return uid;
}

void connectMqttBroker() {
  while (!mqttClient.connected() && WiFi.status() == WL_CONNECTED) {
    Serial.println("Connecting to MQTT broker: " + String(MQTT_HOST));
    if (mqttClient.connect(CLIENT_NAME)) {
      Serial.println("Connected to MQTT broker: " + String(MQTT_HOST));
      mqttClient.subscribe(MQTT_SUB_TOPIC);
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

bool publishUID(const char* uid) {
  Serial.print("Attempting to publish UID: ");
  Serial.println(uid);
  if (mqttClient.publish(MQTT_PUB_TOPIC, uid)) {
    Serial.print("UID successfully published on topic [");
    Serial.print(MQTT_PUB_TOPIC);
    Serial.print("]: ");
    Serial.println(uid);
    return true;
  }
  else {
    Serial.println("Failed to publish UID");
    return false;
  }
}

void onReceive(uint8_t *macAddr, uint8_t *data, uint8_t dataLen) {
  String message = String((char*)data);
  Serial.print("Received message: ");
  Serial.println(message);

  // Logika apabila terdapat pesan dikirimkan dari Node2.
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

  Wire.begin(I2C_SDA, I2C_SCL);
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
  lcd.print("IP:" + WiFi.localIP().toString());
  delay(2000);
  lcd.clear();

  // Subscribe to subTopic
  mqttClient.setCallback(callback);
  mqttClient.subscribe(MQTT_SUB_TOPIC);
  initializeText();

  // Initialize ESPNOW
  if (esp_now_init() != 0) {
    Serial.println("Error initializing ESPNOW");
    return;
  }
  esp_now_set_self_role(ESP_NOW_ROLE_COMBO);
  esp_now_register_recv_cb(onReceive);
}

void initializeText(){
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("# Smartendance #");
  lcd.setCursor(0, 1);
  lcd.print("Tap your card");
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

  if (!isDeactivated) {
    if (currentMillis - lastReadTime >= 1000) { // Read UID every second
      lastReadTime = currentMillis;
      String uid = readUID();
      if (uid.length() > 0) {
        bool success = publishUID(uid.c_str());
        if(!success) {
          lcd.clear();
          lcd.setCursor(0,0);
          lcd.print("Failed!");
          lcd.setCursor(0,1);
          lcd.print("MQTT publish");
          delay(2000);
          lcd.clear();
          initializeText();
        }
      }
    }
  }
}
