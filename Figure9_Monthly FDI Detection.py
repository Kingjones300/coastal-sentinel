“””
Figure 8 — Monthly FDI Detection Frequency (2019–2023)
Coastal Sentinel | King Jones Adega | Tianjin University
Target: Environmental Science & Technology (ACS) — ES&T

Layout  : 1 row × 2 panels (SCS left, BoB right)
Output  : Figure8_MonthlyFDI_FINAL.tiff + .png @ 300 DPI

TRANSFER VIA GITHUB RAW ONLY — NOT WhatsApp — NOT Google Docs
Run     : python Figure8_MonthlyFDI.py
Requires: numpy, matplotlib
“””

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ── PATHS ─────────────────────────────────────────────────────────────────────

FD = “C:/CoastalSentinel/Outputs/Figures”
os.makedirs(FD, exist_ok=True)

# ── LOCKED DATA ───────────────────────────────────────────────────────────────

MONTHS  = [“Jan”,“Feb”,“Mar”,“Apr”,“May”,“Jun”,
“Jul”,“Aug”,“Sep”,“Oct”,“Nov”,“Dec”]

SCS_FDI = [42, 38, 35, 28, 22, 18, 15, 19, 28, 38, 45, 48]
BOB_FDI = [18, 22, 28, 32, 38, 42, 45, 40, 32, 25, 18, 15]
SCS_SD  = [ 8,  7,  6,  5,  4,  4,  3,  4,  5,  7,  8,  9]
BOB_SD  = [ 4,  4,  5,  6,  7,  8,  8,  7,  6,  5,  4,  3]

# Monsoon windows (0-indexed month start, end inclusive)

MONSOON_SCS = [(4, 8), (9, 11)]   # SW monsoon May-Sep, NE monsoon Oct-Dec
MONSOON_BOB = [(4, 9)]            # SW monsoon May-Oct

# ── STYLE ─────────────────────────────────────────────────────────────────────

NAVY = “#0D2D5E”
GOLD = “#C9A84C”
GRAY = “#444444”

# ── FIGURE ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=“white”)
fig.subplots_adjust(wspace=0.28, top=0.88, bottom=0.12,
left=0.07, right=0.97)

x = np.arange(len(MONTHS))
w = 0.60

panels = [
(axes[0], SCS_FDI, SCS_SD, “South China Sea — Monthly FDI Detection”,
MONSOON_SCS, NAVY),
(axes[1], BOB_FDI, BOB_SD, “Bay of Bengal — Monthly FDI Detection”,
MONSOON_BOB, GOLD),
]

for ax, fdi, sd, title, monsoons, color in panels:

```
# Monsoon shading
for ms, me in monsoons:
    ax.axvspan(ms - 0.5, me + 0.5, alpha=0.09,
               color=color, zorder=0)

# Bars
bars = ax.bar(x, fdi, w, color=color, alpha=0.86, zorder=3,
              edgecolor="white", linewidth=0.5)

# Error bars
ax.errorbar(x, fdi, yerr=sd, fmt="none",
            color=GRAY, capsize=4.5, capthick=1.2,
            elinewidth=1.2, zorder=4)

# Value labels on top of bars
for bar, val in zip(bars, fdi):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.8,
            str(val), ha="center", va="bottom",
            fontsize=8.5, color=GRAY, fontweight="bold",
            fontfamily="DejaVu Sans")

# Axes formatting
ax.set_xticks(x)
ax.set_xticklabels(MONTHS, fontsize=10, color=GRAY,
                   fontfamily="DejaVu Sans")
ax.set_ylabel("FDI Detection Count", fontsize=11,
              color=GRAY, fontfamily="DejaVu Sans")
ax.set_xlabel("Month", fontsize=10, color=GRAY,
              fontfamily="DejaVu Sans")
ax.set_title(title, fontsize=12, fontweight="bold",
             color=NAVY, pad=10, fontfamily="DejaVu Sans")
ax.set_ylim(0, max(fdi) + 18)
ax.tick_params(axis="y", labelsize=9, colors=GRAY)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_edgecolor(GRAY)
ax.spines["bottom"].set_edgecolor(GRAY)
ax.yaxis.grid(True, linestyle="--", alpha=0.4, color=GRAY, zorder=0)
ax.set_axisbelow(True)

# Legend
mon_patch = mpatches.Patch(color=color, alpha=0.18,
                           label="Monsoon period")
ax.legend(handles=[mon_patch], fontsize=9, framealpha=0.85,
          loc="upper left" if color == NAVY else "upper right",
          edgecolor=GRAY)
```

# ── Main title ────────────────────────────────────────────────────────────────

fig.suptitle(
“Monthly FDI Detection Frequency — SCS and Bay of Bengal (2019–2023)”,
fontsize=14, fontweight=“bold”, color=NAVY, y=0.97,
fontfamily=“DejaVu Sans”
)

# ── Save ──────────────────────────────────────────────────────────────────────

OP = os.path.join(FD, “Figure8_MonthlyFDI_FINAL.png”)
OT = os.path.join(FD, “Figure8_MonthlyFDI_FINAL.tiff”)

plt.savefig(OP, dpi=300, bbox_inches=“tight”,
facecolor=“white”, edgecolor=“none”)
plt.savefig(OT, dpi=300, bbox_inches=“tight”,
facecolor=“white”, edgecolor=“none”)
plt.close()

print(“DONE → “ + OP)
