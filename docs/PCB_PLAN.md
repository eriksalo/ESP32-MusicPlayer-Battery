# PCB plan

Target: a 2-layer module-carrier board you can order from JLCPCB or PCBWay.
Almost no SMD soldering required — modules drop in via 2.54 mm headers, the
only "real" SMD parts are 0805 caps, an 0805 resistor, and (optionally) a
ferrite bead.

This document is **the spec for the PCB**. Once parts arrive, draw the
schematic and PCB in KiCad following the netlist (`NETLIST.md`) and the
placement plan below. A KiCad project skeleton is provided in `pcb/`.

## 1. Board outline

**Size**: 80 × 55 mm rectangle, 1.6 mm thickness, 2 layers.

```
        80.0 mm
   ┌──────────────────────────────────────┐
   │ M3 mounting hole (φ3.2)         M3   │
   │  ●                              ●    │
   │                                       │   55.0 mm
   │   (component placement plan below)    │
   │                                       │
   │  ●                              ●    │
   │ M3                              M3   │
   └──────────────────────────────────────┘
```

- Four **M3 mounting holes**, φ3.2 mm, 5 mm in from each corner.
- Internal cutout(s): none for v1. (If you mount the 18650 holder *on* the PCB,
  it sits over solid copper / silkscreen — no cutout needed.)

If your enclosure is different, change only the outline in KiCad — the
internal placement still works.

## 2. Layer plan

| Layer | Use |
|-------|-----|
| **F.Cu** (top) | Module pads, signal traces, +5V short fan-out |
| **B.Cu** (bottom) | GND fill (poured), a few crossover signals if needed |
| **F.SilkS** | Reference designators, "VOL" / "BTN" / "LED" / "SPK+/-" labels, polarity arrows |
| **F.Mask / B.Mask** | Standard openings |
| **Edge.Cuts** | Outline + mounting holes |

Single ground pour on B.Cu, stitched to top with vias around module
ground pads and at the IP5306 input.

## 3. Component placement plan

Looking at the **top** of the board (component side), USB-C ports facing
**right**, speaker out on the **left**:

```
       ┌──────────────────────────────────────────────────────────────┐
       │  ┌────────────┐                          ┌─────────────────┐ │
       │  │ 18650 holder│                         │   IP5306 module │═│ ← USB-C
       │  │   (H1, BT1) │                         │      (U4)       │═│   charge
       │  │             │                         └─────────────────┘ │
       │  └────────────┘                                              │
       │                                                              │
       │  ┌──────────────┐    ┌──────────────┐    ┌────────────────┐ │
       │  │ MAX98357A U2 │    │  XIAO ESP32  │    │  microSD U3    │ │
       │  │              │    │   -S3  (U1)  │═│  │                │ │
       │  │   I2S DIN ←──┼────┼─ I2S out     │═│  │  SPI to U1     │ │
       │  └──────────────┘    └──────────────┘    └────────────────┘ │
       │       ↑↑                                                     │
       │     SPK+ SPK- (J1, edge connector or screw terminal)         │
       │  ┌────┐                                                      │
       │  │ J1 │ ← speaker out                                        │
       │  └────┘                                                      │
       │                                                              │
       │   J_PWR  J_VOL  J_BTN  J_LED                                 │
       │   ┌──┐   ┌──┐   ┌──┐   ┌──┐                                  │
       │   │  │   │  │   │  │   │  │   ← panel-wire JST-PH headers    │
       │   └──┘   └──┘   └──┘   └──┘                                  │
       └──────────────────────────────────────────────────────────────┘
```

### Why this arrangement

- **18650 holder upper-left**: heaviest part; balances mass against the modules
  on the right edge. Cell length runs along the long axis of the board.
- **IP5306 upper-right with its USB-C facing the edge**: keeps the charging
  port accessible on the enclosure side.
- **XIAO in the centre**: shortest possible I²S traces to the amp on its left
  and SPI traces to the SD on its right. The XIAO's antenna end (opposite USB-C)
  faces the bottom edge — keep a 5 mm copper keep-out under it.
- **MAX98357A on the left**: speaker output `J1` is on the same side, so
  speaker leads stay short and twisted.
- **Panel-wire connectors (J_PWR, J_VOL, J_BTN, J_LED) along the bottom edge**:
  one row of JST-PH headers makes wiring to the front panel of the enclosure
  tidy.

## 4. Routing guidelines

| Net group | Recommended trace width | Notes |
|-----------|------------------------|-------|
| VBAT_SW, +5V (battery rails) | **0.6 mm (24 mil)** | Up to 2 A under charge / heavy bass. |
| GND | pour on B.Cu | Single uninterrupted plane; stitch with vias. |
| +3V3 | 0.4 mm (16 mil) | <500 mA. |
| I²S (`I2S_BCLK`, `I2S_LRCLK`, `I2S_DOUT`) | 0.2 mm (8 mil), routed together | Keep all three within ~5 mm of each other and away from the antenna. Length-matching is not required at audio rates. |
| SPI (`SD_*`) | 0.2 mm (8 mil) | Keep `SD_SCK` away from `I2S_BCLK`; ideally route them on different layers near the module pins. |
| Pot, button, LED | 0.2 mm (8 mil) | Slow signals; route freely. |
| Speaker out (SPK±) | 0.5 mm (20 mil) | Keep these two traces close together; if possible, **don't** put them on the bottom layer over the GND pour for the digital section — the magnetic-field return looks better with the dedicated SPK return adjacent. |

