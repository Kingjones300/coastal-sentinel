import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter
import warnings
warnings.filterwarnings("ignore")

RD = "C:/CoastalSentinel/Outputs/Results"
FD = "C:/CoastalSentinel/Outputs/Figures"

SCS_RIVERS = ["SCS_Mekong_Drift.nc", "SCS_Pearl_River_Drift.nc", "SCS_Red_River_Drift.nc"]
BOB_RIVERS = ["BoB_Ganges_Brahmaputra_Drift.nc", "BoB_Irrawaddy_Drift.nc",
              "BoB_Mahanadi_Drift.nc", "BoB_Godavari_Drift.nc"]

SCS_PTS = {
    "Mekong": (106.0, 9.6),
    "Pearl River": (113.6, 22.1),
    "Red River": (106.5, 20.3),
}
BOB_PTS = {
    "Ganges": (89.1, 21.8),
    "Irrawaddy": (95.2, 15.8),
    "Mahanadi": (86.8, 19.9),
    "Godavari": (82.0, 16.3),
}

NAVY = "#0D2D5E"
GOLD = "#C9A84C"
GRAY = "#444444"
LAND = "#E8DCC8"
COAST = "#555555"

print("Building SCS accumulation grid...")
scs_lons = np.arange(99, 122, 0.1)
scs_lats = np.arange(1, 25, 0.1)
scs_acc = np.zeros((len(scs_lats), len(scs_lons)))

for fname in SCS_RIVERS:
    fpath = RD + "/" + fname
    try:
        ds = xr.open_dataset(fpath)
        lo = ds["lon"].values.flatten()
        la = ds["lat"].values.flatten()
        ds.close()
        for lon_v, lat_v in zip(lo, la):
            if not np.isnan(lon_v) and not np.isnan(lat_v):
                li = int((lon_v - 99) / 0.1)
                ai = int((lat_v - 1) / 0.1)
                if 0 <= li < len(scs_lons) and 0 <= ai < len(scs_lats):
                    scs_acc[ai, li] += 1
        print("Loaded " + fname)
    except Exception as e:
        print("Could not load " + fname + ": " + str(e))

scs_smooth = gaussian_filter(scs_acc, sigma=3)

print("Building BoB accumulation grid...")
bob_lons = np.arange(79, 100, 0.1)
bob_lats = np.arange(5, 23, 0.1)
bob_acc = np.zeros((len(bob_lats), len(bob_lons)))

for fname in BOB_RIVERS:
    fpath = RD + "/" + fname
    try:
        ds = xr.open_dataset(fpath)
        lo = ds["lon"].values.flatten()
        la = ds["lat"].values.flatten()
        ds.close()
        for lon_v, lat_v in zip(lo, la):
            if not np.isnan(lon_v) and not np.isnan(lat_v):
                li = int((lon_v - 79) / 0.1)
                ai = int((lat_v - 5) / 0.1)
                if 0 <= li < len(bob_lons) and 0 <= ai < len(bob_lats):
                    bob_acc[ai, li] += 1
        print("Loaded " + fname)
    except Exception as e:
        print("Could not load " + fname + ": " + str(e))

bob_smooth = gaussian_filter(bob_acc, sigma=3)

print("Building figure...")

PR = ccrs.PlateCarree()
fig = plt.figure(figsize=(18, 9), facecolor="white")

fig.text(0.5, 0.97,
         "Composite Debris Risk Maps - South China Sea and Bay of Bengal",
         ha="center", fontsize=13, fontweight="bold", color=NAVY)
fig.text(0.5, 0.945,
         "Drift accumulation probability from all river mouth sources (2019-2023)",
         ha="center", fontsize=9, color=GRAY)

ax1 = fig.add_axes([0.05, 0.08, 0.42, 0.82], projection=PR)
ax2 = fig.add_axes([0.53, 0.08, 0.42, 0.82], projection=PR)

