#!/usr/bin/env python3
"""
Generate a KiCad-compatible netlist for ESP32-MusicPlayer-Battery.

Produces:
  pcb/esp-music-player.net      KiCad netlist (importable into PCB Editor)
  pcb/esp-music-player.bom.csv  Plain-text bill of materials

Usage:
  python3 pcb/gen_netlist.py

This script is the source of truth for both the BOM and the connection list.
It mirrors docs/NETLIST.md. If you change firmware pins in
include/config.h, update PIN_OF_REF and re-run this script.

Importing into KiCad (8.x):
  1. File -> New Project -> save as pcb/esp-music-player.kicad_pro
  2. Open the PCB Editor (pcbnew).
  3. File -> Import Netlist -> choose pcb/esp-music-player.net
  4. KiCad will create footprint instances for every component.
  5. Click Update PCB; assign / verify each footprint, then place + route.
"""

import csv
import datetime
import os
import sys
import uuid as _uuid
from textwrap import indent

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Component table
#   ref:        designator (must be unique)
#   value:      shown in PCB editor footprint property
#   footprint:  "library:footprint_name" — must exist in user's KiCad install
#   pins:       {pin_num: pin_name}
#   pin_types:  {pin_num: type}  ("passive", "power_in", "power_out",
#                                 "input", "output", "bidirectional",
#                                 "tri_state", "open_collector")
#   desc:       free-form description
# ---------------------------------------------------------------------------

PASSIVE = "passive"
PWR_IN  = "power_in"
PWR_OUT = "power_out"
IN      = "input"
OUT     = "output"
BIDIR   = "bidirectional"

