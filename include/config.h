#pragma once

// =====================================================================
// Pin map — Seeed XIAO ESP32-S3
// 4S 18650 + IP2368 USB-C PD + PCM5102A I2S DAC + TPA3116D2 stereo amp
// =====================================================================
// XIAO label  GPIO   Function
//   D0         1     Volume potentiometer (ADC1_CH0)
//   D1         2     Momentary push button (active-low, internal pull-up)
//   D2         3     SD card CS
//   D3         4     I2S BCLK    -> PCM5102A BCK
//   D4         5     I2S LRCLK   -> PCM5102A LCK
//   D5         6     I2S DOUT    -> PCM5102A DIN
//   D6        43     Status LED
//   D7        44     (free / spare for future use)
//   D8         7     SD SCK
//   D9         8     SD MISO
//   D10        9     SD MOSI
//
// On/off switch SW1: inline between BMS P+ and the carrier PCB +14V_SW
// rail. Slide / rocker switch must be rated >= 5A.
//
// Audio path: XIAO I2S -> PCM5102A DAC -> analog L/R -> TPA3116D2
//             stereo class-D amp -> 2x speakers (BTL).

// --- Audio (I2S → PCM5102A) ---
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
#define PIN_LED       43   // edge pin D6

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
