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

1. **Satellite Detection** — Floating Debris Index (FDI) retrieval from Sentinel-2 Level-2A multispectral imagery (Band 8 NIR, Band 6 RE2, Band 11 SWIR)
1. **Oceanographic Transport Analysis** — Basin-mean surface current characterisation from CMEMS GLORYS12V1 reanalysis
1. **Lagrangian Drift Simulation** — Forward particle trajectory forecasting via OpenDrift, synthesised into a Streamlit operational dashboard

Applied continuously across the South China Sea (SCS) and Bay of Bengal (BoB) from January 2019 to December 2023, the system identifies ~12,500 km of coastline at medium-to-high debris risk and delivers 24–72 hour advance warning forecasts with validated ensemble spread.

-----

## Key Results

|Metric                          |Value                                          |
|--------------------------------|-----------------------------------------------|
|SCS annual mean current speed   |0.164 m/s                                      |
|BoB annual mean current speed   |0.144 m/s                                      |
|Weighted mean current speed     |0.156 m/s                                      |
|SCS winter speed                |0.1898 m/s                                     |
|SCS–BoB winter difference       |+34.1% faster (SCS)                            |
|Pearson r (FDI vs current speed)|**0.651**, p < 0.001, n = 60                   |
|Mean Skill Score S              |**0.65** (24 h: 0.57 / 48 h: 0.67 / 72 h: 0.70)|
|Ensemble spread at 24 h         |5.74 km                                        |
|Ensemble spread at 48 h         |8.92 km                                        |
|Ensemble spread at 72 h         |12.11 km                                       |
|Sentinel-2 scenes processed     |847                                            |
|Coastline at medium-to-high risk|~12,500 km                                     |
|Population exposed              |~180 million                                   |

-----

## Repository Structure

```
coastal-sentinel/
├── scripts/
│   ├── drift_simulation.py          # OpenDrift ensemble runner (70 runs)
│   ├── fdi_calculator.py            # FDI retrieval and threshold pipeline
│   ├── skill_score.py               # Skill score and Pearson r validation
│   ├── risk_index.py                # Composite risk index R calculation
│   ├── figure_3_fdi_sensitivity.py  # Figure 3 — ROC/sensitivity 4-panel plot
│   └── dashboard.py                 # Streamlit operational dashboard
├── supplementary/
│   ├── figure_3_fdi_sensitivity.py  # Python script for Figure 3 (ROC plot)
│   └── Table_2_FDI_sensitivity.csv  # FDI threshold sensitivity data (0.03–0.08)
├── data/
│   ├── coordinates/                 # River mouth source coordinates (Table 1)
│   └── README_data.md               # Data access instructions (CMEMS, GEE, ERA5)
├── requirements.txt                 # Python dependencies
├── Fig2_FDI_Detection_GEE.js        # Google Earth Engine FDI detection script
├── dashboard.py                     # Streamlit dashboard (root-level for deployment)
└── README.md
```

-----

## Requirements

### Python Environment (Anaconda recommended)

```bash
conda create -n coastal_sentinel python=3.10
conda activate coastal_sentinel
pip install -r requirements.txt
```

Or install manually:

```bash
pip install numpy scipy pandas matplotlib cartopy
pip install opendrift
pip install streamlit
pip install earthengine-api
pip install copernicusmarine
pip install scikit-learn
```

### External Accounts Required

