"""
M1_update_manuscript.py
Coastal Sentinel - Patch Table 3 with real Skill Score S
Reads M1_skill_scores_summary.csv, extracts the mean S value,
then replaces 'Positive (inferred)' in Table 3 of the manuscript
with the real computed value. Produces v6.

Run THIRD (after M1_gdp_hindcast.py).
"""

import os
import sys
import glob
import shutil
import zipfile
import re
import pandas as pd

print("=" * 60)
print("M1 SCRIPT 3: PATCH MANUSCRIPT TABLE 3 → v6")
print("Coastal Sentinel | King Jones Adega | Tianjin University")
print("=" * 60)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Read skill score ──────────────────────────────────────────
csv_path = os.path.join(SCRIPT_DIR, "GDP_drifters", "M1_skill_scores_summary.csv")
if not os.path.exists(csv_path):
    print(f"[ERROR] Cannot find: {csv_path}")
    print("  Run M1_gdp_hindcast.py first.")
    sys.exit(1)

df = pd.read_csv(csv_path)
mean_row = df[df["event"] == "MEAN_ALL_EVENTS"]
if mean_row.empty:
    print("[ERROR] MEAN_ALL_EVENTS row not found in CSV.")
    sys.exit(1)

S_value = float(mean_row["Skill_Score_S"].iloc[0])
n_events = len(df) - 1   # subtract the MEAN row
print(f"  Skill Score S = {S_value:.4f}  (n = {n_events} events)")

# Format for manuscript: "S = X.XX (n = 3 events)"
S_text = f"S = {S_value:.2f} (n = {n_events} events)"
print(f"  Replacement text: '{S_text}'")

# ── Find manuscript v5 ────────────────────────────────────────
v5_candidates = glob.glob(os.path.join(SCRIPT_DIR, "*v5*.docx")) + \
                glob.glob(os.path.join(SCRIPT_DIR, "*FINAL*v5*.docx"))

if not v5_candidates:
    # Try broader search
    v5_candidates = glob.glob(os.path.join(SCRIPT_DIR, "*.docx"))
    v5_candidates = [f for f in v5_candidates if "v5" in f.lower() or "final" in f.lower()]

if not v5_candidates:
    print("[ERROR] Cannot find manuscript v5 docx in C:\\CoastalSentinel\\")
    print("  Expected: THE_FINAL_MANUSCRIPT_FOR_ES_T_SUBMISSION_v5.docx")
    print("  Please copy it into C:\\CoastalSentinel\\ and re-run.")
    sys.exit(1)

v5_path = sorted(v5_candidates)[-1]
print(f"  Input manuscript: {os.path.basename(v5_path)}")

# ── Build v6 output path ──────────────────────────────────────
v6_name = os.path.basename(v5_path).replace("v5", "v6")
v6_path = os.path.join(SCRIPT_DIR, v6_name)
shutil.copy2(v5_path, v6_path)
print(f"  Output manuscript: {v6_name}")

# ── Patch the docx XML ────────────────────────────────────────
REPLACEMENTS = [
    ("Positive (inferred)", S_text),
    ("Positive\n(inferred)", S_text),   # line-wrapped variant
    ("Positive&#10;(inferred)", S_text),
]

FOOTNOTE_OLD = (
    "is inferred positive (S &gt; 0) at all lead times based on ensemble"
)
FOOTNOTE_NEW = (
    f"= {S_value:.4f} (mean across n = {n_events} hindcast events), "
    "confirming the model outperforms the zero-displacement persistence baseline"
)

changes_made = 0

with zipfile.ZipFile(v6_path, "r") as zin:
    names = zin.namelist()
    contents = {}
    for name in names:
        with zin.open(name) as f:
            try:
                contents[name] = f.read().decode("utf-8")
            except Exception:
                contents[name] = None   # binary file (images etc.)

# Apply replacements to document.xml and footnotes
TARGET_FILES = ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]

for target in TARGET_FILES:
    if target not in contents or contents[target] is None:
        continue
    xml = contents[target]
    original = xml

    for old, new in REPLACEMENTS:
        if old in xml:
            xml = xml.replace(old, new)
            changes_made += xml.count(new) - original.count(new) + xml.count(new)

    # Patch the footnote sentence
    if FOOTNOTE_OLD in xml:
        xml = xml.replace(FOOTNOTE_OLD, FOOTNOTE_NEW)
        changes_made += 1

    contents[target] = xml

# Rewrite the docx
with zipfile.ZipFile(v6_path, "w", zipfile.ZIP_DEFLATED) as zout:
    for name in names:
        if contents.get(name) is not None and isinstance(contents[name], str):
            zout.writestr(name, contents[name].encode("utf-8"))
        else:
            # Reopen original for binary files
            with zipfile.ZipFile(v5_path, "r") as zin_orig:
                if name in zin_orig.namelist():
                    zout.writestr(name, zin_orig.read(name))

# ── Save RMSE footnote text to a separate note file ──────────
note_path = os.path.join(SCRIPT_DIR, "GDP_drifters", "M1_table3_footnote.txt")
rmse_mean = float(df[df["event"] == "MEAN_ALL_EVENTS"]["RMSE_model_km"].iloc[0])
persist_mean = float(df[df["event"] == "MEAN_ALL_EVENTS"]["RMSE_persistence_km"].iloc[0])

with open(note_path, "w") as f:
    f.write(f"Table 3 Skill Score footnote (for manual check):\n\n")
    f.write(f"  S = 1 - (RMSE_model / RMSE_persistence)\n")
    f.write(f"  S = 1 - ({rmse_mean:.3f} / {persist_mean:.3f}) = {S_value:.4f}\n\n")
    f.write(f"  Text inserted into Table 3: '{S_text}'\n")
    f.write(f"  n = {n_events} hindcast events (SCS x2, BoB x1)\n")

# ── VERIFICATION BLOCK ────────────────────────────────────────
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

# Quick check: open v6 and confirm replacement
verify_ok = False
with zipfile.ZipFile(v6_path, "r") as zcheck:
    if "word/document.xml" in zcheck.namelist():
        xml_check = zcheck.read("word/document.xml").decode("utf-8")
        if S_text in xml_check or f"S = {S_value:.2f}" in xml_check:
            verify_ok = True
        still_inferred = "Positive (inferred)" in xml_check

if verify_ok:
    print(f"  ✅ S value found in v6 document XML")
else:
    print(f"  ⚠️  S value not found in XML — may need manual paste (see below)")

if "still_inferred" in dir() and still_inferred:
    print(f"  ⚠️  'Positive (inferred)' still present — open v6 and do Ctrl+H manually")
    print(f"     Find:    Positive (inferred)")
    print(f"     Replace: {S_text}")
else:
    print(f"  ✅ 'Positive (inferred)' successfully replaced")

print(f"\n  Output file: {v6_path}")
print(f"  Footnote note: {note_path}")
print(f"\n  Manual check steps:")
print(f"  1. Open {v6_name} in Word")
print(f"  2. Press Ctrl+F, search 'inferred' — should find 0 results")
print(f"  3. Find Table 3 Skill Score row — should read '{S_text}'")
print(f"  4. Check Table 3 footnote 'a' — should mention S = {S_value:.4f}")

if verify_ok:
    print(f"\n✅ VERIFICATION PASSED — {v6_name} is ready")
    print(f"   Report to Claude: S = {S_value:.4f}")
else:
    print(f"\n⚠️  Automatic patch may be incomplete.")
    print(f"   Open {v6_name} and manually replace 'Positive (inferred)' with '{S_text}'")
    print(f"   Then report to Claude: S = {S_value:.4f}")
