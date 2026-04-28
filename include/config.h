#pragma once

// =====================================================================
// Pin map — Seeed XIAO ESP32-S3
// =====================================================================
// XIAO label  GPIO   Function
//   D0         1     Volume potentiometer (ADC1_CH0)
//   D1         2     Momentary push button (active-low, internal pull-up)
//   D2         3     SD card CS
//   D3         4     I2S BCLK   -> MAX98357A BCLK
//   D4         5     I2S LRCLK  -> MAX98357A LRC
//   D5         6     I2S DOUT   -> MAX98357A DIN
//   D6        43     Status LED (also UART0 TX — disconnect during USB serial debug)
//   D7        44     reserved (UART0 RX)
//   D8         7     SD SCK
//   D9         8     SD MISO
//   D10        9     SD MOSI
//
// On/off switch: inline between 18650 + and IP5306 module battery input.
// (No GPIO required — switch fully isolates the battery.)

// --- Audio (I2S → MAX98357A) ---
#define PIN_I2S_BCLK   4
#define PIN_I2S_LRCLK  5
#define PIN_I2S_DOUT   6

// --- microSD (SPI) ---
#define PIN_SD_CS      3
#define PIN_SD_SCK     7
#define PIN_SD_MISO    8
#define PIN_SD_MOSI    9

// --- Controls / indicators ---
#define PIN_VOL_POT    1   // ADC1_CH0
#define PIN_BUTTON     2   // active-low, INPUT_PULLUP
#define PIN_LED       43

// --- Audio behaviour ---
#define AUDIO_VOLUME_MAX  21  // ESP32-audioI2S volume scale (0..21)
#define MUSIC_DIR    "/music"  // top-level folder on SD; subfolders are albums

// --- Wi-Fi / web ---
#define AP_SSID_PREFIX  "ESP-Music-Setup"
#define AP_PASSWORD     ""        // empty = open AP for first-time setup
#define HOSTNAME        "esp-music"

// --- Button timing (ms) ---
#define BTN_DEBOUNCE_MS    25
#define BTN_LONG_PRESS_MS  600    // long press = next album
#define BTN_DOUBLE_MS      350    // window for double-tap = previous track

// --- LED patterns ---
//   solid                 = playing
//   slow blink (1Hz)      = idle / paused
//   fast blink (5Hz)      = OTA / upload in progress
//   double-blink heartbeat = AP / setup mode
