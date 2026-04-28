// ESP32-MusicPlayer-Battery
//   Hardware: Seeed XIAO ESP32-S3 + PCM5102A I2S DAC + TPA3116D2 stereo
//             class-D amp + microSD + 4S 18650 pack + IP2368 USB-C PD
//             charger module
//   Features: SD MP3 stereo playback, Wi-Fi captive-portal setup, web UI,
//             firmware OTA (ElegantOTA), music upload over HTTP, pot volume,
//             tactile-button track/album navigation, status LED.
//
// Build & flash:
//   pio run -t upload          # firmware
//   pio run -t uploadfs        # web UI from data/ to LittleFS
//
// First-boot flow:
//   1. Power on. LED double-blinks → device is in AP mode "ESP-Music-Setup".
//   2. Connect phone to that AP; captive portal opens; pick Wi-Fi + password.
//   3. Device reboots, joins Wi-Fi, advertises as http://esp-music.local/.

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <ESPmDNS.h>
#include <LittleFS.h>
#include <SD.h>
#include <SPI.h>
#include <ESPAsyncWebServer.h>
#include <ElegantOTA.h>
#include <ArduinoJson.h>
#include <Audio.h>

#include "config.h"

// -------------------------------------------------------------- globals

Audio            audio;
AsyncWebServer   server(80);

struct TrackRef {
  String album;
  String filename;   // e.g. "01 - Track.mp3"
  String fullPath;   // e.g. "/music/Album/01 - Track.mp3"
};
std::vector<TrackRef> playlist;
int      currentIndex = -1;
bool     isPlaying    = false;
uint8_t  audioVolume  = 12;          // 0..AUDIO_VOLUME_MAX
String   currentTitle;

// LED pattern state
enum LedMode { LED_OFF, LED_SOLID, LED_SLOW, LED_FAST, LED_HEARTBEAT };
volatile LedMode ledMode = LED_HEARTBEAT;

// Inter-task command queue for audio actions (web server runs on core 0,
// audio runs on core 1 — keep Audio API calls on the audio core).
enum AudioCmd { CMD_NONE, CMD_PLAY_INDEX, CMD_PAUSE, CMD_RESUME, CMD_NEXT, CMD_PREV, CMD_NEXT_ALBUM, CMD_VOLUME };
struct PendingCmd { AudioCmd cmd; int arg; };
QueueHandle_t cmdQueue;

TaskHandle_t   audioTaskHandle;
SemaphoreHandle_t playlistMutex;

// -------------------------------------------------------------- helpers

static String contentTypeFor(const String& path) {
  if (path.endsWith(".html")) return "text/html";
  if (path.endsWith(".css"))  return "text/css";
  if (path.endsWith(".js"))   return "application/javascript";
  if (path.endsWith(".json")) return "application/json";
  if (path.endsWith(".svg"))  return "image/svg+xml";
  if (path.endsWith(".png"))  return "image/png";
  if (path.endsWith(".ico"))  return "image/x-icon";
  return "text/plain";
}

