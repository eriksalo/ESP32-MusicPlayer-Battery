# Bill of Materials

**Configuration**: 4S 18650 + IP2368 USB-C PD charger + TAS5825M stereo I²S
amp + 2 × 4 Ω full-range drivers, ~30 W total. Handheld form factor
(~22 × 13 × 8 cm).

Two columns: **western (Adafruit / DigiKey / Mouser / Amazon)** for fast
shipping and **AliExpress / generic** for cheaper sourcing if you don't mind
3–4 week lead times. Prices are USD ~2026, indicative only.

> Buy **two of every module and connector** for a first build — they're
> inexpensive and cheaper than the lost weekend recovering one.

## 1. Active modules

| Ref | Part | Western source | Generic source | ~$ | Notes |
|-----|------|----------------|----------------|-----|-------|
| **U1** | Seeed XIAO ESP32-S3 | [seeedstudio.com #113991054](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html) · DigiKey 1597-113991054-ND | AliExpress "Seeed XIAO ESP32-S3" (verify Bazaar/Seeed seller) | $7.50 | **Plain XIAO ESP32-S3**, not "Sense", not "Plus". 8 MB flash + 8 MB PSRAM. |
| **U2** | TAS5825M stereo I²S amp breakout | [Adafruit #6451 TAS5825M breakout](https://www.adafruit.com/product/6451) (or the older TAS5825M kit) · DigiKey 296-TAS5825MRHBT-ND (chip) | AliExpress "TAS5825M I2S amplifier 30W" / "TAS5825M development board" | $15 / $5 | Stereo 2 × ~15 W into 4 Ω at 14 V. I²C control + I²S audio. **Select a breakout that exposes SDA/SCL/PDN/FAULTZ on a header.** |
| **U3** | microSD card breakout (SPI) | [Adafruit #4682](https://www.adafruit.com/product/4682) | AliExpress "Micro SD card module 3V3" | $4 / $1 | 3V3 logic. Push-pull / push-push socket either OK. |
| **U4** | IP2368 USB-C PD all-in-one 4S charger module | [DFRobot DFR1015](https://www.dfrobot.com/product-2700.html) (similar PMIC) · or specifically search "IP2368 4S Li-ion charger 100W USB-C PD module" | AliExpress "IP2368 module 4S 100W bidirectional" | $8–12 | Single module: USB-C PD input (negotiates up to 20 V / 5 A), 4S balance charging, fuel-gauge LEDs, optional discharge output. **Confirm the listing covers 4S** — the IP2366 variant is 1S–3S only. |
| **U5** | 4S → 5 V buck converter module | DigiKey LMR16006XDDCT (chip) · Pololu D24V10F5 module | AliExpress "MP1584 mini 360 buck module" / "LM2596 buck" | $1–3 | 5 V @ 1 A. Adjust the trim pot to exactly 5.0 V before connecting it to the XIAO 5 V pin. **MP1584 is fine; LM2596 also works but is less efficient.** |
| **BMS** | 4S 30 A Li-ion BMS with balance leads | [Battery Hookup](https://batteryhookup.com/) "4S BMS" | AliExpress "4S 30A balanced BMS 18650 li-ion" | $5 | Required even if your IP2368 module advertises balance — the BMS protects against discharge over-current and short. Pick one with ≥ 30 A continuous rating to handle peak amp draw. |

## 2. Battery and speakers

| Ref | Part | Source | ~$ | Notes |
|-----|------|--------|-----|-------|
| **BT1–BT4** | 4 × 18650 cells, 3000–3500 mAh, flat-top | Liion Wholesale, IMR Batteries, 18650BatteryStore — Samsung 30Q / Molicel P26A / LG HG2 | $5–9 each | **Buy from a reputable cell vendor.** Use **identical cells** (same make, capacity, ideally same date code) for balanced 4S behaviour. |
| **H1** | 4 × 18650 PCB-mount holder, **series wired** | Keystone 1042 × 4 + nickel strips, or a single 4-cell series holder (search "4×18650 series holder battery box") | $3–10 | Single-piece holders pre-wire the cells in series with one + and one − terminal exposed (and a balance tap on better ones). Single-piece is dramatically easier to assemble. |
| **LS1** | 2 × 4 Ω 15–25 W full-range driver, 3″ | **Visaton FRS 8** (4 Ω, 30 W, 80 mm) — DigiKey 1497-1090-ND ($25 ea) · **Dayton ND91-4** (4 Ω, 25 W, 91 mm — slightly bigger) · **PUI Audio AS07104PR-WR-R** | AliExpress "3 inch 4 ohm 20W full range speaker" | $5–25 each | Both speakers must be **identical** for stereo balance. **Sealed enclosure mandatory** — open-back ruins low-end on small drivers. |
| **J1, J2** | Speaker output: JST-XH 2-pin (vertical) + matching pigtail × 2 | DigiKey 455-1719-ND (PH) or larger XH for 18 AWG | $0.40 each | Bigger pitch (XH, 2.5 mm) handles higher current cleanly. |

## 3. Power-path connectors and switch

| Ref | Part | DigiKey / Mouser | AliExpress | ~$ | Notes |
|-----|------|------------------|------------|-----|-------|
| **SW1** | SPST slide or rocker switch, **≥ 5 A** | C&K JS202011SCQN | "Rocker switch KCD11 5A" | $1 | In series with the 4S pack. **Must handle ≥ 5 A** — peak amp current at full output crosses 3 A. |
| **J_BAT** | 4S battery + balance harness header | XT60 male/female on PCB (DigiKey "Amass XT60") + 5-pin JST-XH for balance taps | "XT60 + JST-XH 5-pin balance harness" | $2 | XT60 carries the main battery current; JST-XH 5-pin carries the four cell taps + ground for the BMS. RC-hobby-style. |

## 4. Controls and indicator

| Ref | Part | DigiKey / Mouser | AliExpress | ~$ | Notes |
|-----|------|------------------|------------|-----|-------|
| **RV1** | 10 kΩ linear potentiometer, panel-mount, 6 mm shaft | Bourns 3306P-1-103-ND | "10K linear B10K panel pot 6mm" | $1–2 | Linear (B10K). Knob extra. |
| **SW2** | Tactile push button, 12 mm panel-mount momentary | Omron B3F-1000 (DigiKey) | "12 mm momentary panel button" | $0.50 | Or 6×6 mm THT on PCB if mounting directly. |
| **D1** | Status LED, 3 mm or 5 mm | DigiKey 754-1264-ND (5 mm green) | bag of LEDs | $0.10 | Any colour. |
| **R1** | 470 Ω resistor, 0805 SMD | DigiKey RMCF0805JT470RCT-ND | bag of resistors | $0.02 | Series with D1. |
| **R2, R3** | 4.7 kΩ resistor, 0805 — I²C pull-ups | as above | | $0.04 | Some TAS5825M breakouts already have these on board; check yours and omit if so. |
| **R4** | 10 kΩ resistor, 0805 — TAS5825M PDN pull-up | as above | | $0.02 | Tie TAS5825M `PDN` to 3V3 via this; chip stays always-on. |

## 5. Passives

| Ref | Value | Package | ~$ | Notes |
|-----|-------|---------|-----|-------|
| **C1** | 1000 µF / 25 V electrolytic | radial 8 mm | $0.50 | Bulk on amp Vcc rail (4S nominal 14.8 V, peak 16.8 V → spec the cap for 25 V). |
| **C2** | 100 nF / 25 V X7R | 0805 | $0.02 | HF bypass at amp Vcc. |
| **C3** | 22 µF / 25 V X7R | 1206 | $0.30 | Local Vcc decoupling at TAS5825M. |
| **C4** | 10 µF / 10 V X5R | 0805 | $0.02 | Buck output bulk on +5 V rail. |
| **C5** | 100 nF | 0805 | $0.02 | XIAO 3V3 HF. |
| **C6, C7** | 100 nF | 0805 | $0.04 | I²C SDA/SCL ESD bypass (optional). |
| **L1** *(optional, on speaker outputs)* | 22 µH ferrite + 1 µF MLCC | bead inductor + 1206 | $0.50 | Class-D low-pass filter to reduce EMI on long speaker leads. Most TAS5825M breakouts already include the LC filter; verify before populating. |

## 6. Mechanical

| Item | Source | ~$ | Notes |
|------|--------|-----|-------|
| Enclosure | 3D-printed (PETG / ABS) custom or off-the-shelf "boombox" project box | $3–10 | Plan for **2× speaker grilles**, USB-C cutout (IP2368 module side), DC-style ventilation slots above the BMS, panel cutouts for pot/button/LED. ~22 × 13 × 8 cm internal. |
| Knob for RV1 | DigiKey 226-1042-ND or any 6 mm-shaft knob | $1 | Skirted knob with set-screw is forgiving. |
| Standoffs / screws | M3 brass + M3 × 8 mm screws | $5 (kit) | For PCB into enclosure. |
| Speaker grilles | 3D-printed hex pattern, or speaker-cloth-over-frame | $1–3 each | Protects cones from finger damage. |

## 7. PCB

Carrier PCB from JLCPCB / PCBWay using design files in `pcb/` once routed.
- **Board size**: target ~110 × 75 mm (fits IP2368, BMS, modules, no battery — 4S pack mounts in enclosure).
- **Layers**: 2 (4-layer if you want better EMI on the audio side; not strictly required at this power level).
- **Thickness**: 1.6 mm.
- **Surface finish**: HASL lead-free OK; ENIG nicer.
- **Min trace / space**: 6/6 mil.
- **Solder mask colour**: any.
- **Copper weight**: **2 oz on power layer recommended** for the 4S → amp current path, especially if you push to 50 W later.

5 boards from JLCPCB: **~$8 + $12 shipping** (slightly more than 1S because of the larger panel size).

## 8. Tools

Same as 1S build, plus:
| Tool | Why |
|------|-----|
| 4S charger (lab supply or RC-style) | For initial bring-up and BMS testing **before** plugging in USB-C PD. |
| **USB-C PD trigger / charger** that delivers 20 V | E.g. Anker Nano II 65 W, Apple 96 W, any laptop charger. ≥ 65 W recommended for fast charging. |
| Hot-air rework station | If you go discrete TAS5825M instead of breakout. |

## 9. Order summary (single-build, mid-tier sourcing)

| Group | Approx total |
|-------|--------------|
| Active modules (U1–U5 + BMS) | $40 |
| 4 × 18650 cells + holder | $30 |
| Speakers (2×) | $15–50 |
| Connectors + switch | $5 |
| Controls + indicator | $5 |
| Passives | $4 |
| PCB (5 pcs incl. shipping) | $20 |
| **Total** | **~$120–155** |

## 10. Sanity checklist before you buy

- [ ] **IP2368** (4S-capable), not IP2366 (1S–3S).
- [ ] TAS5825M breakout exposes SDA/SCL/PDN/FAULTZ on a header.
- [ ] 4S BMS rated **≥ 30 A continuous** with **balance leads**.
- [ ] All 4 cells: **same brand, same capacity, same date code if possible.**
- [ ] Speakers are **identical** units (same model, same impedance).
- [ ] Slide / rocker switch SW1 is rated **≥ 5 A** (4S battery line).
- [ ] You have a **USB-C PD charger** that can deliver 20 V (≥ 65 W).
- [ ] You have a **balance plug pigtail** (5-pin JST-XH) matching the BMS / pack.
- [ ] USB-C **data** cable on hand for XIAO programming (separate from PD-capable cable for charging).
