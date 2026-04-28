# Bill of Materials

**Configuration**: 4S 18650 + IP2368 USB-C PD charger + TAS5805M stereo I²S
amp + 2 × 4 Ω full-range drivers, ~30 W total. Handheld form factor
(~22 × 13 × 8 cm).

Most lines have **two purchase paths**: a primary (manufacturer page or
Western distributor) and a generic alternative (AliExpress / search). The
primary is more reliable and faster; the generic is cheaper but takes 3–4
weeks. Prices in USD ~2026, indicative only.

> **Honest note about links**: manufacturer / distributor product pages are
> stable and verified. Distributor URLs are **search URLs** — the search
> term is correct but click through and pick the in-stock option that
> matches the description. AliExpress URLs are search-only because product
> URLs there expire. **None** of the links below are affiliate.

> Buy **two of every breakout module and connector** for a first build —
> they're cheap and a desoldering job to recover one is a lost weekend.

## 1. Active modules

| Ref | Part | Primary source | Generic / cheap | ~$ |
|-----|------|----------------|-----------------|-----|
| **U1** | Seeed XIAO ESP32-S3 | [Seeed Studio (canonical product page)](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html) · [DigiKey search "XIAO ESP32-S3"](https://www.digikey.com/en/products/result?keywords=XIAO+ESP32-S3) · [Mouser search](https://www.mouser.com/c/?q=XIAO%20ESP32-S3) | [AliExpress search](https://www.aliexpress.com/wholesale?SearchText=Seeed+XIAO+ESP32-S3) (verify Bazaar/Seeed seller) | $7.50 |
| **U2** | **TAS5805M** I²S stereo amp breakout | [DFRobot Fermion DFR0721 product page](https://www.dfrobot.com/product-2614.html) · [DigiKey listing of DFR0721](https://www.digikey.com/en/products/result?keywords=DFR0721) · [Amazon "DFRobot TAS5805M"](https://www.amazon.com/s?k=DFRobot+TAS5805M) | [AliExpress "TAS5805M I2S amplifier"](https://www.aliexpress.com/wholesale?SearchText=TAS5805M+I2S+amplifier+30W) | $15 |
| | *Alternate*: TAS5825M breakout | only AliExpress (no Western distributor stocks the breakout): [search](https://www.aliexpress.com/wholesale?SearchText=TAS5825M+I2S+amplifier) | | $5–10 |
| **U3** | microSD card breakout (SPI, 3V3) | [Adafruit #4682 product page](https://www.adafruit.com/product/4682) · [DigiKey search](https://www.digikey.com/en/products/result?keywords=adafruit%204682) | [AliExpress "Micro SD card module 3V3"](https://www.aliexpress.com/wholesale?SearchText=micro+SD+card+module+3V3) | $4 / $1 |
| **U4** | IP2368 USB-C PD all-in-one 4S charger module (100 W) | [DFRobot DFR1015 product page](https://www.dfrobot.com/product-2700.html) (verify it's the IP2368 / 4S variant when ordering) | [AliExpress "IP2368 4S 100W bidirectional"](https://www.aliexpress.com/wholesale?SearchText=IP2368+4S+100W+bidirectional+module) | $12 / $8 |
| **U5** | 5 V buck converter module (4 S → 5 V @ 1 A) | [Pololu D24V10F5 product page](https://www.pololu.com/product/2831) · [DigiKey search "MP1584 module"](https://www.digikey.com/en/products/result?keywords=MP1584+module) | [AliExpress "MP1584 mini buck"](https://www.aliexpress.com/wholesale?SearchText=MP1584+mini+360+buck+module) | $7 / $1 |
| **BMS** | 4S 30 A balanced Li-ion BMS (common port) | [Battery Hookup search "4S BMS"](https://batteryhookup.com/search?q=4S+BMS) · [Amazon "4S 30A BMS"](https://www.amazon.com/s?k=4S+30A+BMS+balanced) | [AliExpress search](https://www.aliexpress.com/wholesale?SearchText=4S+30A+balanced+BMS+18650) | $5 |

## 2. Battery and speakers

| Ref | Part | Primary source | Generic | ~$ |
|-----|------|----------------|---------|-----|
| **BT1–BT4** | 4 × 18650 cells, 3000–3500 mAh, flat-top | [18650 Battery Store (Samsung 30Q et al.)](https://www.18650batterystore.com/collections/18650-batteries) · [Liion Wholesale](https://liionwholesale.com/collections/18650-li-ion-batteries) · [IMR Batteries](https://www.imrbatteries.com/18650-batteries/) | **Avoid Amazon and AliExpress for cells** — counterfeits are rampant. | $5–9 each |
| **H1** | 4-cell series 18650 holder (single piece, with pigtail) | [Adafruit #2812 (4-cell holder, parallel — needs rewiring for series)](https://www.adafruit.com/product/2812) — easier to find true series holders on AliExpress | [AliExpress "4×18650 series battery holder"](https://www.aliexpress.com/wholesale?SearchText=4x18650+series+battery+holder+with+leads) | $3–10 |
| **LS1, LS2** | 2 × 4 Ω 15–25 W full-range driver, 3″–4″ | [Visaton FRS 8 4Ω at Parts Express](https://www.parts-express.com/Visaton-FRS-8-3-Full-Range-4-Ohm-292-454) · [Dayton ND91-4 at Parts Express](https://www.parts-express.com/Dayton-Audio-ND91-4-3-1-2-Aluminum-Cone-Full-Range-Driver-4-Ohm-290-216) | [AliExpress "3 inch 4 ohm 20W full range"](https://www.aliexpress.com/wholesale?SearchText=3+inch+4+ohm+20W+full+range+speaker) | $5–25 each |
| **J1, J2** | 2 × JST-XH 2-pin (vertical, on-PCB) + matching pigtail | [DigiKey search "JST XH 2 pin vertical"](https://www.digikey.com/en/products/result?keywords=JST+XH+2+pin+vertical) | [AliExpress "JST XH 2.5mm 2pin connector kit"](https://www.aliexpress.com/wholesale?SearchText=JST+XH+2.5mm+2pin+connector+kit) | $0.40 each |

## 3. Power-path connectors and switch

| Ref | Part | Primary | Generic | ~$ |
|-----|------|---------|---------|-----|
| **SW1** | SPST rocker or slide switch, **≥ 5 A**, panel-mount | [DigiKey search "rocker switch 5A SPST panel"](https://www.digikey.com/en/products/result?keywords=rocker+switch+5A+SPST+panel) | [AliExpress "KCD11 rocker switch 5A"](https://www.aliexpress.com/wholesale?SearchText=KCD11+rocker+switch+5A) | $1 |
| **J_BAT** | XT60 male connector (PCB or panel) | [Amass XT60 at DigiKey](https://www.digikey.com/en/products/result?keywords=Amass+XT60) · [HobbyKing Amass XT60](https://hobbyking.com/en_us/?route=product/search&search=xt60) | [AliExpress "XT60 connector pair"](https://www.aliexpress.com/wholesale?SearchText=XT60+male+female+connector) | $1 |
| **J_BAL** | JST-XH 5-pin balance harness (on-PCB) + matching plug | [DigiKey search "JST XH 5 pin"](https://www.digikey.com/en/products/result?keywords=JST+XH+5+pin) | [AliExpress "JST XH 5pin 4S balance harness"](https://www.aliexpress.com/wholesale?SearchText=JST+XH+4S+balance+harness) | $1 |

## 4. Controls and indicator

| Ref | Part | Primary | Generic | ~$ |
|-----|------|---------|---------|-----|
| **RV1** | 10 kΩ linear potentiometer, panel-mount, 6 mm shaft | [Bourns 3306P-1-103 at DigiKey](https://www.digikey.com/en/products/result?keywords=Bourns+3306P-1-103) | [AliExpress "10K linear B10K panel pot 6mm"](https://www.aliexpress.com/wholesale?SearchText=10K+linear+B10K+panel+pot+6mm) | $1–2 |
| **SW2** | 12 mm panel-mount momentary push button | [Adafruit #1439 (16 mm, similar)](https://www.adafruit.com/product/1439) · [DigiKey search "12mm panel pushbutton"](https://www.digikey.com/en/products/result?keywords=12mm+panel+pushbutton) | [AliExpress "12mm momentary panel button"](https://www.aliexpress.com/wholesale?SearchText=12mm+momentary+panel+push+button) | $0.50–2 |
| **D1** | LED, 3 mm or 5 mm, any colour | [DigiKey search "5mm LED through-hole"](https://www.digikey.com/en/products/result?keywords=5mm+LED+through-hole) | bag from any electronics store | $0.10 |
| **R1** | 470 Ω resistor, 0805 SMD | [DigiKey RMCF0805JT470RCT-ND](https://www.digikey.com/en/products/result?keywords=RMCF0805JT470R) | [AliExpress 0805 resistor kit](https://www.aliexpress.com/wholesale?SearchText=0805+SMD+resistor+kit) | $0.02 |
| **R2, R3** | 4.7 kΩ resistor, 0805 — I²C pull-ups | [DigiKey 0805 4.7K](https://www.digikey.com/en/products/result?keywords=0805+4.7k+resistor) | (kit) | $0.04 |
| **R4** | 10 kΩ resistor, 0805 — TAS PDN pull-up | (kit) | (kit) | $0.02 |

> Tip: a 0805 resistor sample kit (~$10 from AliExpress / Amazon) covers
> R1–R4 and any future tweaks, far cheaper than buying single values.

## 5. Passives

| Ref | Value | Package | Primary | ~$ |
|-----|-------|---------|---------|-----|
| **C1** | 1000 µF / 25 V | radial electrolytic, 8 mm | [DigiKey search "1000uF 25V radial"](https://www.digikey.com/en/products/result?keywords=1000uF+25V+radial+electrolytic) | $0.50 |
| **C2** | 100 nF / 25 V X7R | 0805 | [DigiKey search "0805 100nF 25V X7R"](https://www.digikey.com/en/products/result?keywords=0805+100nF+25V+X7R) | $0.02 |
| **C3** | 22 µF / 25 V X7R | 1206 | [DigiKey search "1206 22uF 25V"](https://www.digikey.com/en/products/result?keywords=1206+22uF+25V+X7R) | $0.30 |
| **C4** | 10 µF / 10 V X5R | 0805 | (kit) | $0.02 |
| **C5–C7** | 100 nF | 0805 | (kit) | $0.02 ea |
| **L1** *(optional, on speaker outputs)* | 22 µH ferrite + 1 µF MLCC | bead inductor + 1206 | only needed if your TAS5805M breakout doesn't already include the LC filter — check before buying | $0.50 |

> Tip: a 0805 + 1206 capacitor sample kit covers C2–C7 and most future
> tweaks for ~$15.

## 6. Mechanical

| Item | Primary | ~$ |
|------|---------|-----|
| Enclosure (3D-printed PETG / ABS, custom) | self-printed or [send STL to JLCPCB 3D printing](https://jlcpcb.com/3d-printing) / [PCBWay 3D printing](https://www.pcbway.com/rapid-prototyping/manufacture/) | $3–10 |
| Knob for RV1 (6 mm shaft, set-screw) | [DigiKey search "knob 6mm shaft"](https://www.digikey.com/en/products/result?keywords=knob+6mm+shaft+setscrew) · [AliExpress "aluminum knob 6mm shaft"](https://www.aliexpress.com/wholesale?SearchText=aluminum+knob+6mm+shaft+setscrew) | $1 |
| M3 brass standoffs + screws (kit) | [Amazon "M3 brass standoff kit"](https://www.amazon.com/s?k=M3+brass+standoff+kit) · [AliExpress](https://www.aliexpress.com/wholesale?SearchText=M3+brass+standoff+kit+female) | $5 |
| Speaker grille / cloth | [Parts Express search "speaker grille"](https://www.parts-express.com/cat/speaker-grills/2/2026) | $1–3 |

## 7. PCB

Carrier PCB from JLCPCB / PCBWay using design files in `pcb/` once routed.

| Spec | Value |
|------|-------|
| Order page | [JLCPCB upload](https://cart.jlcpcb.com/quote) · [PCBWay upload](https://www.pcbway.com/orderonline.aspx) |
| Board size | 110 × 75 mm |
| Layers | 2 |
| Thickness | 1.6 mm |
| Copper weight | **2 oz on top + bottom** (recommended for 4S power path) |
| Surface finish | HASL lead-free (cheap) or ENIG (~$3 more, recommended) |
| Quantity | 5 (minimum tier) |
| Approx total | **$8 fab + $12 shipping** |

## 8. Tools

| Tool | Source | Notes |
|------|--------|-------|
| Soldering iron, fine + chisel tips | [Pinecil v2](https://pine64.com/product/pinecil-smart-mini-portable-soldering-iron-v2/) · [TS80P](https://www.miniware.com.cn/product/ts80p-soldering-iron/) · [Hakko FX-888D](https://www.hakkousa.com/products/hakko-fx888d-soldering-station) | Any of these are great. |
| Solder, leaded 0.6–0.8 mm, flux core | [DigiKey leaded solder](https://www.digikey.com/en/products/result?keywords=leaded+solder+0.6mm+flux+core) | Easier than lead-free for hand soldering. |
| Liquid flux pen | [DigiKey flux pen](https://www.digikey.com/en/products/result?keywords=flux+pen+rosin) | Saves iffy joints. |
| Multimeter with continuity beep | (any decent DMM) | Confirm IP2368 polarity before connecting cells. |
| **USB-C PD charger ≥ 65 W** | [Anker Nano II 65 W](https://www.anker.com/products/a2663) · any laptop USB-C charger | For charging the pack via IP2368. |
| USB-C **data** cable | (any) | For XIAO programming. Many cheap cables are charge-only — verify. |

## 9. Order summary (single-build, primary sourcing)

| Group | Approx total |
|-------|--------------|
| Active modules (U1–U5 + BMS) | $50 |
| 4 × 18650 cells + holder | $30 |
| Speakers (2×) | $15–50 |
| Connectors + switch | $5 |
| Controls + indicator | $5 |
| Passives | $4 |
| PCB (5 pcs incl. shipping) | $20 |
| **Total** | **~$130–165** |

## 10. Sanity checklist before you buy

- [ ] **DFRobot DFR0721 is TAS5805M** (not TAS5825M, not MAX98357A — verify the part number on the breakout's silkscreen when it arrives).
- [ ] **IP2368** (4S-capable) — IP2366 is 1S–3S only.
- [ ] 4S BMS rated **≥ 30 A continuous, common-port (single P+/P-)**, with balance leads.
- [ ] All 4 cells: **same brand, same capacity, same date code** if possible.
- [ ] Speakers are **identical** units (same model, same impedance).
- [ ] Switch SW1 rated **≥ 5 A**.
- [ ] You have a **USB-C PD charger ≥ 30 W**, ideally 65 W for fast charging.
- [ ] You have a **balance plug** (5-pin JST-XH) on order with the BMS or pack.
- [ ] USB-C **data** cable for XIAO programming (separate from the PD charging cable).
