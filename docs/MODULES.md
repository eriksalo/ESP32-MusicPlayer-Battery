# Module reference cards

Pinouts and mechanical data for every module on the carrier PCB. Use these
when laying out the schematic and PCB. Verify against the datasheet of the
exact module you receive — clones differ slightly.

---

## U1 — Seeed XIAO ESP32-S3

**Mechanical**: 21.0 × 17.5 × 3.5 mm. Castellated edges + bottom pads, also
2 × 7-pin 2.54 mm header rows on top side (one row of 7 pins per long edge).

```
                       USB-C
                  ┌──────────┐
                  │          │
              5V ─┤ 1     14 ├─ 3V3
             GND ─┤ 2     13 ├─ GND
            3V3 ─┤ 3     12 ├─ GPIO9   (D10, MOSI)
       GPIO1/D0 ─┤ 4     11 ├─ GPIO8   (D9,  MISO)
       GPIO2/D1 ─┤ 5     10 ├─ GPIO7   (D8,  SCK)
       GPIO3/D2 ─┤ 6      9 ├─ GPIO44  (D7,  RX)
       GPIO4/D3 ─┤ 7      8 ├─ GPIO43  (D6,  TX)
       GPIO5/D4 ─┤
       GPIO6/D5 ─┤  (D4 and D5 are pins 8 and 9 on the LEFT row,
                     but the board breaks all 11 GPIOs on the two side rows
                     — see Seeed's datasheet for exact pin numbering.)
                  └──────────┘
```

> The XIAO datasheet's pin numbering is the authoritative reference. The map
> above is for orientation only — match by **silkscreen label** (D0..D10, 5V,
> GND, 3V3) on the actual module, not pin number.

