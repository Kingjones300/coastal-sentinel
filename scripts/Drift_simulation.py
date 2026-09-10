# “””
drift_simulation.py


Coastal Sentinel — OpenDrift Ensemble Runner
Runs 70 ensemble simulations across 7 river mouth sources, 2 seasons, 5 years.


Configuration (locked, M3 sensitivity Δkm = 0.0 ROBUST):


- Windage coefficient : 3.5 %
- Horizontal diffusivity : 10 m²/s
- Time-stepping scheme : RK4, 1-hour intervals
- Simulation duration : 72 hours
- Particles per source : 100
- Seeding radius : 0.1°
- Total ensembles : 70


Author: King Jones Adega | Tianjin University | Supervisor: Prof. Wenchao Ma
“””


import os
import numpy as np
from datetime import datetime, timedelta
from opendrift.models.oceandrift import OceanDrift


# ── River mouth source coordinates (Table 1) ──────────────────────────────────


SOURCES = {
“Ganges-Brahmaputra”: {“lat”: 21.7,  “lon”: 89.1},
“Irrawaddy”:          {“lat”: 15.5,  “lon”: 95.2},
“Mekong”:             {“lat”: 10.0,  “lon”: 106.75},
“Pearl_River”:        {“lat”: 22.1,  “lon”: 113.6},
“Red_River”:          {“lat”: 20.3,  “lon”: 106.5},
“Mahanadi”:           {“lat”: 20.3,  “lon”: 86.7},
“Godavari”:           {“lat”: 16.3,  “lon”: 82.3},
}


# ── Simulation parameters (locked) ────────────────────────────────────────────


WINDAGE           = 0.035        # 3.5 %
DIFFUSIVITY       = 10.0         # m²/s horizontal
TIMESTEP_MINUTES  = 60           # RK4, 1-hour intervals
DURATION_HOURS    = 72
PARTICLES         = 100
SEED_RADIUS_DEG   = 0.1
YEARS             = [2019, 2020, 2021, 2022, 2023]


# Monsoon seasons — start dates (YYYY adjusted per year at runtime)


SEASONS = {
“SWM”:  {“month”: 6,  “day”: 1},   # South-West Monsoon  (Jun–Sep)
“NEM”:  {“month”: 11, “day”: 1},   # North-East Monsoon  (Nov–Feb)
}


# ── Output directory ───────────────────────────────────────────────────────────


OUTPUT_DIR = “outputs/drift_trajectories”
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_single_simulation(source_name: str, lat: float, lon: float,
start_date: datetime, run_id: str) -> None:
“””
Runs a single 72-hour OpenDrift OceanDrift ensemble simulation.


```
Parameters
----------
source_name : str   River name (used in output filename)
lat, lon    : float Seeding location (river mouth centre)
start_date  : datetime  Simulation start time
run_id      : str   Unique label for this run (e.g. 'Mekong_SWM_2021')
"""
o = OceanDrift(loglevel=20)


# ── Reader: use CMEMS GLORYS12V1 NetCDF (update path as needed) ──────────
# from opendrift.readers import reader_netCDF_CF_generic
# reader_current = reader_netCDF_CF_generic.Reader(
#     'data/netcdf/glorys12v1_scs_bob_surface_<year>.nc')
# reader_wind = reader_netCDF_CF_generic.Reader(
#     'data/netcdf/era5_wind_10m_<year>.nc')
# o.add_reader([reader_current, reader_wind])
#
# For a quick offline test, uncomment the line below to use
# OpenDrift's built-in test reader (uniform flow, not for publication):
# o.set_config('environment:fallback:x_sea_water_velocity', 0.1)
# o.set_config('environment:fallback:y_sea_water_velocity', 0.05)


# ── Physics configuration ─────────────────────────────────────────────────
o.set_config('drift:windage_coeff', WINDAGE)
o.set_config('drift:horizontal_diffusivity', DIFFUSIVITY)
o.set_config('general:time_step_minutes', TIMESTEP_MINUTES)


# ── Seed particles around river mouth ─────────────────────────────────────
o.seed_elements(
    lon=np.random.uniform(lon - SEED_RADIUS_DEG, lon + SEED_RADIUS_DEG, PARTICLES),
    lat=np.random.uniform(lat - SEED_RADIUS_DEG, lat + SEED_RADIUS_DEG, PARTICLES),
    time=start_date,
    number=PARTICLES,
)


# ── Run simulation ─────────────────────────────────────────────────────────
outfile = os.path.join(OUTPUT_DIR, f"{run_id}.nc")
o.run(
    duration=timedelta(hours=DURATION_HOURS),
    time_step=timedelta(minutes=TIMESTEP_MINUTES),
    time_step_output=timedelta(hours=1),
    outfile=outfile,
)


print(f"  ✓  {run_id}  →  {outfile}")
```


def main():
“””
Runs all 70 ensemble simulations:
7 sources × 2 seasons × 5 years = 70 total.
“””
print(”=” * 60)
print(“Coastal Sentinel — OpenDrift Ensemble Runner”)
print(f”Sources : {len(SOURCES)} | Seasons : {len(SEASONS)} | Years : {len(YEARS)}”)
print(f”Total runs : {len(SOURCES) * len(SEASONS) * len(YEARS)}”)
print(”=” * 60)


```
run_count = 0
for source_name, coords in SOURCES.items():
    for season_label, season_start in SEASONS.items():
        for year in YEARS:
            start_date = datetime(year,
                                  season_start["month"],
                                  season_start["day"],
                                  0, 0, 0)
            run_id = f"{source_name}_{season_label}_{year}"
            print(f"\nRunning : {run_id}  (start: {start_date.date()})")


            run_single_simulation(
                source_name=source_name,
                lat=coords["lat"],
                lon=coords["lon"],
                start_date=start_date,
                run_id=run_id,
            )
            run_count += 1


print(f"\n{'=' * 60}")
print(f"All {run_count} ensemble simulations complete.")
print(f"Trajectory NetCDF files saved to: {OUTPUT_DIR}/")
```


if **name** == “**main**”:
main()