def style_panel(ax, ext, title):
    ax.set_extent(ext, crs=PR)
    ax.add_feature(cfeature.LAND, facecolor=LAND, zorder=1)
    ax.add_feature(cfeature.OCEAN, facecolor="#C8DCF0", zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.7, edgecolor=COAST, zorder=4)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor=COAST, zorder=4)
    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color="gray",
                      alpha=0.5, zorder=2)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 8, "color": GRAY}
    gl.ylabel_style = {"size": 8, "color": GRAY}
    ax.set_title(title, fontsize=11, fontweight="bold", color=NAVY, pad=6)

def add_risk(ax, lons, lats, data, ext):
    levels = np.linspace(0, data.max(), 12)
    if data.max() == 0:
        levels = np.linspace(0, 1, 12)
    cf = ax.contourf(lons, lats, data,
                     levels=levels,
                     cmap="RdYlGn_r",
                     alpha=0.75,
                     transform=PR,
                     zorder=2)
    return cf

def add_stars(ax, pts):
    for name in pts:
        rlo = pts[name][0]
        rla = pts[name][1]
        ax.plot(rlo, rla, "*", markersize=11, color=GOLD,
                markeredgecolor=NAVY, markeredgewidth=0.7,
                transform=PR, zorder=6)
        ax.text(rlo+0.3, rla+0.3, name, fontsize=7.5,
                color=NAVY, fontweight="bold",
                transform=PR, zorder=7,
                bbox=dict(facecolor="white", alpha=0.65,
                          edgecolor="none", pad=1.5))

style_panel(ax1, [99, 122, 1, 24], "South China Sea - Composite Risk Map")
cf1 = add_risk(ax1, scs_lons, scs_lats, scs_smooth, [99, 122, 1, 24])
add_stars(ax1, SCS_PTS)

ax1.text(0.02, 0.04, "HIGH RISK", transform=ax1.transAxes,
         fontsize=8, fontweight="bold", color="#B71C1C",
         bbox=dict(facecolor="white", alpha=0.8, edgecolor="#B71C1C", pad=3))

cb1_ax = fig.add_axes([0.05, 0.04, 0.42, 0.018])
norm1 = mcolors.Normalize(vmin=0, vmax=scs_smooth.max() if scs_smooth.max() > 0 else 1)
sm1 = plt.cm.ScalarMappable(cmap="RdYlGn_r", norm=norm1)
sm1.set_array([])
cb1 = fig.colorbar(sm1, cax=cb1_ax, orientation="horizontal")
cb1.set_label("Debris Accumulation Risk (Low to High)", fontsize=8, color=GRAY)
cb1.ax.tick_params(labelsize=7)

style_panel(ax2, [79, 100, 5, 23], "Bay of Bengal - Composite Risk Map")
cf2 = add_risk(ax2, bob_lons, bob_lats, bob_smooth, [79, 100, 5, 23])
add_stars(ax2, BOB_PTS)

ax2.text(0.02, 0.04, "HIGH RISK", transform=ax2.transAxes,
         fontsize=8, fontweight="bold", color="#B71C1C",
         bbox=dict(facecolor="white", alpha=0.8, edgecolor="#B71C1C", pad=3))

cb2_ax = fig.add_axes([0.53, 0.04, 0.42, 0.018])
norm2 = mcolors.Normalize(vmin=0, vmax=bob_smooth.max() if bob_smooth.max() > 0 else 1)
sm2 = plt.cm.ScalarMappable(cmap="RdYlGn_r", norm=norm2)
sm2.set_array([])
cb2 = fig.colorbar(sm2, cax=cb2_ax, orientation="horizontal")
cb2.set_label("Debris Accumulation Risk (Low to High)", fontsize=8, color=GRAY)
cb2.ax.tick_params(labelsize=7)

OP = FD + "/Figure6_CompositeRiskMaps_FINAL.png"
OT = FD + "/Figure6_CompositeRiskMaps_FINAL.tiff"

print("Saving...")
plt.savefig(OP, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.savefig(OT, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.close()

print("DONE")
print("PNG  -> " + OP)
print("TIFF -> " + OT)
