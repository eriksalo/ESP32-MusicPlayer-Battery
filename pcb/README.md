# `pcb/` — KiCad project

This folder is where the KiCad design files live. It's intentionally
**empty for now** — the design is fully specified in the docs, but the
KiCad files themselves should be authored in KiCad (not hand-edited),
because hand-written `.kicad_sch` / `.kicad_pcb` files are easy to
silently corrupt without the tool to verify them.

## Specification (read these first)

The PCB is fully specified by three documents:

1. [`../docs/BOM.md`](../docs/BOM.md) — exact parts and where to buy.
2. [`../docs/MODULES.md`](../docs/MODULES.md) — pinouts and mechanical
   dimensions of every module.
3. [`../docs/NETLIST.md`](../docs/NETLIST.md) — every electrical net.
4. [`../docs/PCB_PLAN.md`](../docs/PCB_PLAN.md) — board outline,
   placement, layer plan, design rules, JLCPCB order spec.

## Workflow to draw the board

### 1. Install KiCad 8.x

- macOS: `brew install --cask kicad`
- Linux: `sudo apt install kicad` (≥ 8.0) or use the official AppImage
- Windows: download from <https://www.kicad.org/download/>

### 2. Add the Seeed footprint/symbol library

The XIAO ESP32-S3 isn't in KiCad's stock libraries.

```sh
git clone https://github.com/Seeed-Studio/OPL_Kicad_Library.git ~/kicad-libs/seeed
```

In KiCad: **Preferences → Manage Symbol Libraries → Add (folder icon) →**
point at `~/kicad-libs/seeed/Seeed Studio.kicad_sym`. Repeat for footprints
(**Manage Footprint Libraries → Add → `Seeed Studio.pretty`**).

The XIAO ESP32-S3 symbol is named `XIAO-ESP32S3` and the footprint is
`XIAO-ESP32-S3` (with the bottom castellated + bottom pad layout).

### 3. Create the project here

In KiCad: **File → New Project →** save as
`pcb/esp-music-player.kicad_pro`. Open the schematic editor.

### 4. Draw the schematic from `NETLIST.md`

Place these symbols (use built-in KiCad libraries unless noted):

| Ref | Symbol | Library |
|-----|--------|---------|
| U1 | `XIAO-ESP32S3` | Seeed Studio (added above) |
| U2 | `Conn_01x07_Female` | Connector_Generic |
| U3 | `Conn_01x06_Female` | Connector_Generic |
| U4 | `Conn_01x04_Female` | Connector_Generic *(or x06 — match your IP5306 module)* |
| BT1 / H1 | `BatteryHolder_Keystone_1042_1x18650` | Battery |
| RV1 | `R_Potentiometer` | Device |
| SW1 | `SW_SPDT` *(use as SPST)* | Switch |
| SW2 | `SW_Push` | Switch |
| D1 | `LED` | Device |
| R1 | `R` | Device |
| C1, C3 | `C` (10 µF) | Device |
| C2, C4 | `C` (100 nF) | Device |
| FB1 *(optional)* | `Ferrite_Bead` | Device |
| J1 | `Conn_01x02_Female` | Connector_Generic |
| J_PWR / J_VOL / J_BTN / J_LED | `Conn_01x02` / `Conn_01x03` etc. | Connector_Generic |

Wire them per `NETLIST.md`. Add **power flags** on `+5V` and `+3V3` so ERC
doesn't complain. Save (`Ctrl-S`), then **Tools → Electrical Rules Check**.
Fix any unconnected-pin errors before proceeding.

### 5. Assign footprints

**Tools → Assign Footprints** (or `Ctrl-Shift-F`). Match every symbol to a
footprint:

- U1: `Seeed Studio:XIAO-ESP32-S3`
- U2, U3, U4: `Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical`
  (and 1x06 / 1x04 variants)
- BT1/H1: `Battery:BatteryHolder_Keystone_1042_1x18650`
- RV1: `Potentiometer_THT:Potentiometer_Bourns_PDB181-K_Vertical`
  (or whatever fits the panel pot you ordered — for **panel-wired** pots,
  use a 3-pin JST-PH `Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical`
  on the PCB instead and wire to the pot off-board)
- SW1: 3-pin JST-PH or solder pads
- SW2: 2-pin JST-PH
- D1: 2-pin JST-PH (panel-wired) or `LED_THT:LED_D5.0mm`
- R1, C1–C4: `Resistor_SMD:R_0805_2012Metric` / `Capacitor_SMD:C_0805_2012Metric`
- J1: `Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical`
- J_PWR/etc: same JST-PH family

### 6. Layout the PCB

**Tools → Update PCB from Schematic**. Follow `PCB_PLAN.md` §3 for
placement and §4 for routing widths. Recommended order:

1. Set the board outline on `Edge.Cuts`: 80 × 55 mm rectangle, four M3 holes.
2. Place the big modules first (XIAO centre, IP5306 right, 18650 holder
   left, MAX98357A left of XIAO, microSD right of XIAO).
3. Place panel connectors along the bottom edge.
4. Place SMD passives near their respective module Vin pins.
5. Route power (`+5V`, `VBAT_SW`) at 0.6 mm.
6. Route signals (I²S, SPI) at 0.2 mm.
7. Route speaker output at 0.5 mm.
8. Pour `GND` on B.Cu (Filled Zone, B.Cu, net `GND`).
9. **Tools → Design Rules Check**. Fix any clearance / unconnected errors.

### 7. Generate fab outputs

Follow `PCB_PLAN.md` §6. Resulting `.zip` of gerbers + drills uploads
directly to JLCPCB / PCBWay.

## What ends up in this folder

After you save the project, this folder will contain:

```
pcb/
├── esp-music-player.kicad_pro
├── esp-music-player.kicad_sch
├── esp-music-player.kicad_pcb
├── esp-music-player.kicad_prl     (local project state — gitignore-able)
├── fp-info-cache                  (local — gitignore-able)
└── gerbers/                       (export output for JLCPCB)
```

Commit the `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, and any custom
symbol/footprint libraries. Don't commit `.kicad_prl`, `fp-info-cache`,
or `gerbers/` — those are derived.