static void scanLibrary() {
  // Build playlist by walking /music/<album>/*.mp3 on SD.
  // Sorted alphabetically by (album, filename) so behaviour is deterministic.
  std::vector<TrackRef> next;
  File root = SD.open(MUSIC_DIR);
  if (!root || !root.isDirectory()) {
    log_w("No %s directory on SD", MUSIC_DIR);
    if (root) root.close();
    xSemaphoreTake(playlistMutex, portMAX_DELAY);
    playlist.swap(next);
    xSemaphoreGive(playlistMutex);
    return;
  }
  while (File alb = root.openNextFile()) {
    if (alb.isDirectory()) {
      String albumName = String(alb.name());
      // SD library on ESP32 may return either bare or full path; normalise.
      int slash = albumName.lastIndexOf('/');
      if (slash >= 0) albumName = albumName.substring(slash + 1);
      while (File f = alb.openNextFile()) {
        if (!f.isDirectory()) {
          String fname = String(f.name());
          int s = fname.lastIndexOf('/');
          if (s >= 0) fname = fname.substring(s + 1);
          String lower = fname; lower.toLowerCase();
          if (lower.endsWith(".mp3") || lower.endsWith(".wav") ||
              lower.endsWith(".aac") || lower.endsWith(".flac")) {
            TrackRef t;
            t.album    = albumName;
            t.filename = fname;
            t.fullPath = String(MUSIC_DIR) + "/" + albumName + "/" + fname;
            next.push_back(t);
          }
        }
        f.close();
      }
    }
    alb.close();
  }
  root.close();

  std::sort(next.begin(), next.end(), [](const TrackRef& a, const TrackRef& b){
    if (a.album != b.album) return a.album < b.album;
    return a.filename < b.filename;
  });

  xSemaphoreTake(playlistMutex, portMAX_DELAY);
  playlist.swap(next);
  xSemaphoreGive(playlistMutex);
  log_i("Library: %u tracks", playlist.size());
}

static void enqueue(AudioCmd c, int arg = 0) {
  PendingCmd p { c, arg };
  xQueueSend(cmdQueue, &p, 0);
}

static int findTrackByPath(const String& path) {
  xSemaphoreTake(playlistMutex, portMAX_DELAY);
  int idx = -1;
  for (size_t i = 0; i < playlist.size(); ++i) {
    if (playlist[i].fullPath == path) { idx = (int)i; break; }
  }
  xSemaphoreGive(playlistMutex);
  return idx;
}

static int nextAlbumIndex(int from) {
  xSemaphoreTake(playlistMutex, portMAX_DELAY);
  int result = -1;
  if (!playlist.empty()) {
    String currentAlbum = (from >= 0 && from < (int)playlist.size()) ? playlist[from].album : "";
    for (size_t i = 1; i <= playlist.size(); ++i) {
      size_t j = (from + i) % playlist.size();
      if (playlist[j].album != currentAlbum) { result = (int)j; break; }
    }
    if (result < 0) result = 0;  // only one album → wrap to start
  }
  xSemaphoreGive(playlistMutex);
  return result;
}

// -------------------------------------------------------------- audio task

static void startTrack(int idx) {
  xSemaphoreTake(playlistMutex, portMAX_DELAY);
  if (idx < 0 || idx >= (int)playlist.size()) { xSemaphoreGive(playlistMutex); return; }
  String path = playlist[idx].fullPath;
  String title = playlist[idx].album + " — " + playlist[idx].filename;
  xSemaphoreGive(playlistMutex);

  audio.stopSong();
  if (audio.connecttoFS(SD, path.c_str())) {
    currentIndex = idx;
    currentTitle = title;
    isPlaying    = true;
    ledMode      = LED_SOLID;
    log_i("Playing [%d] %s", idx, path.c_str());
  } else {
    log_e("Failed to open %s", path.c_str());
    isPlaying = false;
    ledMode   = LED_SLOW;
  }
}

static void audioTask(void*) {
  audio.setPinout(PIN_I2S_BCLK, PIN_I2S_LRCLK, PIN_I2S_DOUT);
  audio.setVolume(audioVolume);

  for (;;) {
    PendingCmd p;
    while (xQueueReceive(cmdQueue, &p, 0) == pdTRUE) {
      switch (p.cmd) {
        case CMD_PLAY_INDEX: startTrack(p.arg); break;
        case CMD_PAUSE:
          if (isPlaying) { audio.pauseResume(); isPlaying = false; ledMode = LED_SLOW; }
          break;
        case CMD_RESUME:
          if (!isPlaying && currentIndex >= 0) { audio.pauseResume(); isPlaying = true; ledMode = LED_SOLID; }
          else if (currentIndex < 0) { startTrack(0); }
          break;
        case CMD_NEXT: {
          int n = (currentIndex + 1);
          xSemaphoreTake(playlistMutex, portMAX_DELAY);
          int sz = (int)playlist.size();
          xSemaphoreGive(playlistMutex);
          if (sz > 0) startTrack(n % sz);
          break;
        }
        case CMD_PREV: {
          int n = (currentIndex <= 0) ? 0 : currentIndex - 1;
          startTrack(n);
          break;
        }
        case CMD_NEXT_ALBUM: {
          int n = nextAlbumIndex(currentIndex);
          if (n >= 0) startTrack(n);
          break;
        }
        case CMD_VOLUME:
          audioVolume = constrain(p.arg, 0, AUDIO_VOLUME_MAX);
          audio.setVolume(audioVolume);
          break;
        default: break;
      }
    }
    audio.loop();
    vTaskDelay(1);  // yield
  }
}

