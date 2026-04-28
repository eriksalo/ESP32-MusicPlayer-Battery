# Schematic / wiring notes

This is an ASCII reference for prototyping on a breadboard or for laying out
the carrier PCB. A KiCad project will live under `pcb/` once the prototype is
verified on hardware.

## Power chain

```
   18650 (+)──┬──[ SW1 ]──┬─ IP5306 BAT+
              │            │
              └ protection inside IP5306
                           ▼
                 IP5306 5V-OUT ──── 5V rail ─────────────┬──→ XIAO ESP32-S3 5V pin (USB pin)
                                                         ├──→ MAX98357A Vin
                                                         └──→ microSD breakout Vcc (if 5V-tolerant)
                                                                  ↑
                       (most microSD modules want 3V3, take from XIAO 3V3 pin instead)

   IP5306 USB-C IN ←── USB-C cable for charging
   IP5306 GND ──── common ground bus
```

Notes:
- `SW1` is a SPST in series with the cell so the IP5306 boost itself is also
  switched off (otherwise the boost idles ~1–5 mA continuously, which kills the
  battery in storage).
- The XIAO ESP32-S3 has its own USB-C connector for **flashing and serial
  debug**; it can also be used to power the board (the on-board LDO regulates
  to 3V3). For battery operation you feed 5V into the 5V pin from the IP5306.
- If you want both the XIAO USB-C **and** the IP5306 USB-C live simultaneously
  without back-feeding, add a Schottky on the IP5306 5V output.

## Audio (I²S)

```
   XIAO  ──── BCLK  (GPIO4) ──→ MAX98357A  BCLK
   XIAO  ──── LRC   (GPIO5) ──→ MAX98357A  LRC
   XIAO  ──── DOUT  (GPIO6) ──→ MAX98357A  DIN
   5V    ────────────────────→ MAX98357A  Vin    (+ 100 nF + 10 µF decoupling)
   GND   ────────────────────→ MAX98357A  GND
                              MAX98357A  GAIN  ── leave floating (9 dB)
                              MAX98357A  SD/MODE ── tie to Vin (always on, mono = L+R)
                              MAX98357A  OUT+ ──┐
                              MAX98357A  OUT-  ─┘──→ 4Ω 5W speaker (twisted pair to reduce EMI)
```

## SD card (SPI)

```
   XIAO ── SCK   (GPIO7) ──→ SD CLK
   XIAO ── MISO  (GPIO8) ←── SD DO
   XIAO ── MOSI  (GPIO9) ──→ SD DI
   XIAO ── CS    (GPIO3) ──→ SD CS
   3V3 / GND from XIAO
```

The firmware initialises SPI at 20 MHz; if you see CRC errors, lower it in
`src/main.cpp` (`SD.begin(PIN_SD_CS, SPI, 20000000)` → `4000000`).

## Controls and indicator

```
   3V3 ── pot end  ┐
                   ├── 10 kΩ pot, wiper → XIAO D0 (GPIO1)
   GND ── pot end  ┘

   XIAO D1 (GPIO2, INPUT_PULLUP) ── tactile button ── GND

   XIAO D6 (GPIO43) ── 470 Ω ── LED anode; cathode → GND
```

## Layout / EMI tips

- Keep the I²S clock traces (BCLK, LRC) short and away from the antenna end of
  the XIAO module.
- Run the speaker leads as a twisted pair; don't share ground with the digital
  return path on the same trace.
- Decouple MAX98357A Vin with **10 µF + 100 nF** placed within ~5 mm of its
  Vin pin. Without this you may hear the SD card seek noise through the
  speaker.
- The XIAO ESP32-S3 antenna is on the end opposite USB-C; leave a clear
  keep-out around it on the carrier PCB.

## Future PCB notes

When laying out the KiCad board:

- Put the **module footprints as castellated edge cutouts** so the modules
  sit flush. JLCPCB/PCBWay handle this fine in 2-layer.
- A panel-mount 10 kΩ pot, slide switch, and 3.5 mm tactile button can all
  be wired off the PCB if the enclosure dictates.
- If you prefer SMD instead of breakouts: MAX98357A is a TQFN-16 you can
  hand-solder with a hot-air station, and the IP5306 functionality can be
  collapsed to TP4056 + DW01 + MT3608 SOIC parts. Keep the IP5306 module
  for the first revision.
