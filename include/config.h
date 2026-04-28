#pragma once

// =====================================================================
// Pin map — Seeed XIAO ESP32-S3
// 4S 18650 + TAS5825M stereo + IP2368 USB-C PD configuration
// =====================================================================
// XIAO label  GPIO   Function
//   D0         1     Volume potentiometer (ADC1_CH0)
//   D1         2     Momentary push button (active-low, internal pull-up)
//   D2         3     SD card CS
//   D3         4     I2S BCLK    -> TAS5825M SCLK
//   D4         5     I2S LRCLK   -> TAS5825M LRCLK
//   D5         6     I2S DOUT    -> TAS5825M SDIN
//   D6        43     I2C SDA     -> TAS5825M SDA  (also pulled up to 3V3)
//   D7        44     I2C SCL     -> TAS5825M SCL  (also pulled up to 3V3)
//   D8         7     SD SCK
//   D9         8     SD MISO
//   D10        9     SD MOSI
//
// Bottom pad (accessed via via on carrier PCB under the module):
//   PAD       38     Status LED
//
// On/off switch SW1: inline between 4S BMS B+ and the buck converter +
//   amp Vcc rail. Slide switch must be rated >= 5A.
// TAS5825M PDN: pulled high to 3V3 via 10k (always on, no GPIO needed).
// TAS5825M FAULTZ: not connected (open-drain output, monitor optionally).

// --- Audio (I2S → TAS5825M) ---
#define PIN_I2S_BCLK   4
#define PIN_I2S_LRCLK  5
#define PIN_I2S_DOUT   6

// --- I2C (TAS5825M control) ---
#define PIN_I2C_SDA   43
#define PIN_I2C_SCL   44

// --- microSD (SPI) ---
#define PIN_SD_CS      3
#define PIN_SD_SCK     7
#define PIN_SD_MISO    8
#define PIN_SD_MOSI    9

// --- Controls / indicators ---
#define PIN_VOL_POT    1   // ADC1_CH0
#define PIN_BUTTON     2   // active-low, INPUT_PULLUP
#define PIN_LED       38   // bottom-pad GPIO (carrier PCB exposes via)

// --- Audio behaviour ---
#define AUDIO_VOLUME_MAX  21  // ESP32-audioI2S volume scale (0..21)
#define MUSIC_DIR    "/music"  // top-level folder on SD; subfolders are albums

// --- TAS5825M ---
//   ADR pin tied to GND on the module = address 0x4C.
//   Tie ADR to 3V3 for 0x4D (alternate, useful if you wire two amps).
#define TAS5825M_I2C_ADDR  0x4C

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
