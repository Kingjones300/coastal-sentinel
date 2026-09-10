import numpy as np
import xarray as xr
import rasterio
from scipy.ndimage import gaussian_filter
from scipy.interpolate import RegularGridInterpolator
import cartopy.io.shapereader as shpreader
from shapely.geometry import LineString

RD = r'E:\COASTAL SENTINEL\CoastalSentinel\Outputs\Results'
DATA = r'E:\COASTAL SENTINEL\CoastalSentinel\Data'
FIG2 = r'E:\COASTAL SENTINEL\CoastalSentinel\Fig2'

def classify_risk(R):
    return np.where(R >= 0.67, "HIGH", np.where(R >= 0.33, "MEDIUM", "LOW"))

def compute_risk_index(fdi_freq, hydro_exposure, drift_arrival):
    return (fdi_freq + hydro_exposure + drift_arrival) / 3.0

BASINS = {
    'SCS': {
        'ext': [99, 122, 1, 24],
        'fdi_files': ['Fig2a_SCS_NE_Monsoon_CORRECTED.tif', 'Fig2b_SCS_SW_Monsoon_CORRECTED.tif'],
        'current_file': DATA + r'\Ocean_Currents\SCS\SCS_Ocean_Currents_2019_2023.nc',
        'drift_files': ['SCS_Mekong_Drift.nc', 'SCS_Pearl_River_Drift.nc', 'SCS_Red_River_Drift.nc'],
    },
    'BoB': {
        'ext': [79, 100, 5, 23],
        'fdi_files': ['Fig2c_BoB_NE_Monsoon_CORRECTED.tif', 'Fig2d_BoB_SW_Monsoon_CORRECTED.tif'],
        'current_file': DATA + r'\Ocean_Currents\BoB\BoB_Ocean_Currents_2019_2023.nc',
        'drift_files': ['BoB_Ganges_Brahmaputra_Drift.nc', 'BoB_Irrawaddy_Drift.nc',
                         'BoB_Mahanadi_Drift.nc', 'BoB_Godavari_Drift.nc'],
    },
}

GRID_STEP = 0.1

def normalize01(arr):
    valid = arr[np.isfinite(arr)]
    lo, hi = np.nanpercentile(valid, 2), np.nanpercentile(valid, 98)
    out = (arr - lo) / (hi - lo)
    return np.clip(out, 0, 1)

def load_fdi_on_grid(fdi_files, lons, lats):
    LON, LAT = np.meshgrid(lons, lats)
    stack = []
    for fname in fdi_files:
        with rasterio.open(FIG2 + '\\' + fname) as ds:
            band = ds.read(1).astype(float)
            band[band < -1e5] = np.nan
            src_h, src_w = band.shape
            src_lons = np.linspace(ds.bounds.left, ds.bounds.right, src_w)
            src_lats = np.linspace(ds.bounds.top, ds.bounds.bottom, src_h)
            interp = RegularGridInterpolator((src_lats, src_lons), band,
                                              bounds_error=False, fill_value=np.nan)
            pts = np.column_stack([LAT.ravel(), LON.ravel()])
            resampled = interp(pts).reshape(LAT.shape)
            stack.append(resampled)
            print(f'  Regridded {fname}')
    return np.nanmean(np.stack(stack), axis=0)

def load_current_on_grid(current_file, lons, lats):
    ds = xr.open_dataset(current_file)
    u = ds['uo'].isel(depth=0).mean(dim='time').values
    v = ds['vo'].isel(depth=0).mean(dim='time').values
    speed = np.sqrt(u**2 + v**2)
    src_lons = ds['longitude'].values
    src_lats = ds['latitude'].values
    interp = RegularGridInterpolator((src_lats, src_lons), speed,
                                      bounds_error=False, fill_value=np.nan)
    LON, LAT = np.meshgrid(lons, lats)
    pts = np.column_stack([LAT.ravel(), LON.ravel()])
    return interp(pts).reshape(LAT.shape)

def build_drift_grid(drift_files, lons, lats, ext):
    acc = np.zeros((len(lats), len(lons)))
    for fname in drift_files:
        try:
            ds = xr.open_dataset(RD + '\\' + fname)
            lo = ds['lon'].values.flatten()
            la = ds['lat'].values.flatten()
            ds.close()
            for lon_v, lat_v in zip(lo, la):
                if not np.isnan(lon_v) and not np.isnan(lat_v):
                    li = int((lon_v - ext[0]) / GRID_STEP)
                    ai = int((lat_v - ext[2]) / GRID_STEP)
                    if 0 <= li < len(lons) and 0 <= ai < len(lats):
                        acc[ai, li] += 1
        except Exception as e:
            print(f'  Could not load {fname}: {e}')
    return gaussian_filter(acc, sigma=3)

