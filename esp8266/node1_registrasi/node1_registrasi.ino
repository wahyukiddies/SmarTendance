// Node 1: Registrasi

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
const char* WIFI_SSID = "POCO M3 Pro 5G";
const char* WIFI_PASS = "Awikwok123456";
WiFiClient espClient;

/* MQTT BROKER CREDENTIALS */
const char* MQTT_HOST = "192.168.135.252";
const int MQTT_PORT = 1883;
const char* MQTT_USER = ""; // leave blank if no credentials used
const char* MQTT_PASS = ""; // leave blank if no credentials used
const char* CLIENT_NAME = "Node1_Registrasi_ESP8266";
const char* MQTT_PUB_TOPIC = "Smartendance/ESP8266/Register";
PubSubClient mqttClient(espClient);

/* LCD SETUP */
LiquidCrystal_I2C lcd(0x27, 16, 2);

bool cardScanned = false;
unsigned long lastScanTime = 0;
const unsigned long scanBlockDuration = 5000; // 5 seconds

bool isDeactivated = false;

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
      /* Wait 3 seconds before retrying */
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
      lcd.print("UID Sended");

      // Set the flag and record the last scan time
      cardScanned = true;
      lastScanTime = millis();

      // Add a delay before clearing the display
      delay(2000); // Adjust as needed
    } else {
      Serial.println("Failed to publish success message");
      lcd.setCursor(0, 0);
      lcd.print(uid);
      lcd.setCursor(0, 1);
      lcd.print("UID Not Sended");

      // Add a delay before clearing the display
      delay(3000); // Adjust as needed
    }

    initializeText("# SmarTendance #"); // Call after the delay
  }
}

void initializeText(const char* text){
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(text);
  lcd.setCursor(0, 1);
  lcd.print("Tap the card");
  delay(1000);
}

void onReceive(uint8_t *macAddr, uint8_t *data, uint8_t dataLen) {
  String message = String((char*)data);
  Serial.print("Received message: ");
  Serial.println(message);

  if (message.equalsIgnoreCase("activate")) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Normal kembali");
    isDeactivated = false;
    digitalWrite(LED_BUILTIN, LOW); // Turn off LED
  } else if (message.equalsIgnoreCase("deactivate")) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Gagal registrasi");
    lcd.setCursor(0, 1);
    lcd.print("ESP dimatikan");
    isDeactivated = true;
  }
}


void setup() {
  Serial.setDebugOutput(true);
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  pinMode(LED_BUILTIN, OUTPUT);

  connectWiFi();

  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  connectMqttBroker();

  // Initialize LCD
  lcd.init();
  lcd.backlight(); // Turn on backlight (change to HIGH if active low)

  initializeText("# SmarTendance #");
  delay(1000);

  // Initialize ESPNOW
  if (esp_now_init() != 0) {
    Serial.println("Error initializing ESPNOW");
    return;
  }
  esp_now_set_self_role(ESP_NOW_ROLE_COMBO);
  esp_now_register_recv_cb(onReceive);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (!mqttClient.connected()) {
    connectMqttBroker();
  } else {
    mqttClient.loop();
  }

  unsigned long currentTime = millis();

  // Unblock card scanning after the specified duration
  if (cardScanned && (currentTime - lastScanTime >= scanBlockDuration)) {
    cardScanned = false;
  }

  if (!isDeactivated) {
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      String uid = readUID();
      publishUID(uid.c_str());
    }
  } else {
    digitalWrite(LED_BUILTIN, (millis() / 500) % 2); // Blink LED_BUILTIN every 500 ms
  }
}
