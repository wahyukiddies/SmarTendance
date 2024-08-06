// KELOMPOK 2 - Smartendance
// Node2: Gateway (ESPNOW Router)
// WORK ONLY ON ESP8266 !

/* REQUIRED LIBRARIES */
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <espnow.h>

// Replace with your network credentials and MQTT broker details
const char* ssid = "Rahasia";     // Update this to your own WiFi ssid.
const char* password = "rahasiatuhan";  // Update this to your own WiFi password.
const char* mqtt_server = "192.168.237.252"; // Update this to your PC/device IP address which is the MQTT broker/host.
const int mqtt_port = 1883; // Don't change the default mqtt port until you change the `mosquitto.conf` configuration in the source code.

// MQTT topics
const char* subTopic1 = "Smartendance/ESP8266/DeactivateESP"; // Don't change this subs topic.
const char* subTopic2 = "Smartendance/ESP8266/ActivateESP";   // Don't change this subs topic.

// ESP-NOW peer addresses (MAC addresses)
// MAC Address Node1_Registrasi: C8:C9:A3:33:9F:2F
uint8_t node1Address[] = {0xC8, 0xC9, 0xA3, 0x33, 0x9F, 0x2F}; // update this to your node 1 mac address.
// MAC Address Node3_Absensi: 8C:AA:B5:F8:9B:9C
uint8_t node3Address[] = {0x8C, 0xAA, 0xB5, 0xF8, 0x9B, 0x9C}; // update this to your node 3 mac address.

WiFiClient espClient;
PubSubClient client(espClient);

// Variables to measure latency
unsigned long sendTime1, sendTime2, receiveTime;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  if (esp_now_init() != 0) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  esp_now_set_self_role(ESP_NOW_ROLE_COMBO);

  esp_now_add_peer(node1Address, ESP_NOW_ROLE_COMBO, 1, NULL, 0);
  esp_now_add_peer(node3Address, ESP_NOW_ROLE_COMBO, 1, NULL, 0);

  esp_now_register_recv_cb(onReceive);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("Node2_ESP8266")) {
      Serial.println("connected");
      client.subscribe(subTopic1);
      client.subscribe(subTopic2);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  Serial.println(message);

  // Send the message via ESPNOW to Node1_Registrasi and Node3_Absensi
  sendMessage(node1Address, message);
  sendTime1 = millis();
  sendMessage(node3Address, message);
  sendTime2 = millis();
}

void sendMessage(uint8_t *address, String message) {
  // message += "," + String(sendTime); // Append send timestamp to the message
  esp_now_send(address, (uint8_t *)message.c_str(), message.length());
  Serial.print("Sent message to ");
  for (int i = 0; i < 6; i++) {
    Serial.print(address[i], HEX);
    if (i < 5) Serial.print(":");
  }
  Serial.print(". Message: ");
  Serial.println(message);
}

void onReceive(uint8_t *macAddr, uint8_t *data, uint8_t dataLen) {
  receiveTime = millis();
  char macStr[18];
  snprintf(macStr, sizeof(macStr), "%02X:%02X:%02X:%02X:%02X:%02X", macAddr[0], macAddr[1], macAddr[2], macAddr[3], macAddr[4], macAddr[5]);
  String message = String((char*)data);
  Serial.print("Received message: ");
  Serial.println(message);

  if (String(macStr) == "C8:C9:A3:33:9F:2F"){
    long latency = receiveTime - sendTime1;
    String messagePrint = String(sendTime1) + "," + String(receiveTime) + "," + message + "," + String(macStr) + "," + String(latency);
    Serial.println(messagePrint);
  }
  else if (String(macStr) == "8C:AA:B5:F8:9B:9C"){
    long latency = receiveTime - sendTime2;
    String messagePrint = String(sendTime2) + "," + String(receiveTime) + "," + message + "," + String(macStr) + "," + String(latency);
    Serial.println(messagePrint);
  }
}