**Footprint**: use the official Seeed footprint from
[`seeed-kicad-library`](https://github.com/Seeed-Studio/OPL_Kicad_Library)
(symbol: *XIAO-ESP32S3*, footprint: *XIAO-ESP32-S3*). It models both the
castellated edges and the bottom pads — solder either way.

**Power**:
- Feed **5 V** into the 5 V pin from the IP5306. The XIAO's on-board LDO drops
  to 3V3 (capable of ~500 mA out on the 3V3 pin for downstream loads).
- USB-C on the XIAO is used for **flashing and serial debug**, not battery
  power. Don't connect 5 V from XIAO USB and the IP5306 5 V together unless
  you add a Schottky on the IP5306 side.

---

## U2 — MAX98357A I²S amp (Adafruit #3006 layout)

**Mechanical**: 20.6 × 17.8 mm; 7 pins on a 2.54 mm header row on one long edge.

```
       ┌─────────────────────────┐
       │     MAX98357A breakout  │
       │                         │
       │  Vin GND SD GAIN DIN BCLK LRC │
       └────┴────┴──┴────┴───┴────┴────┘
          1   2  3   4    5   6    7
```

| Pin | Name | Connection |
|-----|------|------------|
| 1 | Vin | 5 V rail (with 10 µF + 100 nF decoupling within ~5 mm) |
| 2 | GND | Ground |
| 3 | SD / MODE | Tie to **Vin** for "always on, mono = (L+R)/2". (Float = also enabled but L only; tie 1.4 V = right only; GND = shutdown.) |
| 4 | GAIN | **Leave floating = 9 dB.** GND = 12 dB, Vin = 6 dB. |
| 5 | DIN | I²S data in ← XIAO `PIN_I2S_DOUT` (GPIO6) |
| 6 | BCLK | I²S bit clock ← XIAO `PIN_I2S_BCLK` (GPIO4) |
| 7 | LRC | I²S word select ← XIAO `PIN_I2S_LRCLK` (GPIO5) |

**Outputs** are differential class-D on a separate 2-pin block: `Speaker +`,
`Speaker -`. **Do not** ground either side — it's a bridge-tied load.

**Performance budget**: 3.2 W into 4 Ω at 5 V (rated, 10 % THD). With a 4 Ω
5 W full-range driver in a sealed enclosure this is plenty loud for personal
or small-room use.

---

## U3 — microSD breakout (SPI mode)

**Mechanical**: typical Adafruit #4682 is 39 × 24 mm; clones vary slightly.
Most expose a 6-pin header.

| Pin | Name | Connection |
|-----|------|------------|
| 1 | 3V3 (or VCC) | XIAO 3V3 pin (or 5 V if the module has a regulator + level shifter, but prefer 3V3 direct) |
| 2 | GND | Ground |
| 3 | CS | XIAO `PIN_SD_CS` (GPIO3) |
| 4 | MOSI | XIAO `PIN_SD_MOSI` (GPIO9) |
| 5 | SCK / CLK | XIAO `PIN_SD_SCK` (GPIO7) |
| 6 | MISO | XIAO `PIN_SD_MISO` (GPIO8) |

**Card detect / write protect** pins are usually not exposed on small breakouts.
Firmware uses a simple "is the card mountable" check at boot.

---

## U4 — IP5306 18650 charger + boost module

There are several common form factors. The block diagram and pin labels
below describe the typical hobby module — confirm against your specific
board's silkscreen.

```
         ┌───────────────────────────────────┐
         │        USB-C input (charging)     │
         │   ┌─────┐                         │
         │   │ USB │   IP5306 IC             │
         │   └─────┘                         │
         │                                   │
         │   BAT+  BAT-     OUT+  GND        │
         └────┬─────┬────────┬─────┬─────────┘
              │     │        │     │
              │     │        └─── 5 V to carrier PCB
              │     └─── battery -
              └──────── battery + (via SW1)
```

**Pads / pins to watch for**:
- `BAT+` / `B+`: 18650 positive (through SW1)
- `BAT-` / `B-`: 18650 negative
- `OUT+` / `5V` / `VOUT`: 5 V boost output
- `GND` / `OUT-`: shared ground
- An on-board push-button on some variants is for the fuel-gauge LEDs and is
  **not** a power-on input on auto-on variants.

**Auto-on**: confirm in the listing or datasheet. Some IP5306 modules require
a button press to enable the boost; you want one that powers on as soon as
load is drawn (so the slide switch SW1 fully controls power).

**Quiescent draw with no load**: ~5 mA on most boards. SW1 in the BAT+ line
defeats this when the player is "off".

**Charge current**: IP5306 supports up to 2.1 A charge via USB-C. Use a 2 A
USB-C charger to charge a 3000 mAh cell in roughly 2 hours.

---

## H1 — 18650 holder (Keystone 1042 or similar)

**Mechanical**: 76.0 × 21.0 × 19.5 mm with cell installed. Two PCB pins on
each end (positive + negative), 65 mm pin centre-to-pin centre.

Mount on the back side of the PCB if you can — keeps the front panel clear.

---

## RV1 — 10 kΩ panel-mount potentiometer

**Mechanical**: 6 mm D-shaft, 7 mm threaded bushing, M7×0.75, ~10 mm panel
hole. Three solder lugs on 5 mm centres.

| Lug | Connection |
|-----|------------|
| 1 (CCW end) | GND |
| 2 (wiper)   | XIAO `PIN_VOL_POT` (GPIO1) |
| 3 (CW end)  | 3V3 |

> If the volume goes the wrong way, swap lugs 1 and 3.

A small 100 nF cap from wiper to GND is optional but reduces ADC jitter on
slow movements. The firmware also low-pass-filters with hysteresis, so this
isn't strictly required.

---

## SW1 — power slide switch

Wire the **common** lug between the 18650 `+` terminal and the IP5306 `BAT+`
input. The switch must carry the IP5306's input current, which under heavy
charging can spike near 2 A — choose a part rated ≥ 2 A.

---

## SW2 — momentary push button

**Active-low** to GND. The XIAO GPIO has internal pull-up enabled in firmware,
so you only need a 2-pin connection from button to GND.

For a 12 mm panel-mount button, a series 100 Ω current-limiting resistor in
the GPIO line is cheap insurance against ESD.

---

## D1 — status LED

5 mm or 3 mm, anode through R1 (470 Ω) to XIAO `PIN_LED` (GPIO43), cathode to
GND. Pick a colour visible against your enclosure — green/blue read well in
both light and dark.
