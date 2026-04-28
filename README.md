# ESP32-MusicPlayer-Battery

A portable, battery-powered MP3 player built on the **Seeed XIAO ESP32-S3** with
a **MAX98357A** I²S amplifier, **microSD** music storage, and an **IP5306**
18650 power module. Designed for low-SMT hand assembly: most of the
"hard" parts are pre-made breakout modules dropped onto a carrier PCB.

Status: **scaffold / unverified on hardware.** The firmware compiles against the
listed library versions and the architecture is sound, but it has not yet been
tested on a physical device. Changes are likely once the prototype boots.

## Features

- **MP3 / AAC / WAV / FLAC** playback from microSD via I²S → MAX98357A
- **Wi-Fi captive portal** for first-boot setup (WiFiManager)
- **Web UI** (responsive, mobile-friendly) — play / pause / next / volume,
  library browser, multi-file upload to SD
- **OTA updates** for firmware (ElegantOTA at `/update`) and music (HTTP upload)
- **Physical controls**: 10 kΩ pot for volume, momentary push button
  (short = next track, long = next album, double-tap = previous)
- **LED status**: solid = playing, slow blink = idle, fast blink = OTA / upload,
  heartbeat = setup AP mode
- **Single-cell 18650** battery with charge + boost + protection on one IP5306
  module; on/off switch in series with the battery

## Hardware

See [`docs/BOM.md`](docs/BOM.md) for parts list and [`docs/PINMAP.md`](docs/PINMAP.md)
for the GPIO assignments. A wiring diagram lives in
[`docs/SCHEMATIC.md`](docs/SCHEMATIC.md).

Top-level block diagram:

```
                       ┌──────────────────────────┐
   18650 ── [SW1] ──── │  IP5306 charge+boost     │ ── 5V ──┬─── XIAO ESP32-S3 (3V3)
        ↑              │  (USB-C charge in)       │          │
   protection in       └──────────────────────────┘          │
                                                             ├── MAX98357A (Vin=5V) ── 4Ω 5W speaker
                                                             ├── microSD socket (3V3 logic)
                                                             ├── 10k pot → ADC
                                                             ├── push-button → GPIO
                                                             └── LED → GPIO
```

## Software

**Firmware** (`src/`, `include/`):
- Arduino framework on PlatformIO
- Libraries:
  [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S),
  [ESPAsyncWebServer](https://github.com/ESP32Async/ESPAsyncWebServer),
  [WiFiManager](https://github.com/tzapu/WiFiManager),
  [ElegantOTA](https://github.com/ayushsharma82/ElegantOTA),
  ArduinoJson

**Web UI** (`data/`): plain HTML + CSS + JS, served from LittleFS. No build step.

### Build & flash

Install [PlatformIO](https://platformio.org/) (VS Code extension or `pip install platformio`), then:

```sh
pio run                  # compile firmware
pio run -t upload        # flash firmware over USB
pio run -t uploadfs      # upload web UI in data/ to LittleFS
pio device monitor       # serial console (115200 baud)
```

After the first flash, future firmware updates can be done over the air via
`http://esp-music.local/update` from the web UI.

### First-boot Wi-Fi setup

1. Power on. The LED double-blinks → device is broadcasting an open AP named
   `ESP-Music-Setup-XXXXXX`.
2. Connect a phone or laptop to that AP. A captive portal should pop up
   automatically (otherwise visit `http://192.168.4.1`).
3. Pick your home Wi-Fi, enter the password, save. The device reboots and
   joins your network.
4. Open `http://esp-music.local/` (or whatever IP it printed on serial). The
   library page is the home; firmware OTA is at `/update`.

To force re-provisioning later, hit **Forget Wi-Fi** in the web UI or hold the
button while booting (not yet implemented — see TODO).

### Loading music

Two ways:

1. **microSD over a card reader** (fastest for big libraries): create
   `/music/<Album>/*.mp3` on the SD, insert into the player. Press *↻ rescan* in
   the UI.
2. **Web upload**: pick an album name, choose one or more audio files, hit
   *upload*. Files stream to the SD card; the library auto-rescans on completion.

## Repository layout

```
.
├── platformio.ini       # firmware build config (target: seeed_xiao_esp32s3)
├── include/config.h     # pin map and firmware tunables
├── src/main.cpp         # firmware
├── data/                # web UI (uploaded to LittleFS via `pio run -t uploadfs`)
│   ├── index.html
│   ├── app.js
│   └── style.css
├── docs/                # hardware spec
│   ├── BOM.md           # parts list with concrete SKUs and distributor links
│   ├── MODULES.md       # pinouts and mechanical dimensions of each module
│   ├── NETLIST.md       # every electrical net (source of truth for the schematic)
│   ├── PINMAP.md        # MCU GPIO assignments
│   ├── PCB_PLAN.md      # board outline, placement, layer plan, JLCPCB order spec
│   └── SCHEMATIC.md     # ASCII wiring + EMI/decoupling notes
├── pcb/                 # KiCad project (draw locally — see pcb/README.md)
└── README.md            # you are here
```

## Hardware-first checklist

If you're starting from parts, follow this order:

1. **Order parts** using [`docs/BOM.md`](docs/BOM.md). Sanity-check the
   "before you buy" list at the bottom.
2. **Draw the schematic and PCB** in KiCad using
   [`docs/NETLIST.md`](docs/NETLIST.md) and
   [`docs/PCB_PLAN.md`](docs/PCB_PLAN.md). Skeleton + step-by-step in
   [`pcb/README.md`](pcb/README.md).
3. **Order the PCB** from JLCPCB / PCBWay using the gerbers exported from
   KiCad (see `docs/PCB_PLAN.md` §6).
4. **Assemble** following `docs/PCB_PLAN.md` §7. Bring up on a bench supply
   before inserting the cell.
5. **Flash firmware + web UI** (see *Build & flash* above).

## Roadmap / TODO

- [ ] Verify on hardware and adjust pin map / I²S timings as needed
- [ ] Commit the KiCad project under `pcb/` after the schematic is drawn
- [ ] Boot-time button hold to force Wi-Fi reset (no UI access required)
- [ ] Persistent state (last played track, volume) in NVS
- [ ] ID3 tag parsing for nicer track names
- [ ] Battery voltage sensing on a free ADC + low-battery LED pattern

## License

Pick one before publishing. MIT or Apache-2.0 are reasonable defaults for
hardware/firmware projects of this kind.
