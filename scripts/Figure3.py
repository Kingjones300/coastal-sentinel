import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
import matplotlib.ticker as mticker
import os

FIG2 = r'E:\COASTAL SENTINEL\CoastalSentinel\Fig2'
OUT_DIR = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes'
DOWNLOADS = os.path.expanduser(r'~\Downloads')

thresholds = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08]

BASINS = {
    'SCS': {'ext': [99, 122, 1, 24], 'files': ['Fig2a_SCS_NE_Monsoon_CORRECTED.tif', 'Fig2b_SCS_SW_Monsoon_CORRECTED.tif'],
            'mask': 'SCS_DeepWaterMask_20m.tif'},
    'BoB': {'ext': [79, 100, 5, 23], 'files': ['Fig2c_BoB_NE_Monsoon_CORRECTED.tif', 'Fig2d_BoB_SW_Monsoon_CORRECTED.tif'],
            'mask': 'BoB_DeepWaterMask_20m.tif'},
}

print('=== Loading real deep-water-only scene detection counts (Panel A) ===')
scs_scenes = pd.read_csv(DOWNLOADS + r'\FDI_max_DEEPWATER_SCS.csv')
bob_scenes = pd.read_csv(DOWNLOADS + r'\FDI_max_DEEPWATER_BoB.csv')
scs_scene_counts = [int((scs_scenes['fdi_max'] > t).sum()) for t in thresholds]
bob_scene_counts = [int((bob_scenes['fdi_max'] > t).sum()) for t in thresholds]
total_scene_counts = [s + b for s, b in zip(scs_scene_counts, bob_scene_counts)]
print('SCS:', scs_scene_counts)
print('BoB:', bob_scene_counts)

print('=== Computing real depth-masked unique area for Panel B ===')
panelB_areas = {}
for basin, cfg in BASINS.items():
    with rasterio.open(FIG2 + '\\' + cfg['files'][0]) as ds:
        ne_data = ds.read(1).astype(float)
        ne_data[ne_data < -1e5] = np.nan
        ref_transform, ref_crs, ref_shape = ds.transform, ds.crs, ne_data.shape
        res_x = (ds.bounds.right - ds.bounds.left) / ds.width
        res_y = (ds.bounds.top - ds.bounds.bottom) / ds.height
        lat_mid = (ds.bounds.top + ds.bounds.bottom) / 2
        pixel_area_km2 = (res_x * 111.0 * np.cos(np.radians(lat_mid))) * (res_y * 111.0)
    with rasterio.open(FIG2 + '\\' + cfg['files'][1]) as ds:
        sw_data = ds.read(1).astype(float)
        sw_data[sw_data < -1e5] = np.nan
    with rasterio.open(FIG2 + '\\' + cfg['mask']) as ds_mask:
        mask_raw = ds_mask.read(1).astype(float)
        mask_aligned = np.empty(ref_shape, dtype=np.float32)
        reproject(source=mask_raw, destination=mask_aligned,
                  src_transform=ds_mask.transform, src_crs=ds_mask.crs,
                  dst_transform=ref_transform, dst_crs=ref_crs, resampling=Resampling.nearest)
    deep_water = mask_aligned > 0.5

    areas_this_basin = []
    for t in thresholds:
        ne_exceeds = np.nan_to_num(ne_data, nan=-999) > t
        sw_exceeds = np.nan_to_num(sw_data, nan=-999) > t
        unique_exceeds = (ne_exceeds | sw_exceeds) & deep_water
        areas_this_basin.append(np.sum(unique_exceeds) * pixel_area_km2)
    panelB_areas[basin] = areas_this_basin
    print(f'{basin}:', [round(a) for a in areas_this_basin])

print('=== Computing real Panels C and D (unaffected, cross-seasonal) ===')
GRID_STEP = 0.05

def regrid_one(fname, lons, lats):
    LON, LAT = np.meshgrid(lons, lats)
    with rasterio.open(FIG2 + '\\' + fname) as ds:
        band = ds.read(1).astype(float)
        band[band < -1e5] = np.nan
        src_lons = np.linspace(ds.bounds.left, ds.bounds.right, band.shape[1])
        src_lats = np.linspace(ds.bounds.top, ds.bounds.bottom, band.shape[0])
        interp = RegularGridInterpolator((src_lats, src_lons), band, bounds_error=False, fill_value=np.nan)
        pts = np.column_stack([LAT.ravel(), LON.ravel()])
        return interp(pts).reshape(LAT.shape)

all_A, all_B = [], []
for basin, cfg in BASINS.items():
    ext = cfg['ext']
    lons = np.arange(ext[0], ext[1], GRID_STEP)
    lats = np.arange(ext[2], ext[3], GRID_STEP)
    season_A = regrid_one(cfg['files'][0], lons, lats)
    season_B = regrid_one(cfg['files'][1], lons, lats)
    valid = np.isfinite(season_A) & np.isfinite(season_B)
    all_A.append(season_A[valid])
    all_B.append(season_B[valid])

