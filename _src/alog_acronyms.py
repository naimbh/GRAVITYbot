"""
alog_acronyms.py

Find the acronyms used in a week's aLOG entries and look each one up, so the
prompt carries only the expansions that week needs instead of the full
800-entry list (which, in Round 2, distracted the model).

Steps:
    1. Collect all-caps tokens from the entry titles and text
       (e.g. ETMX, SQZ, HAM1, A2L), skipping ordinary English words,
       time zones, site names and channel-name fragments.
    2. Normalize variants to a base form: ETMX -> ETM (X arm), HAM1 -> HAM,
       ITMY -> ITM (Y arm), SR3 -> SR3 or SR.
    3. Look the base form up, in this order:
         a. corrections for Hanford usage (entries the LIGO list gets wrong
            or lacks, found in the Round 2 evaluation);
         b. the LIGO Abbreviations and Acronyms list (M080375-v26), LIGO
            entries before Virgo-only ones.
    4. Return the acronyms found, most frequent first, with the expansion
       and its source. Acronyms with no expansion are left out; the prompt
       tells the model to keep those as written.
"""
import csv
import logging
import pathlib
import re
from collections import Counter

import config

logger = logging.getLogger(__name__)

# The LIGO list is not stored in the repository. As in summary_test, it is read from
# the data folder (GRAVITYBOT_DATA_FOLDER_PATH, default _data/) under its DCC file name.
# The small English word list ships with the code in resources/.
RESOURCES = pathlib.Path(__file__).resolve().parent / "resources"
LIST_FILENAME = "M080375-v26 Abbreviations and Acronyms.csv"
WORDS_FILENAME = "english_caps_words.txt"

# Hanford usage. These override the LIGO list, which has wrong or missing
# entries for several terms common in the LHO aLOG (Round 2 evaluation).
CORRECTIONS = {
    "ESD": "Electrostatic Drive (applies electric force to push a test mass)",
    "ALS": "Arm Length Stabilization (green lasers used while locking the arms)",
    "BRS": "Beam Rotation Sensor (measures ground tilt at the end stations)",
    "RM": "relay mirror (RM1/RM2 small steering mirrors)",
    "HV": "High Voltage",
    "IOC": "Input/Output Controller (control-system software process)",
    "NLG": "nonlinear gain (how strongly the squeezer works)",
    "A2L": "angle-to-length coupling (mirror tilt turning into a false length signal)",
    "FC": "filter cavity (part of the squeezer)",
    "CPS": "capacitive position sensor (seismic isolation sensor)",
    "DCPD": "DC photodiode (the main readout photodiodes)",
    "OSEM": "optical sensor and electromagnetic actuator (suspension sensor/actuator)",
    "PI": "parametric instability (a mirror vibration mode rung up by laser power)",
    "NLN": "Nominal Low Noise (fully locked, lowest-noise state)",
    "SRCL": "signal recycling cavity length",
    "PRCL": "power recycling cavity length",
    "MICH": "Michelson (the beamsplitter length control loop)",
    "DHARD": "differential hard alignment mode",
    "CHARD": "common hard alignment mode",
    "DSOFT": "differential soft alignment mode",
    "CSOFT": "common soft alignment mode",
    "SHG": "second-harmonic generator (part of the squeezer)",
    "PMC": "pre-mode cleaner",
    "FSS": "frequency stabilization servo (laser)",
    "ISS": "intensity stabilization servo (laser)",
    "PSL": "pre-stabilized laser",
    "LVEA": "Laser and Vacuum Equipment Area (corner-station hall)",
    "EX": "X-arm end station",
    "EY": "Y-arm end station",
    "CS": "corner station",
    "TMS": "transmission monitor suspension",
    "HWS": "Hartmann wavefront sensor",
    "SATAMP": "satellite amplifier (suspension sensor electronics)",
    "DQ": "data quality",
    "DETCHAR": "Detector Characterization (data-quality team)",
    "OM": "output-optics mirror (OM1/OM2/OM3)",
    "SR": "signal recycling cavity mirror (SR2/SR3/SRM)",
    "PR": "power recycling cavity mirror (PR2/PR3/PRM)",
    "FM": "filter module (a numbered slot in a control filter bank, FM1-FM10)",
    "CP": "cryopump (CP1 and so on; liquid-nitrogen vacuum pump); in optics, compensation plate",
    "LSC": "Length Sensing and Control",
    "FAC": "facilities (site buildings and services)",
    "MC": "input mode cleaner mirror (MC1/MC2/MC3)",
    "IMC": "input mode cleaner",
    "RF": "radio frequency (e.g. RF45 = 45 MHz sideband)",
    "VE": "vacuum equipment",
    "CAL": "calibration",
    "SUS": "suspensions (the pendulums that hang the mirrors)",
    "HAM": "HAM chamber (Horizontal Access Module: vacuum chamber holding auxiliary optics)",
}

