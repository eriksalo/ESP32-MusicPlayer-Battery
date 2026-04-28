# Bill of Materials

Quantities and prices are rough (USD, ~2026 retail) for sourcing planning.
Most parts are pre-made modules, which keeps the carrier PCB nearly all
through-hole / castellated.

## Core electronics

| # | Qty | Part | Notes | ~Price |
|---|-----|------|-------|--------|
| U1 | 1 | **Seeed XIAO ESP32-S3** | Castellated module. ESP32-S3, 8MB flash, 8MB PSRAM, native USB-C, Wi-Fi + BLE. | $7 |
| U2 | 1 | **MAX98357A I²S amp breakout** | Adafruit #3006 or generic clone. 3.2W into 4Ω at 5V; gain set by GAIN pin or onboard solder jumper. | $5 |
| U3 | 1 | **microSD card socket breakout** | Pick a push-push variant for nicer ergonomics. SPI mode. | $2 |
| U4 | 1 | **IP5306 18650 power module** | Combined charger + 5V boost + protection + USB-C input. Choose one with auto-on (no double-press to enable). | $4 |
| BT1 | 1 | **18650 cell** | Genuine Samsung/LG/Sony, 3000–3500mAh, button-top or flat depending on holder. | $5–10 |
| H1 | 1 | **18650 PCB-mount holder** | Through-hole pins, fits cell cleanly to PCB. | $1 |
| LS1 | 1 | **4Ω 5W speaker** | ~40–60mm full-range works well; sealed enclosure recommended. | $3–8 |

## Controls / indicators

| # | Qty | Part | Notes | ~Price |
|---|-----|------|-------|--------|
| RV1 | 1 | **10 kΩ linear potentiometer** | Panel-mount or PCB-mount; logarithmic also fine since gain is digital. | $1 |
| SW1 | 1 | **SPST slide switch** | Latching, panel mount; rated ≥2A (battery line). | $1 |
| SW2 | 1 | **6×6 mm tactile push button** | Through-hole; or a panel-mount momentary if you want a nicer feel. | $0.20 |
| D1 | 1 | **5 mm or 3 mm LED** | Any colour; pair with R1. | $0.10 |
| R1 | 1 | **330–1 kΩ resistor** | Series with LED. | $0.05 |

## Passives & connectors

| # | Qty | Part | Notes |
|---|-----|------|-------|
| C1, C2 | 2 | 10 µF / 6.3V ceramic | Local decoupling for XIAO 3V3 and MAX98357A Vin. |
| C3 | 1 | 100 nF ceramic | Decoupling near MAX98357A Vin. |
| J1 | 1 | 2-pin JST-PH or screw terminal | Speaker output. |
| J2 | 1 | 2-pin JST-PH | Battery to IP5306 (if module isn't on-board). |
| —  | — | Header pins / sockets | For mounting modules. |

## Optional / nice-to-have

- **Battery sense divider**: 100 kΩ + 100 kΩ on a free ADC pin to monitor cell
  voltage. Add a low-battery LED pattern in firmware.
- **Schottky diode** (e.g. SS14) on the 5V rail if you want load-sharing
  between the IP5306 boost and an external USB power input.
- **Ferrite bead** in series with MAX98357A Vin if you hear digital noise
  through the speaker.

## Total estimate

Roughly **$30–45** in parts at hobby quantities, dominated by the cell, speaker,
and modules. The custom carrier PCB itself is ~$5 from JLCPCB/PCBWay for 5
boards.
