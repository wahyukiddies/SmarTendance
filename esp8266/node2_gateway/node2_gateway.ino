// Node2: Gateway (ESPNOW Router)

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <espnow.h>

// Replace with your network credentials and MQTT broker details
const char* ssid = "POCO M3 Pro 5G";
const char* password = "Awikwok123456";
const char* mqtt_server = "192.168.135.252";
const int mqtt_port = 1883;

// MQTT topics
const char* subTopic1 = "Smartendance/ESP8266/DeactivateClass";
const char* subTopic2 = "Smartendance/ESP8266/ActivateClass";

// ESP-NOW peer addresses (MAC addresses)
// MAC Address Node1_Registrasi: C8:C9:A3:33:9F:2F
uint8_t node1Address[] = {0xC8, 0xC9, 0xA3, 0x33, 0x9F, 0x2F};
// MAC Address Node3_Absensi: 8C:AA:B5:F8:9B:9C
uint8_t node3Address[] = {0x8C, 0xAA, 0xB5, 0xF8, 0x9B, 0x9C};

WiFiClient espClient;
PubSubClient client(espClient);

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
  sendMessage(node3Address, message);
}

void sendMessage(uint8_t *address, String message) {
  esp_now_send(address, (uint8_t *)message.c_str(), message.length());
  Serial.print("Sent message to ");
  for (int i = 0; i < 6; i++) {
    Serial.print(address[i], HEX);
    if (i < 5) Serial.print(":");
  }
  Serial.print(". Message: ");
  Serial.println(message);
}
