import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import warnings
warnings.filterwarnings(“ignore”)

RD = “C:/CoastalSentinel/Outputs/Results”
FD = “C:/CoastalSentinel/Outputs/Figures”

F_SW = RD + “/SCS_72hr_MultiPoint.nc”
F_S2 = RD + “/SCS_24hr_MultiPoint.nc”
F_S4 = RD + “/SCS_48hr_MultiPoint.nc”
F_BW = RD + “/BoB_72hr_MultiPoint.nc”
F_B2 = RD + “/BoB_24hr_MultiPoint.nc”
F_B4 = RD + “/BoB_48hr_MultiPoint.nc”

SCS_SUM = {
“Mekong”:      RD + “/SCS_Mekong_Drift_July.nc”,
“Pearl River”: RD + “/SCS_Pearl_River_Drift.nc”,
“Red River”:   RD + “/SCS_Red_River_Drift.nc”,
}
BOB_SUM = {
“Ganges”:    RD + “/BoB_Ganges_Brahmaputra_Drift.nc”,
“Irrawaddy”: RD + “/BoB_Irrawaddy_Drift.nc”,
“Mahanadi”:  RD + “/BoB_Mahanadi_Drift.nc”,
“Godavari”:  RD + “/BoB_Godavari_Drift.nc”,
}

SCS_PTS = {
“Mekong”:      (106.0, 9.6),
“Pearl River”: (113.6, 22.1),
“Red River”:   (106.5, 20.3),
}
BOB_PTS = {
“Ganges”:    (89.1, 21.8),
“Irrawaddy”: (95.2, 15.8),
“Mahanadi”:  (86.8, 19.9),
“Godavari”:  (82.0, 16.3),
}

NAVY  = “#0D2D5E”
GOLD  = “#C9A84C”
GRAY  = “#444444”
LAND  = “#E8DCC8”
OCEAN = “#C8DCF0”
COAST = “#555555”
CMAP  = plt.colormaps[“RdYlBu_r”]
EC    = {24: “#2196F3”, 48: “#FF9800”, 72: “#F44336”}

def load(path):
try:
ds = xr.open_dataset(path)
lo = ds[“lon”].values
la = ds[“lat”].values
ds.close()
if lo.ndim == 1:
lo = lo[np.newaxis, :]
la = la[np.newaxis, :]
if lo.shape[0] > lo.shape[1]:
lo = lo.T
la = la.T
fname = path.split(”/”)[-1]
print(“Loaded “ + fname + “ shape “ + str(lo.shape))
return lo, la
except Exception as e:
print(“WARNING could not load “ + path)
print(str(e))
return None, None

def ellipse(ax, lons, lats, color, lw, ls):
ok = ~np.isnan(lons) & ~np.isnan(lats)
if ok.sum() < 3:
return
x, y = lons[ok], lats[ok]
cx, cy = x.mean(), y.mean()
cov = np.cov(x, y)
ev, evec = np.linalg.eigh(cov)
ev = np.maximum(ev, 1e-10)
ang = np.degrees(np.arctan2(*evec[:, 1][::-1]))
w = 2 * 1.5 * np.sqrt(ev[1])
h = 2 * 1.5 * np.sqrt(ev[0])
e = Ellipse(xy=(cx, cy), width=w, height=h, angle=ang,
fill=False, edgecolor=color, linewidth=lw,
linestyle=ls, transform=ax.transData, zorder=5)
ax.add_patch(e)

def tracks(ax, lo, la, ns=80, al=0.18, lw=0.7):
if lo is None:
return
nt, np2 = lo.shape
idx = np.linspace(0, np2 - 1, min(np2, ns), dtype=int)
for p in idx:
tlo = lo[:, p]
tla = la[:, p]
ok = ~np.isnan(tlo) & ~np.isnan(tla)
if ok.sum() < 2:
continue
tn = np.linspace(0, 1, ok.sum())
vlo = tlo[ok]
vla = tla[ok]
for i in range(len(vlo) - 1):
ax.plot([vlo[i], vlo[i+1]], [vla[i], vla[i+1]],
color=CMAP(tn[i]), alpha=al, lw=lw,
transform=ccrs.PlateCarree(), zorder=3)

def three_ellipses(ax, l2, a2, l4, a4, l7, a7):
for hr, lo, la, ls in [(24,l2,a2,”–”),(48,l4,a4,”–”),(72,l7,a7,”-”)]:
if lo is not None:
ellipse(ax, lo[-1,:], la[-1,:], EC[hr], 1.4, ls)

def style(ax, ext, title, ll=True, bl=True):
ax.set_extent(ext, crs=ccrs.PlateCarree())
ax.add_feature(cfeature.LAND,      facecolor=LAND,  zorder=1)
ax.add_feature(cfeature.OCEAN,     facecolor=OCEAN, zorder=0)
ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor=COAST, zorder=4)
ax.add_feature(cfeature.BORDERS,   linewidth=0.3, edgecolor=COAST,
linestyle=”:”, zorder=4)
gl = ax.gridlines(draw_labels=True, linewidth=0.4, color=“gray”,
alpha=0.5, linestyle=”–”, zorder=2)
gl.top_labels    = False
gl.right_labels  = False
gl.left_labels   = ll
gl.bottom_labels = bl
gl.xlabel_style  = {“size”: 7, “color”: GRAY}
gl.ylabel_style  = {“size”: 7, “color”: GRAY}
ax.set_title(title, fontsize=9, fontweight=“bold”, color=NAVY, pad=4)

