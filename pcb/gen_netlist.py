#!/usr/bin/env python3
"""
Generate a KiCad-compatible netlist for ESP32-MusicPlayer-Battery.

Configuration: 4S 18650 + IP2368 USB-C PD charger + TAS5805M (or
TAS5825M) stereo I2S amp + buck-to-5V + microSD.

Produces:
  pcb/esp-music-player.net      KiCad netlist (importable into PCB Editor)
  pcb/esp-music-player.bom.csv  Plain-text bill of materials

Usage:
  python3 pcb/gen_netlist.py

This script is the source of truth for both the BOM and the connection
list. It mirrors docs/NETLIST.md. If you change firmware pins in
include/config.h, update PIN_OF_REF here and re-run this script.

Importing into KiCad (8.x):
  1. File -> New Project -> save as pcb/esp-music-player.kicad_pro
  2. Open the PCB Editor (pcbnew).
  3. File -> Import Netlist -> choose pcb/esp-music-player.net
  4. KiCad creates footprint instances for every component.
  5. Update PCB; assign / verify each footprint, then place + route.
"""

import csv
import datetime
import os
import sys
import uuid as _uuid

HERE = os.path.dirname(os.path.abspath(__file__))


PASSIVE = "passive"
PWR_IN  = "power_in"
PWR_OUT = "power_out"
IN      = "input"
OUT     = "output"
BIDIR   = "bidirectional"
OD      = "open_collector"   # for I2C / FAULTZ-style open-drain


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------
COMPONENTS = [
    # ----- U1: Seeed XIAO ESP32-S3 -----
    # Pins 1-11: D0..D10 (edge), 12=3V3, 13=GND, 14=5V, 15=GPIO38 (bottom pad).
    # Verify after import: the Seeed footprint's pad numbering should match;
    # if not, remap in KiCad with "Edit Symbol Pin Names" or relabel here.
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
            "13": "GND",        "14": "+5V",        "15": "GPIO38_BOT",
        },
        "pin_types": {
            "12": PWR_OUT, "13": PWR_IN, "14": PWR_IN, "15": PASSIVE,
            **{p: PASSIVE for p in ["1","2","3","4","5","6","7","8","9","10","11"]},
        },
    },

    # ----- U2: TAS5805M / TAS5825M stereo I2S amp breakout (DFR0721 style) -----
    # 14-pin model: 10 control + 4 speaker outputs.
    {
        "ref": "U2",
        "value": "TAS5805M_Breakout",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x14_P2.54mm_Vertical",
        "desc": "TAS5805M stereo I2S class-D amp breakout (DFRobot DFR0721 or equivalent)",
        "pins": {
            "1":  "VCC",    "2":  "GND",    "3":  "BCLK",    "4":  "LRCLK",
            "5":  "SDIN",   "6":  "SDA",    "7":  "SCL",     "8":  "PDN",
            "9":  "FAULTZ", "10": "MUTE",
            "11": "SPK_L+", "12": "SPK_L-", "13": "SPK_R+",  "14": "SPK_R-",
        },
        "pin_types": {
            "1": PWR_IN, "2": PWR_IN,
            "3": IN, "4": IN, "5": IN,
            "6": BIDIR, "7": IN, "8": IN, "9": OD, "10": IN,
            "11": OUT, "12": OUT, "13": OUT, "14": OUT,
        },
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

    # ----- U4: IP2368 USB-C PD charger module (4S, all-in-one) -----
    # 6-pin header: BAT+, BAT-, BAL1, BAL2, BAL3, GND
    {
        "ref": "U4",
        "value": "IP2368_Module",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical",
        "desc": "IP2368 USB-C PD all-in-one 4S Li-ion charger module (DFR1015 or AliExpress equivalent)",
        "pins": {"1":"BAT+","2":"BAT-","3":"BAL1","4":"BAL2","5":"BAL3","6":"GND"},
        "pin_types": {"1":PWR_OUT,"2":PWR_IN,"3":PASSIVE,"4":PASSIVE,"5":PASSIVE,"6":PWR_IN},
    },

    # ----- U5: 4S -> 5V buck converter module -----
    {
        "ref": "U5",
        "value": "Buck_5V_Module",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        "desc": "Adjustable buck converter set to 5.0V (MP1584 or LM2596 module)",
        "pins": {"1":"VIN+","2":"VIN-","3":"VOUT+","4":"VOUT-"},
        "pin_types": {"1":PWR_IN,"2":PWR_IN,"3":PWR_OUT,"4":PWR_OUT},
    },

    # ----- J_BAT: XT60 battery connector (main current path) -----
    {
        "ref": "J_BAT",
        "value": "XT60_Connector",
        "footprint": "Connector:XT60_Connector",
        "desc": "XT60 main battery connector (carries +14V_RAW and GND)",
        "pins": {"1":"+","2":"-"},
        "pin_types": {"1":PWR_IN,"2":PWR_IN},
    },

    # ----- J_BAL: 5-pin JST-XH balance harness -----
    # Standard RC LiPo balance order: pin 1 = pack negative, pin 5 = pack positive
    {
        "ref": "J_BAL",
        "value": "JSTXH_5pin_Balance",
        "footprint": "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical",
        "desc": "5-pin JST-XH balance harness (RC LiPo standard pin order)",
        "pins": {"1":"GND","2":"BAL1","3":"BAL2","4":"BAL3","5":"BAT+"},
        "pin_types": {"1":PWR_IN,"2":PASSIVE,"3":PASSIVE,"4":PASSIVE,"5":PASSIVE},
    },

    # ----- J_PWR: panel-mount slide / rocker switch SW1 (>=5A) -----
    {
        "ref": "J_PWR",
        "value": "PWR_SW_JSTPH2",
        "footprint": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "desc": "Off-board >=5A SPST switch SW1 (battery line, between BMS P+ and +14V_SW)",
        "pins": {"1":"SW_IN","2":"SW_OUT"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },

    # ----- J1: left speaker output (JST-XH 2-pin) -----
    {
        "ref": "J1",
        "value": "SPK_L_JSTXH2",
        "footprint": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
        "desc": "Left speaker output (JST-XH 2-pin)",
        "pins": {"1":"SPK_L+","2":"SPK_L-"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },

    # ----- J2: right speaker output (JST-XH 2-pin) -----
    {
        "ref": "J2",
        "value": "SPK_R_JSTXH2",
        "footprint": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
        "desc": "Right speaker output (JST-XH 2-pin)",
        "pins": {"1":"SPK_R+","2":"SPK_R-"},
        "pin_types": {"1":PASSIVE,"2":PASSIVE},
    },

    # ----- J_VOL: panel pot RV1 (JST-PH 3-pin) -----
    {
        "ref": "J_VOL",
        "value": "VOL_POT_JSTPH3",
        "footprint": "Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
        "desc": "Off-board 10k volume pot RV1",
        "pins": {"1":"GND","2":"WIPER","3":"VCC"},
        "pin_types": {"1":PWR_IN,"2":OUT,"3":PWR_IN},
    },

    # ----- J_BTN: panel push button SW2 (JST-PH 2-pin) -----
    {
        "ref": "J_BTN",
        "value": "BTN_JSTPH2",
        "footprint": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "desc": "Off-board momentary push button SW2",
        "pins": {"1":"BTN_N","2":"GND"},
        "pin_types": {"1":IN,"2":PWR_IN},
    },

    # ----- J_LED: panel LED D1 (JST-PH 2-pin; R1 is on the PCB) -----
    {
        "ref": "J_LED",
        "value": "LED_JSTPH2",
        "footprint": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "desc": "Off-board status LED D1",
        "pins": {"1":"ANODE","2":"CATHODE"},
        "pin_types": {"1":IN,"2":PWR_IN},
    },

    # ----- Resistors -----
    {"ref": "R1", "value": "470",
     "footprint": "Resistor_SMD:R_0805_2012Metric",
     "desc": "LED current-limit resistor",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "R2", "value": "4.7k",
     "footprint": "Resistor_SMD:R_0805_2012Metric",
     "desc": "I2C SDA pull-up to +3V3 (omit if amp breakout has its own)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "R3", "value": "4.7k",
     "footprint": "Resistor_SMD:R_0805_2012Metric",
     "desc": "I2C SCL pull-up to +3V3 (omit if amp breakout has its own)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "R4", "value": "10k",
     "footprint": "Resistor_SMD:R_0805_2012Metric",
     "desc": "TAS5805M PDN pull-up to +3V3 (always-on)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},

    # ----- Capacitors -----
    {"ref": "C1", "value": "1000uF/25V",
     "footprint": "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
     "desc": "Bulk on +14V_SW (TAS5805M Vcc)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C2", "value": "100nF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "HF bypass on +14V_SW",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C3", "value": "22uF/25V",
     "footprint": "Capacitor_SMD:C_1206_3216Metric",
     "desc": "Local Vcc decoupling at TAS5805M (omit if breakout has its own)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C4", "value": "10uF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "Buck output bulk on +5V",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C5", "value": "100nF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "HF decoupling at XIAO 3V3 pin",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C6", "value": "100nF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "I2C SDA ESD bypass (optional)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C7", "value": "100nF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "I2C SCL ESD bypass (optional)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
]


# ---------------------------------------------------------------------------
# Nets — mirrors docs/NETLIST.md
# ---------------------------------------------------------------------------
NETS = [
    # ---- power chain ----
    # XT60 + and balance plug pin 5 are the same node (pack positive output).
    # XT60 + → SW1 → +14V_SW. Also IP2368 BAT+ connects to the same pack
    # positive node (charge path).
    ("VBAT_RAW", [
        ("J_BAT", "1"),       # XT60 +
        ("J_BAL", "5"),       # balance plug pin 5 (BAT+)
        ("J_PWR", "1"),       # SW1 input
        ("U4", "1"),          # IP2368 BAT+
    ]),
    ("+14V_SW", [
        ("J_PWR", "2"),       # SW1 output
        ("U2", "1"),          # TAS5805M Vcc
        ("U5", "1"),          # buck VIN+
        ("C1", "1"), ("C2", "1"), ("C3", "1"),
    ]),
    ("+5V", [
        ("U5", "3"),          # buck VOUT+
        ("U1", "14"),         # XIAO 5V
        ("U3", "1"),          # microSD VCC (some breakouts; could also be on 3V3)
        ("C4", "1"),
    ]),
    ("+3V3", [
        ("U1", "12"),         # XIAO 3V3 LDO out
        ("J_VOL", "3"),       # pot top
        ("R2", "2"),          # I2C SDA pull-up
        ("R3", "2"),          # I2C SCL pull-up
        ("R4", "2"),          # TAS PDN pull-up
        ("C5", "1"),
    ]),
    ("GND", [
        ("J_BAT", "2"),       # XT60 -
        ("J_BAL", "1"),       # balance plug pin 1 (pack -)
        ("U4", "2"), ("U4", "6"),   # IP2368 BAT- and GND
        ("U5", "2"), ("U5", "4"),   # buck VIN- and VOUT-
        ("U1", "13"),         # XIAO GND
        ("U2", "2"),          # TAS5805M GND
        ("U3", "2"),          # microSD GND
        ("J_VOL", "1"),
        ("J_BTN", "2"),
        ("J_LED", "2"),
        ("C1", "2"), ("C2", "2"), ("C3", "2"),
        ("C4", "2"), ("C5", "2"), ("C6", "2"), ("C7", "2"),
    ]),

    # ---- balance taps to IP2368 (cell junctions) ----
    ("BAL_1", [("U4", "3"), ("J_BAL", "2")]),
    ("BAL_2", [("U4", "4"), ("J_BAL", "3")]),
    ("BAL_3", [("U4", "5"), ("J_BAL", "4")]),

    # ---- I2S audio ----
    ("I2S_BCLK",  [("U1", "4"),  ("U2", "3")]),
    ("I2S_LRCLK", [("U1", "5"),  ("U2", "4")]),
    ("I2S_DOUT",  [("U1", "6"),  ("U2", "5")]),

    # ---- I2C control ----
    ("I2C_SDA", [("U1", "7"),  ("U2", "6"), ("R2", "1"), ("C6", "1")]),
    ("I2C_SCL", [("U1", "8"),  ("U2", "7"), ("R3", "1"), ("C7", "1")]),

    # ---- TAS5805M tie-offs ----
    ("AMP_PDN", [("U2", "8"), ("R4", "1")]),

    # ---- Speaker outputs ----
    ("SPK_L+", [("U2", "11"), ("J1", "1")]),
    ("SPK_L-", [("U2", "12"), ("J1", "2")]),
    ("SPK_R+", [("U2", "13"), ("J2", "1")]),
    ("SPK_R-", [("U2", "14"), ("J2", "2")]),

    # ---- microSD SPI ----
    ("SD_CS",   [("U1", "3"),  ("U3", "3")]),
    ("SD_MOSI", [("U1", "11"), ("U3", "4")]),
    ("SD_SCK",  [("U1", "9"),  ("U3", "5")]),
    ("SD_MISO", [("U1", "10"), ("U3", "6")]),

    # ---- Controls / indicator ----
    ("VOL_WIPER", [("J_VOL", "2"), ("U1", "1")]),
    ("BTN_N",     [("J_BTN", "1"), ("U1", "2")]),
    ("LED_DRV",   [("U1", "15"), ("R1", "1")]),    # GPIO38 bottom-pad → R1 → LED
    ("LED_A",     [("R1", "2"),  ("J_LED", "1")]),
]


# Pins we deliberately leave unconnected.
INTENTIONALLY_UNCONNECTED = {
    ("U1", "8"),    # GPIO44 / D7 reserved (same as before)... wait, with I2C we now use D6/D7
                    # Actually GPIO43=D6 is SDA (pin 7) and GPIO44=D7 is SCL (pin 8). Both used.
                    # No edge GPIOs left unused now.
    ("U2", "9"),    # FAULTZ — open-drain status, optional
    ("U2", "10"),   # MUTE — leave NC; software mute via DEVICE_CTRL_2
}


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
def sanity_check():
    refs = {c["ref"] for c in COMPONENTS}
    ref_pins = {c["ref"]: set(c["pins"].keys()) for c in COMPONENTS}
    used = {(c["ref"], p): False for c in COMPONENTS for p in c["pins"]}
    errors = []

    for net_name, nodes in NETS:
        if not nodes:
            errors.append(f"net {net_name!r} has no nodes")
        for ref, pin in nodes:
            if ref not in refs:
                errors.append(f"net {net_name!r} references unknown ref {ref!r}")
                continue
            if pin not in ref_pins[ref]:
                errors.append(f"net {net_name!r} references unknown pin {ref}.{pin}")
                continue
            if used[(ref, pin)]:
                errors.append(f"pin {ref}.{pin} on multiple nets (last: {net_name!r})")
            used[(ref, pin)] = True

    unconnected = [k for k, v in used.items() if not v]
    truly = [u for u in unconnected if u not in INTENTIONALLY_UNCONNECTED]
    intentional = [u for u in unconnected if u in INTENTIONALLY_UNCONNECTED]

    if truly:
        errors.append(
            "unconnected pins: " + ", ".join(f"{r}.{p}" for r, p in truly)
        )
    if intentional:
        print(
            "note: leaving "
            f"{len(intentional)} pin(s) intentionally unconnected: "
            + ", ".join(f"{r}.{p}" for r, p in intentional)
        )

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
    out = []
    out.append('(export (version "E")')
    out.append('  (design')
    out.append('    (source "esp-music-player.kicad_sch")')
    out.append(f'    (date "{today}")')
    out.append('    (tool "gen_netlist.py")')
    out.append('    (sheet (number "1") (name "/") (tstamps "/")')
    out.append('      (title_block')
    out.append('        (title "ESP32-MusicPlayer-Battery (4S stereo)")')
    out.append('        (company "")')
    out.append(f'        (rev "2") (date "{today}")')
    out.append('        (source "esp-music-player.kicad_sch")')
    out.append('        (comment (number "1") (value ""))')
    out.append('        (comment (number "2") (value ""))')
    out.append('        (comment (number "3") (value ""))')
    out.append('        (comment (number "4") (value "")))))')

    out.append('  (components')
    for c in COMPONENTS:
        u = stable_uuid("comp:" + c["ref"])
        out.append(f'    (comp (ref "{c["ref"]}")')
        out.append(f'      (value "{c["value"]}")')
        out.append(f'      (footprint "{c["footprint"]}")')
        out.append(f'      (description "{c["desc"]}")')
        out.append(f'      (libsource (lib "esp-music-player") (part "{c["value"]}") (description "{c["desc"]}"))')
        out.append('      (sheetpath (names "/") (tstamps "/"))')
        out.append(f'      (tstamps "{u}"))')
    out.append('  )')

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

    out.append('  (libraries')
    out.append('    (library (logical "esp-music-player")')
    out.append('      (uri "esp-music-player")))')

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
    rows = [(c["ref"], c["value"], c["footprint"], c["desc"]) for c in COMPONENTS]
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