A_pool = np.concatenate(all_A)
B_pool = np.concatenate(all_B)

tp_rate, fp_rate = [], []
for t in thresholds:
    A_pos, B_pos = A_pool > t, B_pool > t
    TP, FN = np.sum(A_pos & B_pos), np.sum(~A_pos & B_pos)
    FP, TN = np.sum(A_pos & ~B_pos), np.sum(~A_pos & ~B_pos)
    tp_rate.append(TP / max(TP + FN, 1))
    fp_rate.append(FP / max(FP + TN, 1))

print('=== Building final figure ===')
BLUE, ORANGE, GREEN, GRAY, SELECT, LBLUE = '#1A4F8A', '#D4711A', '#2A7A4B', '#333333', '#C0392B', '#4A90C4'
PANEL_BG = '#F7F9FC'

fig = plt.figure(figsize=(15, 11.5), facecolor='white')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.32, left=0.08, right=0.97, top=0.90, bottom=0.11)

def style_ax(ax, title):
    ax.set_facecolor(PANEL_BG)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.tick_params(colors=GRAY, labelsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1A1A2E', pad=10)
    ax.grid(True, linestyle='--', linewidth=0.5, color='#DDDDDD', alpha=0.8)
    ax.set_axisbelow(True)

ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, '(A) Scene Detection Count by Basin (Deep-Water Only)')
ax1.plot(thresholds, scs_scene_counts, 'o-', color=BLUE, linewidth=2.5, markersize=9, label='SCS', zorder=4)
ax1.plot(thresholds, bob_scene_counts, 's-', color=ORANGE, linewidth=2.5, markersize=9, label='BoB', zorder=4)
ax1.plot(thresholds, total_scene_counts, '^--', color=GREEN, linewidth=2, markersize=8, label='Total', zorder=3, alpha=0.8)
ax1.scatter([0.05], [scs_scene_counts[2]], s=150, color=SELECT, zorder=6, edgecolors='white', linewidth=2)
ax1.scatter([0.05], [bob_scene_counts[2]], s=150, color=SELECT, zorder=6, edgecolors='white', linewidth=2)
ax1.axvline(x=0.05, color=SELECT, linewidth=1.5, linestyle='--', alpha=0.7, zorder=2)
ax1.set_xlabel('FDI Threshold', fontsize=13, color=GRAY, fontweight='bold')
ax1.set_ylabel('Scene Detection Count', fontsize=13, color=GRAY, fontweight='bold')
ax1.set_xticks(thresholds)
ax1.legend(fontsize=11.5, framealpha=0.9, loc='upper right')

ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, '(B) FDI-Positive Area by Basin (Deep-Water Only)')
ax2.fill_between(thresholds, panelB_areas['SCS'], alpha=0.18, color=BLUE)
ax2.fill_between(thresholds, panelB_areas['BoB'], alpha=0.18, color=ORANGE)
ax2.plot(thresholds, panelB_areas['SCS'], 'o-', color=BLUE, linewidth=2.5, markersize=9, label='SCS')
ax2.plot(thresholds, panelB_areas['BoB'], 's-', color=ORANGE, linewidth=2.5, markersize=9, label='BoB')
ax2.scatter([0.05], [panelB_areas['SCS'][2]], s=150, color=SELECT, zorder=6, edgecolors='white', linewidth=2)
ax2.scatter([0.05], [panelB_areas['BoB'][2]], s=150, color=SELECT, zorder=6, edgecolors='white', linewidth=2)
ax2.axvline(x=0.05, color=SELECT, linewidth=1.5, linestyle='--', alpha=0.7, zorder=2)
ax2.set_xlabel('FDI Threshold', fontsize=13, color=GRAY, fontweight='bold')
ax2.set_ylabel('FDI-Positive Area (km\u00b2)', fontsize=13, color=GRAY, fontweight='bold')
ax2.set_xticks(thresholds)
ax2.legend(fontsize=11.5, framealpha=0.9, loc='upper right')

ax3 = fig.add_subplot(gs[1, 0])
style_ax(ax3, '(C) Cross-Seasonal Detection Consistency (ROC-Style)')
ax3.plot([0, 1], [0, 1], '--', color='#888888', linewidth=1.8, label='Random classifier', zorder=1)
ax3.plot(fp_rate, tp_rate, 'o-', color=LBLUE, linewidth=2.5, markersize=10, zorder=3, label='FDI thresholds 0.03 to 0.08')
for i, (fp, tp, thr) in enumerate(zip(fp_rate, tp_rate, thresholds)):
    if thr == 0.05:
        ax3.scatter([fp], [tp], s=220, color=SELECT, zorder=6, edgecolors='white', linewidth=2.5,
                    label='Selected: 0.05 (Biermann et al. 2020)')
    ax3.annotate(str(i + 1), (fp, tp), ha='center', va='center', fontsize=9.5, fontweight='bold', color='white', zorder=7)
