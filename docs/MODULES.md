# Module reference cards

Pinouts and mechanical data for every module on the carrier PCB. Use these
when laying out the schematic and PCB. **Verify against the datasheet of
the exact module you receive — clones differ slightly.**

---

## U1 — Seeed XIAO ESP32-S3

**Mechanical**: 21.0 × 17.5 × 3.5 mm. Castellated edges + bottom pads,
plus 2 × 7-pin 2.54 mm header rows on top.

The carrier PCB also exposes a **bottom-side via** beneath the module to
access **GPIO38**, used for the status LED. (See `PINMAP.md`.)

| XIAO label | GPIO | Function in this design |
|------------|------|------------------------|
| 5V | — | Power input from buck (U5) |
| 3V3 | — | LDO output, available on the +3V3 rail |
| GND | — | Common ground |
| D0  | 1  | Volume potentiometer (ADC1_CH0) |
| D1  | 2  | Push button (active-low, INPUT_PULLUP) |
| D2  | 3  | SD CS |
| D3  | 4  | I²S BCLK |
| D4  | 5  | I²S LRCLK |
| D5  | 6  | I²S DOUT |
| D6  | 43 | I²C SDA |
| D7  | 44 | I²C SCL |
| D8  | 7  | SD SCK |
| D9  | 8  | SD MISO |
| D10 | 9  | SD MOSI |
| (bottom pad) | 38 | Status LED (carrier PCB exposes a via under the module) |

