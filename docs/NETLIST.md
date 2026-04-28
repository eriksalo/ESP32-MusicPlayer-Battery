# Netlist

Every electrical connection on the carrier PCB. Use this as the source of
truth when drawing the schematic. Reference designators here match
[`docs/BOM.md`](BOM.md) and [`docs/MODULES.md`](MODULES.md).

The Python in [`pcb/gen_netlist.py`](../pcb/gen_netlist.py) implements
the same connections and emits a KiCad-importable `.net` file.

## Power nets

| Net | Source | Loads | Notes |
|-----|--------|-------|-------|
| **VBAT_RAW** | 4S pack `+` (BMS P+) | SW1 in, IP2368 BAT+ (charge path), J_BAL pin 5 | Pack output node. ~14.8 V nominal. |
| **+14V_SW** | SW1 throw | TPA3116D2 U2A Vcc, buck U5 VIN, C1 (1000 µF), C2 (100 nF) | Main power rail. SW1 must be rated ≥ 5 A. |
| **+5V** | Buck U5 VOUT | XIAO U1 5V, microSD U3 VCC, PCM5102A U2 VIN, C3 (10 µF) | Trim buck to **exactly 5.0 V** before connecting downstream. |
| **+3V3** | XIAO U1 3V3 (LDO output) | RV1 high lug, C4 (100 nF) | XIAO LDO; ~500 mA budget. |
| **GND** | BMS P-, IP2368 GND, all module GNDs | Everything else | Single uninterrupted plane on B.Cu, stitched with vias. |

## Charging path (USB-C PD)

The IP2368 module manages USB-C PD ↔ 4S charge internally. From the
carrier PCB's perspective, only its battery-side pins matter:

| Net | From | To |
|-----|------|----|
| `BAT_PACK_PLUS` | IP2368 BAT+ | BMS B+ (via balance harness if your BMS expects charge through the balance plug; verify with your specific BMS) |
| `BAT_PACK_MINUS` | IP2368 BAT- | BMS B- (= GND star) |
| `BAL_1` | IP2368 BAL1 | Cell 1 / Cell 2 junction (BT1- / BT2+) |
| `BAL_2` | IP2368 BAL2 | Cell 2 / Cell 3 junction (BT2- / BT3+) |
| `BAL_3` | IP2368 BAL3 | Cell 3 / Cell 4 junction (BT3- / BT4+) |

In practice, both the IP2368 module and the BMS module each get their
own balance plug (5-pin JST-XH) into the cell pack. The carrier PCB
exposes a single 5-pin JST-XH header (`J_BAL`) wired to the cell taps,
and the IP2368 + BMS modules each plug into one. Or the BMS can be a
"protect-only" board and balance is delegated to IP2368.

## Audio signal nets

### I²S (XIAO → PCM5102A DAC)

| Net | From | To |
|-----|------|----|
| `I2S_BCLK`  | U1 GPIO4 (D3) | U2 BCK |
| `I2S_LRCLK` | U1 GPIO5 (D4) | U2 LCK |
| `I2S_DOUT`  | U1 GPIO6 (D5) | U2 DIN |

### Analog audio (PCM5102A → TPA3116D2)

| Net | From | To |
|-----|------|----|
| `AUDIO_L`  | U2 LOUT | U2A L_IN |
| `AUDIO_R`  | U2 ROUT | U2A R_IN |
| `AUDIO_GND` | U2 AGND | U2A AGND_IN | (tied to main GND at one star point) |

### Speaker outputs (TPA3116D2 → 2 speakers, BTL stereo)

| Net | From | To |
|-----|------|----|
| `SPK_L_PLUS`  | U2A SPK_L+ | J1 pin 1 → left speaker LS1 `+` |
| `SPK_L_MINUS` | U2A SPK_L- | J1 pin 2 → left speaker LS1 `-` |
| `SPK_R_PLUS`  | U2A SPK_R+ | J2 pin 1 → right speaker LS2 `+` |
| `SPK_R_MINUS` | U2A SPK_R- | J2 pin 2 → right speaker LS2 `-` |

### microSD (SPI)