// Called by ESP32-audioI2S when a track ends — auto-advance.
void audio_eof_mp3(const char* /*info*/) {
  enqueue(CMD_NEXT);
}

// -------------------------------------------------------------- web API

static void handleStatus(AsyncWebServerRequest* req) {
  JsonDocument doc;
  doc["playing"] = isPlaying;
  doc["index"]   = currentIndex;
  doc["title"]   = currentTitle;
  doc["volume"]  = audioVolume;
  doc["volumeMax"] = AUDIO_VOLUME_MAX;
  doc["wifi"]    = WiFi.SSID();
  doc["ip"]      = WiFi.localIP().toString();
  doc["heap"]    = (uint32_t)ESP.getFreeHeap();
  String out; serializeJson(doc, out);
  req->send(200, "application/json", out);
}

static void handleFiles(AsyncWebServerRequest* req) {
  JsonDocument doc;
  JsonArray arr = doc["tracks"].to<JsonArray>();
  xSemaphoreTake(playlistMutex, portMAX_DELAY);
  for (size_t i = 0; i < playlist.size(); ++i) {
    JsonObject o = arr.add<JsonObject>();
    o["i"]     = (uint32_t)i;
    o["album"] = playlist[i].album;
    o["name"]  = playlist[i].filename;
    o["path"]  = playlist[i].fullPath;
  }
  xSemaphoreGive(playlistMutex);
  String out; serializeJson(doc, out);
  req->send(200, "application/json", out);
}

// Streaming upload to /music/<album>/<file>.  ?album=Foo&name=bar.mp3
static File   uploadFile;
static String uploadPath;
static void handleUpload(AsyncWebServerRequest* req, String filename, size_t index,
                         uint8_t* data, size_t len, bool final) {
  if (index == 0) {
    String album = req->hasParam("album", true) ? req->getParam("album", true)->value() : "Uploads";
    String name  = filename.length() ? filename : "upload.mp3";
    String dir   = String(MUSIC_DIR) + "/" + album;
    SD.mkdir(MUSIC_DIR);
    SD.mkdir(dir);
    uploadPath = dir + "/" + name;
    if (SD.exists(uploadPath)) SD.remove(uploadPath);
    uploadFile = SD.open(uploadPath, FILE_WRITE);
    ledMode    = LED_FAST;
    log_i("Upload start: %s", uploadPath.c_str());
  }
  if (uploadFile && len) uploadFile.write(data, len);
  if (final) {
    if (uploadFile) uploadFile.close();
    log_i("Upload done: %s (%u bytes)", uploadPath.c_str(), (unsigned)(index + len));
    scanLibrary();
    ledMode = isPlaying ? LED_SOLID : LED_SLOW;
  }
}