**Footprint**: use the official Seeed footprint from
[`OPL_Kicad_Library`](https://github.com/Seeed-Studio/OPL_Kicad_Library)
(symbol: `XIAO-ESP32S3`, footprint: `XIAO-ESP32-S3`). The footprint includes
the bottom castellated pads — drop a small via to GPIO38 in the carrier
PCB to access the LED line.

---

## U2 — TAS5825M stereo I²S amp breakout

**Mechanical**: varies by manufacturer. Adafruit's TAS5825M breakout is
~36 × 22 mm with two 2.54 mm 1×6 + 1×4 headers. AliExpress modules are
similar size with all signals on a single 2 × 7 or 1 × 14 header.

```
    Adafruit-style breakout (verify against your specific board):

       ┌────────────────────────────────────┐
       │ 2-pin terminal block: SPK_L+/L-    │
       │                                    │
       │       TAS5825M                     │
       │                                    │
       │  Vcc GND PDN ADR  SDIN BCLK LRCLK  │
       │  ┌──┬──┬──┬──┐    ┌──┬──┬────┐    │
       │  │  │  │  │  │    │  │  │    │    │
       │  └──┴──┴──┴──┘    └──┴──┴────┘    │
       │       │  │            ↑            │
       │       │  │       I²S audio in      │
       │       │  └─ I²C addr select        │
       │       └──── shutdown               │
       │  SDA SCL FAULTZ (additional pins)  │
       │  ┌──┬──┬──┐                       │
       │                                    │
       │ 2-pin terminal block: SPK_R+/R-    │
       └────────────────────────────────────┘
```

**Pin function summary** (pin order varies — go by silkscreen label):

| Label | Connection in this design |
|-------|---------------------------|
| Vcc / VBAT | 4S rail (~14 V nominal, 16.8 V max) — **directly from BMS output via SW1** |
| GND | Common ground |
| PDN (active-low shutdown) | Tie to **+3V3 via R4 (10 kΩ)** — chip stays always-on; no GPIO needed |
| ADR | Tie to **GND** (I²C addr 0x4C). To 3V3 → 0x4D. |
| SDIN | I²S data in ← XIAO `PIN_I2S_DOUT` (GPIO6) |
| BCLK | I²S bit clock ← XIAO `PIN_I2S_BCLK` (GPIO4) |
| LRCLK | I²S word select ← XIAO `PIN_I2S_LRCLK` (GPIO5) |
| SDA | I²C data ↔ XIAO `PIN_I2C_SDA` (GPIO43). 4.7 kΩ pull-up to **+3V3** (R2). |
| SCL | I²C clock ← XIAO `PIN_I2C_SCL` (GPIO44). 4.7 kΩ pull-up to **+3V3** (R3). |
| FAULTZ | open-drain fault output. Optional — leave NC, or pull to 3V3 and route to a free GPIO if you want to read fault status. |
| SPK_L+, SPK_L- | Left speaker (BTL — do not ground either side) |
| SPK_R+, SPK_R- | Right speaker (BTL — do not ground either side) |

> Some breakouts already include 4.7 kΩ I²C pull-ups on SDA/SCL — check
> with a multimeter before populating R2/R3. Two pull-ups in parallel won't
> cause harm but lowers the bus impedance more than necessary.

**Performance budget at 14 V**: ~15 W RMS into 4 Ω per channel BTL, or
~25 W per channel briefly under transient. Headroom is comfortable for
"loud" use of 3″ full-range drivers.

**I²C address**: 0x4C (ADR pin → GND) by default. The init code in
`src/main.cpp` writes a small register sequence (page 0 / book 0,
DEVICE_CTRL_2 = Play, DIG_VOL = -24 dB) at boot. Defaults handle BTL
stereo and auto-detect of sample rate.

---

## U3 — microSD breakout

Same as 1S build — 6-pin SPI breakout, 3V3 logic. See `PINMAP.md` for
GPIO assignments.

| Pin | Connection |
|-----|------------|
| VCC | +3V3 |
| GND | GND |
| CS | XIAO GPIO3 |
| MOSI | XIAO GPIO9 |
| SCK | XIAO GPIO7 |
| MISO | XIAO GPIO8 |

---

## U4 — IP2368 USB-C PD all-in-one charger module

**Mechanical**: typical hobby boards are 50–60 × 25–30 mm with a USB-C
connector on one end and 4 fuel-gauge LEDs on top.

**Block diagram (functional)**:

```
   USB-C IN ──┬── USB-C PD controller (negotiates 5/9/12/15/20 V)
              │
              ▼
       ┌──────────────────┐
       │      IP2368      │  bidirectional buck/boost charger
       │                  │
       │  4S charge logic │  CC/CV terminating at 16.8 V
       │  Cell balancer   │  via balance taps
       │  Fuel gauge      │  4 LEDs on top
       │  USB output PD   │  optional (not used here)
       └──────────────────┘
              │
              ├── BAT+/BAT- → 4S pack (through BMS)
              ├── BAL1..BAL3 → cell taps for balance charging
              ├── 5V output (optional) → not used; we have our own buck
              └── Fault / status pins
```

**Pin function summary** (varies by module; verify against silkscreen):

| Label | Connection |
|-------|------------|
| BAT+ | 4S BMS B+ |
| BAT- | 4S BMS B- (= GND) |
| BAL1, BAL2, BAL3 | Cell taps after BT1, BT2, BT3 (balance harness) |
| GND | Common ground |
| (optional) 5V_OUT | Not used. Leave NC. |

> **Important**: The IP2368 module manages its own USB-C connector. Do
> not also expose the 5 V output to your PCB unless you've added a
> Schottky on the buck path — back-feeding will damage things.

**Charging time**: a 65 W USB-C PD charger negotiates 20 V × 3.25 A. The
IP2368 throttles to whatever the cells can take (typically 1 C, so ~3 A
into 3000 mAh = 1 hour to charge a depleted 4S pack).

---

## U5 — 4S → 5 V buck converter module

**Mechanical**: MP1584-based "Mini-360" modules are tiny (~22 × 17 mm,
4 pins). LM2596 modules are ~45 × 20 mm.

| Pin | Connection |
|-----|------------|
| VIN+ | 4S rail (~14 V) — same node as TAS5825M Vcc, downstream of SW1 |
| VIN- | GND |
| VOUT+ | +5 V (XIAO 5 V pin and microSD VCC) |
| VOUT- | GND |

> **Critical first-time setup**: the trim pot on the buck module sets
> output voltage. Connect VIN to a bench supply at 14 V, **before
> connecting the XIAO**, and adjust the trim until VOUT reads exactly
> 5.0 V. Mark the pot with a dab of thread-lock so it doesn't drift.

---

## BMS — 4S 30 A Li-ion BMS

**Mechanical**: thin PCB, ~50 × 20 × 4 mm. Wires out to the cell terminals
and balance taps.

```
    Cells:        BMS:
    BT1 (+)  ──────  B+
    BT1 (-) /BT2(+)  B1
    BT2 (-) /BT3(+)  B2
    BT3 (-) /BT4(+)  B3
    BT4 (-)  ──────  B-

    BMS output to PCB:
    P+  → SW1 → carrier PCB +14V
    P-  → carrier PCB GND (also to IP2368 GND)
```

**Things the BMS does for you**:
- Per-cell over- and under-voltage protection (~3.0 V cutoff, 4.25 V trip).
- Pack-level over-current and short-circuit protection.
- Balance during charge (slow, but adequate).

**Things the BMS does NOT do**:
- Charging — the IP2368 handles charge current and termination.
- Reverse polarity protection — that's on you and the connector keying.

---

## RV1 — 10 kΩ panel-mount potentiometer

Same as 1S build. Linear B10K, 3 lugs:
- CCW (lug 1) → GND
- Wiper (lug 2) → XIAO GPIO1 (ADC)
- CW (lug 3) → +3V3

If the volume goes the wrong way, swap lugs 1 and 3.

---

## SW1 — 4S power slide / rocker switch

**Must be rated ≥ 5 A** to handle peak amp current. Wire **between the
BMS P+ output and the carrier PCB +14 V input**. The IP2368's USB-C
charging path remains live when SW1 is off, so you can charge with the
device powered down.

> A small toggle or rocker switch fits the panel best. Avoid the tiny
> SS12D00 slide — it's only 0.3 A rated.

---

## SW2 — momentary push button

**Active-low** to GND. XIAO GPIO has internal pull-up enabled in
firmware — 2-pin connection only.

---

## D1 — status LED

5 mm or 3 mm. Anode through R1 (470 Ω) to **XIAO GPIO38** (bottom-pad
via on the carrier PCB), cathode to GND.

---

## Speakers (LS1, LS2)

**4 Ω, 15–25 W rated, 3″–4″ full-range drivers, identical pair.**

Recommended:
- **Visaton FRS 8 (4 Ω, 30 W, 80 mm)** — clean, neutral, well-matched.
- **Dayton ND91-4 (4 Ω, 25 W, 91 mm)** — slightly more bass, bigger.
- AliExpress 3″ 4 Ω 20 W full-range — cheap, decent, variable QC.

**Wiring**: each driver to its own JST-XH 2-pin connector on the carrier
PCB. **Do not bridge SPK+/SPK- to ground** — the TAS5825M is bridge-tied
load (BTL), both terminals swing.

**Enclosure**: a sealed enclosure is **mandatory** at this driver size.
Open-back / vented kills the low end. ~0.3–0.5 L per driver of internal
volume is a good starting point.