results = {}
for basin, cfg in BASINS.items():
    print(f'\n=== {basin} ===')
    ext = cfg['ext']
    lons = np.arange(ext[0], ext[1], GRID_STEP)
    lats = np.arange(ext[2], ext[3], GRID_STEP)

    print('Loading real FDI detection rasters...')
    fdi_raw = load_fdi_on_grid(cfg['fdi_files'], lons, lats)

    print('Loading real CMEMS current speed...')
    speed_raw = load_current_on_grid(cfg['current_file'], lons, lats)

    print('Building real drift accumulation grid...')
    drift_raw = build_drift_grid(cfg['drift_files'], lons, lats, ext)

    fdi_freq = normalize01(fdi_raw)
    hydro_exposure = normalize01(speed_raw)
    drift_arrival = normalize01(drift_raw)

    mask = np.isfinite(fdi_freq) & np.isfinite(hydro_exposure) & np.isfinite(drift_arrival)
    fdi_freq_f = np.where(mask, fdi_freq, 0)
    hydro_f = np.where(mask, hydro_exposure, 0)
    drift_f = np.where(mask, drift_arrival, 0)

    R = compute_risk_index(fdi_freq_f, hydro_f, drift_f)
    R[~mask] = np.nan
    classes = classify_risk(R)

    results[basin] = {'R': R, 'classes': classes, 'lons': lons, 'lats': lats, 'mask': mask,
                       'high_km': 0.0, 'medium_km': 0.0, 'low_km': 0.0, 'checked_km': 0.0}
    valid_R = R[mask]
    print(f'  Real mean R: {np.nanmean(valid_R):.3f}')
    print(f'  Pixels HIGH: {np.sum(classes=="HIGH")}, MEDIUM: {np.sum(classes=="MEDIUM")}, LOW: {np.sum(classes=="LOW")}')

print('\n=== Measuring REAL coastline length at risk, PER BASIN ===')
shp_path = shpreader.natural_earth(resolution='10m', category='physical', name='coastline')
reader = shpreader.Reader(shp_path)

def get_risk_at_point(lon, lat, basin_data, ext):
    lons, lats = basin_data['lons'], basin_data['lats']
    if not (ext[0] <= lon <= ext[1] and ext[2] <= lat <= ext[3]):
        return None
    li = int((lon - ext[0]) / GRID_STEP)
    ai = int((lat - ext[2]) / GRID_STEP)
    if 0 <= li < len(lons) and 0 <= ai < len(lats):
        if not basin_data['mask'][ai, li]:
            return None
        return basin_data['classes'][ai, li]
    return None

for geom in reader.geometries():
    lines = [geom] if geom.geom_type == 'LineString' else list(geom.geoms)
    for line in lines:
        coords = list(line.coords)
        for i in range(len(coords) - 1):
            lon1, lat1 = coords[i]
            lon2, lat2 = coords[i+1]
            mlon, mlat = (lon1+lon2)/2, (lat1+lat2)/2
            seg_km = LineString([coords[i], coords[i+1]]).length * 111.0

            for basin, cfg in BASINS.items():
                ext = cfg['ext']
                cls = get_risk_at_point(mlon, mlat, results[basin], ext)
                if cls is not None:
                    results[basin]['checked_km'] += seg_km
                    if cls == 'HIGH':
                        results[basin]['high_km'] += seg_km
                    elif cls == 'MEDIUM':
                        results[basin]['medium_km'] += seg_km
                    else:
                        results[basin]['low_km'] += seg_km
                    break

print('\n=== PER-BASIN REAL RESULTS ===')
for basin in BASINS:
    r = results[basin]
    print(f'\n{basin}:')
    print(f'  Checked coastline: {r["checked_km"]:.1f} km')
    print(f'  HIGH risk: {r["high_km"]:.1f} km')
    print(f'  MEDIUM risk: {r["medium_km"]:.1f} km')
    print(f'  LOW risk: {r["low_km"]:.1f} km')
    print(f'  MEDIUM-TO-HIGH: {r["high_km"]+r["medium_km"]:.1f} km ({100*(r["high_km"]+r["medium_km"])/r["checked_km"]:.1f}%)')

total_checked = sum(results[b]['checked_km'] for b in BASINS)
total_med_high = sum(results[b]['high_km']+results[b]['medium_km'] for b in BASINS)
print(f'\n=== COMBINED ===')
print(f'Total checked: {total_checked:.1f} km')
print(f'Total medium-to-high: {total_med_high:.1f} km ({100*total_med_high/total_checked:.1f}%)')
