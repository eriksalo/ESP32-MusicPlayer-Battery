# PCB plan

Target: a 2-layer module-carrier board you can order from JLCPCB or
PCBWay. **The 4 × 18650 pack lives in the enclosure, not on the PCB** —
only the BMS, IP2368 charger, buck, amp, XIAO, and microSD ride along.

This is the spec for the PCB. Once parts arrive, draw the schematic and
PCB in KiCad following the netlist (`NETLIST.md`) and the placement plan
below. A KiCad project skeleton + netlist generator is provided in
`pcb/`.

## 1. Board outline

**Size**: 110 × 75 mm rectangle, 1.6 mm thickness, 2 layers, **2 oz copper
on the power layer recommended** (handles the 4S → amp current path).

```
              110 mm
   ┌────────────────────────────────────────────────────┐
   │ M3                                              M3 │
   │  ●                                              ●  │
   │                                                    │   75 mm
   │   (component placement plan below)                 │
   │                                                    │
   │  ●                                              ●  │
   │ M3                                              M3 │
   └────────────────────────────────────────────────────┘
```

- Four **M3 mounting holes**, φ3.2 mm, 5 mm in from each corner.
- USB-C cutout on the **right edge** for the IP2368 module.
- USB-C cutout on the **bottom edge** for the XIAO module (programming).
- Speaker output JSTs on the **left edge**.
- Panel-wire JSTs (J_PWR, J_VOL, J_BTN, J_LED) on the **front edge**.

Adjust dimensions to your enclosure — internal connections stay valid.

## 2. Layer plan

| Layer | Use |
|-------|-----|
| **F.Cu** (top) | Module pads, signal traces, +3V3 / +5 V short fan-outs |
| **B.Cu** (bottom) | **GND fill (poured)**, +14 V_SW power pour as a separate filled zone routed island, audio crossovers if needed |
| **F.SilkS** | Reference designators, "L SPK" / "R SPK" / "VOL" / "BTN" / "LED" / "USB-C" labels, polarity arrows, "+14 V" warning near amp Vcc |
| **F.Mask / B.Mask** | Standard openings, plus mask-open via for the GPIO38 LED probe |
| **Edge.Cuts** | Outline + mounting holes |

GND pour on B.Cu (full plane), with a separate +14 V_SW filled zone on
B.Cu in the area between IP2368/BMS-input and TAS5825M/buck inputs.
Stitch GND with vias around module pads.

## 3. Component placement plan

Looking at the **top** of the board, USB-C ports facing **right** and
**bottom**, speakers on the **left**:

```
  ┌────────────────────────────────────────────────────────────────────┐
  │ ┌──────────┐  ┌─────────┐    ┌───────────────────┐                 │
  │ │   BMS    │  │  4S     │    │   IP2368 module   │═══ ← USB-C PD   │
  │ │   30A    │  │ balance │    │  (charger + PD)   │═══   charge in  │
  │ │          │  │  pads   │    └───────────────────┘                 │
  │ └────┬─────┘  └─────────┘                                          │
  │      │                                                              │
  │      │   ┌──────────────┐  ┌───────────────────┐  ┌───────────┐   │
  │      └──▶│  PCM5102A    │  │ TPA3116D2 (U2A)   │  │ buck U5   │   │
  │ J1   ◀───┤  DAC (U2)    │─▶│ stereo class-D    │  │ 14V→5V    │   │
  │ SPK_L│   │  L+R analog  │  │ BTL out, C1 1000µF│  └───────────┘   │
  │      ◀───┤              │  │                    │                    │
  │ J2       └──────────────┘  │                    │                    │
  │ SPK_R│                     └───────────────────┘                    │
  │      │                                                              │
  │      │   ┌──────────────┐    ┌────────────────┐                    │
  │      │   │  XIAO ESP32  │    │  microSD U3    │                    │
  │      │   │   -S3  (U1)  │═│  │                │                    │
  │      │   └──────────────┘    └────────────────┘                    │
  │      │            ║                                                 │
  │      │       USB-C (programming)                                    │
  │      │                                                              │
  │   J_PWR  J_VOL  J_BTN  J_LED         J_BAT (XT60)  J_BAL (5p XH)   │
  │   ┌──┐   ┌──┐   ┌──┐   ┌──┐          ┌────┐        ┌──────┐       │
  │   │  │   │  │   │  │   │  │          │    │        │      │       │
  │   └──┘   └──┘   └──┘   └──┘          └────┘        └──────┘       │
  └────────────────────────────────────────────────────────────────────┘
```

