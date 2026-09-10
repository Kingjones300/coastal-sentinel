import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

OUT_DIR = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes'

FULL_EXT = [78, 124, -1, 26]
NAVY = '#0D2D5E'
GRAY = '#222222'

SCS_RIVERS = [
    ('Mekong', 10.00, 106.75),
    ('Pearl River', 22.10, 113.60),
    ('Red River', 20.30, 106.50),
]
BOB_RIVERS = [
    ('Ganges-Brahmaputra', 21.70, 89.10),
    ('Irrawaddy', 15.50, 95.20),
    ('Mahanadi', 20.30, 86.70),
    ('Godavari', 16.30, 82.30),
]

CITIES = [
    ('Hanoi', 21.03, 105.85, (8, -14)),
    ('Bangkok', 13.75, 100.50, (7, 7)),
    ('Manila', 14.60, 120.98, (7, 7)),
    ('Hong Kong', 22.32, 114.17, (7, -14)),
    ('Singapore', 1.35, 103.82, (7, 7)),
    ('Yangon', 16.87, 96.20, (7, 7)),
    ('Kolkata', 22.57, 88.36, (-10, 10)),
    ('Chennai', 13.08, 80.27, (7, 7)),
    ('Colombo', 6.93, 79.85, (7, 7)),
    ('Dhaka', 23.81, 90.41, (7, 7)),
    ('Andaman Islands', 11.70, 92.60, (7, 7)),
]

class EsriImagery(cimgt.GoogleTiles):
    def _image_url(self, tile):
        x, y, z = tile
        return (f'https://server.arcgisonline.com/ArcGIS/rest/services/'
                f'World_Imagery/MapServer/tile/{z}/{y}/{x}')

tiler = EsriImagery()
proj = tiler.crs

fig = plt.figure(figsize=(18, 10), facecolor='white')
ax = fig.add_axes([0.03, 0.14, 0.94, 0.72], projection=proj)
ax.set_extent(FULL_EXT, crs=ccrs.PlateCarree())
ax.add_image(tiler, 6)

ax.add_patch(plt.Rectangle((FULL_EXT[0], FULL_EXT[2]), FULL_EXT[1]-FULL_EXT[0], FULL_EXT[3]-FULL_EXT[2],
                            fill=False, edgecolor='#FF3333', linewidth=3.0,
                            transform=ccrs.PlateCarree(), zorder=5))

ax.text(114.5, 11, 'SOUTH CHINA SEA', fontsize=17, fontweight='bold', color='white',
        style='italic', ha='center', transform=ccrs.PlateCarree(), zorder=6,
        path_effects=[pe.withStroke(linewidth=3, foreground=NAVY)])
ax.text(88.5, 13, 'BAY OF BENGAL', fontsize=17, fontweight='bold', color='white',
        style='italic', ha='center', transform=ccrs.PlateCarree(), zorder=6,
        path_effects=[pe.withStroke(linewidth=3, foreground=NAVY)])

def plot_rivers(rivers, marker):
    for name, lat, lon in rivers:
        ax.plot(lon, lat, marker=marker, markersize=15, color='#FFD700',
                markeredgecolor='black', markeredgewidth=1.4,
                transform=ccrs.PlateCarree(), zorder=8)
        ax.annotate(name, (lon, lat), xytext=(7, 7), textcoords='offset points',
                    fontsize=10, fontweight='bold', color='white',
                    bbox=dict(facecolor=NAVY, alpha=0.92, pad=2.8, edgecolor='white',
                              linewidth=0.7, boxstyle='round,pad=0.3'),
                    transform=ccrs.PlateCarree(), zorder=9)

plot_rivers(SCS_RIVERS, 'o')
plot_rivers(BOB_RIVERS, '^')

for name, lat, lon, offset in CITIES:
    ax.plot(lon, lat, marker='s', markersize=5, color='white',
            markeredgecolor='black', markeredgewidth=0.7,
            transform=ccrs.PlateCarree(), zorder=8)
    ax.annotate(name, (lon, lat), xytext=offset, textcoords='offset points',
                fontsize=8.5, fontweight='bold', color='white', style='italic',
                transform=ccrs.PlateCarree(), zorder=9,
                path_effects=[pe.withStroke(linewidth=2.0, foreground='black')])

gl = ax.gridlines(draw_labels=True, linewidth=0.4, color='white', alpha=0.5,
                   linestyle='--', xlocs=range(-180, 180, 5), ylocs=range(-90, 90, 5))
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 12, 'weight': 'bold', 'color': 'black'}
gl.ylabel_style = {'size': 12, 'weight': 'bold', 'color': 'black'}

compass_ax = fig.add_axes([0.06, 0.78, 0.05, 0.12])
compass_ax.axis('off')
compass_ax.annotate('N', xy=(0.5, 0.85), fontsize=14, fontweight='bold', ha='center', color=NAVY)
compass_ax.annotate('', xy=(0.5, 0.78), xytext=(0.5, 0.15),
                     arrowprops=dict(facecolor=NAVY, edgecolor=NAVY, width=4, headwidth=14))

scale_ax = fig.add_axes([0.72, 0.055, 0.20, 0.025])
scale_ax.axis('off')
scale_ax.set_xlim(0, 1)
scale_ax.set_ylim(0, 1)
scale_ax.plot([0, 1], [0.5, 0.5], color='black', linewidth=2)
for x in [0, 0.5, 1]:
    scale_ax.plot([x, x], [0.25, 0.75], color='black', linewidth=2)
scale_ax.text(0, 1.1, '0', fontsize=9, ha='center')
scale_ax.text(0.5, 1.1, '250', fontsize=9, ha='center')
scale_ax.text(1, 1.1, '500 km', fontsize=9, ha='center')

legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFD700', markeredgecolor='black',
           markersize=13, label='SCS river mouth source'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor='#FFD700', markeredgecolor='black',
           markersize=13, label='BoB river mouth source'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='white', markeredgecolor='black',
           markersize=8, label='Reference city'),
    Line2D([0], [0], color='#FF3333', linewidth=3.0, label='Study domain boundary'),
]
leg = fig.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 0.005),
                  ncol=4, fontsize=11, frameon=True, facecolor='white', edgecolor=GRAY,
                  handletextpad=1.0, columnspacing=1.6)
leg.get_frame().set_linewidth(1.2)

fig.suptitle('Study Domain and River Mouth Source Locations',
             fontsize=19, fontweight='bold', color=NAVY, y=0.965)
fig.text(0.5, 0.90, 'South China Sea and Bay of Bengal, 2019\u20132023 study period',
         ha='center', fontsize=13, style='italic', color=GRAY)

OP = OUT_DIR + '\\Figure2_StudyDomain_v9.png'
OT = OUT_DIR + '\\Figure2_StudyDomain_v9.tiff'
fig.savefig(OP, dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OT, dpi=600, bbox_inches='tight', facecolor='white')
plt.close()
print(f'Saved: {OP}')
print(f'Saved: {OT}')
