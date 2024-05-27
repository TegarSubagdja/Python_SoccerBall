#include <WiFi.h>
#include <WebServer.h>
#include <esp32cam.h>

// Ganti dengan nama SSID dan password WiFi Anda
const char* ssid = "Cimohay";
const char* password = "pasti151002";

// Alamat IP statis yang ingin kita tetapkan
IPAddress local_IP(192, 168, 1, 10);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

WebServer server(80);  // Membuat server web pada port 80

static auto hiRes = esp32cam::Resolution::find(1280, 720);

void handleData() {
  // Mendapatkan nilai dari URL
  if (server.hasArg("value")) {
    String value = server.arg("value");
    Serial.println(value);
    // server.send(200, "text/plain", "Value received: " + value);
  } else {
    // server.send(200, "text/plain", "No value received");
  }
}

void serveJpg() {
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  // Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
  //               static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleJpg() {
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void setup() {
  Serial.begin(9600);

  Serial.println();
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(90);

    bool ok = Camera.begin(cfg);
    // Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }

  // Menginisialisasi koneksi WiFi dengan alamat IP statis
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }

  WiFi.begin(ssid, password);

  // Menunggu sampai terhubung ke WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/data", handleData);  // Menangani permintaan ke URL /data
  server.on("/jpg", handleJpg);    // Menangani permintaan ke URL /jpg
  server.begin();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Reconnecting...");

    // Reconnect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
    }

    Serial.println("WiFi reconnected");
  }
  server.handleClient();  // Menangani klien yang terhubung ke server
}