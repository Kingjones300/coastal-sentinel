import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors

FIG2 = r'E:\COASTAL SENTINEL\CoastalSentinel\Fig2'
OUT_DIR = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes'

PANELS = [
    ('a', 'South China Sea - NE Monsoon (Jan-Mar 2021)', 'Fig2a_SCS_NE_Monsoon_CORRECTED.tif'),
    ('b', 'South China Sea - SW Monsoon (Jun-Aug 2021)', 'Fig2b_SCS_SW_Monsoon_CORRECTED.tif'),
    ('c', 'Bay of Bengal - NE Monsoon (Jan-Mar 2021)', 'Fig2c_BoB_NE_Monsoon_CORRECTED.tif'),
    ('d', 'Bay of Bengal - SW Monsoon (Jun-Aug 2021)', 'Fig2d_BoB_SW_Monsoon_CORRECTED.tif'),
]

NAVY = '#0D2D5E'
GRAY = '#333333'

fig = plt.figure(figsize=(15, 12), facecolor='white')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.32, wspace=0.22,
                        left=0.06, right=0.95, top=0.87, bottom=0.10)

# Original color range restored (this is what looked right before)
vmin, vmax = -0.1, 0.3
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
cmap = plt.get_cmap('RdYlBu_r').copy()
cmap.set_bad(color='#F2F2EF')  # clean neutral gray for masked/land pixels

print('Building Figure 4')
for i, (letter, title, fname) in enumerate(PANELS):
    ax = fig.add_subplot(gs[i // 2, i % 2])
    with rasterio.open(FIG2 + '\\' + fname) as ds:
        data = ds.read(1).astype(float)
        data[data < -1e5] = np.nan
        bounds = ds.bounds
    im = ax.imshow(data, cmap=cmap, norm=norm,
                   extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
                   origin='upper', aspect='auto')
    ax.set_title('(' + letter + ') ' + title, fontsize=13, fontweight='bold', color=NAVY, pad=10)
    ax.set_xlabel('Longitude', fontsize=12, color=GRAY, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, color=GRAY, fontweight='bold')
    ax.tick_params(labelsize=11, colors=GRAY)
    print('Panel ' + letter + ': real mean FDI = ' + str(round(np.nanmean(data), 5)))

# Horizontal colorbar, same layout as the version that looked right
cbar_ax = fig.add_axes([0.28, 0.035, 0.44, 0.02])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
# Single combined label line, with enough padding to clear the tick numbers below it
cbar.set_label('Floating Debris Index (FDI)  \u2014  Higher values indicate greater debris signal',
                fontsize=11.5, color=GRAY, fontweight='bold', labelpad=10)
cbar.ax.tick_params(labelsize=11)

fig.suptitle('Representative FDI Detection Maps: SCS and BoB Seasonal Hotspot Distribution',
             fontsize=15, fontweight='bold', color=NAVY, y=0.965)
fig.text(0.5, 0.915, 'Selected threshold: FDI > 0.05',
          ha='center', fontsize=11.5, color=NAVY, fontweight='bold', style='italic')

OP = OUT_DIR + '\\Figure4_FDIDetectionMaps.png'
OT = OUT_DIR + '\\Figure4_FDIDetectionMaps.tiff'
fig.savefig(OP, dpi=600, bbox_inches='tight', facecolor='white')
fig.savefig(OT, dpi=600, bbox_inches='tight', facecolor='white')
plt.close()
print('Saved: ' + OP)
print('Saved: ' + OT)