# Tokens that look like acronyms but are not useful to expand.
SKIP = {"UTC", "PST", "PDT", "GPS", "LHO", "LLO", "LIGO", "H1", "L1", "OK", "AM", "PM",
        "ID", "US", "USA", "FAMIS", "FRS", "WP", "TJ", "EOD", "FYI", "TBD", "NA", "PDF", "PNG"}

_TOKEN = re.compile(r"(?<![A-Za-z0-9_:/.\-])([A-Z][A-Z0-9]{1,9})(?![a-z0-9_:])")


def _load_list(data_folder):
    table = {}
    path = pathlib.Path(data_folder) / LIST_FILENAME
    if not path.exists():
        logger.warning(f"{path} not found; using the Hanford corrections only")
        return table
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            acr = (row.get("Abbreviation / Acronym") or "").strip()
            exp = (row.get("Expansion") or "").strip()
            if not acr or not exp:
                continue
            virgo = "virgo" in (row.get("Collaboration") or "").lower()
            table.setdefault(acr.upper(), []).append((virgo, exp))
    return {k: [e for _, e in sorted(v)] for k, v in table.items()}       # LIGO entries first


def _english(data_folder):
    """Ordinary English words seen in capitals in the aLOG (bundled list; no system dictionary needed)."""
    for folder in (pathlib.Path(data_folder), RESOURCES):
        p = folder / WORDS_FILENAME
        if p.exists():
            return {w.strip().lower() for w in p.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")}
    return set()


def _candidates(tok):
    """Base forms to try, most specific first: ETMX -> ETMX, ETM (X arm)."""
    out = [(tok, "")]
    m = re.match(r"^([A-Z]+?)(\d+)$", tok)                  # HAM1, SR3, OM2
    if m:
        out.append((m.group(1), ""))
    m = re.match(r"^([A-Z]{3,})([XY])$", tok)                # ETMX, ITMY (not DAY -> DA + Y)
    if m:
        out.append((m.group(1), f" ({m.group(2)} arm)"))
    return out


def find_acronyms(current, data_folder=None, limit=60):
    """Return [(token, expansion, source, count)] for acronyms in this week's entries."""
    data_folder = data_folder or config.DATA_FOLDER_PATH
    table = _load_list(data_folder)
    english = _english(data_folder)
    text = " ".join(f"{r.get('comment_title', '')} {r.get('comment', '')}" for r in current.to_dict("records"))
    counts = Counter(_TOKEN.findall(text))
    found = []
    for tok, n in counts.most_common():
        if tok in SKIP or sum(c.isalpha() for c in tok) < 2:
            continue
        if tok.lower() in english and tok not in CORRECTIONS:
            continue                    # an English word written in capitals (DAY, LOCK, DOWN)
        cands = _candidates(tok)
        hit = next(((tok, CORRECTIONS[b] + suf, "Hanford usage", n) for b, suf in cands if b in CORRECTIONS), None)
        if not hit:
            for b, suf in cands:
                if b in table:
                    exps = []
                    for e in table[b]:
                        if not any(e.lower() in x.lower() or x.lower() in e.lower() for x in exps):
                            exps.append(e)
                    hit = (tok, "; or ".join(exps[:2]) + suf, "LIGO acronym list", n)
                    break
        if hit:
            found.append(hit)
        if len(found) >= limit:
            break
    return found


def acronym_block(current, data_folder=None, limit=60):
    rows = find_acronyms(current, data_folder, limit)
    if not rows:
        return "(none found)"
    return "\n".join(f"- {tok}: {exp} [{src}; {n}x]" for tok, exp, src, n in rows)
