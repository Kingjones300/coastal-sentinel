import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

FD = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes'
os.makedirs(FD, exist_ok=True)

SCS_CSV = r'E:\COASTAL SENTINEL\CoastalSentinel\GEE_FDI_EXPORTS\SCS_monthly_FDI_counts.csv'
BOB_CSV = r'E:\COASTAL SENTINEL\CoastalSentinel\GEE_FDI_EXPORTS\BoB_monthly_FDI_counts.csv'

scs_df = pd.read_csv(SCS_CSV)
bob_df = pd.read_csv(BOB_CSV)

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def monthly_mean_sd(df):
    grouped = df.groupby('month')['fdi_pixel_count']
    means = [grouped.get_group(m).mean() if m in grouped.groups else np.nan for m in range(1, 13)]
    sds = [grouped.get_group(m).std() if m in grouped.groups else np.nan for m in range(1, 13)]
    return means, sds

scs_fdi, scs_sd = monthly_mean_sd(scs_df)
bob_fdi, bob_sd = monthly_mean_sd(bob_df)

MONSOON_SCS = [(4, 8), (9, 11)]
MONSOON_BOB = [(4, 9)]

NAVY = "#0D2D5E"
GRAY = "#444444"
BLUE = "#1A4F8A"
ORANGE = "#D4711A"

fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor="white")
fig.subplots_adjust(wspace=0.28, top=0.88, bottom=0.12, left=0.07, right=0.97)

x = np.arange(len(MONTHS))
w = 0.60

panels = [
    (axes[0], scs_fdi, scs_sd, "South China Sea - Monthly FDI Detection (Real)", MONSOON_SCS, BLUE),
    (axes[1], bob_fdi, bob_sd, "Bay of Bengal - Monthly FDI Detection (Real)", MONSOON_BOB, ORANGE),
]

for ax, fdi, sd, title, monsoons, color in panels:
    for ms, me in monsoons:
        ax.axvspan(ms - 0.5, me + 0.5, alpha=0.10, color=color, zorder=0)

    bars = ax.bar(x, fdi, w, color=color, alpha=0.88, zorder=3, edgecolor="white", linewidth=0.6)
    ax.errorbar(x, fdi, yerr=sd, fmt="none", color=GRAY, capsize=4.5, capthick=1.2, elinewidth=1.2, zorder=4)

    for bar, val in zip(bars, fdi):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(fdi)*0.015,
                f'{val:,.0f}', ha="center", va="bottom", fontsize=7.5, color=GRAY, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=10, color=GRAY)
    ax.set_ylabel("Mean FDI Pixel Count (2019-2023)", fontsize=11, color=GRAY)
    ax.set_xlabel("Month", fontsize=10, color=GRAY)
    ax.set_title(title, fontsize=12, fontweight="bold", color=NAVY, pad=10)
    ax.tick_params(axis="y", labelsize=9, colors=GRAY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, color=GRAY, zorder=0)
    ax.set_axisbelow(True)

    mon_patch = mpatches.Patch(color=color, alpha=0.20, label="Monsoon period")
    ax.legend(handles=[mon_patch], fontsize=9, framealpha=0.85,
              loc="upper left" if color == BLUE else "upper right", edgecolor=GRAY)

fig.suptitle("Real Monthly FDI Detection Frequency - SCS and Bay of Bengal (2019-2023)",
             fontsize=14, fontweight="bold", color=NAVY, y=0.97)

OP = os.path.join(FD, "Figure9_MonthlyFDI_REAL.png")
OT = os.path.join(FD, "Figure9_MonthlyFDI_REAL.tiff")
plt.savefig(OP, dpi=600, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.savefig(OT, dpi=600, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.close()

print("DONE")
print("PNG ->", OP)
print("Real SCS monthly means:", [round(v,0) for v in scs_fdi])
print("Real BoB monthly means:", [round(v,0) for v in bob_fdi])