static void setupWebServer() {
  // Static web UI from LittleFS.
  server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

  // ----- API
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/files",  HTTP_GET, handleFiles);

  server.on("/api/play", HTTP_POST, [](AsyncWebServerRequest* req){
    if (req->hasParam("i", true)) {
      enqueue(CMD_PLAY_INDEX, req->getParam("i", true)->value().toInt());
    } else if (req->hasParam("path", true)) {
      int idx = findTrackByPath(req->getParam("path", true)->value());
      if (idx >= 0) enqueue(CMD_PLAY_INDEX, idx);
    } else {
      enqueue(CMD_RESUME);
    }
    req->send(200, "application/json", "{\"ok\":true}");
  });
  server.on("/api/pause", HTTP_POST, [](AsyncWebServerRequest* req){
    enqueue(CMD_PAUSE); req->send(200, "application/json", "{\"ok\":true}");
  });
  server.on("/api/next",  HTTP_POST, [](AsyncWebServerRequest* req){
    enqueue(CMD_NEXT); req->send(200, "application/json", "{\"ok\":true}");
  });
  server.on("/api/prev",  HTTP_POST, [](AsyncWebServerRequest* req){
    enqueue(CMD_PREV); req->send(200, "application/json", "{\"ok\":true}");
  });
  server.on("/api/next_album", HTTP_POST, [](AsyncWebServerRequest* req){
    enqueue(CMD_NEXT_ALBUM); req->send(200, "application/json", "{\"ok\":true}");
  });
  server.on("/api/volume", HTTP_POST, [](AsyncWebServerRequest* req){
    if (req->hasParam("v", true)) {
      int v = req->getParam("v", true)->value().toInt();   // 0..100 from UI
      int mapped = (v * AUDIO_VOLUME_MAX) / 100;
      enqueue(CMD_VOLUME, mapped);
    }
    req->send(200, "application/json", "{\"ok\":true}");
  });
  server.on("/api/rescan", HTTP_POST, [](AsyncWebServerRequest* req){
    scanLibrary(); req->send(200, "application/json", "{\"ok\":true}");
  });
  server.on("/api/wifi_reset", HTTP_POST, [](AsyncWebServerRequest* req){
    req->send(200, "application/json", "{\"ok\":true,\"msg\":\"rebooting into setup AP\"}");
    delay(250);
    WiFi.disconnect(true, true);
    ESP.restart();
  });

  // Upload music files (multipart/form-data, field name "file").
  server.on("/api/upload", HTTP_POST,
    [](AsyncWebServerRequest* req){ req->send(200, "application/json", "{\"ok\":true}"); },
    handleUpload);

  // Firmware OTA at /update
  ElegantOTA.begin(&server);
  ElegantOTA.onStart([](){ ledMode = LED_FAST; });
  ElegantOTA.onEnd([](bool success){ ledMode = success ? LED_SOLID : LED_SLOW; });

  server.onNotFound([](AsyncWebServerRequest* req){
    req->send(404, "text/plain", "not found");
  });
  server.begin();
}

// -------------------------------------------------------------- inputs

static void handleVolumePot() {
  // Read pot, apply hysteresis, push volume command if it crossed a step.
  static uint32_t lastRead = 0;
  static int      lastStep = -1;
  if (millis() - lastRead < 80) return;
  lastRead = millis();

  int raw = analogRead(PIN_VOL_POT);                 // 0..4095
  int step = (raw * (AUDIO_VOLUME_MAX + 1)) / 4096;  // 0..AUDIO_VOLUME_MAX
  if (step != lastStep) {
    lastStep = step;
    enqueue(CMD_VOLUME, step);
  }
}

static void handleButton() {
  // Active-low. Short press = next track; long press = next album;
  // double-tap inside BTN_DOUBLE_MS = previous track.
  static bool     pressed         = false;
  static uint32_t pressStart      = 0;
  static uint32_t lastReleaseTime = 0;
  static bool     longFired       = false;
  static uint32_t lastEdge        = 0;

  bool down = (digitalRead(PIN_BUTTON) == LOW);
  uint32_t now = millis();
  if (now - lastEdge < BTN_DEBOUNCE_MS) return;

  if (down && !pressed) {
    pressed = true; pressStart = now; longFired = false; lastEdge = now;
  } else if (!down && pressed) {
    pressed = false; lastEdge = now;
    if (!longFired) {
      uint32_t held = now - pressStart;
      if (held < BTN_LONG_PRESS_MS) {
        if (now - lastReleaseTime < BTN_DOUBLE_MS) {
          enqueue(CMD_PREV);
          lastReleaseTime = 0;
        } else {
          enqueue(CMD_NEXT);
          lastReleaseTime = now;
        }
      }
    }
  } else if (down && pressed && !longFired && (now - pressStart) >= BTN_LONG_PRESS_MS) {
    enqueue(CMD_NEXT_ALBUM);
    longFired = true;
  }
}