### Why this arrangement

- **BMS upper-left**: short fat traces from XT60 (J_BAT) to BMS to SW1 to
  the +14 V_SW pour. Carries the most current — keep paths short.
- **IP2368 upper-right with USB-C facing the edge**: charging port
  accessible on the enclosure side. Balance harness (J_BAL) is on the
  bottom edge with short routing to the IP2368 BAL pads.
- **TAS5825M centre-left, near the speaker connectors**: minimises
  speaker output trace length to J1/J2.
- **Buck (U5) between IP2368 and TAS5825M area**: takes 14 V from the
  +14 V_SW pour, outputs 5 V to a small +5 V trace running under the
  XIAO.
- **XIAO + microSD bottom-centre**: short I²S traces up to the TAS5825M,
  short I²C traces up too. SD SPI is local to the XIAO.
- **Panel-wire JSTs along bottom edge**: clean wiring to the front panel.

## 4. Routing guidelines

| Net group | Trace width | Notes |
|-----------|------------|-------|
| **VBAT_4S, +14V_SW (battery → amp)** | **0.8 mm (32 mil)** or pour | Up to 4 A peak under heavy bass. Use a poured zone where possible. **2 oz copper on this layer.** |
| **GND** | full pour on B.Cu | Single uninterrupted plane. Stitch with vias. |
| **+5V** | 0.4 mm (16 mil) | < 500 mA. |
| **+3V3** | 0.3 mm (12 mil) | < 200 mA. |
| **I²S** (BCLK, LRCLK, DOUT) | 0.2 mm (8 mil), routed parallel | Keep all three within ~5 mm of each other and away from the antenna. |
| **Analog audio** (AUDIO_L, AUDIO_R) | 0.2 mm (8 mil), short, **away from buck switching node** | Single-ended low-level signals; treat like analog mic-level. Run AUDIO_GND adjacent. |
| **SPI** (SD_*) | 0.2 mm (8 mil) | Keep `SD_SCK` away from `I2S_BCLK`. |
| **Pot, button, LED** | 0.2 mm (8 mil) | Slow signals. |
| **Speaker outputs (SPK_L±, SPK_R±)** | **0.5 mm (20 mil)**, route adjacent | Treat each pair as a differential pair. **The TPA3116D2 is BTL** — both sides swing. Don't ground either. |

### EMI / cross-talk specifics

1. **Antenna keep-out**: under and to the right of the antenna end of the
   XIAO ESP32-S3 module, leave a 5 mm × full-width copper-free keep-out on
   both layers. **No traces under the antenna.**
2. **TPA3116D2 decoupling**: place C1 (1000 µF) and C2 (100 nF) within 5 mm
   of the amp module's Vcc pin. Short, fat returns to GND.
3. **Speaker-output discipline**: the TPA3116D2 is class-D BTL, switching
   at ~400 kHz; the LC output filter is on the breakout itself, but still
   keep each speaker pair (L+/L-, R+/R-) tightly coupled on-board and
   twist the off-board wires.
4. **Analog audio shielding**: the L/R analog lines between PCM5102A and
   TPA3116D2 are the most noise-sensitive part of the chain. Keep them
   short (< 30 mm), away from the buck switching node, and run AUDIO_GND
   alongside as a shield.
5. **Buck switching node**: the buck module has its own switching node
   that can radiate. Keep it physically away (≥10 mm) from the XIAO
   antenna, the analog audio lines, and the I²S bus.

## 5. Design rules (JLCPCB-compatible)

| Rule | Value |
|------|-------|
| Min trace width | 6 mil (0.15 mm) |
| Min spacing | 6 mil (0.15 mm) |
| Min via diameter | 0.6 mm |
| Min drill | 0.3 mm |
| Annular ring | 0.15 mm |
| Min hole-to-hole | 0.5 mm |
| Edge-to-track | 0.3 mm |
| **Copper weight** | **2 oz on top + bottom (recommended for 4S power path)** |

## 6. Fabrication output (gerbers)

Same workflow as 1S build. Export from KiCad:

**Plot → Gerbers**:
- Layers: `F.Cu`, `B.Cu`, `F.Paste`, `B.Paste`, `F.Silkscreen`,
  `B.Silkscreen`, `F.Mask`, `B.Mask`, `Edge.Cuts`
- Format: Gerber X2
- Subtract soldermask from silkscreen: yes
- Plot reference designators: yes (top side at minimum)

