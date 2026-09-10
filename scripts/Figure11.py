“””
Figure 10 — OpenDrift Ensemble Spread and Forecast Skill Score
Coastal Sentinel | King Jones Adega | Tianjin University
Target: Environmental Science & Technology (ACS) — ES&T

LOCKED: Spread 5.74 / 8.92 / 12.11 km at 24 / 48 / 72 h
Skill S = 0.57 / 0.67 / 0.70  |  Mean S = 0.65
Output : Figure10_EnsembleSpread_FINAL.tiff + .png @ 300 DPI

TRANSFER VIA GITHUB RAW ONLY — NOT WhatsApp — NOT Google Docs
Run     : python Figure10_EnsembleSpread.py
Requires: numpy, matplotlib
“””

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ── PATHS ─────────────────────────────────────────────────────────────────────

FD = “C:/CoastalSentinel/Outputs/Figures”
os.makedirs(FD, exist_ok=True)

# ── LOCKED VALUES — NEVER CHANGE ─────────────────────────────────────────────

SPREAD_24 = 5.74
SPREAD_48 = 8.92
SPREAD_72 = 12.11
S_SCORES  = [0.57, 0.67, 0.70]
S_MEAN    = 0.65
LABELS    = [“24 hr”, “48 hr”, “72 hr”]
TIERS     = [“WATCH”, “WARNING”, “ALERT”]

# ── STYLE ─────────────────────────────────────────────────────────────────────

NAVY   = “#0D2D5E”
GOLD   = “#C9A84C”
GRAY   = “#444444”
BLUE   = “#1565C0”
ORANGE = “#E65100”
RED    = “#B71C1C”
COLORS = [BLUE, ORANGE, RED]

# ── FIGURE ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=“white”)
fig.subplots_adjust(wspace=0.30, top=0.88, bottom=0.12,
left=0.07, right=0.97)

spreads = [SPREAD_24, SPREAD_48, SPREAD_72]

# ── Panel A: Ensemble spread ──────────────────────────────────────────────────

ax1 = axes[0]
bars1 = ax1.bar(LABELS, spreads, color=COLORS, alpha=0.86,
width=0.50, zorder=3, edgecolor=“white”, linewidth=0.5)

# Value labels

for bar, val in zip(bars1, spreads):
ax1.text(bar.get_x() + bar.get_width() / 2,
bar.get_height() + 0.18,
f”{val} km”, ha=“center”, va=“bottom”,
fontsize=12, fontweight=“bold”, color=NAVY,
fontfamily=“DejaVu Sans”)

# Tier labels inside bars

for bar, tier, col in zip(bars1, TIERS, COLORS):
ax1.text(bar.get_x() + bar.get_width() / 2,
bar.get_height() / 2,
tier, ha=“center”, va=“center”,
fontsize=10, fontweight=“bold”, color=“white”,
fontfamily=“DejaVu Sans”)

# 10 km reference line

ax1.axhline(y=10, color=GRAY, lw=0.9, ls=”–”, alpha=0.6, zorder=2)
ax1.text(2.38, 10.25, “10 km limit”,
fontsize=8.5, color=GRAY, fontfamily=“DejaVu Sans”)

ax1.set_ylabel(“Mean Pairwise Ensemble Spread (km)”,
fontsize=11, color=GRAY, fontfamily=“DejaVu Sans”)
ax1.set_title(“Ensemble Drift Spread at 24 / 48 / 72 Hours”,
fontsize=12, fontweight=“bold”, color=NAVY,
pad=10, fontfamily=“DejaVu Sans”)
ax1.set_ylim(0, 16)
ax1.set_xlabel(“Forecast Horizon”, fontsize=10, color=GRAY,
fontfamily=“DejaVu Sans”)
ax1.tick_params(axis=“both”, labelsize=10, colors=GRAY)
ax1.spines[“top”].set_visible(False)
ax1.spines[“right”].set_visible(False)
ax1.spines[“left”].set_edgecolor(GRAY)
ax1.spines[“bottom”].set_edgecolor(GRAY)
ax1.yaxis.grid(True, linestyle=”–”, alpha=0.35, color=GRAY, zorder=0)
ax1.set_axisbelow(True)

# ── Panel B: Skill scores ─────────────────────────────────────────────────────

ax2 = axes[1]
bars2 = ax2.bar(LABELS, S_SCORES, color=COLORS, alpha=0.86,
width=0.50, zorder=3, edgecolor=“white”, linewidth=0.5)

# Value labels

for bar, val in zip(bars2, S_SCORES):
ax2.text(bar.get_x() + bar.get_width() / 2,
bar.get_height() + 0.012,
f”S = {val}”, ha=“center”, va=“bottom”,
fontsize=12, fontweight=“bold”, color=NAVY,
fontfamily=“DejaVu Sans”)

# Mean skill line

ax2.axhline(y=S_MEAN, color=GOLD, lw=1.8, ls=”–”, alpha=0.85, zorder=2)
ax2.text(2.38, S_MEAN + 0.008, f”Mean S = {S_MEAN}”,
fontsize=8.5, color=GOLD, fontweight=“bold”,
fontfamily=“DejaVu Sans”)

# S > 0 reference

ax2.axhline(y=0, color=GRAY, lw=0.7, ls=”-”, alpha=0.5, zorder=2)

ax2.set_ylabel(“Forecast Skill Score (S)”,
fontsize=11, color=GRAY, fontfamily=“DejaVu Sans”)
ax2.set_title(“OpenDrift Forecast Skill Score  (S > 0 = Skilful)”,
fontsize=12, fontweight=“bold”, color=NAVY,
pad=10, fontfamily=“DejaVu Sans”)
ax2.set_ylim(0, 0.85)
ax2.set_xlabel(“Forecast Horizon”, fontsize=10, color=GRAY,
fontfamily=“DejaVu Sans”)
ax2.tick_params(axis=“both”, labelsize=10, colors=GRAY)
ax2.spines[“top”].set_visible(False)
ax2.spines[“right”].set_visible(False)
ax2.spines[“left”].set_edgecolor(GRAY)
ax2.spines[“bottom”].set_edgecolor(GRAY)
ax2.yaxis.grid(True, linestyle=”–”, alpha=0.35, color=GRAY, zorder=0)
ax2.set_axisbelow(True)

# ── Main title ────────────────────────────────────────────────────────────────

fig.suptitle(“OpenDrift Ensemble Performance — Spread and Skill Score”,
fontsize=14, fontweight=“bold”, color=NAVY, y=0.97,
fontfamily=“DejaVu Sans”)

# ── Save ──────────────────────────────────────────────────────────────────────

OP = os.path.join(FD, “Figure10_EnsembleSpread_FINAL.png”)
OT = os.path.join(FD, “Figure10_EnsembleSpread_FINAL.tiff”)

plt.savefig(OP, dpi=300, bbox_inches=“tight”,
facecolor=“white”, edgecolor=“none”)
plt.savefig(OT, dpi=300, bbox_inches=“tight”,
facecolor=“white”, edgecolor=“none”)
plt.close()

print(f”DONE — Spread 5.74 / 8.92 / 12.11 LOCKED | S = 0.57/0.67/0.70 LOCKED”)
print(f”PNG  → {OP}”)
