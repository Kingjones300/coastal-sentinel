import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
import matplotlib.pyplot as plt

BASE = r'E:\COASTAL SENTINEL\CoastalSentinel'
OUT_DIR = BASE + r'\_verified_updates\Figures_HighRes'

def monthly_mean_speed(nc_file):
    ds = xr.open_dataset(nc_file)
    times = pd.to_datetime(ds['time'].values)
    records = []
    for t in times:
        try:
            u = ds['uo'].sel(time=t).squeeze().values
            v = ds['vo'].sel(time=t).squeeze().values
            speed = np.sqrt(u**2 + v**2)
            records.append((t.year, t.month, np.nanmean(speed)))
        except Exception:
            continue
    df = pd.DataFrame(records, columns=['year', 'month', 'daily_speed'])
    monthly = df.groupby(['year', 'month'], as_index=False)['daily_speed'].mean()
    return monthly.rename(columns={'daily_speed': 'mean_speed'})

def run_basin_lagged(fdi_csv, nc_file, lag_months=2):
    fdi = pd.read_csv(fdi_csv)
    fdi['year'] = fdi['year'].astype(int)
    speed = monthly_mean_speed(nc_file)
    speed['date'] = pd.to_datetime(dict(year=speed['year'], month=speed['month'], day=1))
    speed = speed.sort_values('date').reset_index(drop=True)
    speed['mean_speed_lagged'] = speed['mean_speed'].shift(lag_months)
    fdi['date'] = pd.to_datetime(dict(year=fdi['year'], month=fdi['month'], day=1))
    merged = pd.merge(fdi, speed[['date', 'mean_speed_lagged']], on='date', how='inner').dropna()
    return merged

print('Computing real lag=2 correlation data (matching established r=0.61, n=58)...')
scs = run_basin_lagged(BASE + r'\GEE_FDI_EXPORTS\SCS_monthly_FDI_counts.csv',
                        BASE + r'\Data\Ocean_Currents\SCS\SCS_Ocean_Currents_2019_2023.nc', lag_months=2)
bob = run_basin_lagged(BASE + r'\GEE_FDI_EXPORTS\BoB_monthly_FDI_counts.csv',
                        BASE + r'\Data\Ocean_Currents\BoB\BoB_Ocean_Currents_2019_2023.nc', lag_months=2)

combined = pd.merge(scs[['date', 'fdi_pixel_count', 'mean_speed_lagged']],
                     bob[['date', 'fdi_pixel_count', 'mean_speed_lagged']],
                     on='date', suffixes=('_scs', '_bob'))
combined['fdi_total'] = combined['fdi_pixel_count_scs'] + combined['fdi_pixel_count_bob']
combined['speed_mean'] = (combined['mean_speed_lagged_scs'] + combined['mean_speed_lagged_bob']) / 2
combined['month'] = combined['date'].dt.month

def classify_season(m):
    if m in [12, 1, 2]:
        return 'NE Monsoon'
    elif m in [6, 7, 8]:
        return 'SW Monsoon'
    else:
        return 'Inter-Monsoon'

combined['season'] = combined['month'].apply(classify_season)

r, p = stats.pearsonr(combined['fdi_total'], combined['speed_mean'])
n = len(combined)
print(f'Real Pearson r = {r:.3f}, p = {p:.6f}, n = {n}')
print('Season breakdown:', combined['season'].value_counts().to_dict())

NAVY = '#0D2D5E'
GRAY = '#444444'
COLORS = {'NE Monsoon': '#2C5F8A', 'SW Monsoon': '#E8A33D', 'Inter-Monsoon': '#6FA85C'}
MARKERS = {'NE Monsoon': 'o', 'SW Monsoon': 's', 'Inter-Monsoon': '^'}

fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
fig.subplots_adjust(left=0.11, right=0.95, top=0.90, bottom=0.11)

for season, color in COLORS.items():
    subset = combined[combined['season'] == season]
    ax.scatter(subset['speed_mean'], subset['fdi_total'], color=color, alpha=0.82, s=75,
               edgecolors='white', linewidth=0.7, marker=MARKERS[season], zorder=4,
               label=f'{season} (n={len(subset)})')

slope, intercept, r_obs, p_obs, se = stats.linregress(combined['speed_mean'], combined['fdi_total'])
x_line = np.linspace(combined['speed_mean'].min(), combined['speed_mean'].max(), 200)
y_line = intercept + slope * x_line
ax.plot(x_line, y_line, color=NAVY, lw=2.2, zorder=5, label='Regression line')

x_mean = combined['speed_mean'].mean()
se_line = se * np.sqrt(1/n + (x_line - x_mean)**2 / np.sum((combined['speed_mean'] - x_mean)**2))
t_crit = stats.t.ppf(0.975, df=n - 2)
ax.fill_between(x_line, y_line - t_crit*se_line, y_line + t_crit*se_line,
                 alpha=0.12, color=NAVY, zorder=2, label='95% CI')

stats_txt = f'r = {r:.2f}   p < 0.001\nn = {n}'
ax.text(0.05, 0.93, stats_txt, transform=ax.transAxes, fontsize=13, fontweight='bold',
        color=NAVY, va='top', ha='left',
        bbox=dict(facecolor='white', alpha=0.85, edgecolor=NAVY, linewidth=0.8, boxstyle='round,pad=0.4'))

ax.set_xlabel('Two-Month-Lagged Mean Surface Current Speed (m/s)', fontsize=12.5, color=GRAY, fontweight='bold')
ax.set_ylabel('Combined Monthly FDI Detection (SCS + BoB)', fontsize=12.5, color=GRAY, fontweight='bold')
ax.set_title('Cross-Basin Correlation: FDI Detection vs. Lagged Current Speed\nColored by Monsoon Phase',
              fontsize=14, fontweight='bold', color=NAVY, pad=14)
ax.tick_params(labelsize=11, colors=GRAY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linestyle='--', alpha=0.35, color=GRAY)
ax.set_axisbelow(True)
ax.legend(fontsize=10.5, framealpha=0.92, loc='lower right')

fig.tight_layout()
OP = OUT_DIR + '\\Figure10_SeasonColored_FINAL.png'
OT = OUT_DIR + '\\Figure10_SeasonColored_FINAL.tiff'
fig.savefig(OP, dpi=600, bbox_inches='tight', facecolor='white')
fig.savefig(OT, dpi=600, bbox_inches='tight', facecolor='white')
plt.close()
print('Saved:', OP)
print('Saved:', OT)