static void handleLed() {
  static uint32_t last = 0;
  static int      phase = 0;
  uint32_t now = millis();
  switch (ledMode) {
    case LED_OFF:    digitalWrite(PIN_LED, LOW); break;
    case LED_SOLID:  digitalWrite(PIN_LED, HIGH); break;
    case LED_SLOW:
      if (now - last > 500) { last = now; digitalWrite(PIN_LED, !digitalRead(PIN_LED)); }
      break;
    case LED_FAST:
      if (now - last > 100) { last = now; digitalWrite(PIN_LED, !digitalRead(PIN_LED)); }
      break;
    case LED_HEARTBEAT:
      // pattern: on, off, on, off-long
      if (now - last > 120) {
        last = now;
        const bool pat[] = { true, false, true, false, false, false, false, false };
        digitalWrite(PIN_LED, pat[phase] ? HIGH : LOW);
        phase = (phase + 1) & 7;
      }
      break;
  }
}

// PCM5102A DAC + TPA3116D2 amp need no software init: the DAC strapping
// is hardwired on the breakout (XSMT/FMT/DEMP/SCK pins tied at fab time),
// and the amp is fully analog after that. Volume is set entirely in
// software via the audioI2S library (`audio.setVolume`) on the digital
// side, scaled by AUDIO_VOLUME_MAX.

// -------------------------------------------------------------- setup / loop

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  analogReadResolution(12);

  ledMode = LED_HEARTBEAT;

  if (!LittleFS.begin(true)) log_e("LittleFS mount failed");

  // SD card on dedicated SPI bus (avoid conflicting with default VSPI defaults).
  SPI.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
  if (!SD.begin(PIN_SD_CS, SPI, 20000000)) {
    log_e("SD card mount failed — playback disabled until card is inserted");
  } else {
    log_i("SD card OK, %llu MB", SD.cardSize() / (1024ULL * 1024ULL));
    SD.mkdir(MUSIC_DIR);
  }

  cmdQueue       = xQueueCreate(8, sizeof(PendingCmd));
  playlistMutex  = xSemaphoreCreateMutex();
  scanLibrary();

  // Wi-Fi: WiFiManager handles captive-portal-on-no-creds.
  WiFiManager wm;
  wm.setConfigPortalTimeout(180);
  String apName = String(AP_SSID_PREFIX) + "-" +
                  String((uint32_t)(ESP.getEfuseMac() & 0xFFFFFF), HEX);
  if (!wm.autoConnect(apName.c_str(), AP_PASSWORD[0] ? AP_PASSWORD : nullptr)) {
    log_w("Wi-Fi setup timed out, restarting");
    ESP.restart();
  }
  log_i("Wi-Fi connected: %s  IP=%s", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str());
  if (MDNS.begin(HOSTNAME)) MDNS.addService("http", "tcp", 80);

  setupWebServer();

  // Audio runs on core 1, web/Wi-Fi on core 0 (Arduino default for ESP32-S3).
  xTaskCreatePinnedToCore(audioTask, "audio", 8192, nullptr, 5, &audioTaskHandle, 1);

  ledMode = LED_SLOW;   // ready, not yet playing
}

void loop() {
  ElegantOTA.loop();
  handleVolumePot();
  handleButton();
  handleLed();
  delay(5);
}