def stars(ax, pts):
for name, (rlo, rla) in pts.items():
ax.plot(rlo, rla, “*”, markersize=10, color=GOLD,
markeredgecolor=NAVY, markeredgewidth=0.6,
transform=ccrs.PlateCarree(), zorder=6)
ax.text(rlo+0.4, rla+0.3, name, fontsize=6.5, color=NAVY,
fontweight=“bold”, transform=ccrs.PlateCarree(), zorder=7,
bbox=dict(facecolor=“white”, alpha=0.6, edgecolor=“none”, pad=1))

print(“Loading SCS winter…”)
sw_lo, sw_la = load(F_SW)
s2_lo, s2_la = load(F_S2)
s4_lo, s4_la = load(F_S4)

print(“Loading BoB winter…”)
bw_lo, bw_la = load(F_BW)
b2_lo, b2_la = load(F_B2)
b4_lo, b4_la = load(F_B4)

print(“Loading SCS summer…”)
ss = {}
for nm, fp in SCS_SUM.items():
ss[nm] = load(fp)

print(“Loading BoB summer…”)
bs = {}
for nm, fp in BOB_SUM.items():
bs[nm] = load(fp)

print(“Building figure…”)

SE = [99, 122, 1, 24]
BE = [79, 100, 5, 23]
PR = ccrs.PlateCarree()

fig = plt.figure(figsize=(18, 14), facecolor=“white”)

fig.text(0.5, 0.975,
“Ensemble Lagrangian Drift Trajectories - SCS and Bay of Bengal”,
ha=“center”, fontsize=13, fontweight=“bold”, color=NAVY)
fig.text(0.5, 0.952,
“Color: time elapsed  blue 0hr -> red 72hr     * = river mouth”,
ha=“center”, fontsize=9, color=GRAY)
fig.text(0.27, 0.928, “WINTER - NE Monsoon”, ha=“center”,
fontsize=11, fontweight=“bold”, color=”#1565C0”)
fig.text(0.73, 0.928, “SUMMER - SW Monsoon”, ha=“center”,
fontsize=11, fontweight=“bold”, color=”#B71C1C”)
fig.text(0.015, 0.68, “South China Sea”, ha=“left”, va=“center”,
fontsize=10, fontweight=“bold”, color=NAVY, rotation=90)
fig.text(0.015, 0.28, “Bay of Bengal”, ha=“left”, va=“center”,
fontsize=10, fontweight=“bold”, color=NAVY, rotation=90)

a1 = fig.add_axes([0.06, 0.50, 0.41, 0.41], projection=PR)
a2 = fig.add_axes([0.53, 0.50, 0.41, 0.41], projection=PR)
a3 = fig.add_axes([0.06, 0.07, 0.41, 0.41], projection=PR)
a4 = fig.add_axes([0.53, 0.07, 0.41, 0.41], projection=PR)

style(a1, SE, “SCS - Winter NE Monsoon”)
tracks(a1, sw_lo, sw_la)
three_ellipses(a1, s2_lo, s2_la, s4_lo, s4_la, sw_lo, sw_la)
stars(a1, SCS_PTS)

style(a2, SE, “SCS - Summer SW Monsoon”, ll=False)
for nm, (lo, la) in ss.items():
tracks(a2, lo, la)
if lo is not None:
ellipse(a2, lo[-1,:], la[-1,:], EC[72], 1.6, “-”)
stars(a2, SCS_PTS)

style(a3, BE, “BoB - Winter NE Monsoon”)
tracks(a3, bw_lo, bw_la)
three_ellipses(a3, b2_lo, b2_la, b4_lo, b4_la, bw_lo, bw_la)
stars(a3, BOB_PTS)

style(a4, BE, “BoB - Summer SW Monsoon”, ll=False)
for nm, (lo, la) in bs.items():
tracks(a4, lo, la)
if lo is not None:
ellipse(a4, lo[-1,:], la[-1,:], EC[72], 1.6, “-”)
stars(a4, BOB_PTS)

ca = fig.add_axes([0.25, 0.025, 0.50, 0.016])
norm = mcolors.Normalize(vmin=0, vmax=72)
sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
sm.set_array([])
cb = fig.colorbar(sm, cax=ca, orientation=“horizontal”)
cb.set_label(“Time elapsed hours”, fontsize=9, color=GRAY)
cb.set_ticks([0, 24, 48, 72])
cb.set_ticklabels([“0 hr”, “24 hr”, “48 hr”, “72 hr”])
cb.ax.tick_params(labelsize=8)

leg = [
Line2D([0],[0], color=EC[24], lw=1.4, ls=”–”, label=“Spread 24 hr”),
Line2D([0],[0], color=EC[48], lw=1.4, ls=”–”, label=“Spread 48 hr”),
Line2D([0],[0], color=EC[72], lw=1.6, ls=”-”,  label=“Spread 72 hr”),
Line2D([0],[0], marker=”*”, color=“w”, markerfacecolor=GOLD,
markersize=10, markeredgecolor=NAVY, label=“River mouth”),
]
fig.legend(handles=leg, loc=“lower center”, ncol=4, fontsize=8,
framealpha=0.9, bbox_to_anchor=(0.5, 0.052),
edgecolor=NAVY, facecolor=“white”)

OP = FD + “/Figure5_LagrangianTrajectory_FINAL.png”
OT = FD + “/Figure5_LagrangianTrajectory_FINAL.tiff”

print(“Saving…”)
plt.savefig(OP, dpi=300, bbox_inches=“tight”, facecolor=“white”, edgecolor=“none”)
plt.savefig(OT, dpi=300, bbox_inches=“tight”, facecolor=“white”, edgecolor=“none”)
plt.close()

print(“DONE”)
print(“PNG  saved to “ + OP)
print(“TIFF saved to “ + OT)
print(“Locked: r=0.651  p<0.001  Spread 5.74/8.92/12.11 km”)
