#!/usr/bin/env python3
"""
Generate a KiCad-compatible netlist for ESP32-MusicPlayer-Battery.

Configuration: 4S 18650 + IP2368 USB-C PD charger + PCM5102A I2S DAC +
TPA3116D2 stereo class-D amp + buck-to-5V + microSD.

Produces:
  pcb/esp-music-player.net      KiCad netlist (importable into PCB Editor)
  pcb/esp-music-player.bom.csv  Plain-text bill of materials

Usage:
  python3 pcb/gen_netlist.py

This script is the source of truth for both the BOM and the connection
list. It mirrors docs/NETLIST.md. If you change firmware pins in
include/config.h, update the relevant nets here and re-run.

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


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------
COMPONENTS = [
    # ----- U1: Seeed XIAO ESP32-S3 -----
    # Pins 1-11: D0..D10 (edge), 12=3V3, 13=GND, 14=5V.
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

    # ----- U2: PCM5102A I2S DAC breakout (typical "GY-PCM5102") -----
    # Pin order varies between vendors; verify against silkscreen on import.
    {
        "ref": "U2",
        "value": "PCM5102A_DAC",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical",
        "desc": "PCM5102A I2S DAC breakout (GY-PCM5102 or equivalent)",
        "pins": {
            "1": "VIN", "2": "GND", "3": "BCK", "4": "LCK", "5": "DIN",
            "6": "SCK", "7": "LOUT", "8": "ROUT", "9": "AGND", "10": "XSMT",
        },
        "pin_types": {
            "1": PWR_IN, "2": PWR_IN,
            "3": IN, "4": IN, "5": IN, "6": IN,
            "7": OUT, "8": OUT, "9": PWR_IN, "10": IN,
        },
    },

    # ----- U2A: TPA3116D2 stereo class-D amp module -----
    {
        "ref": "U2A",
        "value": "TPA3116D2_Amp",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical",
        "desc": "TPA3116D2 stereo class-D amp module (analog input, 12-24V supply)",
        "pins": {
            "1": "VCC", "2": "GND",
            "3": "L_IN", "4": "AGND_IN", "5": "R_IN",
            "6": "SPK_L+", "7": "SPK_L-",
            "8": "SPK_R+", "9": "SPK_R-",
        },
        "pin_types": {
            "1": PWR_IN, "2": PWR_IN,
            "3": IN, "4": PWR_IN, "5": IN,
            "6": OUT, "7": OUT, "8": OUT, "9": OUT,
        },
    },

    # ----- U3: microSD breakout -----
    {
        "ref": "U3",
        "value": "microSD_Breakout",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical",
        "desc": "microSD card breakout, SPI mode (3V3 logic)",
        "pins": {"1":"VCC","2":"GND","3":"CS","4":"MOSI","5":"SCK","6":"MISO"},
        "pin_types": {"1":PWR_IN,"2":PWR_IN,"3":IN,"4":IN,"5":IN,"6":OUT},
    },

    # ----- U4: IP2368 USB-C PD charger module (4S, AliExpress sourced) -----
    {
        "ref": "U4",
        "value": "IP2368_Module",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical",
        "desc": "IP2368 USB-C PD all-in-one 4S Li-ion charger module (AliExpress)",
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

    # ----- J_BAT: XT60 main battery connector -----
    {
        "ref": "J_BAT",
        "value": "XT60_Connector",
        "footprint": "Connector:XT60_Connector",
        "desc": "XT60 main battery connector (carries pack + and GND)",
        "pins": {"1":"+","2":"-"},
        "pin_types": {"1":PWR_IN,"2":PWR_IN},
    },

    # ----- J_BAL: 5-pin JST-XH balance harness -----
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
        "desc": "Off-board >=5A SPST switch SW1 (battery line, BMS P+ → +14V_SW)",
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

    # ----- Capacitors -----
    {"ref": "C1", "value": "1000uF/25V",
     "footprint": "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
     "desc": "Bulk on +14V_SW (TPA3116D2 Vcc)",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C2", "value": "100nF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "HF bypass on +14V_SW",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C3", "value": "10uF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "Buck output bulk on +5V",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
    {"ref": "C4", "value": "100nF",
     "footprint": "Capacitor_SMD:C_0805_2012Metric",
     "desc": "HF decoupling at XIAO 3V3 pin",
     "pins": {"1":"~","2":"~"},
     "pin_types": {"1":PASSIVE,"2":PASSIVE}},
]


# ---------------------------------------------------------------------------
# Nets — mirrors docs/NETLIST.md
# ---------------------------------------------------------------------------
NETS = [
    # ---- power chain ----
    ("VBAT_RAW", [
        ("J_BAT", "1"),       # XT60 +
        ("J_BAL", "5"),       # balance plug pin 5 (BAT+)
        ("J_PWR", "1"),       # SW1 input
        ("U4", "1"),          # IP2368 BAT+
    ]),
    ("+14V_SW", [
        ("J_PWR", "2"),       # SW1 output
        ("U2A", "1"),         # TPA3116D2 Vcc
        ("U5", "1"),          # buck VIN+
        ("C1", "1"), ("C2", "1"),
    ]),
    ("+5V", [
        ("U5", "3"),          # buck VOUT+
        ("U1", "14"),         # XIAO 5V
        ("U2", "1"),          # PCM5102A VIN
        ("U3", "1"),          # microSD VCC
        ("C3", "1"),
    ]),
    ("+3V3", [
        ("U1", "12"),         # XIAO 3V3 LDO out
        ("J_VOL", "3"),       # pot top
        ("U2", "10"),         # PCM5102A XSMT (un-mute)
        ("C4", "1"),
    ]),
    ("GND", [
        ("J_BAT", "2"),
        ("J_BAL", "1"),
        ("U4", "2"), ("U4", "6"),
        ("U5", "2"), ("U5", "4"),
        ("U1", "13"),
        ("U2", "2"), ("U2", "6"), ("U2", "9"),  # PCM5102A GND, SCK (no MCK), AGND
        ("U2A", "2"), ("U2A", "4"),             # TPA3116D2 power GND + AGND_IN
        ("U3", "2"),
        ("J_VOL", "1"),
        ("J_BTN", "2"),
        ("J_LED", "2"),
        ("C1", "2"), ("C2", "2"), ("C3", "2"), ("C4", "2"),
    ]),

    # ---- balance taps to IP2368 (cell junctions) ----
    ("BAL_1", [("U4", "3"), ("J_BAL", "2")]),
    ("BAL_2", [("U4", "4"), ("J_BAL", "3")]),
    ("BAL_3", [("U4", "5"), ("J_BAL", "4")]),

    # ---- I2S audio (XIAO -> PCM5102A) ----
    ("I2S_BCLK",  [("U1", "4"), ("U2", "3")]),
    ("I2S_LRCLK", [("U1", "5"), ("U2", "4")]),
    ("I2S_DOUT",  [("U1", "6"), ("U2", "5")]),

    # ---- Analog audio (PCM5102A -> TPA3116D2) ----
    ("AUDIO_L", [("U2", "7"), ("U2A", "3")]),
    ("AUDIO_R", [("U2", "8"), ("U2A", "5")]),

    # ---- Speaker outputs ----
    ("SPK_L+", [("U2A", "6"), ("J1", "1")]),
    ("SPK_L-", [("U2A", "7"), ("J1", "2")]),
    ("SPK_R+", [("U2A", "8"), ("J2", "1")]),
    ("SPK_R-", [("U2A", "9"), ("J2", "2")]),

    # ---- microSD SPI ----
    ("SD_CS",   [("U1", "3"),  ("U3", "3")]),
    ("SD_MOSI", [("U1", "11"), ("U3", "4")]),
    ("SD_SCK",  [("U1", "9"),  ("U3", "5")]),
    ("SD_MISO", [("U1", "10"), ("U3", "6")]),

    # ---- Controls / indicator ----
    ("VOL_WIPER", [("J_VOL", "2"), ("U1", "1")]),
    ("BTN_N",     [("J_BTN", "1"), ("U1", "2")]),
    ("LED_DRV",   [("U1", "7"), ("R1", "1")]),
    ("LED_A",     [("R1", "2"), ("J_LED", "1")]),
]


# Pins we deliberately leave unconnected.
INTENTIONALLY_UNCONNECTED = {
    ("U1", "8"),   # GPIO44 / D7 — spare for future use
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
        errors.append("unconnected pins: " + ", ".join(f"{r}.{p}" for r, p in truly))
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
    out.append('        (title "ESP32-MusicPlayer-Battery (4S stereo, PCM5102A + TPA3116D2)")')
    out.append('        (company "")')
    out.append(f'        (rev "3") (date "{today}")')
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