COMPONENTS = [
    # ----- U1: Seeed XIAO ESP32-S3 (14-pin module — uses Seeed footprint) -----
    {
        "ref": "U1",
        "value": "XIAO_ESP32S3",
        "footprint": "Seeed Studio:XIAO-ESP32-S3",
        "desc": "Seeed XIAO ESP32-S3 module",
        "pins": {
            "1":  "D0_GPIO1",   "2":  "D1_GPIO2",   "3":  "D2_GPIO3",
            "4":  "D3_GPIO4",   "5":  "D4_GPIO5",   "6":  "D5_GPIO6",
            "7":  "D6_GPIO43",  "8":  "D7_GPIO44",  "9":  "D8_GPIO7",
            "10": "D9_GPIO8",   "11": "D10_GPIO9",  "12": "+3V3",
            "13": "GND",        "14": "+5V",
        },
        "pin_types": {
            "12": PWR_OUT, "13": PWR_IN, "14": PWR_IN,
            **{p: PASSIVE for p in ["1","2","3","4","5","6","7","8","9","10","11"]},
        },
    },

    # ----- U2: MAX98357A I²S amp breakout (7-pin header) -----
    {
        "ref": "U2",
        "value": "MAX98357A",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical",
        "desc": "MAX98357A I2S amplifier breakout",
        "pins": {"1":"Vin","2":"GND","3":"SD","4":"GAIN","5":"DIN","6":"BCLK","7":"LRC"},
        "pin_types": {"1":PWR_IN,"2":PWR_IN,"3":PASSIVE,"4":PASSIVE,
                      "5":IN,"6":IN,"7":IN},
    },

    # ----- U3: microSD breakout (SPI, 6-pin) -----
    {
        "ref": "U3",
        "value": "microSD_Breakout",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical",
        "desc": "microSD card breakout, SPI mode (3V3 logic)",
        "pins": {"1":"VCC","2":"GND","3":"CS","4":"MOSI","5":"SCK","6":"MISO"},
        "pin_types": {"1":PWR_IN,"2":PWR_IN,"3":IN,"4":IN,"5":IN,"6":OUT},
    },

    # ----- U4: IP5306 18650 charger + boost module -----
    # 4-pin header: BAT+, BAT-, OUT+(5V), GND  (USB-C charging is on-board)
    {
        "ref": "U4",
        "value": "IP5306_Module",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        "desc": "IP5306 18650 charger + 5V boost module (USB-C in)",
        "pins": {"1":"BAT+","2":"BAT-","3":"OUT_5V","4":"GND"},
        "pin_types": {"1":PWR_IN,"2":PWR_IN,"3":PWR_OUT,"4":PWR_IN},
    },

    # ----- BT1: 18650 cell + Keystone holder -----
    {
        "ref": "BT1",
        "value": "Battery_18650",
        "footprint": "Battery:BatteryHolder_Keystone_1042_1x18650",
        "desc": "18650 cell + Keystone 1042 holder",
        "pins": {"1":"+","2":"-"},
        "pin_types": {"1":PWR_OUT,"2":PWR_OUT},
    },

    # ----- J1: speaker output (2-pin JST-PH) -----
    {
        "ref": "J1",
        "value": "SPK_OUT_JSTPH2",
        "footprint": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "desc": "Speaker output (wires from MAX98357A SPK+/SPK- pads)",
        "pins": {"1":"SPK+","2":"SPK-"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },

    # ----- J_PWR: off-board slide switch SW1 (2-pin JST-PH) -----
    {
        "ref": "J_PWR",
        "value": "PWR_SW_JSTPH2",
        "footprint": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "desc": "Off-board SPST slide switch SW1 (battery line)",
        "pins": {"1":"BAT_RAW","2":"BAT_SW"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },

    # ----- J_VOL: off-board 10k pot RV1 (3-pin JST-PH) -----
    {
        "ref": "J_VOL",
        "value": "VOL_POT_JSTPH3",
        "footprint": "Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
        "desc": "Off-board 10k volume pot RV1",
        "pins": {"1":"GND","2":"WIPER","3":"VCC"},
        "pin_types": {"1":PWR_IN,"2":OUT,"3":PWR_IN},
    },

    # ----- J_BTN: off-board momentary push button SW2 -----
    {
        "ref": "J_BTN",
        "value": "BTN_JSTPH2",
        "footprint": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "desc": "Off-board momentary push button SW2",
        "pins": {"1":"BTN_N","2":"GND"},
        "pin_types": {"1":IN,"2":PWR_IN},
    },

    # ----- J_LED: off-board LED D1 (R1 stays on PCB) -----
    {
        "ref": "J_LED",
        "value": "LED_JSTPH2",
        "footprint": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "desc": "Off-board status LED D1 (R1 lives on PCB)",
        "pins": {"1":"ANODE","2":"CATHODE"},
        "pin_types": {"1":IN,"2":PWR_IN},
    },

    # ----- R1: LED current-limit resistor -----
    {
        "ref": "R1",
        "value": "470",
        "footprint": "Resistor_SMD:R_0805_2012Metric",
        "desc": "LED current-limit resistor (470 ohm)",
        "pins": {"1":"~","2":"~"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },

    # ----- C1: MAX98357A Vin bulk -----
    {
        "ref": "C1",
        "value": "10uF",
        "footprint": "Capacitor_SMD:C_0805_2012Metric",
        "desc": "Bulk decoupling at MAX98357A Vin",
        "pins": {"1":"~","2":"~"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },
    # ----- C2: MAX98357A Vin HF -----
    {
        "ref": "C2",
        "value": "100nF",
        "footprint": "Capacitor_SMD:C_0805_2012Metric",
        "desc": "HF decoupling at MAX98357A Vin",
        "pins": {"1":"~","2":"~"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },
    # ----- C3: +5V bulk near IP5306 output -----
    {
        "ref": "C3",
        "value": "10uF",
        "footprint": "Capacitor_SMD:C_0805_2012Metric",
        "desc": "Bulk decoupling on +5V near IP5306 output",
        "pins": {"1":"~","2":"~"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },
    # ----- C4: XIAO 3V3 HF -----
    {
        "ref": "C4",
        "value": "100nF",
        "footprint": "Capacitor_SMD:C_0805_2012Metric",
        "desc": "HF decoupling at XIAO 3V3 pin",
        "pins": {"1":"~","2":"~"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },
]

# ---------------------------------------------------------------------------
# Net table — list of (net_name, [(ref, pin), ...])
# Mirrors docs/NETLIST.md.
# ---------------------------------------------------------------------------

NETS = [
    # ----- power -----
    ("VBAT_RAW", [("BT1", "1"), ("J_PWR", "1")]),         # 18650 + → switch in
    ("VBAT_SW",  [("J_PWR", "2"), ("U4", "1")]),          # switch out → IP5306 BAT+
    ("GND",      [
        ("BT1", "2"),       # 18650 -
        ("U4", "2"),        # IP5306 BAT-
        ("U4", "4"),        # IP5306 GND
        ("U1", "13"),       # XIAO GND
        ("U2", "2"),        # MAX98357A GND
        ("U3", "2"),        # microSD GND
        ("J_VOL", "1"),
        ("J_BTN", "2"),
        ("J_LED", "2"),
        ("C1", "2"), ("C2", "2"), ("C3", "2"), ("C4", "2"),
    ]),
    ("+5V",      [
        ("U4", "3"),        # IP5306 5V out
        ("U1", "14"),       # XIAO 5V in
        ("U2", "1"),        # MAX98357A Vin
        ("U2", "3"),        # MAX98357A SD/MODE → Vin (always-on, mono)
        ("C1", "1"), ("C2", "1"), ("C3", "1"),
    ]),
    ("+3V3",     [
        ("U1", "12"),       # XIAO 3V3 LDO out
        ("U3", "1"),        # microSD VCC
        ("J_VOL", "3"),     # pot top
        ("C4", "1"),
    ]),

    # ----- I2S audio -----
    ("I2S_BCLK",  [("U1", "4"), ("U2", "6")]),
    ("I2S_LRCLK", [("U1", "5"), ("U2", "7")]),
    ("I2S_DOUT",  [("U1", "6"), ("U2", "5")]),

    # ----- speaker out (J1 wired off-board to MAX98357A's onboard SPK terminal) -----
    ("SPK+", [("J1", "1")]),
    ("SPK-", [("J1", "2")]),

    # ----- microSD SPI -----
    ("SD_CS",   [("U1", "3"),  ("U3", "3")]),
    ("SD_MOSI", [("U1", "11"), ("U3", "4")]),
    ("SD_SCK",  [("U1", "9"),  ("U3", "5")]),
    ("SD_MISO", [("U1", "10"), ("U3", "6")]),

    # ----- controls / indicator -----
    ("VOL_WIPER", [("J_VOL", "2"), ("U1", "1")]),
    ("BTN_N",     [("J_BTN", "1"), ("U1", "2")]),
    ("LED_DRV",   [("U1", "7"), ("R1", "1")]),
    ("LED_A",     [("R1", "2"), ("J_LED", "1")]),
]


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------

def sanity_check():
    refs = {c["ref"] for c in COMPONENTS}
    ref_pins = {c["ref"]: set(c["pins"].keys()) for c in COMPONENTS}
    errors = []
    used = {(c["ref"], p): False for c in COMPONENTS for p in c["pins"]}

    for net_name, nodes in NETS:
        if len(nodes) < 1:
            errors.append(f"net {net_name!r} has no nodes")
        for ref, pin in nodes:
            if ref not in refs:
                errors.append(f"net {net_name!r} references unknown ref {ref!r}")
                continue
            if pin not in ref_pins[ref]:
                errors.append(f"net {net_name!r} references unknown pin {ref}.{pin}")
                continue
            if used[(ref, pin)]:
                errors.append(f"pin {ref}.{pin} used in multiple nets (last: {net_name!r})")
            used[(ref, pin)] = True

    unconnected = [k for k, v in used.items() if not v]
    if unconnected:
        names = ", ".join(f"{r}.{p}" for r, p in unconnected)
        # GAIN, D7 (UART RX), D7_GPIO44 are intentionally unconnected
        intentional = {("U2", "4"), ("U1", "8")}
        truly = [u for u in unconnected if u not in intentional]
        if truly:
            errors.append(f"unconnected pins: {', '.join(f'{r}.{p}' for r,p in truly)}")
        intentionally_skipped = [u for u in unconnected if u in intentional]
        if intentionally_skipped:
            print(f"note: leaving {len(intentionally_skipped)} pin(s) intentionally unconnected: "
                  + ", ".join(f"{r}.{p}" for r, p in intentionally_skipped))

    if errors:
        for e in errors:
            print("ERR:", e, file=sys.stderr)
        sys.exit(1)
    print(f"sanity: {len(COMPONENTS)} components, {len(NETS)} nets, ok.")


# ---------------------------------------------------------------------------
# KiCad netlist emitter
# ---------------------------------------------------------------------------

def stable_uuid(seed):
    return str(_uuid.uuid5(_uuid.NAMESPACE_OID, seed))


def emit_netlist():
    today = datetime.date.today().isoformat()

    # Header / design block
    out = []
    out.append('(export (version "E")')
    out.append('  (design')
    out.append('    (source "esp-music-player.kicad_sch")')
    out.append(f'    (date "{today}")')
    out.append('    (tool "gen_netlist.py")')
    out.append('    (sheet (number "1") (name "/") (tstamps "/")')
    out.append('      (title_block')
    out.append('        (title "ESP32-MusicPlayer-Battery")')
    out.append('        (company "")')
    out.append(f'        (rev "1") (date "{today}")')
    out.append('        (source "esp-music-player.kicad_sch")')
    out.append('        (comment (number "1") (value ""))')
    out.append('        (comment (number "2") (value ""))')
    out.append('        (comment (number "3") (value ""))')
    out.append('        (comment (number "4") (value "")))))')

    # Components block
    out.append('  (components')
    for c in COMPONENTS:
        u = stable_uuid("comp:" + c["ref"])
        out.append(f'    (comp (ref "{c["ref"]}")')
        out.append(f'      (value "{c["value"]}")')
        out.append(f'      (footprint "{c["footprint"]}")')
        out.append(f'      (description "{c["desc"]}")')
        out.append(f'      (libsource (lib "esp-music-player") (part "{c["value"]}") (description "{c["desc"]}"))')
        out.append(f'      (sheetpath (names "/") (tstamps "/"))')
        out.append(f'      (tstamps "{u}"))')
    out.append('  )')

    # Libparts block — one libpart per unique value; describe pins.
    out.append('  (libparts')
    seen = set()
    for c in COMPONENTS:
        if c["value"] in seen: continue
        seen.add(c["value"])
        out.append(f'    (libpart (lib "esp-music-player") (part "{c["value"]}")')
        out.append(f'      (description "{c["desc"]}")')
        out.append(f'      (footprints (fp "{c["footprint"]}"))')
        out.append('      (pins')
        for pin_num, pin_name in sorted(c["pins"].items(), key=lambda x: int(x[0])):
            ptype = c["pin_types"].get(pin_num, PASSIVE)
            out.append(f'        (pin (num "{pin_num}") (name "{pin_name}") (type "{ptype}"))')
        out.append('      ))')
    out.append('  )')

    # Libraries block — single virtual library
    out.append('  (libraries')
    out.append('    (library (logical "esp-music-player")')
    out.append('      (uri "esp-music-player")))')

    # Nets block
    out.append('  (nets')
    for code, (net_name, nodes) in enumerate(NETS, start=1):
        out.append(f'    (net (code "{code}") (name "{net_name}")')
        for ref, pin in nodes:
            comp = next(c for c in COMPONENTS if c["ref"] == ref)
            ptype = comp["pin_types"].get(pin, PASSIVE)
            pname = comp["pins"][pin]
            out.append(f'      (node (ref "{ref}") (pin "{pin}") (pinfunction "{pname}") (pintype "{ptype}"))')
        out.append('    )')
    out.append('  )')

    out.append(')')
    return "\n".join(out) + "\n"


def emit_bom():
    rows = []
    for c in COMPONENTS:
        rows.append([c["ref"], c["value"], c["footprint"], c["desc"]])
    rows.sort(key=lambda r: r[0])
    return rows


def main():
    sanity_check()

    net_path = os.path.join(HERE, "esp-music-player.net")
    with open(net_path, "w") as f:
        f.write(emit_netlist())
    print(f"wrote {net_path}  ({os.path.getsize(net_path)} bytes)")

    bom_path = os.path.join(HERE, "esp-music-player.bom.csv")
    with open(bom_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ref", "value", "footprint", "description"])
        w.writerows(emit_bom())
    print(f"wrote {bom_path}")


if __name__ == "__main__":
    main()
