import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature

BASE = r'E:\COASTAL SENTINEL\CoastalSentinel\Outputs\Results'
HALO = [pe.withStroke(linewidth=2.2, foreground='white')]
proj = ccrs.PlateCarree()
cmap = plt.get_cmap('plasma')
norm = mcolors.Normalize(vmin=0, vmax=72)
TITLE_COLOR = '#0D2D5E'

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dlmb/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

def spread_circle(lon, lat, idx, min_particles=10):
    lo, la = lon[:, idx], lat[:, idx]
    valid = ~np.isnan(lo) & ~np.isnan(la)
    lo, la = lo[valid], la[valid]
    if len(lo) < min_particles:
        return None, None, None, len(lo)
    mlat, mlon = np.mean(la), np.mean(lo)
    d = np.array([haversine_km(mlat, mlon, x, y) for x, y in zip(la, lo)])
    return mlon, mlat, np.std(d), len(lo)

rivers = {
    'SCS': {'Mekong': (106.0, 9.0), 'Pearl River': (113.0, 21.0), 'Red River': (107.0, 19.0)},
    'BoB': {'Ganges-Brahmaputra': (89.1, 21.7), 'Irrawaddy': (95.2, 15.5),
            'Mahanadi': (86.7, 20.3), 'Godavari': (82.3, 16.3)},
}

TARGET_ASPECT = 7.0 / 6.0

def compute_extent(river_dict, base_pad=1.8, target_aspect=TARGET_ASPECT):
    lons = [c[0] for c in river_dict.values()]
    lats = [c[1] for c in river_dict.values()]
    lon_span = max(lons) - min(lons) + 2*base_pad
    lat_span = max(lats) - min(lats) + 2*base_pad
    current_aspect = lon_span / lat_span
    if current_aspect < target_aspect:
        new_lon_span = lat_span * target_aspect
        extra = (new_lon_span - lon_span) / 2
        return [min(lons)-base_pad-extra, max(lons)+base_pad+extra,
                min(lats)-base_pad, max(lats)+base_pad]
    else:
        new_lat_span = lon_span / target_aspect
        extra = (new_lat_span - lat_span) / 2
        return [min(lons)-base_pad, max(lons)+base_pad,
                min(lats)-base_pad-extra, max(lats)+base_pad+extra]

extents = {basin: compute_extent(rivers[basin]) for basin in rivers}

def file_for(basin, river, season):
    safe = river.replace(' ', '_').replace('-', '_')
    tag = 'Drift_SWM_Summer' if season == 'summer' else 'Drift_NEM_Winter'
    return f"{BASE}\\{basin}_{safe}_{tag}.nc"

fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300,
                          subplot_kw={'projection': proj})

panel_map = {(0, 0): ('SCS', 'winter'), (0, 1): ('SCS', 'summer'),
             (1, 0): ('BoB', 'winter'), (1, 1): ('BoB', 'summer')}