ax3.axvspan(0, 0.02, alpha=0.06, color='green')
ax3.text(0.0015, 0.12, 'High\nspecificity\nregion', fontsize=10, color=GREEN, alpha=0.9)
ax3.set_xlabel('False-Positive Rate (season-B non-confirmation)', fontsize=12, color=GRAY, fontweight='bold')
ax3.set_ylabel('True-Positive Rate (season-B confirmation)', fontsize=12, color=GRAY, fontweight='bold')
ax3.set_xlim(-0.001, max(fp_rate) + 0.006)
ax3.set_ylim(0, 0.75)
ax3.legend(fontsize=10.5, framealpha=0.9, loc='lower right')
key_str = '1=0.03  2=0.04  3=0.05  4=0.06  5=0.07  6=0.08'
ax3.text(0.98, 0.335, 'Number key: ' + key_str, transform=ax3.transAxes, fontsize=8.5, ha='right', va='bottom', color=GRAY, style='italic')

axins = inset_axes(ax3, width='38%', height='38%', loc='upper left', borderpad=2.5)
axins.set_facecolor('white')
cluster_idx = [2, 3, 4, 5]
cluster_fp = [fp_rate[i] for i in cluster_idx]
cluster_tp = [tp_rate[i] for i in cluster_idx]
axins.plot(cluster_fp, cluster_tp, '-', color=LBLUE, linewidth=2, zorder=3)
for i in cluster_idx:
    is_selected = (thresholds[i] == 0.05)
    color = SELECT if is_selected else LBLUE
    size = 160 if is_selected else 140
    axins.scatter([fp_rate[i]], [tp_rate[i]], s=size, color=color, zorder=6, edgecolors='white', linewidth=2)
    axins.annotate(str(i + 1), (fp_rate[i], tp_rate[i]), ha='center', va='center', fontsize=9, fontweight='bold', color='white', zorder=7)
pad_x = (max(cluster_fp) - min(cluster_fp)) * 0.35
pad_y = (max(cluster_tp) - min(cluster_tp)) * 0.35
axins.set_xlim(min(cluster_fp) - pad_x, max(cluster_fp) + pad_x)
axins.set_ylim(min(cluster_tp) - pad_y, max(cluster_tp) + pad_y)
axins.tick_params(labelsize=7)
axins.set_title('Zoom: thresholds 3-6', fontsize=8.5, fontweight='bold', color=GRAY)
for spine in axins.spines.values():
    spine.set_edgecolor('#999999')
    spine.set_linewidth(1)
mark_inset(ax3, axins, loc1=1, loc2=3, fc='none', ec='#999999', linewidth=0.8, alpha=0.6)

ax4 = fig.add_subplot(gs[1, 1])
style_ax(ax4, '(D) Detection Efficiency (TPR / FPR Ratio)')
efficiency = [tp / max(fp, 0.001) for tp, fp in zip(tp_rate, fp_rate)]
bar_colors = [SELECT if t == 0.05 else LBLUE for t in thresholds]
bars = ax4.bar([str(t) for t in thresholds], efficiency, color=bar_colors, edgecolor='white', linewidth=1.5, zorder=4)
for bar, val in zip(bars, efficiency):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(efficiency)*0.02, str(round(val, 1)),
              ha='center', va='bottom', fontsize=12, color=GRAY, fontweight='bold')
ax4.set_xlabel('FDI Threshold', fontsize=13, color=GRAY, fontweight='bold')
ax4.set_ylabel('TPR / FPR (Efficiency Ratio)', fontsize=13, color=GRAY, fontweight='bold')
ax4.set_ylim(0, max(efficiency) * 1.2)
legend_elements = [
    Line2D([0], [0], marker='s', color='w', markerfacecolor=SELECT, markersize=12, label='Selected (0.05)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor=LBLUE, markersize=12, label='Other thresholds'),
]
ax4.legend(handles=legend_elements, fontsize=11.5, framealpha=0.9)

fig.suptitle('FDI Threshold Sensitivity Analysis (Thresholds 0.03\u20130.08)\nCoastal Sentinel | South China Sea and Bay of Bengal',
             fontsize=16, fontweight='bold', color='#0D2D5E', y=0.975)
caption_text = ('Panels A-B: real deep-water-only detection counts and FDI-positive area (bathymetry-masked, '
                'excluding waters <20m depth, to remove shallow-water optical contamination). '
                'Panels C-D: real cross-seasonal consistency analysis. '
                'Threshold 0.05 retained per Biermann et al. (2020), TPR=0.598, FPR=0.011, ratio=55.2.')
fig.text(0.5, 0.025, caption_text, ha='center', fontsize=10, style='italic', color=GRAY, wrap=True)

OP = OUT_DIR + '\\Figure3_FINAL_v9.png'
OT = OUT_DIR + '\\Figure3_FINAL_v9.tiff'
fig.savefig(OP, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
fig.savefig(OT, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print('Saved:', OP)
print('Saved:', OT)
