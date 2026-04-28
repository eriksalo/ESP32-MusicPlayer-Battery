# ESP32-MusicPlayer-Battery

A portable, battery-powered stereo MP3 player built on the **Seeed XIAO
ESP32-S3**, with a **PCM5102A** I²S DAC into a **TPA3116D2** stereo class-D
amplifier, **microSD** music storage, a **4S 18650** Li-ion pack, and an
**IP2368** USB-C PD charger module. Designed for low-SMT hand assembly:
every "hard" part is a pre-made breakout module dropped onto a carrier
PCB. **No on-board ICs to hand-solder beyond passives.**

Status: **scaffold / unverified on hardware.** The firmware and the
hardware spec are sound, but no prototype has been built yet. Changes are
likely once the first board is on the bench.

## Features

- **Stereo MP3 / AAC / WAV / FLAC** playback from microSD via
  XIAO → PCM5102A I²S DAC → TPA3116D2 class-D amp
- **~2 × 25 W into 4 Ω** (BTL) into a pair of 3″–4″ full-range drivers
- **4 × 18650 cells (4S, ~14.8 V nominal)** with 4S BMS protection
- **USB-C PD charging** via IP2368 (negotiates up to 100 W) — **charges
  while playing**, like a phone or laptop
- **Wi-Fi captive portal** for first-boot setup (WiFiManager)
- **Web UI** (responsive, mobile-friendly) — play / pause / next / volume,
  library browser, multi-file upload to SD
- **OTA updates** for firmware (ElegantOTA at `/update`) and music (HTTP upload)
- **Physical controls**: 10 kΩ pot for volume, momentary push button
  (short = next track, long = next album, double-tap = previous)
- **LED status**: solid = playing, slow blink = idle, fast blink = OTA / upload,
  heartbeat = setup AP mode

## Hardware

See [`docs/BOM.md`](docs/BOM.md) for parts list with purchase links and
[`docs/PINMAP.md`](docs/PINMAP.md) for GPIO assignments. Wiring diagrams
in [`docs/SCHEMATIC.md`](docs/SCHEMATIC.md), full netlist in
[`docs/NETLIST.md`](docs/NETLIST.md), board layout plan in
[`docs/PCB_PLAN.md`](docs/PCB_PLAN.md).

Top-level block diagram:

```
                          ┌─────────────────┐
   USB-C PD charger ───► │   IP2368 module  │ ──── BAT+/BAT-/BAL × 3 ─────┐
                         │ (PD trig + 4S CC/CV│                            │
                         │  + balance + gauge) │                          │
                         └─────────────────────┘                          │
                                                                          │
                  ┌──────────────┐                                        │
                  │ 4S BMS (30 A)│ ◄───── 4 × 18650 series + balance taps ┘
                  │ common port  │                ▲
                  └─────┬────────┘                │
                        │                          │ JST-XH 5-pin balance
                       P+ ── [ SW1 ≥5 A ] ── +14V_SW ─────┬─── TPA3116D2 Vcc
                                                          │           │
                                                          │           └─► L+/L-, R+/R-
                                                          │                  ↓
                                                          │                2 × 4 Ω
                                                          │
                                                          └─── buck → +5V ─┬─ XIAO ESP32-S3
                                                                            ├─ PCM5102A DAC
                                                                            └─ microSD

   I²S   XIAO → PCM5102A    (digital stereo audio)
   analog L/R PCM5102A → TPA3116D2  (DAC → amp)
   pot, button, LED ── XIAO GPIOs
```

## Software

**Firmware** (`src/`, `include/`):
- Arduino framework on PlatformIO
- Libraries:
  [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S),
  [ESPAsyncWebServer](https://github.com/ESP32Async/ESPAsyncWebServer),
  [WiFiManager](https://github.com/tzapu/WiFiManager),
  [ElegantOTA](https://github.com/ayushsharma82/ElegantOTA),
  ArduinoJson. (No I²C / Wire library used — both audio modules are
  fully strapped on their breakouts.)

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

1. **Order parts** using [`docs/BOM.md`](docs/BOM.md) — every line has a
   purchase link. Sanity-check the "before you buy" list at the bottom.
2. **Draw the schematic and PCB** in KiCad. The netlist generator at
   [`pcb/gen_netlist.py`](pcb/gen_netlist.py) emits an importable
   `.net` — one click in KiCad PCB Editor populates all components and
   ratsnest connections. See [`pcb/README.md`](pcb/README.md) for the
   step-by-step workflow.
3. **Order the PCB** from JLCPCB / PCBWay using the gerbers exported from
   KiCad (see [`docs/PCB_PLAN.md`](docs/PCB_PLAN.md) §6).
4. **Assemble** following [`docs/PCB_PLAN.md`](docs/PCB_PLAN.md) §7.
   Bring up on a bench supply (trim the buck to 5.0 V *first*) before
   plugging in the 4S pack.
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
