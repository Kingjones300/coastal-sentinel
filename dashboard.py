import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Optional xarray import (not available on Streamlit Cloud)
try:
    import xarray as xr
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="The Coastal Sentinel",
    page_icon="🌊",
    layout="wide"
)

# Title
st.markdown("""
    <h1 style='text-align: center; color: #1a5276;'>
    🌊 THE COASTAL SENTINEL
    </h1>
    <h3 style='text-align: center; color: #2874a6;'>
    Marine Plastic Debris Early Warning System
    </h3>
    <hr>
""", unsafe_allow_html=True)

# Cloud mode banner
if not XARRAY_AVAILABLE:
    st.info(
        "ℹ️ **Demo Mode** — Running on Streamlit Cloud with simulated ocean current data. "
        "For full NetCDF data, run locally: `streamlit run dashboard.py`",
        icon="ℹ️"
    )

# Sidebar controls
st.sidebar.title("Control Panel")
st.sidebar.markdown("---")

region = st.sidebar.selectbox(
    "Select Study Region",
    ["South China Sea", "Bay of Bengal"]
)

forecast_hours = st.sidebar.selectbox(
    "Select Forecast Lead Time",
    [24, 48, 72],
    format_func=lambda x: f"{x} Hours"
)

season = st.sidebar.selectbox(
    "Select Season",
    ["Annual", "Winter (Dec-Feb)", "Summer (Jun-Aug)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Alert Status")

# Set region parameters
if region == "South China Sea":
    current_file = r"C:\CoastalSentinel\Data\Ocean_Currents\SCS\SCS_Ocean_Currents_2019_2023.nc"
    extent = [99, 122, 0, 25]
    center_lat = 12.5
    center_lon = 110.5
    river_points = {
        'Mekong':      (106.0, 9.0),
        'Pearl River': (113.0, 21.0),
        'Red River':   (107.0, 19.0),
        'Central SCS': (110.0, 15.0),
        'East SCS':    (115.0, 18.0),
    }
    forecast_file = rf"C:\CoastalSentinel\Outputs\Results\SCS_{forecast_hours}hr_MultiPoint.nc"
    LOCKED_AVG_SPEED = 0.164
    LOCKED_MAX_SPEED = 0.221
else:
    current_file = r"C:\CoastalSentinel\Data\Ocean_Currents\BoB\BoB_Ocean_Currents_2019_2023.nc"
    extent = [80, 100, 5, 23]
    center_lat = 14.0
    center_lon = 90.0
    river_points = {
        'Ganges':      (89.0, 20.0),
        'Irrawaddy':   (95.0, 15.0),
        'Mahanadi':    (87.0, 19.0),
        'Godavari':    (82.0, 15.0),
        'Central BoB': (90.0, 12.0),
    }
    forecast_file = rf"C:\CoastalSentinel\Outputs\Results\BoB_{forecast_hours}hr_MultiPoint.nc"
    LOCKED_AVG_SPEED = 0.144
    LOCKED_MAX_SPEED = 0.198


def generate_demo_field(extent, avg_speed, seed=42):
    """Generate a realistic-looking current speed field for demo mode."""
    np.random.seed(seed)
    lon = np.linspace(extent[0], extent[1], 60)
    lat = np.linspace(extent[2], extent[3], 40)
    lon2d, lat2d = np.meshgrid(lon, lat)
    speed = (avg_speed
             + 0.04 * np.sin(np.radians(lon2d * 3))
             + 0.03 * np.cos(np.radians(lat2d * 4))
             + 0.02 * np.random.randn(*lon2d.shape))
    speed = np.clip(speed, 0.02, avg_speed * 2.2)
    return lon, lat, speed


def get_demo_monthly_speeds(region):
    """Return published monthly speed profile (locked statistics)."""
    if region == "South China Sea":
        return [0.221, 0.195, 0.162, 0.138, 0.145, 0.158,
                0.172, 0.168, 0.155, 0.149, 0.163, 0.210]
    else:
        return [0.128, 0.122, 0.131, 0.140, 0.155, 0.172,
                0.185, 0.178, 0.165, 0.148, 0.135, 0.130]


# Load or simulate current data
LOCAL_DATA = False
if XARRAY_AVAILABLE:
    try:
        ds = xr.open_dataset(current_file)
        if season == "Winter (Dec-Feb)":
            ds = ds.sel(time=ds.time.dt.month.isin([12, 1, 2]))
        elif season == "Summer (Jun-Aug)":
            ds = ds.sel(time=ds.time.dt.month.isin([6, 7, 8]))
        u = ds['uo'].isel(depth=0).mean(dim='time').values
        v = ds['vo'].isel(depth=0).mean(dim='time').values
        speed_field = np.sqrt(u**2 + v**2)
        lon = ds['longitude'].values
        lat = ds['latitude'].values
        avg_speed = float(np.nanmean(speed_field))
        max_speed = float(np.nanmax(speed_field))
        LOCAL_DATA = True
    except Exception:
        lon, lat, speed_field = generate_demo_field(extent, LOCKED_AVG_SPEED)
        avg_speed = LOCKED_AVG_SPEED
        max_speed = LOCKED_MAX_SPEED
else:
    lon, lat, speed_field = generate_demo_field(extent, LOCKED_AVG_SPEED)
    avg_speed = LOCKED_AVG_SPEED
    max_speed = LOCKED_MAX_SPEED

# Risk level
if avg_speed > 0.25:
    risk_level = "HIGH"
    risk_color = "red"
elif avg_speed > 0.15:
    risk_level = "MEDIUM"
    risk_color = "orange"
else:
    risk_level = "LOW"
    risk_color = "green"

# Alert status in sidebar
if risk_level == "HIGH":
    st.sidebar.error("🔴 HIGH RISK")
elif risk_level == "MEDIUM":
    st.sidebar.warning("🟡 MEDIUM RISK")
else:
    st.sidebar.success("🟢 LOW RISK")

# Main metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Region", value=region)
with col2:
    st.metric(label="Avg Current Speed", value=f"{avg_speed:.3f} m/s")
with col3:
    st.metric(label="Max Current Speed", value=f"{max_speed:.3f} m/s")
with col4:
    st.metric(label="Risk Level", value=risk_level)

st.markdown("---")

# Main map
col_map, col_info = st.columns([2, 1])

with col_map:
    st.subheader(f"🗺️ {region} — {forecast_hours}hr Debris Forecast")

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=speed_field,
        x=lon,
        y=lat,
        colorscale='RdYlGn_r',
        opacity=0.6,
        name='Current Speed',
        colorbar=dict(title='Current Speed (m/s)', x=1.02)
    ))

    # Drift results (local) or demo particles
    drift_plotted = False
    if XARRAY_AVAILABLE and LOCAL_DATA:
        try:
            drift = xr.open_dataset(forecast_file)
            end_lons = drift['lon'].values[-1, :]
            end_lats = drift['lat'].values[-1, :]
            valid = ~np.isnan(end_lons) & ~np.isnan(end_lats)
            fig.add_trace(go.Scattergeo(
                lon=end_lons[valid], lat=end_lats[valid],
                mode='markers',
                marker=dict(size=6, color=risk_color, opacity=0.8),
                name=f'Debris at {forecast_hours}hrs'
            ))
            drift.close()
            drift_plotted = True
        except Exception:
            pass

    if not drift_plotted:
        np.random.seed(forecast_hours)
        spread_deg = {24: 5.74, 48: 8.92, 72: 12.11}[forecast_hours] / 111.0
        demo_lons = center_lon + np.random.randn(70) * spread_deg
        demo_lats = center_lat + np.random.randn(70) * spread_deg
        fig.add_trace(go.Scattergeo(
            lon=demo_lons, lat=demo_lats,
            mode='markers',
            marker=dict(size=6, color=risk_color, opacity=0.7),
            name=f'Debris at {forecast_hours}hrs (demo)'
        ))

    for name, (rlon, rlat) in river_points.items():
        fig.add_trace(go.Scattergeo(
            lon=[rlon], lat=[rlat],
            mode='markers+text',
            marker=dict(size=12, color='lime', symbol='star',
                        line=dict(color='black', width=1)),
            text=[name], textposition='top right',
            name=name
        ))

    fig.update_layout(
        geo=dict(
            projection_type='mercator',
            showland=True, landcolor='burlywood',
            showocean=True, oceancolor='lightcyan',
            showcoastlines=True, coastlinecolor='black',
            showcountries=True,
            lonaxis=dict(range=[extent[0], extent[1]]),
            lataxis=dict(range=[extent[2], extent[3]])
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )

    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.subheader("📊 System Information")
    st.markdown(f"""
**Study Region:** {region}

**Forecast Period:** {forecast_hours} hours

**Season:** {season}

**Risk Status:** {risk_level}

**Data Source:** {"Local NetCDF (CMEMS)" if LOCAL_DATA else "Published statistics (demo)"}
    """)
    st.markdown("---")
    st.subheader("🌊 Current Statistics")
    st.markdown(f"""
- **Average Speed:** {avg_speed:.4f} m/s
- **Maximum Speed:** {max_speed:.4f} m/s
- **Data Period:** 2014–2023
- **Pearson r:** 0.651 (p < 0.001, n = 60)
    """)
    st.markdown("---")
    st.subheader("⚠️ Alert Thresholds")
    st.markdown("""
- 🔴 **HIGH:** Speed > 0.25 m/s
- 🟡 **MEDIUM:** Speed > 0.15 m/s
- 🟢 **LOW:** Speed < 0.15 m/s
    """)
    st.markdown("---")
    st.subheader("🏖️ At Risk Coastlines")
    if region == "South China Sea":
        st.markdown("""
- Philippine coastline
- Vietnam coast
- Hainan Island
- Pearl River Delta
        """)
    else:
        st.markdown("""
- Bangladesh coast
- Eastern India
- Myanmar coastline
- Northern Sri Lanka
        """)

st.markdown("---")

# Seasonal comparison
st.subheader("📈 Seasonal Current Speed Comparison")

col_s1, col_s2 = st.columns(2)

month_names = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']

with col_s1:
    if XARRAY_AVAILABLE and LOCAL_DATA:
        try:
            ds_full = xr.open_dataset(current_file)
            monthly_speed = []
            for m in range(1, 13):
                month_data = ds_full.sel(time=ds_full.time.dt.month == m)
                u_m = month_data['uo'].isel(depth=0).mean(dim='time').values
                v_m = month_data['vo'].isel(depth=0).mean(dim='time').values
                monthly_speed.append(float(np.nanmean(np.sqrt(u_m**2 + v_m**2))))
            ds_full.close()
        except Exception:
            monthly_speed = get_demo_monthly_speeds(region)
    else:
        monthly_speed = get_demo_monthly_speeds(region)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=month_names,
        y=monthly_speed,
        marker_color=[
            'red' if s > 0.2 else
            'orange' if s > 0.15 else
            'green' for s in monthly_speed
        ],
        name='Monthly Speed'
    ))
    fig2.update_layout(
        title=f'Monthly Average Current Speed — {region}',
        xaxis_title='Month',
        yaxis_title='Current Speed (m/s)',
        height=300
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_s2:
    st.subheader("🗓️ High Risk Months")
    risk_months = [month_names[i] for i, s in enumerate(monthly_speed) if s > 0.18]
    if risk_months:
        st.error(f"High risk months: {', '.join(risk_months)}")
    else:
        st.success("No extreme high risk months detected")

    st.markdown("---")
    st.markdown("### About The Coastal Sentinel")
    st.markdown(f"""
The Coastal Sentinel is an operational early warning system
for marine plastic debris influx. It integrates:

- Satellite remote sensing (Sentinel-2, Band B6)
- Ocean current modelling (CMEMS, 2014–2023)
- Wind data (ERA5)
- Particle drift simulation (OpenDrift)

**{forecast_hours}-hour advance warning** of plastic debris
arrival at coastal zones in the South China Sea and
Bay of Bengal.

**System specs:** 70 ensembles · 100 particles · 847 scenes
· 12,500 km coastline · ~180M people protected
    """)

st.markdown("---")
st.caption(
    "The Coastal Sentinel — PhD Research | "
    "Tianjin University | "
    "Data: Copernicus Marine Service, ERA5, Sentinel-2 | "
    "GitHub: https://github.com/Kingjones300/coastal-sentinel"
)
