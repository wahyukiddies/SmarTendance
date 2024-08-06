// Node3: Absensi

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
const char* WIFI_SSID = "POCO M3 Pro 5G";
const char* WIFI_PASS = "Awikwok123456";

/* MQTT BROKER CREDENTIALS */
const char* MQTT_HOST = "192.168.135.252";
const int MQTT_PORT = 1883;
const char* MQTT_USER = ""; // leave blank if no credentials used
const char* MQTT_PASS = ""; // leave blank if no credentials used
const char* CLIENT_NAME = "Node3_Absensi_ESP8266";
const char* MQTT_PUB_TOPIC = "Smartendance/ESP8266/AttendanceFinal";
const char* MQTT_SUB_TOPIC = "Smartendance/ESP8266/AttendanceFinal/Response";

const int I2C_SDA = D3;
const int I2C_SCL = D4;

bool messageReceived = false;
bool isDeactivated = false;

/* I2C LCD Setup */
LiquidCrystal_I2C lcd(0x27, 16, 2); // Address 0x27, 16 columns and 2 rows

/* INSTANCE AN OBJECT FROM 'WiFiClient' and 'PubSubClient' CLASSES */
WiFiClient espClient;
PubSubClient mqttClient(espClient);

/* FUNCTION DECLARATIONS */
void connectWiFi();
String readUID();
void connectMqttBroker();
bool publishUID(const char* uid);
bool waitForConfirmation();
void initializeText();
void callback(char* topic, byte* payload, unsigned int length);
void onReceive(uint8_t *macAddr, uint8_t *data, uint8_t dataLen);

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
  delay(2000);
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
  while (!mqttClient.connected() && WiFi.status() == WL_CONNECTED && !mqttClient.subscribe(MQTT_SUB_TOPIC)){
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
      /* Wait 3 seconds before retrying */
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

  if (message.equalsIgnoreCase("activate")) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Normal kembali");
    isDeactivated = false;
    digitalWrite(LED_BUILTIN, LOW); // Turn off LED
  } else if (message.equalsIgnoreCase("deactivate")) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Gagal absensi");
    lcd.setCursor(0, 1);
    lcd.print("ESP dimatikan");
    isDeactivated = true;
  }
}

void setup() {
  Serial.setDebugOutput(true);
  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);

  Wire.begin(I2C_SDA, I2C_SCL);
  SPI.begin();
  mfrc522.PCD_Init();

  connectWiFi();
  
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  connectMqttBroker();

  // Initialize LCD
  lcd.begin(16, 2);
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Connected to WiFi");
  lcd.setCursor(0, 1);
  lcd.print("IP: " + WiFi.localIP().toString());
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
  lcd.print("SmarTendance");
  lcd.setCursor(0, 1);
  lcd.print("Scan the card");
  delay(1000);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Connecting to WiFi...");
    delay(2000);
    lcd.clear();
  }

  if (!mqttClient.connected() || !mqttClient.subscribe(MQTT_SUB_TOPIC)) {
    connectMqttBroker();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Connecting to MQTT...");
    delay(2000);
    lcd.clear();
  }
  else {
    mqttClient.loop();
  }
  
  if (!isDeactivated) {
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
      delay(2000);
      lcd.clear();
      initializeText();
    }
  } else {
    digitalWrite(LED_BUILTIN, HIGH); // Turn on LED to indicate deactivated state
  }
}
