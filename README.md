# The Coastal Sentinel

**An Open-Source Integrated Framework for Satellite Detection, Drift Modelling, and Risk Mapping of Marine Plastic Debris — Evidence from the South China Sea and Bay of Bengal (2019–2023)**

> King Jones Adega | PhD Candidate, Environmental Engineering | Tianjin University
> Supervisor: Prof. Wenchao Ma
> Target Journal: *Environmental Science & Technology* (ACS)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![OpenDrift](https://img.shields.io/badge/OpenDrift-1.x-green.svg)](https://opendrift.github.io/)

-----

## Overview

The Coastal Sentinel is a fully open-source, end-to-end operational pipeline that integrates three independently validated components into a single marine plastic debris early warning system:

1. **Satellite Detection** — Floating Debris Index (FDI) retrieval from Sentinel-2 Level-2A multispectral imagery (Band 8 NIR, Band 6 RE2, Band 11 SWIR), following Biermann et al. (2020)
2. **Oceanographic Transport Analysis** — Basin-mean surface current characterisation from CMEMS GLORYS12V1 reanalysis
3. **Lagrangian Drift Simulation** — Forward particle trajectory forecasting via OpenDrift, synthesised into a Streamlit operational dashboard

Applied continuously across the South China Sea (SCS) and Bay of Bengal (BoB) from January 2019 to December 2023, the system identifies approximately 2,160.5 km of coastline (14.4% of assessed shoreline) at medium-to-high debris risk and delivers 24–72 hour advance warning forecasts with independently validated forecast skill.

## Research Motivation

Marine plastic debris accumulates preferentially along monsoon-influenced coastlines, yet the South China Sea and Bay of Bengal — two of the highest-input, least-monitored ocean basins globally — lack any integrated, operational early warning capability. Existing monitoring efforts are fragmented across satellite detection, oceanographic modeling, and drift forecasting disciplines, with no open-source framework combining all three into a single deployable system. The Coastal Sentinel addresses this gap directly, providing a reproducible pipeline any coastal authority or research group can adapt using freely available Copernicus and NOAA data infrastructure.

## Key Results

| Metric | Value |
|---|---|
| SCS 5-year mean current speed | 0.2405 m/s |
| BoB 5-year mean current speed | 0.2595 m/s |
| SCS winter mean speed | 0.2652 m/s |
| BoB winter mean speed | 0.2642 m/s |
| SCS–BoB winter difference | Nearly identical (within 0.4%) |
| SCS winter vs. own summer | +12.1% |
| BoB winter vs. own summer | +3.9% |
| Pearson r (FDI vs. current speed, 2-month lag) | **0.61**, p < 0.001, n = 58 |
| Skill Score S, SCS (n = 31, 24/48/72h) | 0.42 / 0.46 / 0.47 |
| Skill Score S, BoB (n = 61, 24/48/72h) | 0.56 / 0.55 / 0.52 |
| Ensemble spread at 24h | 6.28 km |
| Ensemble spread at 48h | 7.11 km |
| Ensemble spread at 72h | 8.35 km |
| Mean net advection speed | 0.31 m/s |
| FDI-positive area at selected threshold (deep-water only) | 2,596 km² (SCS); 1,544 km² (BoB) |
| Coastline at medium-to-high risk | ~2,160.5 km (14.4% of assessed shoreline) |

All results validated against independent real-world data (92 NOAA Global Drifter Program buoy trajectories) — not self-referential.

-----

## Repository Structure

```
coastal-sentinel/
├── scripts/
│   ├── Figure2.py                    Study domain and river-mouth source map
│   ├── Figure3.py                    FDI threshold sensitivity analysis
│   ├── Figure4.py                    FDI detection maps (SCS and BoB)
│   ├── Figure5.py                    Monthly surface current speed distribution
│   ├── Figure6.py                    Lagrangian drift trajectory maps
│   ├── Figure7.py                    Composite risk maps
│   ├── Figure9.py                    Monthly FDI detection frequency
│   ├── Figure10.py                   Cross-basin correlation analysis
│   ├── Figure11.py                   Ensemble spread analysis
│   ├── Figure12.py                   Coastline risk exposure by category
│   ├── Drift_simulation.py           OpenDrift ensemble runner (70 runs)
│   ├── Risk_index.py                 Composite risk index calculation
│   ├── Skill_score.py                Forecast skill and lag-correlation validation
│   └── fdi_calculator.py             FDI computation utilities
├── data/
│   ├── Fig2_FDI_Detection_GEE.js     Google Earth Engine FDI detection script
│   ├── M1_download_gdp_drifters.py   GDP drifter data acquisition
│   └── M1_gdp_hindcast.py            Real drifter validation hindcast
├── figures/
│   ├── Figure2.png
│   ├── Figure3.png
│   ├── Figure4.png
│   ├── Figure5.png
│   ├── Figure6.png
│   ├── Figure7.png
│   ├── Figure9.png
│   ├── Figure10.png
│   ├── Figure11.png
│   └── Figure12.png
├── dashboard.py                      Streamlit operational dashboard
├── requirements.txt                  Python dependencies
└── README.md
```

-----

## Requirements

### Python Environment (Anaconda recommended)

```bash
conda create -n coastal_sentinel python=3.10
conda activate coastal_sentinel
pip install -r requirements.txt

Or install manually:

pip install numpy scipy pandas matplotlib cartopy
pip install opendrift
pip install streamlit
pip install earthengine-api
pip install copernicusmarine
pip install scikit-learn
pip install rasterio

External Accounts Required

| Service | Purpose | Registration |
|---|---|---|
| Google Earth Engine | Sentinel-2 scene acquisition | https://earthengine.google.com |
| Copernicus Marine Service (CMEMS) | GLORYS12V1 ocean reanalysis | https://marine.copernicus.eu |
| Copernicus Climate Change Service | ERA5 wind fields | https://climate.copernicus.eu |

Data Sources

| Dataset | Provider | Resolution | Purpose |
|---|---|---|---|
| Sentinel-2 Level-2A | ESA / Copernicus Open Access Hub | 10-20 m, 5-day revisit | FDI debris detection |
| CMEMS GLORYS12V1 | Copernicus Marine Service | 1/12 degree, daily | Surface current fields |
| ERA5 Global Reanalysis | ECMWF / Copernicus | 0.25 degree, hourly | 10-m wind fields for windage |
| NOAA GDP drifter trajectories | NOAA (via OSMC ERDDAP) | - | Independent forecast validation |
| Natural Earth | naturalearthdata.com | 10 m | Coastline geometry for risk mapping |
| ETOPO1 Global Relief Model | NOAA NGDC | ~1.85 km | Bathymetry-based deep-water masking |

	•	Study period: January 2019 – December 2023
	•	SCS domain: 0°–25°N, 100°–122°E
	•	BoB domain: 5°–23°N, 80°–100°E
	•	Real Sentinel-2 scene volume screened (cloud fraction < 20%): 167,439 (SCS: 93,934; BoB: 73,505)

Step-by-Step Reproduction Guide

Step 1 — FDI Detection (Google Earth Engine)

Open Fig2_FDI_Detection_GEE.js in the GEE Code Editor.

This script:

	•	Authenticates with Google Earth Engine
	•	Retrieves Sentinel-2 Level-2A scenes (cloud fraction < 20%)
	•	Computes FDI per pixel: FDI = NIR − [RE2 + (SWIR − RE2) × ((832 − 664.5) / (1610 − 664.5)) × 10]
	•	Applies threshold FDI > 0.05
	•	Exports FDI detection composites

Step 2 — Ocean Current Analysis

Download GLORYS12V1 daily surface current data from CMEMS for the SCS and BoB domains, then run Figure5.py to compute basin-mean current speed distributions.

Step 3 — Drift Simulation (OpenDrift)

python Drift_simulation.py

Runs 70 OpenDrift ensemble simulations (7 river mouths × 2 seasons × 5 years).

Configuration:

Parameter	Value
Windage coefficient	3.5%
Horizontal diffusivity	10 m²/s
Time-stepping scheme	RK4, 1-hour intervals
Simulation duration	72 hours
Particles per source	100
Seeding radius	0.1°
Total ensembles	70

Step 4 — Skill Score Validation

python Skill_score.py

Computes forecast skill S = 1 − (RMSE_model / RMSE_persistence) against 92 independent real NOAA GDP drifter trajectories, and the lag-dependent Pearson correlation between monthly FDI detection frequency and current speed (peaks at 2-month lag, r = 0.61).


Step 5 — Risk Mapping

Composite risk index R is computed as an equal-weighted mean:

R = (FDI_frequency + Hydrodynamic_exposure + Drift_arrival_probability) / 3

python Risk_index.py

Step 6 — Launch Operational Dashboard

streamlit run dashboard.py

Opens at http://localhost:8501. Four panels:

	1.	FDI detection map
	2.	Drift trajectory overlay
	3.	Risk classification map
	4.	Plain-language alert panel

Live dashboard: https://coastal-sentinel-king.streamlit.app

FDI Threshold Sensitivity

The FDI detection threshold was validated across a range of values (0.03–0.08) using cross-seasonal consistency analysis. Threshold 0.05 sits in the high-specificity region and is the value recommended by Biermann et al. (2020). A bathymetry-based deep-water mask (ETOPO1, excluding depths <20m) is applied to isolate genuine open-water detection specificity from shallow-water optical contamination — see Figure3.py for full implementation.

River Mouth Source Coordinates (Table 1)

River	Region	Lat (°N)	Lon (°E)	Global Rank
Ganges-Brahmaputra	BoB — Bangladesh/India	21.7	89.1	Top 5
Irrawaddy	BoB — Myanmar	15.5	95.2	Top 10
Mekong	SCS — Vietnam/Cambodia	10.0	106.75	Top 20
Pearl River	SCS — Guangdong, China	22.1	113.6	Top 50
Red River	SCS — Northern Vietnam	20.3	106.5	Top 100
Mahanadi	BoB — Odisha, India	20.3	86.7	Top 100
Godavari	BoB — Andhra Pradesh, India	16.3	82.3	Top 100

Source: Meijer et al. (2021), Sci. Adv. 7(18), eaaz5803.

Novel Contributions

	1.	Among the first dual-region integrated early warning systems — simultaneous satellite detection, transport analysis, and Lagrangian drift forecasting across both the SCS and BoB within a single operational framework
	2.	Fully open-source, replicable pipeline — deployable by resource-limited environmental monitoring agencies in other data-sparse ocean basins
	3.	Real, independent forecast validation — skill assessed against 92 real NOAA Global Drifter Program buoy trajectories rather than self-referential synthetic data
	4.	Physically grounded seasonal transport analysis — a lag-dependent (2-month) correlation between debris detection frequency and current speed, consistent with a genuine transport mechanism
	5.	Transparent detection specificity validation — bathymetry-based deep-water masking confirms genuine open-water detection specificity, with full methodology documented for reproducibility

Known Limitations

	•	Risk mapping reflects five-year climatological mean conditions; discrete pulse events (e.g., flood-driven debris surges) are not resolved at the temporal resolution of this framework.
	•	Forecast validation uses 92 independent drifter trajectories (n = 31 SCS, n = 61 BoB) — a genuine, independent validation dataset, but modest in size.
	•	The equal-weighted composite risk index assumes no basin-specific weighting between its three input layers; sensitivity analysis confirmed this assumption is robust within the tested range.
	•	The bathymetry-based deep-water mask is intentionally applied only to open-water detection specificity analysis (Table 2, Figure 3), not to coastal risk mapping, which is explicitly concerned with near-shore conditions.
	•	The dashboard currently runs from local/hosted deployment; a permanent public data archive (e.g., Zenodo) is a planned addition.

Citation

Adega, K. J.; Ma, W. The Coastal Sentinel: An Open-Source Integrated Framework for Satellite Detection, Drift Modelling, and Risk Mapping of Marine Plastic Debris — Evidence from the South China Sea and Bay of Bengal (2019–2023). Environmental Science & Technology (submitted).

License

This project is released under the MIT License. All data sources retain their original licensing terms (Copernicus Open Licence for Sentinel-2 and CMEMS products; ECMWF licence for ERA5).

Contact

King Jones Adega
School of Environmental Science and Engineering, Tianjin University
Tianjin 300350, China
Supervisor: Prof. Wenchao Ma
GitHub: Kingjones300/coastal-sentinel

