# Bill of Materials

Two columns: **western (Adafruit / DigiKey / Mouser / Amazon)** for fast / reliable
shipping, and **AliExpress / generic** for cheaper sourcing if you don't mind
3–4 week lead times. Mix and match. Prices are USD ~2026, indicative only.

> Buy **two of every module and connector** for a first build — they're
> inexpensive and a desoldering job to recover one is not.

## 1. Active modules

| Ref | Part | Western source | Generic source | ~$ | Notes |
|-----|------|----------------|----------------|-----|-------|
| **U1** | Seeed XIAO ESP32-S3 | [seeedstudio.com #113991054](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html) · DigiKey 1597-113991054-ND · Mouser 713-113991054 | AliExpress "Seeed XIAO ESP32-S3" (verify the seller is Seeed/Bazaar) | $7.50 | **Get the plain "XIAO ESP32-S3", not "Sense" (camera/mic) and not "Plus".** 8 MB flash, 8 MB PSRAM. |
| **U2** | MAX98357A I²S amp breakout | [Adafruit #3006](https://www.adafruit.com/product/3006) · DigiKey 1528-1786-ND | AliExpress "MAX98357 I2S DAC amplifier module" | $5.95 / $1.50 | Adafruit board is well-laid-out; clones work but check the GAIN solder jumper. |
| **U3** | microSD card breakout (SPI) | [Adafruit #4682](https://www.adafruit.com/product/4682) (push-pull, 3V3 logic) | AliExpress "Micro SD card module" — pick one with on-board level shifter labelled 3V3 + 5V | $3.95 / $1 | Avoid the "Catalex" 5V-only modules — they'll work on 3V3 but include unnecessary regulator + level shifter. |
| **U4** | IP5306 18650 charger + 5 V boost module | DFRobot DFR0470 (similar IP5306 board) · search "IP5306 2A boost charger module" | AliExpress "IP5306 1S 18650 boost module 2A" | $2–4 | Get one with **USB-C input** and **auto-on enabled**. The two main variants are the small "lithium battery shield" boards and the slightly bigger "power bank" boards — either works. |

## 2. Battery / speaker / connectors

| Ref | Part | Source | ~$ | Notes |
|-----|------|--------|-----|-------|
| **BT1** | 18650 cell, 3000–3500 mAh, flat-top | Vapcell, Molicel, Samsung 30Q (Liion Wholesale, IMR Batteries, 18650BatteryStore) | $5–9 | Buy from a reputable cell vendor — counterfeit Samsung/LG cells are rampant on Amazon/AliExpress. |
| **H1** | 18650 PCB-mount holder | Keystone 1042 (DigiKey 36-1042-ND) | $1.50 | Or solder-tabbed cell + JST-PH pigtail. |
| **LS1** | 4 Ω 5 W full-range speaker, 40–60 mm | Visaton, Dayton DAEX25, Adafruit #1314 (4 Ω 3 W close enough) · AliExpress "4 ohm 5W speaker 40mm" | $5–9 | Bigger driver = lower distortion at the same SPL. Sealed enclosure dramatically improves bass. |
| **J1** | Speaker output: JST-PH 2-pin (B2B-PH-K-S, vertical) + matching pigtail | DigiKey 455-1719-ND | $0.30 | Or screw terminal block (Phoenix MKDS, 5 mm pitch) if you prefer. |
| **J2** | Battery to PCB: JST-PH 2-pin or 18650 holder direct pads | as above | — | Skip if H1 sits on the PCB. |
| **J3** | (optional) USB-C breakout for charging if not using IP5306's USB | Adafruit #4090 | $1.50 | Most IP5306 modules already expose USB-C. |

## 3. Controls and indicator

| Ref | Part | DigiKey / Mouser | AliExpress | ~$ | Notes |
|-----|------|------------------|------------|-----|-------|
| **RV1** | 10 kΩ linear potentiometer, panel-mount, 6 mm shaft | Bourns PDB181-K420K-103B (DigiKey 3306P-1-103-ND linear) | "10K linear B10K panel pot 6mm" | $1–2 | Linear is fine since gain is digital. Pick one with a knob that fits your enclosure. |
| **SW1** | SPST slide switch, panel-mount, ≥2 A | C&K JS102011SAQN (DigiKey CKN9559-ND) | "SS12D00G3 slide switch" | $0.80 / $0.10 | **Must be ≥2 A** — it's in the battery line. The tiny SS12D00 is rated 0.3 A only; use the bigger panel slide. |
| **SW2** | Tactile push button, 6×6 mm or 12×12 mm panel-mount | Omron B3F-1000 (DigiKey SW1020-ND) | "12mm momentary panel button" | $0.20 / $0.50 | A panel-mount 12 mm momentary button feels nicer than 6×6. |
| **D1** | LED, 5 mm, any colour | DigiKey 754-1264-ND (5 mm green) | bag of LEDs | $0.10 | Bezel optional. |
| **R1** | 470 Ω resistor, 0805 SMD or through-hole | DigiKey RMCF0805JT470RCT-ND | bag of resistors | $0.02 | Series with D1. |
| **R2, R3** | 10 kΩ resistor, 0805 — for pot reference if you swap to a divider scheme | as above | | | optional |

## 4. Passives

| Ref | Value | Package | ~$ | Notes |
|-----|-------|---------|-----|-------|
| **C1, C2** | 10 µF / 10 V X5R/X7R | 0805 | $0.10 ea | Bulk decoupling on 5 V rail and at MAX98357A Vin. |
| **C3, C4** | 100 nF / 25 V X7R | 0805 | $0.02 ea | High-frequency decoupling near MAX98357A and XIAO 3V3 pin. |
| **C5** *(optional)* | 220 µF / 10 V electrolytic | radial 6.3 mm | $0.10 | Extra bulk on the speaker amp Vin if the IP5306 sags under transient. |
| **FB1** *(optional)* | Ferrite bead, 600 Ω @ 100 MHz, 1A | 0805 | $0.05 | In series with MAX98357A Vin if you hear digital hash through the speaker. |

## 5. Mechanical

| Item | Source | ~$ | Notes |
|------|--------|-----|-------|
| Enclosure | 3D-printed (PLA/PETG) or hammond 1591 series | $0–8 | Plan around the 18650 holder + speaker driver as the largest items. |
| Knob for RV1 | DigiKey 226-1042-ND or any 6 mm-shaft knob | $1 | Skirted knob with set-screw is forgiving. |
| Standoffs / screws | M2.5 brass + M2.5 × 6 mm screws | $5 (kit) | For mounting PCB into enclosure. |
| Speaker grille / cloth | Misc | $1 | Or 3D-print a hex pattern. |

## 6. PCB

Order from JLCPCB or PCBWay using the design files in `pcb/` once routed.
- **Board size**: target ~80 × 55 mm (fits 18650 holder + modules + pot + speaker).
- **Layers**: 2.
- **Thickness**: 1.6 mm.
- **Surface finish**: HASL (lead-free) is fine; ENIG is nicer if it fits the budget.
- **Min trace / space**: 6/6 mil — well within JLCPCB's free tier.
- **Solder mask colour**: any (black hides flux residue; matte black looks great).

5 boards from JLCPCB: ~**$5 + $10 shipping**. Add stencil only if you go SMD on the carrier (not needed for module-heavy build).

## 7. Tools you'll want

| Tool | Why |
|------|-----|
| Soldering iron with fine + chisel tips (TS80P, Pinecil, Hakko FX-888) | Module pin headers. |
| Solder, leaded 0.6–0.8 mm, with flux core | Easier hand-soldering than lead-free. |
| Liquid flux pen | Saves you on iffy joints. |
| Multimeter with continuity beep | Confirm IP5306 polarity *before* connecting the cell. |
| USB-C cable (data + power) | XIAO programming, IP5306 charging. Many cheap cables are charge-only — verify. |

## 8. Order summary (single-build, mid-tier sourcing)

| Group | Approx total |
|-------|--------------|
| Active modules (U1–U4) | $20 |
| Battery, speaker, connectors | $15 |
| Controls + indicator | $4 |
| Passives | $2 |
| PCB (5 pcs incl. shipping) | $15 |
| **Total** | **~$56** |

## 9. Sanity checklist before you buy

- [ ] XIAO ESP32-S3 plain (not Sense, not Plus) — confirm 8 MB PSRAM in the listing.
- [ ] IP5306 module includes USB-C input + auto-on (not "press to enable").
- [ ] microSD breakout is **3V3 logic** (most are; double-check).
- [ ] Slide switch SW1 is rated **≥ 2 A** (battery line).
- [ ] 18650 cell is from a reputable seller (counterfeits are common).
- [ ] You have a USB-C **data** cable on hand for XIAO programming.
