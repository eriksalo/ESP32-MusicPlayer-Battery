# Schematic / wiring notes

ASCII reference for prototyping on the bench or for laying out the
carrier PCB. The KiCad project lives under `pcb/` (drawn locally —
see `pcb/README.md`).

## Power chain

```
       USB-C PD                                        SW1 (≥5A)
   (host charger)                                        │
        ║                                                │
        ▼                                                │
   ┌─────────────────────────────┐                       │
   │  IP2368 USB-C PD module     │                       │
   │   - PD trigger (5/9/15/20V) │                       │
   │   - 4S CC/CV charger        │                       │
   │   - balance support         │                       │
   │   - fuel-gauge LEDs         │                       │
   └─────────────┬───────────────┘                       │
       BAT+/-    │   BAL1..BAL3                          │
                 ▼                                        │
        ┌─────────────────────────┐                      │
        │   4S 18650 pack         │                      │
        │   BT1+── BT2+── BT3+── BT4+                     │
        │   BT1-   BT2-   BT3-   BT4-                     │
        │      │      │      │                             │
        │   (cells in series, each tap to BMS+IP2368)      │
        └─────────────┬───────────┘                       │
                      ▼                                    │
           ┌────────────────────┐                          │
           │  4S 30A BMS        │                          │
           │   - balance        │                          │
           │   - over-discharge │                          │
           │   - over-current   │                          │
           └────┬───────────┬───┘                          │
              P+│         P-│                              │
                ├────────────[ SW1 ]────── +14V_SW ────────┤
                │                          (~14.8V nom)    │
                │                                          │
                ▼                                          │
              GND ─────────────── common ground bus        │
                                                            │
   +14V_SW ───┬─── TPA3116D2 Vcc (C1 1000µF + C2 100nF nearby)
              │
              └─── Buck U5 VIN ──→ +5V ──┬── XIAO 5V pin (LDO → +3V3)
                                          ├── PCM5102A VIN
                                          └── microSD VCC

   +3V3 (XIAO LDO) ──┬── (microSD VCC if your breakout uses 3V3 instead of 5V)
                     ├── pot RV1 high lug
                     └── C4 (100nF) — XIAO 3V3 decoupling
```

## Audio (digital → analog → speakers)

```
   XIAO  ──── BCLK  (GPIO4) ──→ PCM5102A  BCK
   XIAO  ──── LRCLK (GPIO5) ──→ PCM5102A  LCK
   XIAO  ──── DOUT  (GPIO6) ──→ PCM5102A  DIN

   PCM5102A  LOUT ──→ TPA3116D2  L_IN
   PCM5102A  ROUT ──→ TPA3116D2  R_IN
   PCM5102A  AGND ──→ TPA3116D2  AGND_IN  (single-point tied to main GND)

   TPA3116D2  SPK_L+ ──→ J1 pin 1 ──→ Left speaker  (twisted pair to chassis)
   TPA3116D2  SPK_L- ──→ J1 pin 2
   TPA3116D2  SPK_R+ ──→ J2 pin 1 ──→ Right speaker
   TPA3116D2  SPK_R- ──→ J2 pin 2

   No I²C, no software amp init — PCM5102A is hardware-strapped on
   the breakout, TPA3116D2 has no control interface.
```

## SD card (SPI)

```
   XIAO ── SCK   (GPIO7) ──→ SD CLK
   XIAO ── MISO  (GPIO8) ←── SD DO
   XIAO ── MOSI  (GPIO9) ──→ SD DI
   XIAO ── CS    (GPIO3) ──→ SD CS
   +3V3 / GND from XIAO
```

## Controls and indicator

```
   3V3 ── pot end  ┐
                   ├── 10 kΩ pot RV1, wiper → XIAO D0 (GPIO1)
   GND ── pot end  ┘
                       (off-board on J_VOL JST-PH 3-pin)

   XIAO D1 (GPIO2, INPUT_PULLUP) ── SW2 ── GND
                       (off-board on J_BTN JST-PH 2-pin)

   XIAO D6 (GPIO43) ── R1 (470 Ω) ── D1 anode ── GND
                       (R1 on PCB; LED is on J_LED JST-PH 2-pin)
```

## Layout / EMI tips

- **Antenna keep-out** under the XIAO (opposite USB-C end). 5 mm clear of
  copper on both layers.
- **TAS5825M Vcc decoupling**: C1 (1000 µF), C2 (100 nF), C3 (22 µF) all
  within 5 mm of the Vcc pin. Short, fat returns to GND.
- **Speaker leads** as twisted pairs from J1/J2 to the speakers.
- **I²C pull-ups** close to the TAS5825M end of the trace.
- **Buck switching node** physically away from the XIAO antenna and the
  I²S bus.
- **GND plane** continuous on B.Cu — don't carve it up with traces.
- **2 oz copper** on top + bottom for the 4S → amp current path.

## Battery wiring outside the PCB

```
                  XT60 (J_BAT)
                   │ │
                   │ └── BMS B-/P- (= GND)
                   └──── BMS P+ ── carrier PCB +14V (through SW1)

   4S pack:
      BT1+ ── BMS B+ ── balance plug pin 5 (top) ── IP2368 BAT+
      BT1- = BT2+ ────── balance plug pin 4 ─────── IP2368 BAL3
      BT2- = BT3+ ────── balance plug pin 3 ─────── IP2368 BAL2
      BT3- = BT4+ ────── balance plug pin 2 ─────── IP2368 BAL1
      BT4- ─────── BMS B- ── balance plug pin 1 (bottom, GND)

   The 5-pin JST-XH balance plug (J_BAL on the PCB) carries the four
   cell taps + ground to BOTH the IP2368 module (for charge balancing)
   AND the BMS (for protection). In practice: one balance plug is
   parallel-tapped to both modules, or each module has its own balance
   plug into the pack.
```

## Future PCB / KiCad notes

When laying out:
- Use **castellated edge cutouts** for module footprints so modules sit
  flush on the carrier (JLCPCB/PCBWay handle this in 2-layer fine).
- The IP2368 module's USB-C connector should poke through a panel cutout
  on the right edge.
- The XIAO's USB-C should poke through a panel cutout on the bottom edge
  (or be accessible by removing the back of the enclosure for occasional
  reflashes).
- **The 4 × 18650 pack does not sit on the PCB** — it lives in the
  enclosure, wired to the carrier via the XT60 + balance harness.
- A panel-mount slide / rocker switch (SW1), pot (RV1), button (SW2),
  and LED (D1) are off-board and wired to the corresponding JST-PH
  headers along the front edge.

## When to step up to discrete

If you want a v2 with no breakout modules:
- TAS5825M is TQFN-32 — hand-solderable with hot air, plus an LC output
  filter (4 × inductors + 4 × MLCCs).
- IP2368 is QFN-40 — same difficulty as TAS5825M.
- Buck: TPS54331 (SOIC-8) or LM2596 (TO-263).
- BMS can be replaced by a discrete BQ77307 + protection FETs, but the
  layout becomes substantial. Module is the right call for v1.

For now, keep the modules — your board ends up with very few SMD parts
(R1–R4, C1–C7) and stays solidly hand-buildable.
