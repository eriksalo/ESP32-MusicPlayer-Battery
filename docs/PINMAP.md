# GPIO pin map — Seeed XIAO ESP32-S3

The XIAO ESP32-S3 exposes 11 GPIOs on its castellated edge. Assignments
below are also encoded in [`include/config.h`](../include/config.h).

| XIAO label | GPIO | Direction | Function | Connects to |
|------------|------|-----------|----------|-------------|
| D0  | 1   | analog in  | Volume potentiometer (ADC1_CH0) | 10 kΩ pot wiper; ends to 3V3 / GND |
| D1  | 2   | digital in | Momentary push button (active-low, internal pull-up) | Tactile button to GND |
| D2  | 3   | digital out| SD card CS                       | microSD socket CS  |
| D3  | 4   | digital out| I²S BCLK                         | MAX98357A BCLK     |
| D4  | 5   | digital out| I²S LRCLK / WS                   | MAX98357A LRC      |
| D5  | 6   | digital out| I²S DOUT / SD                    | MAX98357A DIN      |
| D6  | 43  | digital out| Status LED *(also UART0 TX)*     | LED + 470Ω → GND   |
| D7  | 44  | —          | reserved (UART0 RX)              | leave unconnected for serial debug |
| D8  | 7   | digital out| SD SCK                           | microSD socket CLK |
| D9  | 8   | digital in | SD MISO                          | microSD socket DO  |
| D10 | 9   | digital out| SD MOSI                          | microSD socket DI  |

## Notes & caveats

- **Power switch is not on a GPIO.** SW1 is wired in series between the 18650
  positive terminal and the IP5306 module's battery input. This fully isolates
  the battery when off (no parasitic drain from the boost converter).
- **LED on GPIO43** doubles as UART0 TX. With `ARDUINO_USB_CDC_ON_BOOT=1`
  (already set in `platformio.ini`) the USB-CDC port is the serial console, so
  GPIO43 is free for the LED. If you re-enable hardware UART for debugging,
  move the LED to a different pin.
- **MAX98357A `GAIN` pin**: leave floating for 9 dB, tie to GND for 12 dB,
  or to Vin for 6 dB. 9 dB is a good starting point with a 4Ω 5W speaker.
- **MAX98357A `SD` pin** (shutdown): tie to Vin (3V3 or 5V) for "always on /
  left+right summed mono". Don't drive it with `PIN_I2S_DOUT` despite the
  similar name — they're unrelated.
- **microSD logic level**: the XIAO's GPIOs are 3V3 — match that with a 3V3
  microSD breakout. Avoid 5V breakouts intended for AVRs.
- **Pot wiring**: connect both ends to 3V3 and GND, wiper to D0. The firmware
  reads with 12-bit resolution and applies hysteresis so a noisy pot doesn't
  spam the audio task.
