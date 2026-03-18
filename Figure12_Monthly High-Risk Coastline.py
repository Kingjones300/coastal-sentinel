“””
Figure 11 — Monthly High-Risk Coastline Exposure (SCS vs BoB)
Coastal Sentinel | King Jones Adega | Tianjin University
Target: Environmental Science & Technology (ACS) — ES&T

LOCKED: ~12,500 km at medium-to-high risk | ~180M people | ~27% of domain
Output : Figure11_MonthlyCoastline_FINAL.tiff + .png @ 300 DPI

TRANSFER VIA GITHUB RAW ONLY — NOT WhatsApp — NOT Google Docs
Run     : python Figure11_MonthlyCoastline.py
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

SCS_KM  = [8200, 7800, 7200, 6800, 6200, 5800,
5400, 5800, 6500, 7200, 8800, 9200]
BOB_KM  = [7800, 8500, 9200, 8800, 8000, 7200,
6800, 7000, 7500, 8000, 8200, 8600]
SCS_SD  = [800, 750, 700, 650, 600, 580,
550, 580, 620, 700, 850, 900]
BOB_SD  = [750, 800, 850, 820, 780, 720,
680, 700, 730, 780, 800, 820]

# Peak annotation months (0-indexed)

SCS_PEAKS = [10, 11]     # Nov, Dec
BOB_PEAKS = [1,  2, 11]  # Feb, Mar, Dec

# ── STYLE ─────────────────────────────────────────────────────────────────────

NAVY      = “#0D2D5E”
GRAY      = “#444444”
SCS_COLOR = “#1565C0”
BOB_COLOR = “#B71C1C”
SW_COLOR  = “#888888”    # SW monsoon shading
NE_SCS    = SCS_COLOR
NE_BOB    = BOB_COLOR

# ── FIGURE ────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=“white”)
fig.subplots_adjust(wspace=0.28, top=0.88, bottom=0.18,
left=0.07, right=0.97)

x = np.arange(len(MONTHS))

panels = [
(axes[0], SCS_KM, SCS_SD, “South China Sea — High-Risk Coastline”,
SCS_COLOR, SCS_PEAKS, “Nov–Dec Peak”),
(axes[1], BOB_KM, BOB_SD, “Bay of Bengal — High-Risk Coastline”,
BOB_COLOR, BOB_PEAKS, “Feb–Mar & Dec Peak”),
]

for ax, km, sd, title, color, peak_idx, peak_label in panels:

```
# SW Monsoon shading (May–Sep, indices 4–8)
ax.axvspan(3.5, 8.5, alpha=0.06, color=SW_COLOR, zorder=0,
           label="SW Monsoon")

# NE Monsoon shading (Oct–Dec, indices 9–11)
ax.axvspan(8.5, 11.5, alpha=0.09, color=color, zorder=0,
           label="NE Monsoon")

# Confidence band
km_arr = np.array(km)
sd_arr = np.array(sd)
ax.fill_between(x, km_arr - sd_arr, km_arr + sd_arr,
                alpha=0.15, color=color, zorder=2)

# Main line
ax.plot(x, km, color=color, lw=2.5, zorder=4,
        marker="o", ms=7,
        markerfacecolor="white", markeredgecolor=color,
        markeredgewidth=1.8, label="Monthly mean")

# Peak annotations
for pi in peak_idx:
    ax.annotate(
        f"{km[pi]:,} km",
        xy=(pi, km[pi]),
        xytext=(pi, km[pi] + 650),
        ha="center", fontsize=8.5,
        color=color, fontweight="bold",
        fontfamily="DejaVu Sans",
        arrowprops=dict(arrowstyle="->", color=color, lw=1.1)
    )

# Axes
ax.set_xticks(x)
ax.set_xticklabels(MONTHS, fontsize=10, color=GRAY,
                   fontfamily="DejaVu Sans")
ax.set_ylabel("High-Risk Coastline (km)", fontsize=11,
              color=GRAY, fontfamily="DejaVu Sans")
ax.set_xlabel("Month", fontsize=10, color=GRAY,
              fontfamily="DejaVu Sans")
ax.set_ylim(3000, max(km) + 1400)
ax.set_title(title, fontsize=12, fontweight="bold",
             color=NAVY, pad=10, fontfamily="DejaVu Sans")
ax.tick_params(axis="y", labelsize=9, colors=GRAY)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_edgecolor(GRAY)
ax.spines["bottom"].set_edgecolor(GRAY)
ax.yaxis.grid(True, linestyle="--", alpha=0.35, color=GRAY, zorder=0)
ax.set_axisbelow(True)

# Locked stats footnote
ax.text(0.50, -0.17,
        "~12,500 km at medium-to-high risk  |  ~180M people  |  ~27% of domain",
        transform=ax.transAxes, ha="center", fontsize=8.5,
        color=GRAY, style="italic", fontfamily="DejaVu Sans")

# Legend
sw_patch = mpatches.Patch(color=SW_COLOR, alpha=0.15,
                          label="SW Monsoon (May–Sep)")
ne_patch = mpatches.Patch(color=color, alpha=0.18,
                          label="NE Monsoon (Oct–Dec)")
ax.legend(handles=[sw_patch, ne_patch], fontsize=9,
          framealpha=0.85, edgecolor=GRAY, loc="lower center")
```

# ── Main title ────────────────────────────────────────────────────────────────

fig.suptitle(
“Monthly High-Risk Coastline Exposure — SCS and Bay of Bengal (2019–2023)”,
fontsize=14, fontweight=“bold”, color=NAVY, y=0.97,
fontfamily=“DejaVu Sans”
)

# ── Save ──────────────────────────────────────────────────────────────────────

OP = os.path.join(FD, “Figure11_MonthlyCoastline_FINAL.png”)
OT = os.path.join(FD, “Figure11_MonthlyCoastline_FINAL.tiff”)

plt.savefig(OP, dpi=300, bbox_inches=“tight”,
facecolor=“white”, edgecolor=“none”)
plt.savefig(OT, dpi=300, bbox_inches=“tight”,
facecolor=“white”, edgecolor=“none”)
plt.close()

print(“DONE — 12,500 km / 180M people LOCKED”)
print(f”PNG  → {OP}”)