### EMI / cross-talk specifics

1. **Antenna keep-out**: under and to the right of the antenna end of the
   XIAO ESP32-S3 module, leave a 5 mm × full-width copper-free keep-out on
   both layers. Don't run traces underneath the antenna.
2. **MAX98357A decoupling**: place C1 (10 µF) and C2 (100 nF) within 5 mm of
   the Vin pin, on the **same** layer as the module, with a short via to GND.
3. **Speaker-return discipline**: the MAX98357A is a class-D bridge; both
   `SPK+` and `SPK-` swing. Treat them like a differential pair — twist the
   wire pigtail and run the on-board traces side-by-side at 0.5 mm/0.5 mm.
4. **Charge / boost noise on +5V**: if you hear hash through the speaker,
   populate `FB1` (ferrite bead) in series with MAX98357A Vin and add
   `C5` (220 µF electrolytic) on the IP5306 5 V output.

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

These match JLCPCB's free 2-layer process. Don't go below 6/6 mil unless you
have a reason — it costs more and is harder to inspect.

## 6. Fabrication output (gerbers)

When the layout is done, export from KiCad:

**Plot → Gerbers**:
- Layers: `F.Cu`, `B.Cu`, `F.Paste`, `B.Paste`, `F.Silkscreen`, `B.Silkscreen`,
  `F.Mask`, `B.Mask`, `Edge.Cuts`
- Format: Gerber X2
- "Use Protel filename extensions": optional (JLCPCB accepts both)
- Subtract soldermask from silkscreen: yes
- Plot reference designators: yes (top side at minimum)

**Drill files** (next button):
- Format: Excellon
- Drill units: mm
- Mirror Y axis: no
- Minimal header: no
- PTH + NPTH in **separate files** (or merged — both are fine)

Zip the resulting folder. Upload to JLCPCB:
- Layers: 2
- Dimensions: 80 × 55 mm
- Thickness: 1.6 mm
- Material: FR-4
- Solder mask: any
- Silkscreen: white (on green/red/blue/black mask) or black (on white mask)
- Surface finish: HASL lead-free (cheap), ENIG (~$2 more, much nicer pads)
- Quantity: 5 (minimum for the cheap tier)

Cost: typically **$5 board fab + $10 shipping** to the US (~2–5 days express,
~3 weeks economy).

## 7. Assembly notes

Order of assembly (lowest profile first):
1. SMD passives on top side: C1, C2, C3, C4, R1 (and FB1 if populating).
2. JST-PH headers along the bottom edge.
3. Speaker connector J1.
4. 2.54 mm headers for the modules — solder these flush to the PCB so the
   module sits parallel.
5. 18650 holder H1 (through-hole, big pins — solder with plenty of heat).
6. Insert modules into headers (XIAO, MAX98357A, microSD, IP5306).
7. **Do not insert the 18650 cell** until everything else is verified.

### Bring-up

1. Visually inspect for solder bridges, especially around the XIAO castellated
   pads.
2. Confirm continuity GND ↔ all module GNDs with multimeter.
3. Confirm no short between +5V and GND, between +3V3 and GND, between
   `VBAT_SW+` and GND.
4. Apply +5V to the 5V pad **manually** from a bench supply (current limit
   100 mA): the XIAO 3V3 LED should illuminate; nothing should get warm.
5. Insert the cell. Confirm the XIAO comes up. Watch on USB serial for the
   captive-portal AP banner from the firmware.

## 8. Where to draw all this

The KiCad project skeleton is at [`pcb/esp-music-player.kicad_pro`](../pcb/).
Open in **KiCad 8.x** (KiCad 7 will work but file format will get auto-upgraded).

Recommended symbol/footprint sources:

| Module | Library |
|--------|---------|
| XIAO ESP32-S3 | [Seeed_KiCad_Library](https://github.com/Seeed-Studio/OPL_Kicad_Library) — symbol `XIAO-ESP32S3`, footprint `XIAO-ESP32-S3` |
| MAX98357A breakout | KiCad built-in `Connector_Generic:Conn_01x07_2.54mm` (treat as a 7-pin header) |
| microSD breakout | `Connector_Generic:Conn_01x06_2.54mm` |
| IP5306 module | `Connector_Generic:Conn_01x04_2.54mm` (or x06 depending on the module) |
| 18650 holder Keystone 1042 | KiCad built-in `Battery:BatteryHolder_Keystone_1042_1x18650` |
| Pot, switch, button, LED | Built-in KiCad libraries |

Use the **netlist** in `NETLIST.md` as your verification — after drawing the
schematic, run KiCad's ERC and the netlist that comes out should match line
for line.
