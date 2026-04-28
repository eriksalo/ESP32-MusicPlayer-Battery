# Netlist

Every electrical connection on the carrier PCB. Use this as the source of
truth when drawing the schematic — reference designators here match
[`docs/BOM.md`](BOM.md) and [`docs/MODULES.md`](MODULES.md).

## Power nets

| Net | Source | Loads | Notes |
|-----|--------|-------|-------|
| **VBAT_SW** | 18650 (BT1) `+` → SW1 common | SW1 throw → IP5306 `BAT+` | The slide switch is **inline with the battery** so all downstream rails are de-energised when off. |
| **VBAT_RTN** | 18650 (BT1) `−` | IP5306 `BAT-`, GND | Battery return tied to the global ground star at the IP5306 module. |
| **+5V** | IP5306 `OUT+` (5 V boost) | XIAO U1 `5V`, MAX98357A U2 `Vin`, C1, C2 | Main system rail. ~2 A capable. |
| **+3V3** | XIAO U1 `3V3` (on-board LDO output) | microSD U3 `VCC`, RV1 high lug, C4 | LDO inside the XIAO; ~500 mA budget. |
| **GND** | IP5306 `OUT-` / `GND` | Everything else | Single ground plane on inner copper or bottom layer. |

## Signal nets

### Audio (I²S, XIAO ↔ MAX98357A)

| Net name | From | To |
|----------|------|----|
| `I2S_BCLK` | U1 GPIO4 (D3) | U2 BCLK (pin 6) |
| `I2S_LRCLK` | U1 GPIO5 (D4) | U2 LRC (pin 7) |
| `I2S_DOUT` | U1 GPIO6 (D5) | U2 DIN (pin 5) |
| `SPK+` | U2 SPK+ | J1 pin 1 → speaker LS1 `+` |
| `SPK-` | U2 SPK- | J1 pin 2 → speaker LS1 `-` |

### microSD (SPI)

| Net name | From | To |
|----------|------|----|
| `SD_CS`   | U1 GPIO3 (D2)  | U3 CS  |
| `SD_MOSI` | U1 GPIO9 (D10) | U3 MOSI |
| `SD_MISO` | U3 MISO        | U1 GPIO8 (D9) |
| `SD_SCK`  | U1 GPIO7 (D8)  | U3 SCK |

### Controls / indicator

| Net name | From | To |
|----------|------|----|
| `VOL_WIPER` | RV1 wiper (lug 2) | U1 GPIO1 (D0) |
| (RV1 lug 1) | GND | RV1 lug 1 |
| (RV1 lug 3) | +3V3 | RV1 lug 3 |
| `BTN_N` | SW2 pin 1 | U1 GPIO2 (D1) |
| (SW2 pin 2) | GND | SW2 pin 2 |
| `LED_DRV` | U1 GPIO43 (D6) | R1 → D1 anode |
| (D1 cathode) | GND | — |

### Static tie-offs on U2 (MAX98357A)

| Pin | Tied to | Why |
|-----|---------|-----|
| `SD/MODE` (pin 3) | +5V | "Always on, mono = (L+R)/2" |
| `GAIN`    (pin 4) | float | 9 dB gain (good starting point) |

## Decoupling and passives

| Ref | Value | Between | Placement |
|-----|-------|---------|-----------|
| C1  | 10 µF / 10 V | +5V — GND | Within 5 mm of MAX98357A U2 `Vin` |
| C2  | 100 nF       | +5V — GND | Within 2 mm of MAX98357A U2 `Vin` |
| C3  | 10 µF        | +5V — GND | Bulk near IP5306 5 V output / connector |
| C4  | 100 nF       | +3V3 — GND | Within 5 mm of XIAO U1 `3V3` pin |
| R1  | 470 Ω         | LED_DRV — D1 anode | Anywhere on net |
| FB1 *(optional)* | 600 Ω @ 100 MHz | +5V → MAX98357A Vin | Series, populate only if you hear digital noise. |

## Connector map

| Connector | Type | Pin 1 | Pin 2 |
|-----------|------|-------|-------|
| **J1** (speaker out) | JST-PH 2-pin or screw terminal | SPK+ | SPK- |
| **U1 USB-C** | XIAO on-board | for flashing/serial only — no carrier-board routing |
| **U4 USB-C** | IP5306 on-board | charging only |

## Off-board (panel-wired) parts

These don't sit on the PCB; they wire from the PCB to the enclosure panel.
Use 26–24 AWG silicone-jacketed wire and JST-PH 2- or 3-pin headers on
the PCB so you can disassemble cleanly.

| Net(s) | Panel part | PCB connector |
|--------|------------|---------------|
| VBAT_SW (2 wires) | SW1 slide switch | J_PWR (JST-PH 2-pin) |
| VOL_WIPER + 3V3 + GND (3 wires) | RV1 pot | J_VOL (JST-PH 3-pin) |
| BTN_N + GND (2 wires) | SW2 button | J_BTN (JST-PH 2-pin) |
| LED_DRV + GND (2 wires) | D1 LED + R1 (or R1 on board, 2 wires to LED) | J_LED (JST-PH 2-pin) |
| SPK+, SPK- (2 wires) | LS1 speaker | J1 (already listed above) |

If you'd rather mount RV1, SW2, D1 directly on the PCB and have it poke
through the front panel, that's also fine — adjust the board outline to
match your panel openings.

## Net counts (summary)

- **Power nets**: 4 (VBAT_SW, +5V, +3V3, GND) + 1 ground return.
- **Signal nets**: 11 (3 I²S + 4 SPI + 4 controls/LED).
- **Total non-power nets**: 11. Easily routable on a 2-layer 80×55 mm board.
