import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATA = r'E:\COASTAL SENTINEL\CoastalSentinel\Data'
OUT_DIR = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes'

SCS_FILE = DATA + r'\Ocean_Currents\SCS\SCS_Ocean_Currents_2019_2023.nc'
BOB_FILE = DATA + r'\Ocean_Currents\BoB\BoB_Ocean_Currents_2019_2023.nc'

def compute_monthly_by_year(filepath):
    ds = xr.open_dataset(filepath)
    u = ds['uo'].isel(depth=0)
    v = ds['vo'].isel(depth=0)
    speed = np.sqrt(u**2 + v**2)
    monthly = speed.resample(time='MS').mean(dim=['time', 'latitude', 'longitude'] if 'latitude' in speed.dims else 'time')
    months = monthly['time'].dt.month.values
    years = monthly['time'].dt.year.values
    values = monthly.values
    ds.close()
    by_month = [values[months == m] for m in range(1, 13)]
    return by_month

print('Computing real SCS monthly values (5 years each)...')
scs_by_month = compute_monthly_by_year(SCS_FILE)
print('Computing real BoB monthly values (5 years each)...')
bob_by_month = compute_monthly_by_year(BOB_FILE)

for i, vals in enumerate(scs_by_month):
    print(f'SCS month {i+1}: {[round(float(v), 4) for v in vals]}')
for i, vals in enumerate(bob_by_month):
    print(f'BoB month {i+1}: {[round(float(v), 4) for v in vals]}')

BLUE_DEEP = '#0D4C8C'
BLUE_LIGHT = '#4A90D9'
ORANGE_DEEP = '#C4581A'
ORANGE_LIGHT = '#F0A050'
GRAY = '#333333'
MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
months = np.arange(1, 13)

fig, ax = plt.subplots(figsize=(13, 6.5), facecolor='white')

positions_scs = months - 0.18
positions_bob = months + 0.18

bp1 = ax.boxplot(scs_by_month, positions=positions_scs, widths=0.32, patch_artist=True,
                  boxprops=dict(facecolor=BLUE_LIGHT, edgecolor=BLUE_DEEP, linewidth=1.6),
                  medianprops=dict(color=BLUE_DEEP, linewidth=2.2),
                  whiskerprops=dict(color=BLUE_DEEP, linewidth=1.4),
                  capprops=dict(color=BLUE_DEEP, linewidth=1.4),
                  flierprops=dict(marker='o', markerfacecolor=BLUE_DEEP, markeredgecolor='white', markersize=5))

bp2 = ax.boxplot(bob_by_month, positions=positions_bob, widths=0.32, patch_artist=True,
                  boxprops=dict(facecolor=ORANGE_LIGHT, edgecolor=ORANGE_DEEP, linewidth=1.6),
                  medianprops=dict(color=ORANGE_DEEP, linewidth=2.2),
                  whiskerprops=dict(color=ORANGE_DEEP, linewidth=1.4),
                  capprops=dict(color=ORANGE_DEEP, linewidth=1.4),
                  flierprops=dict(marker='o', markerfacecolor=ORANGE_DEEP, markeredgecolor='white', markersize=5))

# Subtle monsoon season highlighting as background tint, not full-height bars
ax.axvspan(0.5, 2.5, color='#EAF0F8', zorder=0)
ax.axvspan(12, 12.5, color='#EAF0F8', zorder=0)
ax.axvspan(5.5, 8.5, color='#FDF3E3', zorder=0)

ax.set_xticks(months)
ax.set_xticklabels(MONTH_LABELS, fontsize=11.5)
ax.set_xlim(0.3, 12.7)
ax.set_xlabel('Month', fontsize=13, fontweight='bold', color=GRAY)
ax.set_ylabel('Surface Current Speed (m/s)', fontsize=13, fontweight='bold', color=GRAY)
ax.set_title('Monthly Surface Current Speed Distribution (2019\u20132023)\nSouth China Sea vs. Bay of Bengal',
             fontsize=15, fontweight='bold', color='#0D2D5E', pad=15)
ax.tick_params(labelsize=11, colors=GRAY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#999999')
ax.spines['bottom'].set_color('#999999')
ax.grid(True, axis='y', linestyle='--', linewidth=0.6, color='#E0E0E0', alpha=0.9)
ax.set_axisbelow(True)

legend_elements = [
    Patch(facecolor=BLUE_LIGHT, edgecolor=BLUE_DEEP, label='South China Sea (SCS)'),
    Patch(facecolor=ORANGE_LIGHT, edgecolor=ORANGE_DEEP, label='Bay of Bengal (BoB)'),
]
ax.legend(handles=legend_elements, fontsize=11.5, framealpha=0.95, loc='upper right', edgecolor='#CCCCCC')

fig.tight_layout()

OP = OUT_DIR + '\\Figure5_Boxplot_FINAL.png'
OT = OUT_DIR + '\\Figure5_Boxplot_FINAL.tiff'
fig.savefig(OP, dpi=600, bbox_inches='tight', facecolor='white')
fig.savefig(OT, dpi=600, bbox_inches='tight', facecolor='white')
plt.close()
print('Saved: ' + OP)
print('Saved: ' + OT)
