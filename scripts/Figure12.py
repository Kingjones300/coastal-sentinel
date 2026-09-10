import numpy as np
import matplotlib.pyplot as plt

BASINS = ['South China Sea', 'Bay of Bengal']
HIGH_KM = [15.9, 18.2]
MEDIUM_KM = [1159.6, 966.8]
LOW_KM = [7689.9, 5138.1]
CHECKED_KM = [8865.4, 6123.1]
PCT_MEDHIGH = [13.3, 16.1]

NAVY = '#0D2D5E'
GRAY = '#444444'
SCS_COLOR = '#1565C0'
BOB_COLOR = '#B71C1C'
LOW_COLOR = '#8FA6C4'
MED_COLOR = '#E8A33D'
HIGH_COLOR = '#C0392B'

fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor='white')
fig.subplots_adjust(wspace=0.30, top=0.86, bottom=0.14, left=0.08, right=0.97)

x = np.arange(2)
width = 0.55

ax = axes[0]
ax.bar(x, LOW_KM, width, label='LOW risk', color=LOW_COLOR, edgecolor='white')
ax.bar(x, MEDIUM_KM, width, bottom=LOW_KM, label='MEDIUM risk', color=MED_COLOR, edgecolor='white')
bottom_high = [LOW_KM[i] + MEDIUM_KM[i] for i in range(2)]
ax.bar(x, HIGH_KM, width, bottom=bottom_high, label='HIGH risk', color=HIGH_COLOR, edgecolor='white')

for i in range(2):
    ax.text(i, CHECKED_KM[i] + 200, f'{CHECKED_KM[i]:,.0f} km\nchecked', ha='center', fontsize=9,
            color=GRAY, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(BASINS, fontsize=11, fontweight='bold', color=NAVY)
ax.set_ylabel('Coastline Length (km)', fontsize=11, color=GRAY)
ax.set_title('Real Coastline Length by Risk Category', fontsize=12, fontweight='bold', color=NAVY, pad=10)
ax.legend(loc='upper right', fontsize=9, framealpha=0.9, edgecolor=GRAY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linestyle='--', alpha=0.35, color=GRAY)
ax.set_axisbelow(True)

ax2 = axes[1]
colors = [SCS_COLOR, BOB_COLOR]
ax2.bar(x, PCT_MEDHIGH, width, color=colors, edgecolor='white')
for i, v in enumerate(PCT_MEDHIGH):
    ax2.text(i, v + 1.5, f'{v:.1f}%\n({HIGH_KM[i]+MEDIUM_KM[i]:,.0f} km)', ha='center',
              fontsize=9.5, fontweight='bold', color=colors[i])

ax2.set_xticks(x)
ax2.set_xticklabels(BASINS, fontsize=11, fontweight='bold', color=NAVY)
ax2.set_ylabel('Coastline at Medium-to-High Risk (%)', fontsize=11, color=GRAY)
ax2.set_title('Proportion of Coastline at Medium-to-High Risk', fontsize=12, fontweight='bold', color=NAVY, pad=10)
ax2.set_ylim(0, 25)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.yaxis.grid(True, linestyle='--', alpha=0.35, color=GRAY)
ax2.set_axisbelow(True)

fig.suptitle('Real Coastline Risk Exposure - South China Sea vs. Bay of Bengal (2019-2023)',
             fontsize=14, fontweight='bold', color=NAVY, y=0.965)
fig.text(0.5, 0.02,
         'Computed from real corrected FDI detection rasters, real CMEMS current speed, and real OpenDrift accumulation grids | '
         'Natural Earth 10m coastline geometry',
         ha='center', fontsize=8, color=GRAY, style='italic')

OP = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes\Figure12_RealCoastlineRisk.png'
OT = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes\Figure12_RealCoastlineRisk.tiff'
fig.savefig(OP, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
fig.savefig(OT, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print('Saved: ' + OP)
print('Saved: ' + OT)
