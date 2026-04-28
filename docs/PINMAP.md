# GPIO pin map — Seeed XIAO ESP32-S3

The XIAO ESP32-S3 exposes **11 GPIOs on its castellated edge** plus
additional pads on the bottom. This design needs 12 GPIOs total, so the
status LED moves to a bottom-pad GPIO accessed via a via on the carrier
PCB.

Assignments are encoded in [`include/config.h`](../include/config.h) and
must match the netlist (`docs/NETLIST.md`) and the PCB.

| XIAO label | GPIO | Direction | Function |
|------------|------|-----------|----------|
| D0  | 1  | analog in  | Volume potentiometer (ADC1_CH0) |
| D1  | 2  | digital in | Push button (active-low, INPUT_PULLUP) |
| D2  | 3  | digital out| SD card CS |
| D3  | 4  | digital out| I²S BCLK    → TAS5825M BCLK |
| D4  | 5  | digital out| I²S LRCLK   → TAS5825M LRCLK |
| D5  | 6  | digital out| I²S DOUT    → TAS5825M SDIN |
| D6  | 43 | open-drain | I²C SDA     ↔ TAS5825M SDA  (4.7 kΩ pull-up) |
| D7  | 44 | open-drain | I²C SCL     → TAS5825M SCL  (4.7 kΩ pull-up) |
| D8  | 7  | digital out| SD SCK |
| D9  | 8  | digital in | SD MISO |
| D10 | 9  | digital out| SD MOSI |
| (bottom pad) | 38 | digital out | Status LED (carrier PCB exposes via under module) |

## Bottom-pad LED — carrier PCB workaround

GPIO38 is on the bottom-side pad array of the XIAO ESP32-S3 (the array
of small pads beneath the module that mirror the edge pads but expose
additional GPIOs). The carrier PCB places a **0.6 mm via** under the
module's footprint so GPIO38 is reachable from the bottom layer.

Drill spec for the via: 0.3 mm hole, 0.6 mm pad — fits within the
footprint's bottom pad area for GPIO38. Keep solder mask **open** on the
via if you want to verify access with a probe; otherwise mask it as
normal.

Reference: see Seeed's XIAO ESP32-S3 datasheet for the exact bottom-pad
pinout. GPIO38 is on the side of the module opposite USB-C.

## Notes & caveats

- **Power switch SW1** is in the +14 V battery line, not on a GPIO. The
  BMS protects against over-discharge if you forget to switch off, but
  with no switch the player draws ~5–10 mA continuously, which depletes
  the pack in storage.
- **TAS5825M PDN** is hardware-tied to +3V3 via R4 (10 kΩ) — chip is
  always on as long as +14 V is present. Saves a GPIO. If you want
  software shutdown of the amp later, route PDN to D7/GPIO44 instead and
  share I²C SCL with another bus, or use a bottom-pad GPIO.
- **TAS5825M FAULTZ** open-drain output is left **NC** by default. To
  monitor faults, pull it up to 3V3 and route to a free GPIO (e.g.
  another bottom pad like GPIO39).
- **I²C address 0x4C** is selected by tying the TAS5825M `ADR` pin to
  GND. Tie to 3V3 for 0x4D if you ever wire two TAS5825M chips.
- **microSD logic level**: 3V3, matching XIAO's GPIOs. Avoid 5 V-only
  breakouts (or accept the on-board level shifter).
- **MSB-first 16-bit I²S** is the default both sides agree on; no extra
  init beyond what `tas5825m_init()` does in `src/main.cpp`.
- **Pot wiring**: 3V3 to one end, GND to the other, wiper to D0. If
  volume goes the wrong direction in software, swap the two end lugs.
- **Battery sense (optional, future)**: divide +14V_SW down 10:1 with two
  100 kΩ resistors and read on a free ADC pin (e.g. an unused bottom-pad
  GPIO). Not implemented in v1.
