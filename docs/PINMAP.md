# GPIO pin map — Seeed XIAO ESP32-S3

The XIAO ESP32-S3 exposes **11 GPIOs on its castellated edge**. This
design uses 10; one (D7/GPIO44) is left as a spare.

Assignments are encoded in [`include/config.h`](../include/config.h) and
must match the netlist (`docs/NETLIST.md`) and the PCB.

| XIAO label | GPIO | Direction | Function |
|------------|------|-----------|----------|
| D0  | 1  | analog in  | Volume potentiometer (ADC1_CH0) |
| D1  | 2  | digital in | Push button (active-low, INPUT_PULLUP) |
| D2  | 3  | digital out| SD card CS |
| D3  | 4  | digital out| I²S BCLK    → PCM5102A BCK |
| D4  | 5  | digital out| I²S LRCLK   → PCM5102A LCK |
| D5  | 6  | digital out| I²S DOUT    → PCM5102A DIN |
| D6  | 43 | digital out| Status LED (through R1, 470 Ω) |
| D7  | 44 | —          | spare (could host battery sense, second button, fault input, etc.) |
| D8  | 7  | digital out| SD SCK |
| D9  | 8  | digital in | SD MISO |
| D10 | 9  | digital out| SD MOSI |

## Notes & caveats

- **Power switch SW1** is in the +14 V battery line, not on a GPIO. The
  BMS protects against over-discharge if you forget to switch off, but
  with no switch the player draws ~5–10 mA continuously, which depletes
  the pack in storage.
- **No I²C in this design** — the audio chain is XIAO I²S → PCM5102A
  (hardware-strapped) → analog → TPA3116D2 (no host control). All
  volume / mute / pause is software in the audioI2S library.
- **D7 / GPIO44 is intentionally unused** — reserved for future
  expansion. Common additions: battery voltage sense via a 100 kΩ ÷
  100 kΩ divider on a free ADC pin (note: GPIO44 is not ADC-capable;
  use a bottom-pad ADC GPIO if you add this), TPA3116D2 fault input,
  shutdown-pin control if your amp module exposes one.
- **microSD logic level**: 3V3, matching XIAO's GPIOs. Avoid 5 V-only
  breakouts.
- **MSB-first 16-bit I²S** is the default both sides agree on; no extra
  init needed beyond the audioI2S library's default I²S setup in
  `src/main.cpp`.
- **Pot wiring**: 3V3 to one end, GND to the other, wiper to D0. If
  volume goes the wrong direction in software, swap the two end lugs.
