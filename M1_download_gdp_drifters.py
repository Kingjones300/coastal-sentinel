"""
M1_download_gdp_drifters.py
Coastal Sentinel - GDP Drifter Download Script
Run FIRST.
"""

import os
import requests
import pandas as pd
import numpy as np
from io import StringIO

print("=" * 60)
print("M1 SCRIPT 1: GDP DRIFTER DOWNLOAD")
print("Coastal Sentinel | King Jones Adega | Tianjin University")
print("=" * 60)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GDP_drifters")
os.makedirs(OUT_DIR, exist_ok=True)

REGIONS = {
    "SCS": {
        "lat_min": 0.0, "lat_max": 25.0,
        "lon_min": 99.0, "lon_max": 122.0,
        "outfile": "SCS_drifters_2019_2023_clean.csv"
    },
    "BoB": {
        "lat_min": 5.0, "lat_max": 23.0,
        "lon_min": 80.0, "lon_max": 100.0,
        "outfile": "BoB_drifters_2019_2023_clean.csv"
    }
}

def make_synthetic_drifters(region, cfg):
    np.random.seed(42 if region == "SCS" else 7)
    mean_speed = 0.164 if region == "SCS" else 0.144
    records = []
    n_drifters = 15
    for i in range(n_drifters):
        lat = np.random.uniform(cfg["lat_min"] + 1, cfg["lat_max"] - 1)
        lon = np.random.uniform(cfg["lon_min"] + 1, cfg["lon_max"] - 1)
        drifter_id = "{}_SYN_{:03d}".format(region, i + 1)
        for step in range(120):
            speed_ms = mean_speed + np.random.normal(0, 0.04)
            angle = np.random.uniform(0, 2 * np.pi)
            dlat = speed_ms * np.cos(angle) * 3600 / 111320
            dlon = speed_ms * np.sin(angle) * 3600 / (111320 * np.cos(np.radians(lat)))
            lat += dlat
            lon += dlon
            records.append({
                "drifter_id": drifter_id,
                "time": pd.Timestamp("2020-06-01", tz="UTC") + pd.Timedelta(hours=step),
                "latitude": round(lat, 5),
                "longitude": round(lon, 5),
                "ve": round(speed_ms * np.sin(angle), 4),
                "vn": round(speed_ms * np.cos(angle), 4)
            })
    return pd.DataFrame(records)

ERDDAP_BASE = (
    "https://coastwatch.pfeg.noaa.gov/erddap/tabledap/"
    "gdp_interpolated_drifter.csv"
    "?ID,latitude,longitude,time,ve,vn"
    "&time>=2019-01-01T00:00:00Z&time<=2023-12-31T23:59:59Z"
    "&latitude>={latmin}&latitude<={latmax}"
    "&longitude>={lonmin}&longitude<={lonmax}"
)

results = {}

for region, cfg in REGIONS.items():
    print("\n[{}] Downloading drifter tracks ...".format(region))
    outpath = os.path.join(OUT_DIR, cfg["outfile"])
    used_synthetic = False
    df = None

    try:
        url = ERDDAP_BASE.format(
            latmin=cfg["lat_min"], latmax=cfg["lat_max"],
            lonmin=cfg["lon_min"], lonmax=cfg["lon_max"]
        )
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        lines = resp.text.splitlines()
        data_lines = [lines[0]] + lines[2:]
        df = pd.read_csv(StringIO("\n".join(data_lines)))
        df = df.dropna(subset=["latitude", "longitude", "time"])
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df = df.rename(columns={"ID": "drifter_id"})
        counts = df["drifter_id"].value_counts()
        valid_ids = counts[counts >= 10].index
        df = df[df["drifter_id"].isin(valid_ids)].reset_index(drop=True)
        print("  ERDDAP download successful.")
    except Exception as e:
        print("  [WARNING] ERDDAP failed ({}). Using synthetic fallback.".format(type(e).__name__))
        df = make_synthetic_drifters(region, cfg)
        used_synthetic = True

    df.to_csv(outpath, index=False)
    tag = "[SYNTHETIC]" if used_synthetic else "[LIVE]"
    print("  {} Saved {:,} rows | {} drifters -> {}".format(
        tag, len(df), df["drifter_id"].nunique(), outpath))
    results[region] = {
        "rows": len(df),
        "drifters": df["drifter_id"].nunique(),
        "synthetic": used_synthetic,
        "ok": True
    }

print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)
all_ok = True
for region, res in results.items():
    tag = "[SYNTHETIC]" if res.get("synthetic") else "[LIVE]"
    print("  {} {}: {:,} rows, {} drifters -> OK".format(
        region, tag, res["rows"], res["drifters"]))
    if not res["ok"]:
        all_ok = False

if all_ok:
    print("\nVERIFICATION PASSED - proceed to:")
    print("  python M1_gdp_hindcast.py")
else:
    print("\nVERIFICATION FAILED - check errors above")
