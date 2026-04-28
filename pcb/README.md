# `pcb/` — KiCad design files

This folder contains everything you need to land a routable PCB in KiCad
without drawing the schematic by hand.

## What's here

| File | Purpose |
|------|---------|
| `gen_netlist.py` | Python script that generates the KiCad netlist + BOM. **This is the source of truth** for the connection list — mirrors `docs/NETLIST.md`. |
| `esp-music-player.net` | KiCad-format netlist, importable into KiCad PCB Editor. Regenerate with `python3 pcb/gen_netlist.py`. |
| `esp-music-player.bom.csv` | Plain-text bill of materials extracted from the netlist. |
| (after you start) `esp-music-player.kicad_pro` / `.kicad_pcb` / `.kicad_sch` | KiCad project files — created by KiCad on first open. |

## Workflow (the short version)

1. **Install KiCad 8.x.**
2. **Add the Seeed library** (only required because the XIAO ESP32-S3 isn't
   in KiCad's stock libs):
   ```sh
   git clone https://github.com/Seeed-Studio/OPL_Kicad_Library.git ~/kicad-libs/seeed
   ```
   In KiCad: *Preferences → Manage Symbol Libraries → Add* `~/kicad-libs/seeed/Seeed Studio.kicad_sym`
   and *Manage Footprint Libraries → Add* `~/kicad-libs/seeed/Seeed Studio.pretty`.
3. **Create a new project here**: *File → New Project →* save as
   `pcb/esp-music-player.kicad_pro`.
4. **Open the PCB Editor** (the icon labelled "PCB Editor" / pcbnew).
5. **Import the netlist**: *File → Import Netlist → choose
   `pcb/esp-music-player.net`*. Click *Update PCB*.
   - KiCad creates 15 footprints, dropped in a stack at origin.
   - All ratsnest connections (the thin yellow lines) are drawn from the
     netlist — they encode all 18 nets.
6. **Set the board outline** on `Edge.Cuts` per `docs/PCB_PLAN.md` §1
   (80 × 55 mm rectangle, 4× M3 mounting holes).
7. **Place** components per `docs/PCB_PLAN.md` §3.
8. **Route** per `docs/PCB_PLAN.md` §4 (trace widths matter — 0.6 mm for
   battery/+5V, 0.2 mm for signals, 0.5 mm for speaker).
9. **DRC** (*Inspect → Design Rules Checker*); fix anything that flags.
10. **Generate gerbers** per `docs/PCB_PLAN.md` §6, zip, upload to JLCPCB.

## Why no schematic?

Hand-authoring a `.kicad_sch` for 15 components requires embedding a full
symbol library definition (graphics primitives + pins + properties for
every symbol used) and laying out wires/labels with explicit coordinates.
Without KiCad to validate, every typo silently breaks the file.

The netlist contains the same electrical information that the schematic
would, so you can route the PCB from it directly. If you want a schematic
for visual reference / future edits, draw one in KiCad afterwards —
*Tools → Update Schematic from PCB* will back-annotate the wires.

## When you change firmware pins

If you change a pin assignment in `include/config.h`, also:

1. Update the GPIO labels in `docs/PINMAP.md`.
2. Update the corresponding net in `docs/NETLIST.md`.
3. Update `NETS = [...]` in `pcb/gen_netlist.py`.
4. Re-run `python3 pcb/gen_netlist.py`.
5. In KiCad PCB Editor: *File → Import Netlist* again. KiCad will warn
   about removed/changed connections — accept the changes.

## What to commit

After you've drawn the PCB, commit:

- `esp-music-player.kicad_pro`
- `esp-music-player.kicad_sch` (if you draw one)
- `esp-music-player.kicad_pcb`
- `esp-music-player.net` (regenerated)
- `esp-music-player.bom.csv` (regenerated)
- `gen_netlist.py` (already committed)

`.gitignore` already excludes the local/derived files
(`.kicad_prl`, `fp-info-cache`, `_autosave-*`, `*-backups/`, `gerbers/`).

## Verification before fab

- [ ] DRC passes with **no errors**.
- [ ] Visually verify GND pour completeness on B.Cu.
- [ ] Visually verify the +14V_SW pour reaches TAS5805M Vcc and buck
      VIN+ with adequate copper (≥ 0.8 mm equivalent or pour zone).
- [ ] Verify the LED ratsnest shows GPIO38 connected — if KiCad shows
      U1 pin 15 as a no-connect, your Seeed footprint version doesn't
      include the bottom pad. Drop a small via on the carrier PCB under
      the module's GPIO38 bottom pad and route LED_DRV from there.
- [ ] Verify nothing routes under the XIAO ESP32-S3 antenna (opposite
      end from USB-C).
- [ ] XT60 polarity at J_BAT matches the connector keying.
- [ ] J_BAL pin 1 = pack negative; pin 5 = pack positive (RC LiPo
      standard order). Match your balance harness.
- [ ] IP2368 module pinout matches what `gen_netlist.py` declares —
      different vendors use different pad layouts. If yours differs,
      edit the U4 block in `gen_netlist.py` and re-run.
- [ ] TAS5805M breakout pinout (10 control + 4 speaker) matches what
      `gen_netlist.py` declares. DFRobot DFR0721 is the reference; clones
      may differ.
- [ ] Order of pins on each JST (J_PWR / J_VOL / J_BTN / J_LED / J_BAL)
      matches your harnesses.

## Known limitations / things to verify on the bench

- **TAS5805M breakout pinout**: the netlist models a generic 14-pin header
  layout. The DFRobot DFR0721 silkscreen is the reference. If your breakout
  arrives with a different pin order (especially SDA/SCL position or which
  side speaker outputs come out), edit the U2 block in `gen_netlist.py`,
  re-run, and re-import.
- **IP2368 module variants**: pinout in `MODULES.md` is for the most common
  hobby form factor. Some modules expose 6 pins, others 8 (split charge /
  discharge). Confirm against your actual module's silkscreen.
- **GPIO38 LED bottom-pad access**: requires a via on the carrier PCB
  under the module's bottom pad. The Seeed `XIAO-ESP32-S3` footprint
  includes the bottom pad; if your library version doesn't, you can
  reassign the LED to the unused GPIO44/D7 (currently I²C SCL — swap
  with a different free GPIO).
- **U1 pin numbering**: the netlist uses logical pin numbers 1–15. KiCad
  will match these to whatever the Seeed footprint expects — verify the
  ratsnest after import; if the labels look wrong, your Seeed library
  version uses different pad numbering.