|Service                          |Purpose                     |Registration                             |
|---------------------------------|----------------------------|-----------------------------------------|
|Google Earth Engine              |Sentinel-2 scene acquisition|[signup](https://earthengine.google.com) |
|Copernicus Marine Service (CMEMS)|GLORYS12V1 ocean reanalysis |[register](https://marine.copernicus.eu) |
|Copernicus Climate Change Service|ERA5 wind fields            |[register](https://climate.copernicus.eu)|

-----

## Data Sources

|Dataset               |Provider                        |Resolution            |Purpose                     |
|----------------------|--------------------------------|----------------------|----------------------------|
|Sentinel-2 Level-2A   |ESA / Copernicus Open Access Hub|10–20 m, 5-day revisit|FDI debris detection        |
|CMEMS GLORYS12V1      |Copernicus Marine Service       |1/12°, daily          |Surface current fields      |
|ERA5 Global Reanalysis|ECMWF / Copernicus              |0.25°, hourly         |10-m wind fields for windage|

- Study period: **January 2019 – December 2023**
- SCS domain: **0°–25°N, 100°–122°E**
- BoB domain: **5°–23°N, 80°–100°E**

-----

## Step-by-Step Reproduction Guide

### Step 1 — FDI Detection (Google Earth Engine)

Open `Fig2_FDI_Detection_GEE.js` in the [GEE Code Editor](https://code.earthengine.google.com/).

This script:

- Authenticates with Google Earth Engine
- Retrieves Sentinel-2 Level-2A scenes (cloud fraction < 20%, sun-glint < 15°)
- Computes FDI per pixel: `FDI = B8 − [B6 + (B11 − B6) × ((832 − 740) / (1610 − 740)) × 10]`
- Applies threshold FDI > 0.05
- Exports monthly composite detection maps

### Step 2 — Ocean Current Analysis

Download GLORYS12V1 daily surface current data from CMEMS for the SCS and BoB domains. Then run:

```bash
python scripts/fdi_calculator.py
```

This computes basin-mean current speed time series and performs seasonal decomposition by monsoon phase (SCS seasonal: −14.6%; BoB seasonal: −8.6%).

### Step 3 — Drift Simulation (OpenDrift)

```bash
python scripts/drift_simulation.py
```

Runs **70 OpenDrift ensemble simulations** (7 river mouths × 2 seasons × 5 years).

**Configuration:**

|Parameter             |Value                |
|----------------------|---------------------|
|Windage coefficient   |3.5%                 |
|Horizontal diffusivity|10 m²/s              |
|Time-stepping scheme  |RK4, 1-hour intervals|
|Simulation duration   |72 hours             |
|Particles per source  |100                  |
|Seeding radius        |0.1°                 |
|Total ensembles       |70                   |

### Step 4 — Skill Score Validation

```bash
python scripts/skill_score.py
```

Computes:

- Pearson r = **0.651**, p < 0.001, n = 60
- Mean Skill Score S = **0.65**
- Time-resolved: S = 0.57 / 0.67 / 0.70 at 24 / 48 / 72 h

### Step 5 — Risk Mapping

Risk index R is computed as:

```
R = (FDI_frequency + Hydrodynamic_exposure + Drift_arrival_probability) / 3
```

```bash
python scripts/risk_index.py
```

### Step 6 — Launch Operational Dashboard

```bash
streamlit run dashboard.py
```

Opens at `http://localhost:8501`. Four panels:

1. FDI detection map
1. Drift trajectory overlay
1. Risk classification map
1. Plain-language alert panel

> **Live dashboard:** https://coastal-sentinel-king.streamlit.app
> (Hosted on Streamlit Community Cloud. If the app is sleeping, click “Wake up” or run locally via the command above.)

-----

## FDI Threshold Sensitivity

The FDI detection threshold was validated across a range of values (0.03–0.08). Results are reported at threshold = **0.05** as the optimal operating point (Table 2, Figure 3). Full sensitivity data is in `supplementary/Table_2_FDI_sensitivity.csv` and Figure 3 (ROC curves) in the manuscript.

-----

## River Mouth Source Coordinates (Table 1)

|River             |Region                     |Lat (°N)|Lon (°E)|Global Rank|
|------------------|---------------------------|--------|--------|-----------|
|Ganges-Brahmaputra|BoB — Bangladesh/India     |21.7    |89.1    |Top 5      |
|Irrawaddy         |BoB — Myanmar              |15.5    |95.2    |Top 10     |
|Mekong            |SCS — Vietnam/Cambodia     |10.0    |106.75  |Top 20     |
|Pearl River       |SCS — Guangdong, China     |22.1    |113.6   |Top 50     |
|Red River         |SCS — Northern Vietnam     |20.3    |106.5   |Top 100    |
|Mahanadi          |BoB — Odisha, India        |20.3    |86.7    |Top 100    |
|Godavari          |BoB — Andhra Pradesh, India|16.3    |82.3    |Top 100    |

Source: Meijer et al. (2021), *Sci. Adv.* 7(18), eaaz5803.

-----

## Novel Contributions

1. **First dual-region integrated EWS** — simultaneous satellite detection, transport analysis, and Lagrangian drift forecasting across both the SCS and BoB within a single operational framework
1. **First fully open-source replicable pipeline** — deployable by any coastal authority or research group with access to Copernicus data infrastructure
1. **First five-year quantified seasonal baseline** — statistically validated cross-basin monsoon-debris coupling (r = 0.651, p < 0.001, n = 60)

-----

## Citation

> Adega, K. J. The Coastal Sentinel: An Open-Source Integrated Framework for Satellite Detection, Drift Modelling, and Risk Mapping of Marine Plastic Debris — Evidence from the South China Sea and Bay of Bengal (2019–2023). *Environmental Science & Technology* (submitted).

-----

## License

This project is released under the **MIT License**. All data sources retain their original licensing terms (Copernicus Open Licence for Sentinel-2 and CMEMS products; ECMWF licence for ERA5).

-----

## Contact

King Jones Adega
School of Environmental Science and Engineering, Tianjin University
Tianjin 300350, China
Supervisor: Prof. Wenchao Ma
GitHub: [Kingjones300/coastal-sentinel](https://github.com/Kingjones300/coastal-sentinel)