| Net | From | To |
|-----|------|----|
| `SD_CS`   | U1 GPIO3 (D2)  | U3 CS |
| `SD_MOSI` | U1 GPIO9 (D10) | U3 MOSI |
| `SD_MISO` | U3 MISO        | U1 GPIO8 (D9) |
| `SD_SCK`  | U1 GPIO7 (D8)  | U3 SCK |

### Controls / indicator

| Net | From | To |
|-----|------|----|
| `VOL_WIPER` | RV1 lug 2 (wiper) | U1 GPIO1 (D0) |
| (RV1 lug 1) | GND | RV1 lug 1 |
| (RV1 lug 3) | +3V3 | RV1 lug 3 |
| `BTN_N` | SW2 pin 1 | U1 GPIO2 (D1) |
| (SW2 pin 2) | GND | SW2 pin 2 |
| `LED_DRV` | U1 GPIO43 (D6) | R1 → D1 anode |
| (D1 cathode) | GND | — |

## Static tie-offs on PCM5102A (U2)

PCM5102A breakouts have FLT, DEMP, XSMT, FMT, SCK pins typically
**hardwired by the breakout vendor**. Default strapping (FLT=GND,
DEMP=GND, XSMT=VCC, FMT=GND, SCK=GND) gives I²S mode, normal filter, no
de-emphasis, un-muted. Don't change unless the breakout silkscreen
specifically asks. **No netlist entries needed for these.**

## Decoupling and passives

| Ref | Value | Between | Placement |
|-----|-------|---------|-----------|
| C1 | 1000 µF / 25 V (electrolytic) | +14V_SW — GND | Bulk on amp Vcc rail; place close to U2A Vcc. |
| C2 | 100 nF / 25 V | +14V_SW — GND | HF bypass adjacent to C1. |
| C3 | 10 µF / 10 V | +5V — GND | Buck U5 output bulk. |
| C4 | 100 nF | +3V3 — GND | XIAO U1 3V3 pin. |
| C5, C6 *(optional)* | 1 µF film | AUDIO_L/R coupling | DC-block between PCM5102A and TPA3116D2 — populate only if the TPA3116D2 module doesn't already DC-block its inputs. |
| R1 | 470 Ω | LED_DRV — D1 anode | LED current limit. |

## Connector map

| Connector | Type | Notes |
|-----------|------|-------|
| **J1** (left speaker out) | JST-XH 2-pin | SPK_L+, SPK_L- |
| **J2** (right speaker out) | JST-XH 2-pin | SPK_R+, SPK_R- |
| **J_BAT** (battery main) | XT60 male on PCB | + and − to BMS P+ / P-. Polarity is keyed by XT60 shape. |
| **J_BAL** (balance taps) | JST-XH 5-pin | Cell pack balance harness: GND, BT1-/BT2+, BT2-/BT3+, BT3-/BT4+, BT4+ |
| **J_PWR** (panel switch) | JST-PH 2-pin | SW1 between BMS P+ and +14V_SW |
| **J_VOL** (panel pot) | JST-PH 3-pin | RV1 wires (GND, wiper, +3V3) |
| **J_BTN** (panel button) | JST-PH 2-pin | SW2 + GND |
| **J_LED** (panel LED) | JST-PH 2-pin | LED anode (after R1) + GND |
| **U1 USB-C** | XIAO on-board | for flashing / serial debug only |
| **U4 USB-C** | IP2368 on-board | charging input (USB-C PD) |

## Net counts (summary)

- **Power nets**: 5 (VBAT_RAW, +14V_SW, +5V, +3V3, GND)
- **Charging path**: 3 (BAL_1..3) + GND + BAT+
- **Signal nets**: 17
  - 3 I²S (BCLK, LRCLK, DOUT)
  - 2 analog audio (AUDIO_L, AUDIO_R) + 1 audio ground
  - 4 Speaker (L±, R±)
  - 4 SD SPI (CS, MOSI, MISO, SCK)
  - 4 Controls (VOL_WIPER, BTN_N, LED_DRV, LED_A)
- **Total non-power nets**: ~17. Comfortably routable on 2 layers at 110 × 75 mm.