for (r, c), (basin, season) in panel_map.items():
    ax = axes[r, c]
    ext = extents[basin]
    ax.set_extent(ext, crs=proj)
    ax.set_aspect('auto')

    ax.add_feature(cfeature.OCEAN, facecolor='#eaf3f8', zorder=0)
    # Natural soft green land color, replacing the cream/tan that read as "brown"
    ax.add_feature(cfeature.LAND, facecolor='#D9E8D3', edgecolor='none', zorder=3)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='#5a5a5a', zorder=4)
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='#cccccc', linestyle='--', zorder=1)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 7}
    gl.ylabel_style = {'size': 7}

    season_label = 'NE Monsoon (Winter)' if season == 'winter' else 'SW Monsoon (Summer)'
    # Single consistent title color for all panels, not season-coded
    ax.set_title(f'{basin} \u2014 {season_label}', fontsize=12, fontweight='bold', color=TITLE_COLOR)

    stranded_notes = []
    any_river_checked = False
    for river, (rlon, rlat) in rivers[basin].items():
        fpath = file_for(basin, river, season)
        try:
            ds = xr.open_dataset(fpath)
        except Exception as e:
            print(f"MISSING/FAILED: {fpath} ({e})")
            continue
        any_river_checked = True
        lon = ds['lon'].values
        lat = ds['lat'].values
        n_particles, n_steps = lon.shape

        # Path lines made much more prominent - thicker and more opaque,
        # so the actual trajectory shape reads clearly, not just a dot cloud
        for p in range(n_particles):
            lo_p, la_p = lon[p, :], lat[p, :]
            valid = ~np.isnan(lo_p) & ~np.isnan(la_p)
            if valid.sum() < 2:
                continue
            ax.plot(lo_p[valid], la_p[valid], color='#555555', linewidth=0.9,
                    alpha=0.55, transform=proj, zorder=4)

        # Time-progression dots made smaller and lighter, so they accent
        # the paths rather than visually overpowering them
        for t in range(n_steps):
            lo, la = lon[:, t], lat[:, t]
            valid = ~np.isnan(lo) & ~np.isnan(la)
            if valid.sum() == 0:
                continue
            ax.scatter(lo[valid], la[valid], c=np.full(int(valid.sum()), t), cmap=cmap, norm=norm,
                       s=5, alpha=0.75, edgecolors='none', transform=proj, zorder=5)

        final_idx = min(70, n_steps - 1)
        mlon, mlat, r_km, n_surv = spread_circle(lon, lat, final_idx)
        if mlon is not None:
            r_deg = r_km / 111.0
            ax.add_patch(mpatches.Circle((mlon, mlat), r_deg, facecolor='#c1332e', alpha=0.15,
                         edgecolor='#c1332e', linewidth=1.8, transform=proj, zorder=6))

        ax.plot(rlon, rlat, marker='*', markersize=11, color='#222222',
                markeredgecolor='white', markeredgewidth=0.8, transform=proj, zorder=7)
        t_label = ax.text(rlon, rlat, f'  {river}', fontsize=7.5, color='#222222',
                           transform=proj, zorder=7, va='center')
        t_label.set_path_effects(HALO)

        n_final = int(np.sum(~np.isnan(lon[:, final_idx])))
        pct_stranded = round((1 - n_final / n_particles) * 100)
        if pct_stranded >= 40:
            note = f"{river}: {pct_stranded}% stranded"
            if n_final < 10:
                note += " (n too low)"
            stranded_notes.append(note)

    if not stranded_notes and any_river_checked:
        stranded_notes.append('No significant stranding (<40%)')

    if stranded_notes:
        ax.text(0.03, 0.03, '\n'.join(stranded_notes), transform=ax.transAxes, fontsize=6.8,
                color='#5a3d99', va='bottom', ha='left', zorder=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9,
                          edgecolor='#5a3d99', linewidth=0.6))

fig.suptitle('Ensemble Lagrangian Drift Trajectories \u2014 Real Winter (NEM) and Summer (SWM) Simulations',
             fontsize=15, fontweight='bold', y=0.995, color=TITLE_COLOR)

legend_elements = [
    plt.Line2D([0], [0], color='#555555', linewidth=1.5, alpha=0.7, label='Particle path'),
    plt.Line2D([0], [0], marker='o', color='none', markerfacecolor='#c1332e', alpha=0.4,
               markersize=10, label='Spread radius @ 72h'),
    plt.Line2D([0], [0], marker='*', color='none', markerfacecolor='#222222',
               markeredgecolor='white', markersize=9, label='River mouth'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=10,
           bbox_to_anchor=(0.5, 0.06))

fig.tight_layout(rect=[0, 0.12, 1, 0.96])

cax = fig.add_axes([0.32, 0.035, 0.36, 0.016])
sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
cb = fig.colorbar(sm, cax=cax, orientation='horizontal')
cb.set_label('Time elapsed (hours)', fontsize=9.5, labelpad=6)

out_path = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes\Figure6_v5_Final.png'
out_tiff = r'E:\COASTAL SENTINEL\CoastalSentinel\_verified_updates\Figures_HighRes\Figure6_v5_Final.tiff'
fig.savefig(out_path, dpi=600, facecolor='white', bbox_inches='tight')
fig.savefig(out_tiff, dpi=600, facecolor='white', bbox_inches='tight')
print(f"\nSaved: {out_path}")
print(f"Saved: {out_tiff}")