**Drill files**:
- Format: Excellon, mm

Zip and upload to JLCPCB. Settings:
- Layers: 2
- Dimensions: 110 × 75 mm
- Thickness: 1.6 mm
- Material: FR-4
- Solder mask: any
- Silkscreen: white (on green/red/blue/black) or black (on white)
- Surface finish: HASL lead-free (cheap), ENIG (~$3 more, recommended)
- **Copper weight: 2 oz top and bottom** (~$6 surcharge but worth it for the power path)
- Quantity: 5

Cost: typically **$8 board fab + $12 shipping** at 2 oz copper.

## 7. Assembly notes

### Order of assembly (lowest profile first)
1. SMD passives on top: C1, C2, C3, C4, C5, C6, C7, R1, R2, R3, R4
   (and L1/optional LC filter if not on the breakout).
2. JST-PH headers along the front edge (J_PWR, J_VOL, J_BTN, J_LED).
3. Speaker connectors J1, J2.
4. XT60 (J_BAT) and JST-XH 5-pin (J_BAL).
5. 2.54 mm headers for the modules — solder these flush so modules sit
   parallel.
6. Modules: XIAO, TAS5825M, microSD, IP2368, buck.
7. **The BMS** sits on its own 2-pin or 4-pin header pads (depends on
   your specific BMS — many wire directly via thick wires rather than a
   header).

### Bring-up procedure (do in this order)

1. **Visual inspection**: solder bridges, especially XIAO castellated
   pads and the GPIO38 via.
2. **Continuity check**: GND ↔ all module GND pins. No short between
   +14V_SW and GND. No short between +5V and GND. No short between +3V3
   and GND.
3. **Trim the buck output to 5.0 V**: with a bench supply at 14 V
   feeding the +14V_SW node (via the SW1 throw side), measure VOUT of
   the buck module and adjust the trim until it's exactly 5.0 V (give or
   take 50 mV). *Do this **before** any other module is plugged in.*
4. **Plug in modules**: XIAO, microSD breakout, TAS5825M, IP2368.
5. **Power up via USB-C PD on the IP2368** (no battery yet): you should
   see fuel-gauge LEDs flash on the IP2368, the XIAO's 3V3 LED come up,
   and serial output on the XIAO USB-C port if connected to a host.
6. **Build the 4S pack** (4 cells, BMS, balance harness, XT60 pigtail)
   on a non-conductive surface with a multimeter handy. Verify pack
   voltage at XT60 is 14–16 V. Verify each cell tap is within ±50 mV of
   its neighbours.
7. **Plug in the pack**: SW1 off → measure +14V_SW = 0 V. SW1 on →
   measure +14V_SW = pack voltage. Listen / smell for anything weird.
8. **Flash firmware**, upload web UI, listen for the captive-portal AP.
9. **Connect speakers** (don't crank volume yet). Play a test track at
   low volume; verify left and right channels independently with a
   stereo file.
10. **Run for an hour at moderate volume**, monitor amp Vcc decoupling
    cap and BMS temperature. Anything > 60 °C wants investigation.

## 8. Where to draw all this

The KiCad project skeleton is at [`pcb/README.md`](../pcb/README.md). The
netlist generator at [`pcb/gen_netlist.py`](../pcb/gen_netlist.py) emits
an importable `.net` file — one click in KiCad's PCB editor populates
all components and ratsnest connections.

Recommended symbol/footprint sources:

| Module | Library |
|--------|---------|
| XIAO ESP32-S3 | [Seeed_KiCad_Library](https://github.com/Seeed-Studio/OPL_Kicad_Library) |
| PCM5102A breakout | `Connector_Generic:Conn_01x10_2.54mm` (treat as a 10-pin header — pin order varies by vendor) |
| TPA3116D2 module | `Connector_Generic:Conn_01x09_2.54mm` (or whatever pin count your specific module uses) |
| microSD breakout | `Connector_Generic:Conn_01x06_2.54mm` |
| IP2368 module | `Connector_Generic:Conn_01x06_2.54mm` (or x08 — module-dependent) |
| Buck (MP1584 module) | `Connector_Generic:Conn_01x04_2.54mm` |
| BMS | `Connector_Generic:Conn_01x06` (B+, B-, B1, B2, B3, P+) — wire P- directly to GND |
| XT60 connector | KiCad built-in or `Connector:XT60` from a hobby library |
| JST-XH 5-pin balance | `Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical` |
| Pot, switch, button, LED | Built-in KiCad libraries |
