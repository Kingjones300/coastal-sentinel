# “””
skill_score.py


Coastal Sentinel — Skill Score and Statistical Validation
Computes Pearson r, p-value, and Liu & Weisberg (2011) Skill Score
from OpenDrift ensemble trajectory outputs vs observed drifter positions.


Locked validated statistics (DO NOT MODIFY):
Pearson r = 0.651, p < 0.001, n = 60
Mean Skill Score S = 0.65
Time-resolved: S = 0.57 / 0.67 / 0.70 at 24 / 48 / 72 h
Ensemble spread: 5.74 / 8.92 / 12.11 km at 24 / 48 / 72 h


Reference:
Liu, Y., & Weisberg, R. H. (2011). Evaluation of trajectory modeling
in different dynamic regions using normalized cumulative Lagrangian
separation. Journal of Geophysical Research, 116, C09013.


Author: King Jones Adega | Tianjin University | Supervisor: Prof. Wenchao Ma
“””


import numpy as np
from scipy import stats


# ── Haversine distance helper ─────────────────────────────────────────────────


def haversine_km(lat1: float, lon1: float,
lat2: float, lon2: float) -> float:
“”“Returns great-circle distance in kilometres.”””
R = 6371.0
phi1, phi2 = np.radians(lat1), np.radians(lat2)
dphi  = np.radians(lat2 - lat1)
dlam  = np.radians(lon2 - lon1)
a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2)**2
return 2 * R * np.arcsin(np.sqrt(a))


# ── Liu & Weisberg (2011) Skill Score ─────────────────────────────────────────


def liu_weisberg_skill(sep_distances: np.ndarray,
cumulative_lengths: np.ndarray,
tolerance: float = 1.0) -> float:
“””
Computes the normalised cumulative Lagrangian separation skill score.


```
Parameters
----------
sep_distances     : np.ndarray  Separation between modelled and observed
                                positions at each time step (km)
cumulative_lengths: np.ndarray  Cumulative path length of observed
                                trajectory up to each time step (km)
tolerance         : float       Tolerance scale factor (default 1.0)


Returns
-------
float   Skill Score S in [0, 1]; S > 0.6 = skilful
"""
d  = np.cumsum(sep_distances)
l  = cumulative_lengths
# avoid division by zero
l  = np.where(l == 0, 1e-9, l)
ss = np.mean(d / (tolerance * l))
S  = max(0.0, 1.0 - ss)
return float(S)
```


# ── Ensemble spread ───────────────────────────────────────────────────────────


def ensemble_spread_km(trajectories: np.ndarray,
time_indices: list) -> dict:
“””
Computes ensemble spread (std dev of particle positions) at given hours.


```
Parameters
----------
trajectories : np.ndarray  Shape (n_particles, n_timesteps, 2) — lat/lon
time_indices : list        Time step indices corresponding to 24/48/72 h


Returns
-------
dict  {hour: spread_km}
"""
spreads = {}
for idx, hour in zip(time_indices, [24, 48, 72]):
    lats = trajectories[:, idx, 0]
    lons = trajectories[:, idx, 1]
    mean_lat, mean_lon = np.mean(lats), np.mean(lons)
    distances = np.array([
        haversine_km(mean_lat, mean_lon, la, lo)
        for la, lo in zip(lats, lons)
    ])
    spreads[hour] = float(np.std(distances))
return spreads
```


# ── FDI vs Current speed Pearson correlation ──────────────────────────────────


def compute_pearson(fdi_monthly: np.ndarray,
current_speed_monthly: np.ndarray) -> dict:
“””
Computes Pearson r between monthly FDI detection frequency and
basin-mean current speed.


```
Parameters
----------
fdi_monthly           : np.ndarray  Monthly FDI values (n=60, 5 yr × 12 mo)
current_speed_monthly : np.ndarray  Monthly current speed values (m/s)


Returns
-------
dict  {r, p_value, n}
"""
assert len(fdi_monthly) == len(current_speed_monthly), \
    "FDI and current speed arrays must be the same length."
r, p = stats.pearsonr(fdi_monthly, current_speed_monthly)
return {"r": round(r, 3), "p_value": p, "n": len(fdi_monthly)}
```


# ── Main validation report ────────────────────────────────────────────────────


def print_validation_report(r: float, p: float, n: int,
skill_scores: dict,
spreads: dict) -> None:
print(”\n” + “=” * 55)
print(”  Coastal Sentinel — Statistical Validation Report”)
print(”=” * 55)
print(f”  Pearson r        : {r:.3f}”)
print(f”  p-value          : {’< 0.001’ if p < 0.001 else f’{p:.4f}’}”)
print(f”  n (months)       : {n}”)
print()
print(f”  Skill Score (mean)   : {np.mean(list(skill_scores.values())):.2f}”)
for h in [24, 48, 72]:
print(f”  Skill Score @ {h} h  : {skill_scores.get(h, ‘N/A’):.2f}”)
print()
print(f”  Ensemble spread @ 24 h : {spreads.get(24, ‘N/A’):.2f} km”)
print(f”  Ensemble spread @ 48 h : {spreads.get(48, ‘N/A’):.2f} km”)
print(f”  Ensemble spread @ 72 h : {spreads.get(72, ‘N/A’):.2f} km”)
print(”=” * 55)


# ── Example usage (replace with real data arrays) ─────────────────────────────


if **name** == “**main**”:
# Replace these with actual loaded arrays from your NetCDF / CSV outputs.
# The locked validated values from the manuscript are reproduced below
# as reference benchmarks.


```
# --- Locked reference values (from manuscript v9) ---
LOCKED = {
    "r": 0.651,
    "p": "<0.001",
    "n": 60,
    "skill_mean": 0.65,
    "skill_24h": 0.57,
    "skill_48h": 0.67,
    "skill_72h": 0.70,
    "spread_24h": 5.74,
    "spread_48h": 8.92,
    "spread_72h": 12.11,
}


print("\nLocked validated statistics (Coastal Sentinel v9):")
for k, v in LOCKED.items():
    print(f"  {k:<15}: {v}")


print("\nTo run on your own data, replace the arrays in the")
print("compute_pearson() and ensemble_spread_km() calls above.")
```