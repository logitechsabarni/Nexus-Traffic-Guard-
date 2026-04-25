import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import math
import random
import streamlit.components.v1 as components
import json

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS · Traffic Command",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme State ───────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"


# ── Theme-aware CSS ───────────────────────────────────────────────────────────
_is_dark = st.session_state.theme == "dark"

if _is_dark:
    _bg0="#040810"; _bg2="#0b1425"; _hi="#ddeeff"; _lo="rgba(180,210,240,0.45)"
    _c="#00ffe1"; _c2="#0090ff"; _red="#ff3060"; _amber="#ffaa00"; _green="#00ff88"
    _card="linear-gradient(135deg,rgba(11,20,37,0.9),rgba(7,13,26,0.95))"
    _sidebar="linear-gradient(180deg,#05091a,#030710)"
    _border="rgba(0,255,225,0.12)"; _pbg="rgba(255,255,255,0.06)"
    _ai_msg="linear-gradient(135deg,rgba(0,90,255,0.08),rgba(176,96,255,0.06))"
    _user_msg="rgba(0,255,225,0.05)"
    _tab_sel="rgba(0,255,225,0.1)"
else:
    _bg0="#f0f4f8"; _bg2="#dae4f0"; _hi="#0a1a2a"; _lo="rgba(20,50,80,0.55)"
    _c="#006ecc"; _c2="#0055aa"; _red="#cc1040"; _amber="#cc7700"; _green="#007744"
    _card="linear-gradient(135deg,rgba(255,255,255,0.95),rgba(235,245,255,0.98))"
    _sidebar="linear-gradient(180deg,#e0ecf8,#d8e8f5)"
    _border="rgba(0,110,204,0.18)"; _pbg="rgba(0,0,0,0.07)"
    _ai_msg="linear-gradient(135deg,rgba(0,90,255,0.05),rgba(176,96,255,0.04))"
    _user_msg="rgba(0,110,204,0.06)"
    _tab_sel="rgba(0,110,204,0.12)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {{
  background: {_bg0} !important;
  color: {_hi} !important;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 400;
}}
.stApp {{ background: {_bg0} !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 0.75rem 1.5rem 2rem 1.5rem !important; max-width: 100% !important; }}

section[data-testid="stSidebar"] {{
  background: {_sidebar} !important;
  border-right: 1px solid {_border} !important;
  width: 280px !important;
}}
section[data-testid="stSidebar"] * {{ color: {_hi} !important; }}

.stTabs [data-baseweb="tab-list"] {{
  gap: 2px; background: rgba(0,0,0,0.03);
  border: 1px solid {_border}; border-radius: 10px; padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important; color: {_lo} !important;
  font-family: 'JetBrains Mono', monospace !important; font-size: 0.7rem !important;
  letter-spacing: 1.5px !important; border-radius: 7px !important;
  padding: 6px 14px !important; border: none !important; transition: all 0.2s;
}}
.stTabs [aria-selected="true"] {{
  background: {_tab_sel} !important; color: {_c} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 16px !important; }}

.nx-card {{
  background: {_card};
  border: 1px solid {_border}; border-radius: 12px;
  padding: 18px 20px; position: relative; overflow: hidden;
  margin-bottom: 14px; backdrop-filter: blur(16px);
}}
.nx-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, {_c} 40%, {_c2} 70%, transparent);
  opacity: 0.5;
}}
.nx-card.red {{ border-color: rgba(200,20,60,0.25); }}
.nx-card.amber {{ border-color: rgba(200,120,0,0.25); }}
.nx-card.green {{ border-color: rgba(0,120,70,0.2); }}

.kpi {{ padding: 14px 12px; text-align: center; }}
.kpi-lbl {{
  font-family: 'JetBrains Mono', monospace; font-size: 0.58rem;
  letter-spacing: 2.5px; text-transform: uppercase; color: {_lo}; margin-bottom: 5px;
}}
.kpi-val {{
  font-family: 'Orbitron', sans-serif; font-size: 2rem;
  font-weight: 700; line-height: 1; color: {_c};
}}
.kpi-val.red {{ color: {_red}; }}
.kpi-val.amber {{ color: {_amber}; }}
.kpi-val.green {{ color: {_green}; }}
.kpi-sub {{ font-size: 0.68rem; color: {_lo}; margin-top: 3px; font-family: 'JetBrains Mono', monospace; }}

.sh {{
  font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
  letter-spacing: 3px; text-transform: uppercase; color: {_c};
  margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}}
.sh::after {{ content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, {_border}, transparent); }}

.ticker-outer {{
  overflow: hidden; background: rgba(0,0,0,0.03);
  border: 1px solid {_border}; border-radius: 8px;
  padding: 8px 0; margin-bottom: 18px; white-space: nowrap; position: relative;
}}
.ticker-outer::before, .ticker-outer::after {{
  content:''; position:absolute; top:0; bottom:0; width:60px; z-index:2;
}}
.ticker-outer::before {{ left:0; background: linear-gradient(90deg, {_bg0}, transparent); }}
.ticker-outer::after  {{ right:0; background: linear-gradient(-90deg, {_bg0}, transparent); }}
.ticker-t {{
  display: inline-block; animation: scr 40s linear infinite;
  font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
  color: {_c}; letter-spacing: 1px; padding-left: 100%;
}}
@keyframes scr {{ from{{transform:translateX(0)}} to{{transform:translateX(-50%)}} }}

.b {{
  display:inline-block; padding:2px 8px; border-radius:4px;
  font-size:0.62rem; font-family:'JetBrains Mono',monospace;
  letter-spacing:1px; font-weight:700;
}}
.b-go   {{ background:rgba(0,150,80,0.12);  color:{_green}; border:1px solid rgba(0,150,80,0.35); }}
.b-slow {{ background:rgba(200,120,0,0.12); color:{_amber}; border:1px solid rgba(200,120,0,0.35); }}
.b-stop {{ background:rgba(200,20,60,0.12); color:{_red};   border:1px solid rgba(200,20,60,0.35); }}
.b-info {{ background:rgba(0,110,200,0.08); color:{_c};     border:1px solid rgba(0,110,200,0.3); }}
.b-blue {{ background:rgba(0,85,170,0.12);  color:{_c2};    border:1px solid rgba(0,85,170,0.35); }}

.pb-bg {{ background:{_pbg}; border-radius:4px; height:6px; overflow:hidden; margin:3px 0 10px; }}
.pb-fg {{ height:100%; border-radius:4px; transition:width 1s ease; }}

.inc {{
  background: rgba(200,20,60,0.05);
  border: 1px solid rgba(200,20,60,0.15); border-left: 3px solid {_red};
  border-radius: 8px; padding: 10px 13px; margin-bottom: 8px;
}}

.alert {{ border-radius: 10px; padding: 12px 16px; margin-bottom: 12px; display:flex; align-items:center; gap:12px; }}
.alert-crit {{ background:rgba(200,20,60,0.08); border:1px solid rgba(200,20,60,0.4); }}
.alert-warn {{ background:rgba(200,120,0,0.07); border:1px solid rgba(200,120,0,0.35); }}
.alert-info {{ background:rgba(0,110,200,0.06); border:1px solid rgba(0,110,200,0.25); }}

.pulse {{
  display:inline-block; width:7px; height:7px; border-radius:50%;
  background:{_green}; margin-right:5px; animation:pl 1.6s ease-in-out infinite;
}}
@keyframes pl {{ 0%,100%{{opacity:1;transform:scale(1);}} 50%{{opacity:.8;transform:scale(1.2);}} }}
@keyframes fu {{ from{{opacity:0;transform:translateY(10px)}} to{{opacity:1;transform:translateY(0)}} }}
.fu {{ animation: fu 0.5s ease both; }}

.cmp {{
  display:flex; justify-content:space-between; align-items:center;
  padding:8px 0; border-bottom:1px solid {_border};
  font-family:'JetBrains Mono',monospace; font-size:.75rem;
}}

::-webkit-scrollbar {{ width:4px; height:4px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:rgba(0,110,204,0.25); border-radius:4px; }}

.ai-msg {{
  background:{_ai_msg}; border:1px solid rgba(176,96,255,0.2);
  border-radius:10px; padding:12px 15px; margin-bottom:10px;
  font-size:.82rem; line-height:1.7; color:{_hi};
}}
.user-msg {{
  background:{_user_msg}; border:1px solid {_border};
  border-radius:10px; padding:10px 15px; margin-bottom:10px;
  font-size:.82rem; text-align:right; color:{_c};
}}

.pred-band {{ display:grid; grid-template-columns:repeat(6,1fr); gap:8px; margin-bottom:16px; }}
.pred-cell {{ background:{_bg2}; border:1px solid {_border}; border-radius:8px; padding:10px 8px; text-align:center; }}

div[data-testid="stMetric"] {{ display:none; }}
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
CITIES = {
    "Mumbai, India":        (19.0760, 72.8777),
    "Delhi, India":         (28.7041, 77.1025),
    "Kolkata, India":       (22.5726, 88.3639),
    "Bangalore, India":     (12.9716, 77.5946),
    "Chennai, India":       (13.0827, 80.2707),
    "Hyderabad, India":     (17.3850, 78.4867),
    "Pune, India":          (18.5204, 73.8567),
    "Ahmedabad, India":     (23.0225, 72.5714),
    "New York, USA":        (40.7128, -74.0060),
    "Los Angeles, USA":     (34.0522, -118.2437),
    "Chicago, USA":         (41.8781, -87.6298),
    "London, UK":           (51.5074, -0.1278),
    "Tokyo, Japan":         (35.6762, 139.6503),
    "Paris, France":        (48.8566, 2.3522),
    "Dubai, UAE":           (25.2048, 55.2708),
    "Singapore":            (1.3521, 103.8198),
    "São Paulo, Brazil":    (-23.5505, -46.6333),
    "Cairo, Egypt":         (30.0444, 31.2357),
    "Shanghai, China":      (31.2304, 121.4737),
    "Sydney, Australia":    (-33.8688, 151.2093),
}

WMO_CODES = {
    0:"Clear Sky", 1:"Mainly Clear", 2:"Partly Cloudy", 3:"Overcast",
    45:"Foggy", 48:"Rime Fog", 51:"Light Drizzle", 53:"Drizzle",
    55:"Heavy Drizzle", 61:"Slight Rain", 63:"Rain", 65:"Heavy Rain",
    71:"Slight Snow", 73:"Snow", 75:"Heavy Snow", 80:"Rain Showers",
    81:"Moderate Showers", 82:"Violent Showers", 95:"Thunderstorm",
}

ROAD_SEGMENTS = [
    "NH-8 Expressway", "Ring Road North", "Ring Road South", "Marine Drive",
    "Inner Ring Rd", "Bypass Junction", "Tollgate-3", "Overpass B-12",
    "Eastern Corridor", "Flyover Zone-5", "Metro Link Rd", "Airport Expressway",
    "Port Connector", "Industrial Belt", "CBD Arterial"
]

INTERSECTIONS = [
    "Main×Park", "Downtown×5th", "Harbor×West", "Central×North",
    "East×Bridge", "Ring×Junction", "Market×Bay", "Station×Ave",
    "Temple×MG Rd", "Lake×NH4", "Airport×Ring", "Toll×Bypass"
]

# ── Session State ─────────────────────────────────────────────────────────────
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []
if "alert_log" not in st.session_state:
    st.session_state.alert_log = []
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "custom_thresholds" not in st.session_state:
    st.session_state.custom_thresholds = {"ti_warn": 50, "ti_crit": 75, "aqi_warn": 100, "aqi_crit": 150}

# ── Data Fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
        f"wind_speed_10m,wind_direction_10m,precipitation,weather_code,visibility,surface_pressure"
        f"&hourly=temperature_2m,precipitation_probability,wind_speed_10m,visibility,precipitation"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
        f"&forecast_days=7&timezone=auto"
    )
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except:
        return None

@st.cache_data(ttl=60)
def fetch_air_quality(lat, lon):
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,us_aqi"
        f"&hourly=us_aqi,pm2_5,pm10"
        f"&timezone=auto"
    )
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except:
        return None

@st.cache_data(ttl=120)
def fetch_hourly_forecast(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=precipitation_probability,wind_speed_10m,visibility,weather_code,temperature_2m"
        f"&forecast_days=2&timezone=auto"
    )
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except:
        return None

# ── Traffic Simulation ────────────────────────────────────────────────────────
def simulate_traffic(lat, lon, weather_code, precipitation, wind_speed, aqi, hour_override=None):
    now = datetime.now()
    hour = hour_override if hour_override is not None else now.hour
    weekday = now.weekday()
    is_weekend = weekday >= 5

    rush_am = math.exp(-0.5 * ((hour - 8.5) / 1.3) ** 2)
    rush_pm = math.exp(-0.5 * ((hour - 18.0) / 1.5) ** 2)
    rush = (rush_am + rush_pm) * (0.65 if is_weekend else 1.0)
    base = 25 + rush * 60

    weather_pen = 1.0
    if precipitation > 10:   weather_pen = 1.55
    elif precipitation > 5:  weather_pen = 1.38
    elif precipitation > 1:  weather_pen = 1.20
    if weather_code in (95, 82, 65, 75): weather_pen = max(weather_pen, 1.40)
    if wind_speed > 60: weather_pen *= 1.18
    elif wind_speed > 40: weather_pen *= 1.09
    if aqi and aqi > 200: weather_pen *= 1.12
    elif aqi and aqi > 150: weather_pen *= 1.06

    base = min(base * weather_pen, 100)
    seed = int(lat * 100 + lon * 100 + hour + weekday * 1000)
    rng = random.Random(seed)
    jitter = rng.uniform(-5, 5)
    index = min(max(int(base + jitter), 0), 100)

    intersections = []
    for i, lbl in enumerate(INTERSECTIONS):
        r2 = random.Random(seed + i)
        cng = min(max(int(base + r2.uniform(-28, 28)), 0), 100)
        phase_roll = r2.random()
        phase = "GREEN" if phase_roll > 0.45 else ("YELLOW" if phase_roll > 0.25 else "RED")
        intersections.append({
            "name": lbl, "congestion": cng, "phase": phase,
            "volume": r2.randint(200, 1800),
            "avg_speed": max(8, 90 - int(cng * 0.85)),
            "wait_time": int(cng * 0.4),
        })

    history = []
    for h in range(24):
        rush_h_am = math.exp(-0.5 * ((h - 8.5) / 1.3) ** 2)
        rush_h_pm = math.exp(-0.5 * ((h - 18.0) / 1.5) ** 2)
        bh = 20 + (rush_h_am + rush_h_pm) * 60 * (0.65 if is_weekend else 1.0)
        r3 = random.Random(seed + h * 7)
        cong = min(max(int(bh * weather_pen * 0.85 + r3.uniform(-8, 8)), 0), 100)
        history.append({
            "hour": f"{h:02d}:00",
            "congestion": cong,
            "speed": max(8, 90 - int(cong * 0.82)),
            "volume": int(500 + cong * 20 + r3.randint(-50, 50)),
            "incidents": r3.randint(0, 4 if cong > 60 else 2),
        })

    road_flows = []
    for i, road in enumerate(ROAD_SEGMENTS):
        r5 = random.Random(seed + i * 53)
        cng = min(max(int(base + r5.uniform(-30, 30)), 0), 100)
        road_flows.append({
            "road": road, "congestion": cng,
            "volume": r5.randint(300, 2500),
            "speed": max(10, 90 - int(cng * 0.8)),
            "incidents": r5.randint(0, 2 if cng > 65 else 1),
            "status": "BLOCKED" if cng > 85 else ("HEAVY" if cng > 65 else ("MODERATE" if cng > 40 else "FLOWING")),
        })

    incidents = []
    inc_types = ["🚗 Collision", "🚧 Road Work", "⚠️ Debris", "🚑 Emergency", "🔧 Breakdown", "🌊 Flooding", "⚡ Signal Fault", "🚛 Overturned Vehicle"]
    for i in range(rng.randint(3, 7)):
        r4 = random.Random(seed + i * 31)
        incidents.append({
            "type": r4.choice(inc_types),
            "road": r4.choice(ROAD_SEGMENTS),
            "severity": r4.choice(["Low", "Low", "Medium", "Medium", "High"]),
            "delay": r4.randint(3, 45),
            "lat_offset": r4.uniform(-0.05, 0.05),
            "lon_offset": r4.uniform(-0.05, 0.05),
            "reported": f"{r4.randint(1,59)} min ago",
        })

    weekly = {}
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for d_idx, day in enumerate(days):
        wf = 0.6 if d_idx >= 5 else 1.0
        row = []
        for h in range(24):
            r_am = math.exp(-0.5 * ((h - 8.5) / 1.3) ** 2)
            r_pm = math.exp(-0.5 * ((h - 18.0) / 1.5) ** 2)
            bh = 18 + (r_am + r_pm) * 60 * wf
            rh = random.Random(seed + d_idx * 100 + h)
            row.append(min(max(int(bh + rh.uniform(-10, 10)), 0), 100))
        weekly[day] = row
    
    monthly_trend = []
    for day_n in range(30):
        rm = random.Random(seed + day_n * 999)
        monthly_trend.append({
            "day": day_n + 1,
            "avg_congestion": int(base * 0.9 + rm.uniform(-12, 12)),
            "peak_congestion": min(100, int(base * 1.2 + rm.uniform(-8, 15))),
            "incidents": rm.randint(3, 18),
        })

    return {
        "index": index,
        "intersections": intersections,
        "history": history,
        "incidents": incidents,
        "road_flows": road_flows,
        "weekly": weekly,
        "monthly": monthly_trend,
    }

def get_aqi_label(aqi):
    if aqi is None: return "N/A", "b-info"
    if aqi < 50:   return "Good", "b-go"
    if aqi < 100:  return "Moderate", "b-info"
    if aqi < 150:  return "Unhealthy for Sensitive", "b-slow"
    if aqi < 200:  return "Unhealthy", "b-stop"
    if aqi < 300:  return "Very Unhealthy", "b-stop"
    return "Hazardous", "b-stop"

def ti_color(ti):
    if ti > 70: return "var(--red)"
    if ti > 40: return "var(--amber)"
    return "var(--green)"

def ti_class(ti):
    if ti > 70: return "red"
    if ti > 40: return "amber"
    return "green"

def ti_label(ti):
    if ti > 80: return "CRITICAL"
    if ti > 60: return "HEAVY"
    if ti > 40: return "MODERATE"
    if ti > 20: return "LIGHT"
    return "FLOWING"

def ti_badge(ti):
    if ti > 60: return "b-stop"
    if ti > 35: return "b-slow"
    return "b-go"

# ── Traffic Signal HTML ───────────────────────────────────────────────────────
def traffic_signal_html(phase, countdown, congestion):
    r_a = "active" if phase == "RED"    else ""
    y_a = "active" if phase == "YELLOW" else ""
    g_a = "active" if phase == "GREEN"  else ""
    label = {"RED": "⬛ STOP", "YELLOW": "⚠ SLOW", "GREEN": "▲ GO"}[phase]
    col   = {"RED": "#ff3060", "YELLOW": "#ffaa00", "GREEN": "#00ff88"}[phase]
    bar_c = "#ff3060" if congestion > 70 else "#ffaa00" if congestion > 40 else "#00ff88"

    return f"""<!DOCTYPE html><html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@500&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent;display:flex;justify-content:center;align-items:center;min-height:320px;}}
.wrap{{display:flex;flex-direction:column;align-items:center;gap:10px;}}
.housing{{
  background:linear-gradient(160deg,#0d111e,#06090f);
  border:2px solid #1a2040;
  border-radius:20px;padding:16px 14px;
  display:flex;flex-direction:column;align-items:center;gap:12px;
  box-shadow:0 0 60px rgba(0,0,0,.95),0 4px 30px rgba(0,0,0,.8),inset 0 0 30px rgba(0,0,0,.5);
  position:relative;
}}
.housing::after{{
  content:'';position:absolute;inset:0;border-radius:18px;
  background:linear-gradient(160deg,rgba(255,255,255,.025),transparent 50%);
  pointer-events:none;
}}
.pole{{width:10px;height:50px;background:linear-gradient(180deg,#2a2a3a,#1a1a22);border-radius:0 0 4px 4px;}}
.lens{{
  width:64px;height:64px;border-radius:50%;
  border:3px solid rgba(0,0,0,.7);
  position:relative;transition:all .4s ease;
}}
.lens::after{{
  content:'';position:absolute;top:12%;left:18%;
  width:25%;height:25%;border-radius:50%;
  background:rgba(255,255,255,.18);
}}
.lens.red.active{{
  background:radial-gradient(circle at 35% 35%,#ff7090,#cc0033);
  box-shadow:0 0 20px #ff0040,0 0 50px rgba(255,0,60,.5),0 0 80px rgba(255,0,60,.25);
  animation:tp 1.1s ease-in-out infinite;
}}
.lens.yellow.active{{
  background:radial-gradient(circle at 35% 35%,#ffe060,#cc8800);
  box-shadow:0 0 20px #ffcc00,0 0 50px rgba(255,204,0,.5),0 0 80px rgba(255,204,0,.25);
  animation:tp .7s ease-in-out infinite;
}}
.lens.green.active{{
  background:radial-gradient(circle at 35% 35%,#60ff99,#00bb44);
  box-shadow:0 0 20px #00ff88,0 0 50px rgba(0,255,136,.5),0 0 80px rgba(0,255,136,.25);
  animation:tp 1.4s ease-in-out infinite;
}}
.lens.red:not(.active)   {{background:#1a0308;}}
.lens.yellow:not(.active){{background:#1a1000;}}
.lens.green:not(.active) {{background:#001a08;}}
@keyframes tp{{
  0%,100%{{transform:scale(1);filter:brightness(1);}}
  50%{{transform:scale(1.04);filter:brightness(1.2);}}
}}
.phase-lbl{{
  font-family:'Orbitron',sans-serif;font-size:1.4rem;font-weight:900;
  letter-spacing:3px;color:{col};text-shadow:0 0 20px {col}88;
}}
.cd{{
  font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:500;
  color:rgba(180,200,220,.6);letter-spacing:2px;
}}
.cong-wrap{{width:110px;}}
.cong-lbl{{font-family:'JetBrains Mono',monospace;font-size:.6rem;color:rgba(150,180,200,.45);letter-spacing:1.5px;display:flex;justify-content:space-between;}}
.cong-bg{{background:rgba(255,255,255,.06);border-radius:3px;height:5px;margin-top:4px;overflow:hidden;}}
.cong-fg{{height:100%;border-radius:3px;width:{congestion}%;background:{bar_c};transition:width 1s;}}
</style></head><body>
<div class="wrap">
  <div class="housing">
    <div class="lens red {r_a}"></div>
    <div class="lens yellow {y_a}"></div>
    <div class="lens green {g_a}"></div>
  </div>
  <div class="pole"></div>
  <div class="phase-lbl">{label}</div>
  <div class="cd">T–{countdown:02d}s</div>
  <div class="cong-wrap">
    <div class="cong-lbl"><span>CONGESTION</span><span>{congestion}%</span></div>
    <div class="cong-bg"><div class="cong-fg"></div></div>
  </div>
</div>
</body></html>"""

# ── Plotly Theme ──────────────────────────────────────────────────────────────
def TICK(**extra):
    return dict(tickfont=dict(family="JetBrains Mono", size=9, color="#556677"), **extra)

def GRID(**extra):
    return dict(showgrid=True, gridcolor="rgba(0,255,225,0.05)", zeroline=False,
                tickfont=dict(family="JetBrains Mono", size=9, color="#556677"), **extra)

def NOGRID(**extra):
    return dict(showgrid=False, zeroline=False,
                tickfont=dict(family="JetBrains Mono", size=9, color="#556677"), **extra)

PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#88aabb"),
    margin=dict(l=0, r=0, t=20, b=30),
)


def styled_axis(**kwargs):
    return dict(tickfont=dict(family='JetBrains Mono', size=9, color='#556677'), **kwargs)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 18px;">
      <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:900;
                  letter-spacing:5px;color:#00ffe1;text-shadow:0 0 25px rgba(0,255,225,.5);">
        NEXUS
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;letter-spacing:4px;
                  color:rgba(0,255,225,.4);margin-top:1px;">TRAFFIC COMMAND SYSTEM v3.0</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Theme Toggle ──────────────────────────────────────────────────────────
    th_col1, th_col2 = st.columns([1, 1])
    with th_col1:
        st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;color:rgba(120,180,220,.6);padding-top:8px;">{"🌙 DARK" if _is_dark else "☀️ LIGHT"} MODE</div>', unsafe_allow_html=True)
    with th_col2:
        if st.button("🔄 Switch", use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "light" if _is_dark else "dark"
            st.rerun()
    st.markdown("---")

    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;color:rgba(0,255,225,.4);margin-bottom:6px;">PRIMARY CITY</div>', unsafe_allow_html=True)
    city = st.selectbox("", list(CITIES.keys()), index=2, label_visibility="collapsed")
    lat, lon = CITIES[city]

    st.markdown("---")
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;color:rgba(0,255,225,.4);margin-bottom:6px;">COMPARE MODE</div>', unsafe_allow_html=True)
    compare_mode = st.toggle("Enable City Comparison", value=False)
    if compare_mode:
        city2_options = [c for c in CITIES.keys() if c != city]
        city2 = st.selectbox("Compare With", city2_options, index=0, label_visibility="collapsed")
        lat2, lon2 = CITIES[city2]
    else:
        city2 = lat2 = lon2 = None

    st.markdown("---")
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;color:rgba(0,255,225,.4);margin-bottom:6px;">REFRESH</div>', unsafe_allow_html=True)
    refresh_rate = st.slider("Interval (seconds)", 15, 180, 45, 5)
    auto_refresh  = st.toggle("Auto Refresh", value=True)

    st.markdown("---")
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;color:rgba(0,255,225,.4);margin-bottom:6px;">ETA ESTIMATOR</div>', unsafe_allow_html=True)
    route_dist = st.slider("Route Distance (km)", 1, 100, 15)
    eta_slot = st.empty()

    st.markdown("---")
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;color:rgba(0,255,225,.4);margin-bottom:6px;">ALERT THRESHOLDS</div>', unsafe_allow_html=True)
    ti_warn  = st.slider("TI Warning", 30, 90, st.session_state.custom_thresholds["ti_warn"])
    ti_crit  = st.slider("TI Critical", 50, 100, st.session_state.custom_thresholds["ti_crit"])
    st.session_state.custom_thresholds["ti_warn"] = ti_warn
    st.session_state.custom_thresholds["ti_crit"] = ti_crit

    st.markdown("---")
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;color:rgba(0,255,225,.4);margin-bottom:6px;">DATA SOURCES</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:.68rem;color:rgba(180,210,240,.45);line-height:2;margin-top:6px;font-family:'JetBrains Mono',monospace;">
    ● <span style="color:#00ffe1;">Open-Meteo</span> — Weather<br>
    ● <span style="color:#00ffe1;">Open-Meteo AQ</span> — Air Quality<br>
    ● <span style="color:#0090ff;">NEXUS Engine</span> — Traffic Sim<br>
    ● <span style="color:#b060ff;">AI Module</span> — Intelligence
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    tomtom_key = st.text_input("TomTom API Key (optional)", type="password", placeholder="For live traffic overlay…")

# ── Fetch Data ────────────────────────────────────────────────────────────────
weather_data  = fetch_weather(lat, lon)
aq_data       = fetch_air_quality(lat, lon)
forecast_data = fetch_hourly_forecast(lat, lon)

if weather_data:
    cur         = weather_data["current"]
    temp        = cur.get("temperature_2m", 25)
    feels_like  = cur.get("apparent_temperature", 25)
    humidity    = cur.get("relative_humidity_2m", 60)
    wind_speed  = cur.get("wind_speed_10m", 10)
    wind_dir    = cur.get("wind_direction_10m", 180)
    w_code      = cur.get("weather_code", 0)
    visibility  = cur.get("visibility", 10000)
    pressure    = cur.get("surface_pressure", 1013)
    weather_desc = WMO_CODES.get(w_code, "Unknown")
    # precipitation: use current value; if 0, derive estimate from weather_code
    raw_precip = cur.get("precipitation", 0) or 0
    _wcode_precip = {
        51: 0.3, 53: 0.8, 55: 2.0,
        61: 1.5, 63: 4.0, 65: 10.0,
        71: 0.5, 73: 2.0, 75: 6.0,
        80: 2.5, 81: 6.0, 82: 15.0,
        95: 8.0,
    }
    precip = raw_precip if raw_precip > 0 else _wcode_precip.get(w_code, 0.0)
    # Also try to pull the first non-zero hourly value as fallback
    if precip == 0 and weather_data and "hourly" in weather_data:
        try:
            hrly_p = weather_data["hourly"].get("precipitation", [])
            for p in hrly_p[:3]:
                if p and p > 0:
                    precip = round(p, 1)
                    break
        except:
            pass
else:
    temp=feels_like=humidity=25; wind_speed=precip=0; w_code=0
    visibility=10000; pressure=1013; weather_desc="N/A"; wind_dir=0

if aq_data and "current" in aq_data:
    aqi_val = aq_data["current"].get("us_aqi")
    pm25    = aq_data["current"].get("pm2_5", 0)
    pm10    = aq_data["current"].get("pm10", 0)
    no2     = aq_data["current"].get("nitrogen_dioxide", 0)
    ozone   = aq_data["current"].get("ozone", 0)
    co      = aq_data["current"].get("carbon_monoxide", 0)
else:
    aqi_val=pm25=pm10=no2=ozone=co=0

traffic = simulate_traffic(lat, lon, w_code, precip, wind_speed, aqi_val)
ti      = traffic["index"]

# ETA sidebar
base_spd   = max(10, 80 - int(ti * 0.72))
eta_base   = max(1, int((route_dist / base_spd) * 60))
eta_delay  = int(eta_base * (ti / 100) * 0.5)
eta_slot.markdown(f"""
<div style="background:rgba(0,255,225,0.04);border:1px solid rgba(0,255,225,0.15);
            border-radius:8px;padding:10px 12px;margin-top:6px;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:.55rem;color:rgba(0,255,225,.4);letter-spacing:2px;margin-bottom:4px;">ESTIMATED ETA</div>
  <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:700;color:#00ffe1;">{eta_base + eta_delay} min</div>
  <div style="font-size:.65rem;color:rgba(180,210,240,.4);font-family:'JetBrains Mono',monospace;">
    {eta_base}min base + <span style="color:var(--amber);">{eta_delay}min</span> traffic
  </div>
  <div style="font-size:.6rem;color:rgba(180,210,240,.3);margin-top:4px;">@ {base_spd} km/h avg · {route_dist} km</div>
</div>""", unsafe_allow_html=True)

# Signal phase
phase_sec = int(time.time()) % 90
if phase_sec < 45:   sig_phase = "GREEN";  sig_cd = 45 - phase_sec
elif phase_sec < 56: sig_phase = "YELLOW"; sig_cd = 56 - phase_sec
else:                sig_phase = "RED";    sig_cd = 90 - phase_sec

aqi_lbl, aqi_bdg = get_aqi_label(aqi_val)
aqi_c = "var(--red)" if (aqi_val or 0) > 150 else "var(--amber)" if (aqi_val or 0) > 100 else "var(--green)"

# ─────────────────────────────────────────────────────────────────────────────
# TITLE BAR
# ─────────────────────────────────────────────────────────────────────────────
col_title, col_ti = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <div style="padding:10px 0 6px;">
      <div style="font-family:'Orbitron',sans-serif;font-size:2.2rem;font-weight:900;
                  letter-spacing:5px;background:linear-gradient(90deg,#00ffe1,#0090ff);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;line-height:1.1;">
        NEXUS TRAFFIC COMMAND
      </div>
      <div style="display:flex;align-items:center;gap:16px;margin-top:5px;flex-wrap:wrap;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:rgba(0,255,225,.5);letter-spacing:2px;">
          <span class="pulse"></span>LIVE ·
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:rgba(180,210,240,.6);">
          📍 {city.upper()}
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:rgba(180,210,240,.4);">
          {datetime.now().strftime('%d %b %Y  %H:%M:%S')}
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:rgba(180,210,240,.4);">
          {weather_desc}  {temp:.0f}°C
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_ti:
    ti_c = ti_color(ti)
    st.markdown(f"""
    <div style="text-align:right;padding:10px 0;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:.55rem;color:rgba(0,255,225,.4);letter-spacing:3px;">TRAFFIC INDEX</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:3rem;font-weight:900;
                  color:{ti_c};text-shadow:0 0 30px {ti_c}88;line-height:1;">{ti}</div>
      <span class="b {ti_badge(ti)}" style="font-size:.7rem;">{ti_label(ti)}</span>
    </div>
    """, unsafe_allow_html=True)

# ── Ticker ─────────────────────────────────────────────────────────────────
inc_tck = "  ///  ".join([f"⚑ {i['type']} on {i['road']} — +{i['delay']}min · {i['reported']}" for i in traffic["incidents"]])
st.markdown(f"""<div class="ticker-outer"><div class="ticker-t">{inc_tck} &nbsp;&nbsp;&nbsp; {inc_tck}</div></div>""", unsafe_allow_html=True)

# ── Alerts ─────────────────────────────────────────────────────────────────
if ti >= ti_crit:
    st.markdown(f"""<div class="alert alert-crit"><span style="font-size:1.3rem;">🚨</span>
    <div><div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:var(--red);font-weight:700;letter-spacing:1px;">CRITICAL CONGESTION — INDEX {ti}</div>
    <div style="font-size:.72rem;color:rgba(200,220,230,.65);margin-top:2px;">Severe delays city-wide. Recommend delaying non-essential travel. Activate incident response protocols.</div></div></div>""", unsafe_allow_html=True)
elif ti >= ti_warn:
    st.markdown(f"""<div class="alert alert-warn"><span style="font-size:1.3rem;">⚠️</span>
    <div><div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:var(--amber);font-weight:700;letter-spacing:1px;">CONGESTION WARNING — INDEX {ti}</div>
    <div style="font-size:.72rem;color:rgba(200,220,230,.65);margin-top:2px;">Elevated delays on major corridors. Consider alternate routes or off-peak travel.</div></div></div>""", unsafe_allow_html=True)

if (aqi_val or 0) > 150:
    st.markdown(f"""<div class="alert alert-crit"><span style="font-size:1.3rem;">😷</span>
    <div><div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:var(--red);font-weight:700;letter-spacing:1px;">UNHEALTHY AIR QUALITY — AQI {aqi_val}</div>
    <div style="font-size:.72rem;color:rgba(200,220,230,.65);margin-top:2px;">Limit outdoor exposure. Wear N95 masks during transit. Sensitive groups should stay indoors.</div></div></div>""", unsafe_allow_html=True)

if precip > 5:
    st.markdown(f"""<div class="alert alert-info"><span style="font-size:1.3rem;">🌧️</span>
    <div><div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:var(--c);font-weight:700;letter-spacing:1px;">HEAVY PRECIPITATION — {precip:.1f} mm/hr</div>
    <div style="font-size:.72rem;color:rgba(200,220,230,.65);margin-top:2px;">Reduced road visibility and traction. Expect 20–40% longer travel times.</div></div></div>""", unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────
k = st.columns(8)
def kpi_card(col, label, value, sub, cls=""):
    col.markdown(f"""<div class="nx-card kpi {cls}">
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-val {cls}">{value}</div>
      <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

kpi_card(k[0], "Temperature",  f"{temp:.0f}°C",      f"Feels {feels_like:.0f}°C")
kpi_card(k[1], "Humidity",     f"{humidity:.0f}%",   "Relative")
kpi_card(k[2], "Wind Speed",   f"{wind_speed:.0f}",  "km/h", "amber" if wind_speed > 40 else "")
kpi_card(k[3], "Precipitation",f"{precip:.1f}",      "mm/hr", "red" if precip > 5 else "")
kpi_card(k[4], "Pressure",     f"{pressure:.0f}",    "hPa")
kpi_card(k[5], "Visibility",   f"{visibility/1000:.1f}", "km", "red" if visibility < 2000 else "")
aqi_cls = "red" if (aqi_val or 0)>150 else "amber" if (aqi_val or 0)>100 else "green"
kpi_card(k[6], "Air Quality",  str(aqi_val or "N/A"), aqi_lbl, aqi_cls)
kpi_card(k[7], "PM 2.5",      f"{pm25:.1f}",         "µg/m³", "red" if pm25 > 35 else "amber" if pm25 > 15 else "")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🚦 Live Dashboard",
    "📊 Analytics",
    "🗺️ Road Network",
    "🌤️ Weather Impact",
    "🤖 AI Intelligence",
    "📡 Signal Control",
    "🆚 City Compare",
    "📅 Historical",
    "🔔 Alerts & Logs",
    "⚙️ Config & Export",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: LIVE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    left, mid, right = st.columns([1.0, 2.5, 1.5])

    with left:
        st.markdown('<div class="sh">🚦 ACTIVE SIGNAL</div>', unsafe_allow_html=True)
        components.html(traffic_signal_html(sig_phase, sig_cd, ti), height=320)

        st.markdown('<div class="sh" style="margin-top:12px;">📍 SIGNAL PHASES</div>', unsafe_allow_html=True)
        for inter in traffic["intersections"][:5]:
            p = inter["phase"]; c = inter["congestion"]
            bdg = "b-go" if p=="GREEN" else "b-slow" if p=="YELLOW" else "b-stop"
            fc = "#00ff88" if c < 40 else "#ffaa00" if c < 70 else "#ff3060"
            st.markdown(f"""
            <div style="margin-bottom:9px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">
                <span style="font-size:.75rem;font-family:'JetBrains Mono',monospace;color:#aaccdd;">{inter['name']}</span>
                <div style="display:flex;gap:5px;align-items:center;">
                  <span style="font-size:.65rem;color:{fc};font-family:'JetBrains Mono',monospace;">{c}%</span>
                  <span class="b {bdg}" style="font-size:.58rem;">{p}</span>
                </div>
              </div>
              <div class="pb-bg"><div class="pb-fg" style="width:{c}%;background:{fc};opacity:.8;"></div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sh" style="margin-top:8px;">⏱️ WAIT TIMES</div>', unsafe_allow_html=True)
        for inter in traffic["intersections"][:4]:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;
                        border-bottom:1px solid rgba(0,255,225,0.06);font-family:'JetBrains Mono',monospace;font-size:.7rem;">
              <span style="color:#88aacc;">{inter['name']}</span>
              <span style="color:var(--amber);">{inter['wait_time']}s wait</span>
            </div>""", unsafe_allow_html=True)

    with mid:
        st.markdown('<div class="sh">📈 24-HOUR TRAFFIC FLOW</div>', unsafe_allow_html=True)
        df_h = pd.DataFrame(traffic["history"])
        now_hr = datetime.now().hour

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_h["hour"], y=df_h["congestion"],
            fill="tozeroy", name="Congestion",
            line=dict(color="#00ffe1", width=2),
            fillcolor="rgba(0,255,225,0.07)",
            hovertemplate="<b>%{x}</b><br>Congestion: %{y}%<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=df_h["hour"], y=df_h["speed"],
            name="Avg Speed", yaxis="y2",
            line=dict(color="#00ff88", width=1.8, dash="dot"),
            hovertemplate="<b>%{x}</b><br>Speed: %{y} km/h<extra></extra>"
        ))
        fig.add_trace(go.Bar(
            x=df_h["hour"], y=df_h["volume"],
            name="Volume", yaxis="y3", opacity=0.18,
            marker_color="#0090ff",
            hovertemplate="<b>%{x}</b><br>Volume: %{y} veh/hr<extra></extra>"
        ))
        fig.add_vline(x=now_hr, line_color="#ffaa00", line_dash="dash", line_width=1.5,
                      annotation_text="NOW", annotation_font=dict(color="#ffaa00", size=9))
        fig.update_layout(
            **PLOT_LAYOUT, height=230,
            legend=dict(orientation="h", y=1.08, font=dict(size=9, color="#667788")),
            xaxis=NOGRID(nticks=12),
            yaxis=GRID(range=[0,110], title="Congestion %", title_font=dict(size=9,color="#445566")),
            yaxis2=dict(overlaying="y", side="right", range=[0,100], tickfont=dict(family="JetBrains Mono",size=9,color="#556677"), showgrid=False,
                        title="Speed km/h", title_font=dict(size=9,color="#445566")),
            yaxis3=dict(overlaying="y", side="left", range=[0,6000], showgrid=False, showticklabels=False),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="sh">🗺️ INTERSECTION CONGESTION</div>', unsafe_allow_html=True)
        ints = traffic["intersections"]
        fig2 = go.Figure(go.Bar(
            x=[i["name"] for i in ints],
            y=[i["congestion"] for i in ints],
            marker=dict(
                color=[i["congestion"] for i in ints],
                colorscale=[[0,"#00ff88"],[0.4,"#ffaa00"],[1,"#ff3060"]],
                cmin=0, cmax=100,
                line=dict(color="rgba(0,0,0,.4)", width=1)
            ),
            text=[f"{i['congestion']}%" for i in ints],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=9, color="#667788"),
            customdata=[[i["volume"], i["avg_speed"]] for i in ints],
            hovertemplate="<b>%{x}</b><br>Congestion: %{y}%<br>Volume: %{customdata[0]} veh/hr<br>Speed: %{customdata[1]} km/h<extra></extra>"
        ))
        fig2.update_layout(**PLOT_LAYOUT, height=200,
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(family="JetBrains Mono",size=9,color="#556677")),
            yaxis=GRID(range=[0,125]),
            showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        # 6-hour prediction
        st.markdown('<div class="sh">🔮 6-HOUR PREDICTION</div>', unsafe_allow_html=True)
        fut_hrs = [(datetime.now() + timedelta(hours=i)).strftime("%H:%M") for i in range(1, 7)]
        fut_vals = []
        for i in range(6):
            h = (datetime.now().hour + i + 1) % 24
            r_am = math.exp(-0.5 * ((h-8.5)/1.3)**2)
            r_pm = math.exp(-0.5 * ((h-18.0)/1.5)**2)
            pred = max(0, min(100, int(25 + (r_am + r_pm)*58 + random.Random(int(lat+lon)+i).randint(-6,6))))
            fut_vals.append(pred)
        st.markdown('<div class="pred-band">', unsafe_allow_html=True)
        for fh, fv in zip(fut_hrs, fut_vals):
            fc_p = "var(--red)" if fv > 70 else "var(--amber)" if fv > 40 else "var(--green)"
            st.markdown(f"""<div class="pred-cell">
              <div style="font-family:'JetBrains Mono',monospace;font-size:.6rem;color:var(--lo);">{fh}</div>
              <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:700;color:{fc_p};margin:4px 0;">{fv}</div>
              <span class="b {ti_badge(fv)}" style="font-size:.55rem;">{ti_label(fv)}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sh">🌫️ AIR QUALITY</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="nx-card {aqi_cls}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <div style="font-family:'Orbitron',sans-serif;font-size:2.2rem;font-weight:700;color:{aqi_c};">{aqi_val or 'N/A'}</div>
            <span class="b {aqi_bdg}">{aqi_lbl}</span>
          </div>
          {''.join([
            f'<div class="cmp"><span>{k}</span><span style="color:#ddeeff;">{v:.1f} µg/m³</span></div>'
            for k,v in [("PM2.5",pm25),("PM10",pm10),("NO₂",no2),("Ozone",ozone)]
          ])}
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sh">⚠️ LIVE INCIDENTS</div>', unsafe_allow_html=True)
        sev_cls = {"Low":"b-go","Medium":"b-slow","High":"b-stop"}
        for inc in traffic["incidents"][:5]:
            st.markdown(f"""
            <div class="inc">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-weight:600;font-size:.82rem;">{inc['type']}</span>
                <span class="b {sev_cls[inc['severity']]}">{inc['severity']}</span>
              </div>
              <div style="font-size:.72rem;color:var(--lo);font-family:'JetBrains Mono',monospace;">{inc['road']}</div>
              <div style="display:flex;justify-content:space-between;margin-top:3px;">
                <span style="font-size:.68rem;color:var(--amber);">+{inc['delay']} min delay</span>
                <span style="font-size:.65rem;color:rgba(150,180,200,.4);">{inc['reported']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sh" style="margin-top:4px;">🏎️ SPEED DISTRIBUTION</div>', unsafe_allow_html=True)
        rng_s = random.Random(int(lat*10+lon*10+datetime.now().hour))
        slow = rng_s.randint(10,25); mod = rng_s.randint(25,45); fast = 100-slow-mod
        fig_d = go.Figure(go.Pie(
            values=[slow,mod,fast],
            labels=["< 20 km/h","20–60 km/h","> 60 km/h"],
            hole=0.65,
            marker=dict(colors=["#ff3060","#ffaa00","#00ff88"], line=dict(color="#040810", width=3)),
            textfont=dict(family="JetBrains Mono", size=8, color="#889aaa"),
            hovertemplate="%{label}: %{value}%<extra></extra>",
        ))
        fig_d.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=0,b=0), height=155,
            legend=dict(orientation="h", y=-0.12, font=dict(size=8, color="#667788", family="JetBrains Mono")),
            annotations=[dict(text=f"<b>{fast}%</b><br><span style='font-size:10px'>FAST</span>",
                              x=0.5, y=0.5, font=dict(size=13, color="#00ff88", family="Orbitron"), showarrow=False)]
        )
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="sh">📊 DEEP ANALYTICS DASHBOARD</div>', unsafe_allow_html=True)

    a1, a2 = st.columns(2)
    with a1:
        st.markdown('<div class="sh">📡 TRAFFIC RADAR</div>', unsafe_allow_html=True)
        dirs = ["N","NE","E","SE","S","SW","W","NW"]
        seed_r = int(lat*10+lon*10+datetime.now().hour)
        radar_v = [random.Random(seed_r+i).randint(20,95) for i in range(8)]
        fig_rad = go.Figure(go.Scatterpolar(
            r=radar_v+[radar_v[0]], theta=dirs+[dirs[0]],
            fill="toself",
            line=dict(color="#00ffe1", width=2),
            fillcolor="rgba(0,255,225,0.08)",
            marker=dict(size=6, color="#00ffe1"),
            hovertemplate="%{theta}: %{r}%<extra>Congestion</extra>"
        ))
        fig_rad.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(range=[0,100], tickfont=dict(size=8,color="#445566"), gridcolor="rgba(0,255,225,0.07)"),
                angularaxis=dict(tickfont=dict(size=10,color="#667788",family="JetBrains Mono"), gridcolor="rgba(0,255,225,0.07)"),
            ),
            margin=dict(l=30,r=30,t=20,b=20), height=300, showlegend=False,
        )
        st.plotly_chart(fig_rad, use_container_width=True, config={"displayModeBar": False})

    with a2:
        st.markdown('<div class="sh">📉 SPEED vs CONGESTION CORRELATION</div>', unsafe_allow_html=True)
        sc_x = [h["congestion"] for h in traffic["history"]]
        sc_y = [h["speed"] for h in traffic["history"]]
        sc_l = [h["hour"] for h in traffic["history"]]
        coeffs = np.polyfit(sc_x, sc_y, 1)
        xl = np.linspace(0,100,50)
        yl = np.polyval(coeffs, xl)
        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=sc_x, y=sc_y, mode="markers",
            marker=dict(size=9, color=sc_x,
                colorscale=[[0,"#00ff88"],[0.5,"#ffaa00"],[1,"#ff3060"]],
                cmin=0, cmax=100, line=dict(color="#000",width=1)),
            text=sc_l,
            hovertemplate="<b>%{text}</b><br>Congestion: %{x}%<br>Speed: %{y} km/h<extra></extra>"
        ))
        fig_sc.add_trace(go.Scatter(x=xl, y=yl, mode="lines",
            line=dict(color="rgba(0,255,225,0.35)",width=2,dash="dot"), showlegend=False, hoverinfo="skip"))
        r_val = np.corrcoef(sc_x, sc_y)[0,1]
        fig_sc.add_annotation(text=f"r = {r_val:.3f}", x=0.05, y=0.95, xref="paper", yref="paper",
            font=dict(size=11,color="#00ffe1",family="JetBrains Mono"), showarrow=False)
        fig_sc.update_layout(**PLOT_LAYOUT, height=300,
            xaxis=GRID(title="Congestion %", title_font=dict(size=9,color="#445566")),
            yaxis=GRID(title="Speed km/h", title_font=dict(size=9,color="#445566")),
            showlegend=False)
        st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar": False})

    a3, a4 = st.columns(2)
    with a3:
        st.markdown('<div class="sh">📊 VOLUME DISTRIBUTION BY HOUR</div>', unsafe_allow_html=True)
        fig_v = go.Figure()
        hours_v = [h["hour"] for h in traffic["history"]]
        vols_v  = [h["volume"] for h in traffic["history"]]
        fig_v.add_trace(go.Bar(
            x=hours_v, y=vols_v,
            marker=dict(
                color=vols_v, colorscale=[[0,"#0a2040"],[0.5,"#0090ff"],[1,"#00ffe1"]],
                line=dict(color="rgba(0,0,0,.3)",width=1)
            ),
            hovertemplate="<b>%{x}</b><br>Volume: %{y} veh/hr<extra></extra>"
        ))
        fig_v.update_layout(**PLOT_LAYOUT, height=250,
            xaxis=NOGRID(nticks=12),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,255,225,0.05)", zeroline=False, tickfont=dict(family="JetBrains Mono",size=9,color="#556677")),
            showlegend=False)
        st.plotly_chart(fig_v, use_container_width=True, config={"displayModeBar": False})

    with a4:
        st.markdown('<div class="sh">🚨 INCIDENTS BY HOUR</div>', unsafe_allow_html=True)
        fig_i = go.Figure()
        inc_hrs = [h["hour"] for h in traffic["history"]]
        inc_v   = [h["incidents"] for h in traffic["history"]]
        fig_i.add_trace(go.Scatter(
            x=inc_hrs, y=inc_v,
            fill="tozeroy", mode="lines+markers",
            line=dict(color="#ff3060", width=2),
            fillcolor="rgba(255,48,96,0.08)",
            marker=dict(size=5, color="#ff3060"),
            hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>"
        ))
        fig_i.update_layout(**PLOT_LAYOUT, height=250,
            xaxis=NOGRID(nticks=12),
            yaxis=GRID(range=[0,8]),
            showlegend=False)
        st.plotly_chart(fig_i, use_container_width=True, config={"displayModeBar": False})

    # Congestion gauge
    st.markdown('<div class="sh">⚡ CURRENT CONGESTION GAUGES</div>', unsafe_allow_html=True)
    g_cols = st.columns(4)
    gauge_data = [
        ("Traffic Index", ti, 100),
        ("PM2.5 Index", min(pm25*2, 100), 100),
        ("Wind Stress", min(wind_speed*1.5, 100), 100),
        ("Weather Impact", min(precip*8+w_code*0.5, 100), 100),
    ]
    for col, (label, val, max_v) in zip(g_cols, gauge_data):
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            domain=dict(x=[0,1],y=[0,1]),
            title=dict(text=label, font=dict(size=10,color="#667788",family="JetBrains Mono")),
            number=dict(font=dict(size=20,color="#00ffe1",family="Orbitron"), suffix="%"),
            gauge=dict(
                axis=dict(range=[0,max_v], tickfont=dict(size=8,color="#445566")),
                bar=dict(color="#00ffe1" if val<50 else "#ffaa00" if val<75 else "#ff3060"),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,255,225,0.1)",
                steps=[
                    dict(range=[0,40],color="rgba(0,255,136,0.06)"),
                    dict(range=[40,70],color="rgba(255,170,0,0.06)"),
                    dict(range=[70,100],color="rgba(255,48,96,0.06)"),
                ],
                threshold=dict(line=dict(color="#ff3060",width=2), thickness=0.75, value=ti_crit),
            )
        ))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=10,t=30,b=10), height=180)
        col.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

    # Road flow waterfall
    st.markdown('<div class="sh">🛣️ ROAD SEGMENT FLOW ANALYSIS</div>', unsafe_allow_html=True)
    rf = traffic["road_flows"]
    df_rf = pd.DataFrame(rf)
    fig_rf = go.Figure()
    fig_rf.add_trace(go.Bar(name="Volume (veh/hr)", x=df_rf["road"], y=df_rf["volume"],
        marker_color="rgba(0,144,255,0.6)", yaxis="y"))
    fig_rf.add_trace(go.Scatter(name="Congestion %", x=df_rf["road"], y=df_rf["congestion"],
        mode="lines+markers", line=dict(color="#00ffe1",width=2),
        marker=dict(size=7,color=df_rf["congestion"].tolist(),
            colorscale=[[0,"#00ff88"],[0.5,"#ffaa00"],[1,"#ff3060"]],cmin=0,cmax=100),
        yaxis="y2"))
    fig_rf.update_layout(**PLOT_LAYOUT, height=280,
        legend=dict(orientation="h",y=1.08,font=dict(size=9,color="#667788")),
        xaxis=NOGRID(tickangle=-30),
        yaxis=GRID(title="Volume", title_font=dict(size=9,color="#445566")),
        yaxis2=dict(overlaying="y",side="right",range=[0,110],showgrid=False,tickfont=dict(family="JetBrains Mono",size=9,color="#556677"),
            title="Congestion %",title_font=dict(size=9,color="#445566")),
        barmode="group")
    st.plotly_chart(fig_rf, use_container_width=True, config={"displayModeBar": False})

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: ROAD NETWORK
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="sh">🗺️ ROAD NETWORK STATUS</div>', unsafe_allow_html=True)

    r1, r2 = st.columns([2, 1])
    with r1:
        # Simulated map using scatter on a grid
        st.markdown('<div class="sh">📍 INTERSECTION CONGESTION MAP</div>', unsafe_allow_html=True)
        rng_m = random.Random(int(lat*100+lon*100))
        map_data = []
        for inter in traffic["intersections"]:
            map_data.append({
                "name": inter["name"],
                "lat": lat + rng_m.uniform(-0.08, 0.08),
                "lon": lon + rng_m.uniform(-0.08, 0.08),
                "congestion": inter["congestion"],
                "phase": inter["phase"],
                "volume": inter["volume"],
                "speed": inter["avg_speed"],
            })
        df_map = pd.DataFrame(map_data)

        # Build color list from congestion values
        def cong_to_color(c):
            if c < 40:   return "#00ff88"
            elif c < 70: return "#ffaa00"
            else:        return "#ff3060"

        # Scale marker sizes from volume
        vols = [d["volume"] for d in map_data]
        v_min, v_max = min(vols), max(vols) if max(vols) > min(vols) else min(vols)+1
        sizes = [12 + int((v - v_min) / (v_max - v_min) * 24) for v in vols]

        fig_map = go.Figure()

        # Main intersection bubbles
        fig_map.add_trace(go.Scatter(
            x=[d["lon"] for d in map_data],
            y=[d["lat"] for d in map_data],
            mode="markers+text",
            marker=dict(
                size=sizes,
                color=[d["congestion"] for d in map_data],
                colorscale=[[0,"#00ff88"],[0.4,"#ffaa00"],[1,"#ff3060"]],
                cmin=0, cmax=100,
                showscale=True,
                colorbar=dict(
                    title="Cong %",
                    thickness=12, len=0.7,
                    tickfont=dict(family="JetBrains Mono",size=8,color="#667788"),
                    title_font=dict(size=9,color="#667788"),
                ),
                line=dict(color="rgba(0,0,0,0.4)", width=1),
                opacity=0.85,
            ),
            text=[d["name"].split("×")[0] for d in map_data],
            textposition="top center",
            textfont=dict(family="JetBrains Mono", size=8, color="#889aaa"),
            customdata=[[d["name"], d["congestion"], d["volume"], d["speed"]] for d in map_data],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Congestion: %{customdata[1]}%<br>"
                "Volume: %{customdata[2]} veh/hr<br>"
                "Speed: %{customdata[3]} km/h<extra></extra>"
            ),
            showlegend=False,
        ))

        # Incident markers
        for inc in traffic["incidents"][:5]:
            fig_map.add_trace(go.Scatter(
                x=[lon + inc["lon_offset"]],
                y=[lat + inc["lat_offset"]],
                mode="markers",
                marker=dict(symbol="x", size=14, color="#ff3060",
                            line=dict(width=2, color="#ff6080")),
                showlegend=False,
                hovertemplate=f"{inc['type']}<br>{inc['road']}<br>+{inc['delay']}min<extra></extra>",
            ))

        fig_map.update_layout(
            **PLOT_LAYOUT,
            height=400,
            xaxis=dict(
                title="Longitude",
                showgrid=True, gridcolor="rgba(0,255,225,0.05)", zeroline=False,
                tickfont=dict(family="JetBrains Mono", size=9, color="#556677"),
                title_font=dict(size=9, color="#445566"),
            ),
            yaxis=dict(
                title="Latitude",
                showgrid=True, gridcolor="rgba(0,255,225,0.05)", zeroline=False,
                tickfont=dict(family="JetBrains Mono", size=9, color="#556677"),
                title_font=dict(size=9, color="#445566"),
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

    with r2:
        st.markdown('<div class="sh">🛣️ ROAD STATUS TABLE</div>', unsafe_allow_html=True)
        status_colors = {"FLOWING":"var(--green)","MODERATE":"var(--amber)","HEAVY":"var(--red)","BLOCKED":"var(--red)"}
        for rf_item in traffic["road_flows"][:12]:
            sc = status_colors.get(rf_item["status"], "var(--c)")
            st.markdown(f"""
            <div style="padding:7px 0;border-bottom:1px solid rgba(0,255,225,0.07);">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#aaccdd;">{rf_item['road']}</span>
                <span style="font-size:.65rem;color:{sc};font-family:'JetBrains Mono',monospace;font-weight:700;">{rf_item['status']}</span>
              </div>
              <div style="display:flex;gap:12px;margin-top:3px;">
                <span style="font-size:.62rem;color:var(--lo);">{rf_item['congestion']}% cong</span>
                <span style="font-size:.62rem;color:var(--lo);">{rf_item['speed']} km/h</span>
                <span style="font-size:.62rem;color:var(--lo);">{rf_item['volume']} veh/hr</span>
              </div>
            </div>""", unsafe_allow_html=True)

    # Heatmap
    st.markdown('<div class="sh" style="margin-top:18px;">🔥 INTERSECTION FLOW HEATMAP</div>', unsafe_allow_html=True)
    ints_n = [i["name"] for i in traffic["intersections"]]
    metrics_n = ["Congestion", "Speed Index", "Volume Index", "Wait Time"]
    heat_m = []
    for inter in traffic["intersections"]:
        heat_m.append([
            inter["congestion"],
            100 - inter["congestion"],
            min(100, inter["volume"]//18),
            inter["wait_time"],
        ])
    fig_hm = go.Figure(go.Heatmap(
        z=np.array(heat_m).T.tolist(),
        x=ints_n, y=metrics_n,
        colorscale=[[0,"#0a1525"],[0.3,"#0090ff"],[0.6,"#00ffe1"],[1,"#ff3060"]],
        hovertemplate="<b>%{x}</b><br>%{y}: %{z}<extra></extra>",
        colorbar=dict(tickfont=dict(family="JetBrains Mono",size=8,color="#667788"))
    ))
    fig_hm.update_layout(**PLOT_LAYOUT, height=250,
        xaxis=NOGRID(),
        yaxis=NOGRID())
    st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: WEATHER IMPACT
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    w1, w2 = st.columns(2)
    with w1:
        st.markdown('<div class="sh">🌧️ 48H WEATHER FORECAST</div>', unsafe_allow_html=True)
        if forecast_data and "hourly" in forecast_data:
            hly = forecast_data["hourly"]
            n = min(48, len(hly["time"]))
            df_fc = pd.DataFrame({
                "time": [t[11:16] for t in hly["time"][:n]],
                "precip": hly["precipitation_probability"][:n],
                "wind": hly["wind_speed_10m"][:n],
                "temp": hly["temperature_2m"][:n],
                "vis": [v/1000 for v in hly["visibility"][:n]],
            })
            fig_wf = go.Figure()
            fig_wf.add_trace(go.Bar(x=df_fc["time"], y=df_fc["precip"], name="Rain Prob %",
                marker_color="rgba(0,144,255,0.5)", hovertemplate="%{x}: %{y}%<extra>Rain</extra>"))
            fig_wf.add_trace(go.Scatter(x=df_fc["time"], y=df_fc["wind"], name="Wind km/h", yaxis="y2",
                line=dict(color="#ffaa00",width=2), hovertemplate="%{x}: %{y}<extra>Wind</extra>"))
            fig_wf.add_trace(go.Scatter(x=df_fc["time"], y=df_fc["temp"], name="Temp °C", yaxis="y3",
                line=dict(color="#ff3060",width=1.5,dash="dot"), hovertemplate="%{x}: %{y}°C<extra>Temp</extra>"))
            fig_wf.update_layout(**PLOT_LAYOUT, height=280,
                legend=dict(orientation="h",y=1.1,font=dict(size=9,color="#667788")),
                xaxis=NOGRID(nticks=16,tickangle=-45),
                yaxis=GRID(range=[0,110]),
                yaxis2=TICK(overlaying="y",side="right",showgrid=False),
                yaxis3=dict(overlaying="y",side="right",showgrid=False,showticklabels=False),
            )
            st.plotly_chart(fig_wf, use_container_width=True, config={"displayModeBar": False})

    with w2:
        st.markdown('<div class="sh">🌡️ 7-DAY TEMPERATURE & PRECIP</div>', unsafe_allow_html=True)
        if weather_data and "daily" in weather_data:
            dl = weather_data["daily"]
            n7 = len(dl["time"])
            df_7 = pd.DataFrame({
                "date": dl["time"],
                "max_t": dl["temperature_2m_max"],
                "min_t": dl["temperature_2m_min"],
                "precip": dl["precipitation_sum"],
                "wind_max": dl["wind_speed_10m_max"],
            })
            fig_7 = go.Figure()
            fig_7.add_trace(go.Scatter(x=df_7["date"],y=df_7["max_t"],name="Max Temp",
                line=dict(color="#ff3060",width=2),fill=None,
                hovertemplate="%{x}: %{y}°C<extra>Max</extra>"))
            fig_7.add_trace(go.Scatter(x=df_7["date"],y=df_7["min_t"],name="Min Temp",
                line=dict(color="#0090ff",width=2),
                fill="tonexty",fillcolor="rgba(0,144,255,0.08)",
                hovertemplate="%{x}: %{y}°C<extra>Min</extra>"))
            fig_7.add_trace(go.Bar(x=df_7["date"],y=df_7["precip"],name="Precip mm",
                marker_color="rgba(0,255,225,0.3)",yaxis="y2",
                hovertemplate="%{x}: %{y}mm<extra>Precip</extra>"))
            fig_7.update_layout(**PLOT_LAYOUT, height=280,
                legend=dict(orientation="h",y=1.1,font=dict(size=9,color="#667788")),
                xaxis=NOGRID(),
                yaxis=GRID(title="Temp °C",title_font=dict(size=9,color="#445566")),
                yaxis2=dict(overlaying="y",side="right",showgrid=False,tickfont=dict(family="JetBrains Mono",size=9,color="#556677"),
                    title="Precip mm",title_font=dict(size=9,color="#445566")))
            st.plotly_chart(fig_7, use_container_width=True, config={"displayModeBar": False})

    # Weather-traffic impact matrix
    st.markdown('<div class="sh">🔗 WEATHER → TRAFFIC IMPACT MATRIX</div>', unsafe_allow_html=True)
    impact_data = {
        "Clear Sky":     [0, 0, 0, 0, 0],
        "Light Rain":    [20, 15, 10, 5, 12],
        "Heavy Rain":    [45, 38, 30, 20, 35],
        "Fog":           [35, 42, 50, 18, 30],
        "Thunderstorm":  [55, 60, 65, 40, 55],
        "Snow":          [70, 75, 80, 60, 68],
        "High Wind":     [15, 20, 25, 10, 18],
    }
    impact_metrics = ["Speed Loss", "Capacity Drop", "Incident Risk", "Visibility Impact", "Delay Index"]
    fig_imp = go.Figure(go.Heatmap(
        z=list(impact_data.values()),
        x=impact_metrics,
        y=list(impact_data.keys()),
        colorscale=[[0,"#0a1525"],[0.3,"#004488"],[0.6,"#ffaa00"],[1,"#ff3060"]],
        zmin=0, zmax=80,
        text=[[f"{v}%" for v in row] for row in impact_data.values()],
        texttemplate="%{text}",
        textfont=dict(size=9,color="white",family="JetBrains Mono"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z}%<extra></extra>",
        colorbar=dict(tickfont=dict(family="JetBrains Mono",size=8,color="#667788"))
    ))
    fig_imp.update_layout(**PLOT_LAYOUT, height=280,
        xaxis=NOGRID(),
        yaxis=NOGRID())
    st.plotly_chart(fig_imp, use_container_width=True, config={"displayModeBar": False})

    # AQI trend
    if aq_data and "hourly" in aq_data:
        st.markdown('<div class="sh">🌫️ AQI 24H TREND</div>', unsafe_allow_html=True)
        aq_h = aq_data["hourly"]
        n_aq = min(24, len(aq_h.get("time",[])))
        if n_aq > 0:
            df_aq = pd.DataFrame({
                "time": [t[11:16] for t in aq_h["time"][:n_aq]],
                "aqi":  aq_h.get("us_aqi",  [0]*n_aq)[:n_aq],
                "pm25": aq_h.get("pm2_5",   [0]*n_aq)[:n_aq],
                "pm10": aq_h.get("pm10",    [0]*n_aq)[:n_aq],
            })
            fig_aq = go.Figure()
            fig_aq.add_trace(go.Scatter(x=df_aq["time"],y=df_aq["aqi"],name="US AQI",
                fill="tozeroy",line=dict(color=aqi_c,width=2),fillcolor=f"rgba(0,255,225,0.06)",
                hovertemplate="%{x}: AQI %{y}<extra></extra>"))
            fig_aq.add_trace(go.Scatter(x=df_aq["time"],y=df_aq["pm25"],name="PM2.5",
                line=dict(color="#b060ff",width=1.5,dash="dot"),yaxis="y2",
                hovertemplate="%{x}: PM2.5 %{y}<extra></extra>"))
            fig_aq.add_hrect(y0=100,y1=400,fillcolor="rgba(255,48,96,0.05)",line_width=0)
            fig_aq.update_layout(**PLOT_LAYOUT, height=240,
                legend=dict(orientation="h",y=1.1,font=dict(size=9,color="#667788")),
                xaxis=NOGRID(),
                yaxis=GRID(title="AQI",title_font=dict(size=9,color="#445566")),
                yaxis2=dict(overlaying="y",side="right",showgrid=False,tickfont=dict(family="JetBrains Mono",size=9,color="#556677"),
                    title="PM2.5 µg/m³",title_font=dict(size=9,color="#445566")))
            st.plotly_chart(fig_aq, use_container_width=True, config={"displayModeBar": False})

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: AI INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    ai1, ai2 = st.columns([1.5, 1])
    with ai1:
        st.markdown('<div class="sh">🤖 AI TRAFFIC ANALYST</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(176,96,255,0.06);border:1px solid rgba(176,96,255,0.2);
                    border-radius:10px;padding:14px 16px;margin-bottom:14px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:.62rem;color:rgba(176,96,255,.6);letter-spacing:2px;margin-bottom:8px;">NEXUS AI MODULE</div>
          <div style="font-size:.8rem;color:rgba(200,220,240,.7);line-height:1.7;">
            Ask the AI analyst about current traffic conditions, route recommendations, 
            incident analysis, weather impacts, or historical patterns.
          </div>
        </div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.ai_chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg"><span style="color:#b060ff;font-family:\'JetBrains Mono\',monospace;font-size:.6rem;letter-spacing:1px;">NEXUS AI ·</span> {msg["content"]}</div>', unsafe_allow_html=True)

        user_q = st.text_input("Ask the AI Traffic Analyst…", placeholder="e.g. What's causing the congestion on Ring Road?", key="ai_input")
        acol1, acol2, acol3 = st.columns([1,1,2])
        ask_btn = acol1.button("🤖 Analyze", use_container_width=True)
        clr_btn = acol2.button("🗑️ Clear", use_container_width=True)

        # Quick prompts
        st.markdown('<div style="margin-top:8px;margin-bottom:4px;font-family:\'JetBrains Mono\',monospace;font-size:.58rem;color:var(--lo);letter-spacing:2px;">QUICK QUERIES:</div>', unsafe_allow_html=True)
        qp_cols = st.columns(5)
        quick_prompts = ["Best route now?", "Incident report", "When will it clear?", "Air quality?", "Full briefing"]
        for qcol, qp in zip(qp_cols, quick_prompts):
            if qcol.button(qp, key=f"qp_{qp}", use_container_width=True):
                st.session_state.ai_chat_history.append({"role": "user", "content": qp})
                # will be processed on next rerun via the same logic
                st.session_state["_pending_ai"] = qp
                st.rerun()

        if clr_btn:
            st.session_state.ai_chat_history = []
            st.rerun()

        # Process quick-prompt or typed query
        _pending = st.session_state.pop("_pending_ai", None)
        _effective_q = _pending or (user_q if ask_btn and user_q else None)

        if _effective_q and (not st.session_state.ai_chat_history or st.session_state.ai_chat_history[-1]["content"] != _effective_q or st.session_state.ai_chat_history[-1]["role"] != "user"):
            if not _pending:  # typed query not yet added
                st.session_state.ai_chat_history.append({"role": "user", "content": _effective_q})
        if _effective_q:
            st.session_state.ai_chat_history.append({"role": "user", "content": user_q})

            # ── Fully local AI engine — no API key needed ──────────────────
            q = user_q.lower()
            now_hr = datetime.now().hour
            peak_h = max(traffic["history"], key=lambda x: x["congestion"])
            low_h  = min(traffic["history"], key=lambda x: x["congestion"])
            worst_rd  = sorted(traffic["road_flows"], key=lambda x: -x["congestion"])[0]
            best_rd   = sorted(traffic["road_flows"], key=lambda x:  x["congestion"])[0]
            worst_int = sorted(traffic["intersections"], key=lambda x: -x["congestion"])[0]
            avg_delay = int(np.mean([i["delay"] for i in traffic["incidents"]])) if traffic["incidents"] else 0
            hrs_to_clear = max(0, int((ti - 30) / 12)) if ti > 30 else 0

            if any(w in q for w in ["route", "best way", "how to get", "path", "navigate", "travel"]):
                ai_reply = f"""**🗺️ Route Intelligence — {city}**

**Current Conditions:** TI {ti}/100 · {ti_label(ti)}

**✅ Recommended Route**
Use **{best_rd['road']}** — only {best_rd['congestion']}% congested at {best_rd['speed']} km/h avg speed.

**🚫 Avoid These Roads**
• {worst_rd['road']} — {worst_rd['congestion']}% congested, {worst_rd['speed']} km/h ({worst_rd['status']})
• {traffic['road_flows'][1]['road']} — {traffic['road_flows'][1]['congestion']}% congested

**⏱️ ETA Estimate**
• {route_dist} km route: **{eta_base + eta_delay} min** total
• Normal baseline: {eta_base} min | Traffic penalty: +{eta_delay} min
• Optimal departure: **{low_h['hour']}** (only {low_h['congestion']}% congestion)

**💡 Tip:** {'Heavy precipitation reducing traction — allow extra stopping distance.' if precip > 3 else 'Road conditions appear normal for current traffic level.'}"""

            elif any(w in q for w in ["incident", "accident", "crash", "breakdown", "emergency", "event"]):
                ai_reply = f"""**🚨 Active Incident Report — {city}**

**{len(traffic['incidents'])} incidents detected** · Average delay: +{avg_delay} min

**Incident Log:**
""" + "\n".join([
    f"• **{i['type']}** on {i['road']}\n  Severity: {i['severity']} | Delay: +{i['delay']} min | Reported: {i['reported']}"
    for i in traffic["incidents"]
]) + f"""

**Impact Analysis:**
• High-severity incidents: {sum(1 for i in traffic['incidents'] if i['severity']=='High')}
• Medium-severity incidents: {sum(1 for i in traffic['incidents'] if i['severity']=='Medium')}
• Total delay impact: +{sum(i['delay'] for i in traffic['incidents'])} min across network

**Recommendation:** {'Activate traffic management protocols. Consider signal priority adjustments.' if any(i['severity']=='High' for i in traffic['incidents']) else 'Monitor situation — no immediate escalation required.'}"""

            elif any(w in q for w in ["air", "aqi", "pollution", "pm2", "quality", "breathe", "mask"]):
                ai_reply = f"""**🌫️ Air Quality Intelligence — {city}**

**Current AQI: {aqi_val or 'N/A'}** ({aqi_lbl})

**Pollutant Breakdown:**
• PM2.5: {pm25:.1f} µg/m³ — {'⚠️ Exceeds WHO 24hr guideline of 15 µg/m³' if pm25 > 15 else '✅ Within WHO guidelines'}
• PM10: {pm10:.1f} µg/m³ — {'⚠️ Elevated' if pm10 > 45 else '✅ Acceptable'}
• NO₂: {no2:.1f} µg/m³
• Ozone: {ozone:.1f} µg/m³

**Traffic–Air Quality Link:**
• Current TI of {ti} means {'significant vehicular emissions contributing to AQI' if ti > 50 else 'moderate emission contribution from vehicles'}
• {'Heavy congestion trapping pollutants at street level' if ti > 70 else 'Normal dispersion conditions'}

**Health Recommendations:**
{'🔴 Sensitive groups should stay indoors. All commuters: wear N95 mask.' if (aqi_val or 0) > 150 else '🟡 Sensitive groups limit outdoor time. General public: acceptable for normal activity.' if (aqi_val or 0) > 100 else '🟢 Air quality is acceptable. Enjoy outdoor travel.'}"""

            elif any(w in q for w in ["weather", "rain", "wind", "temperature", "fog", "visibility", "forecast"]):
                ai_reply = f"""**🌤️ Weather Impact Analysis — {city}**

**Current Conditions:**
• {weather_desc} | {temp:.0f}°C (feels {feels_like:.0f}°C)
• Wind: {wind_speed:.0f} km/h | Precipitation: {precip:.1f} mm/hr
• Visibility: {visibility/1000:.1f} km | Humidity: {humidity:.0f}%

**Traffic Impact from Weather:**
• {'🔴 Heavy rain severely impacting road capacity — expect 35–55% delays' if precip > 8 else '🟡 Light rain adding 15–25% to journey times' if precip > 1 else '🟢 Dry conditions — weather not a significant factor'}
• {'⚠️ Strong winds may affect large vehicles on flyovers and expressways' if wind_speed > 40 else '✅ Wind conditions are acceptable'}
• {'⚠️ Reduced visibility affecting driver reaction times' if visibility < 3000 else '✅ Good visibility conditions'}

**Weather-Adjusted ETA:** {eta_base + eta_delay} min for {route_dist} km
**Weather contribution to delay:** {'~{:.0f} min'.format(eta_delay * 0.6) if precip > 2 else 'Minimal'}"""

            elif any(w in q for w in ["clear", "when", "how long", "peak", "ease", "improve", "better"]):
                ai_reply = f"""**🔮 Traffic Forecast — {city}**

**Current Status:** TI {ti}/100 ({ti_label(ti)})

**When Will It Clear?**
• Estimated improvement: **{hrs_to_clear} hour{'s' if hrs_to_clear!=1 else ''}** from now
• Target clear time: ~**{(now_hr + hrs_to_clear) % 24:02d}:00**

**Today's Traffic Profile:**
• Current hour ({now_hr:02d}:00): {ti}% congestion
• Peak today: **{peak_h['hour']}** at {peak_h['congestion']}% congestion
• Best window: **{low_h['hour']}** at {low_h['congestion']}% congestion

**6-Hour Outlook:**"""  + "\n" + "\n".join([
    f"• {(datetime.now() + timedelta(hours=i+1)).strftime('%H:%M')}: ~{max(0,min(100,int(25 + (math.exp(-0.5*((((datetime.now().hour+i+1)%24)-8.5)/1.3)**2)+math.exp(-0.5*((((datetime.now().hour+i+1)%24)-18)/1.5)**2))*58)))}%"
    for i in range(6)
]) + f"\n\n**Recommendation:** {'Wait {hrs_to_clear}h before departing if flexible.'.format(hrs_to_clear=hrs_to_clear) if ti > 60 else 'Travel now is reasonable with minor delays.'}"

            elif any(w in q for w in ["signal", "intersection", "traffic light", "junction", "phase"]):
                ai_reply = f"""**🚦 Signal Intelligence — {city}**

**Network Overview:** {len(traffic['intersections'])} monitored intersections
• Green: {sum(1 for i in traffic['intersections'] if i['phase']=='GREEN')} signals
• Yellow: {sum(1 for i in traffic['intersections'] if i['phase']=='YELLOW')} signals  
• Red: {sum(1 for i in traffic['intersections'] if i['phase']=='RED')} signals

**Most Congested Intersections:**
""" + "\n".join([
    f"• **{i['name']}** — {i['congestion']}% congested | {i['wait_time']}s avg wait | {i['volume']} veh/hr"
    for i in sorted(traffic['intersections'], key=lambda x: -x['congestion'])[:4]
]) + f"""

**Bottleneck:** {worst_int['name']} at {worst_int['congestion']}% — {'consider signal priority adjustment' if worst_int['congestion'] > 70 else 'within manageable range'}
**Total Network Volume:** {sum(i['volume'] for i in traffic['intersections']):,} vehicles/hour
**Avg Wait Time:** {int(np.mean([i['wait_time'] for i in traffic['intersections']]))}s across all signals"""

            elif any(w in q for w in ["summary", "overview", "status", "report", "briefing", "situation"]):
                ai_reply = f"""**📋 Full Traffic Briefing — {city}**
*{datetime.now().strftime('%d %b %Y, %H:%M')}*

**TRAFFIC STATUS: {ti_label(ti)} (TI {ti}/100)**

**Key Metrics:**
• Active incidents: {len(traffic['incidents'])} | Total delay impact: {sum(i['delay'] for i in traffic['incidents'])} min
• Worst road: {worst_rd['road']} at {worst_rd['congestion']}%
• Best road: {best_rd['road']} at {best_rd['congestion']}%
• Peak today: {peak_h['hour']} ({peak_h['congestion']}%) | Off-peak: {low_h['hour']} ({low_h['congestion']}%)

**Environment:**
• Weather: {weather_desc}, {temp:.0f}°C | Precip: {precip:.1f} mm/hr
• AQI: {aqi_val or 'N/A'} ({aqi_lbl}) | Visibility: {visibility/1000:.1f} km

**ETA for {route_dist} km:** {eta_base + eta_delay} min

**Action Items:**
{'🔴 Deploy incident response to ' + traffic['incidents'][0]['road'] if any(i['severity']=='High' for i in traffic['incidents']) else '🟢 No immediate action required'}
{'⚠️ Consider public advisory for air quality' if (aqi_val or 0) > 150 else ''}
{'⚠️ Issue weather advisory for precipitation' if precip > 5 else ''}"""

            else:
                ai_reply = f"""**🤖 NEXUS AI Analysis — {city}**

**Traffic Index: {ti}/100 · {ti_label(ti)}**

**Current Situation:**
• {len(traffic['incidents'])} active incidents causing avg +{avg_delay} min delays
• Primary bottleneck: **{worst_int['name']}** at {worst_int['congestion']}% congestion
• Fastest corridor: **{best_rd['road']}** at {best_rd['speed']} km/h

**Weather:** {weather_desc}, {temp:.0f}°C | AQI: {aqi_val or 'N/A'}
**Today's peak:** {peak_h['hour']} ({peak_h['congestion']}%) | **Best time:** {low_h['hour']} ({low_h['congestion']}%)

**Recommendation:** {'Delay non-essential travel. Use ' + best_rd['road'] + '.' if ti > 70 else 'Minor delays expected. ' + best_rd['road'] + ' is your best option.' if ti > 40 else 'Normal conditions. Good time to travel.'}

*Try asking: "best route", "when will traffic clear", "incident report", "air quality", "signal status", or "full briefing"*"""

            st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

    with ai2:
        st.markdown('<div class="sh">📊 AI INSIGHTS PANEL</div>', unsafe_allow_html=True)
        
        # Automated insights
        insights = []
        peak_h = max(traffic["history"], key=lambda x: x["congestion"])
        low_h  = min(traffic["history"], key=lambda x: x["congestion"])
        
        if ti > ti_crit:
            insights.append(("🚨", "Critical Load", f"Traffic index {ti} exceeds critical threshold. Immediate response recommended.", "red"))
        if precip > 3:
            insights.append(("🌧️", "Weather Degradation", f"{precip:.1f}mm/hr precipitation reducing road capacity by ~{int(precip*5)}%.", "amber"))
        if (aqi_val or 0) > 100:
            insights.append(("😷", "Air Quality Alert", f"AQI {aqi_val} may reduce driver comfort and reaction times.", "amber"))
        insights.append(("📈", "Peak Hour", f"Today's predicted peak at {peak_h['hour']} with {peak_h['congestion']}% congestion.", "blue"))
        insights.append(("📉", "Best Travel", f"Optimal travel window at {low_h['hour']} — only {low_h['congestion']}% congestion.", "green"))
        
        high_cong_roads = sorted(traffic["road_flows"], key=lambda x: -x["congestion"])[:2]
        insights.append(("🛣️", "Bottleneck", f"{high_cong_roads[0]['road']} at {high_cong_roads[0]['congestion']}% — primary bottleneck.", "red" if high_cong_roads[0]["congestion"]>70 else "amber"))

        cls_map = {"red":"var(--red)","amber":"var(--amber)","green":"var(--green)","blue":"var(--c2)"}
        for icon, title, msg, cls in insights:
            st.markdown(f"""
            <div class="nx-card" style="margin-bottom:10px;padding:12px 14px;border-color:rgba(0,255,225,0.1);">
              <div style="display:flex;gap:10px;align-items:flex-start;">
                <span style="font-size:1.1rem;">{icon}</span>
                <div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:{cls_map[cls]};
                              letter-spacing:1px;margin-bottom:4px;">{title}</div>
                  <div style="font-size:.75rem;color:rgba(180,210,240,.7);line-height:1.5;">{msg}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Confidence scores
        st.markdown('<div class="sh" style="margin-top:8px;">📐 MODEL CONFIDENCE</div>', unsafe_allow_html=True)
        for metric, conf in [("Congestion Prediction", 87), ("Incident Probability", 72), ("ETA Accuracy", 81), ("Weather Correlation", 91)]:
            st.markdown(f"""
            <div style="margin-bottom:8px;">
              <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:.65rem;color:var(--lo);margin-bottom:2px;">
                <span>{metric}</span><span style="color:var(--c);">{conf}%</span>
              </div>
              <div class="pb-bg"><div class="pb-fg" style="width:{conf}%;background:linear-gradient(90deg,#0090ff,#00ffe1);"></div></div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6: SIGNAL CONTROL
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    sig1, sig2, sig3 = st.columns([1, 2, 1])

    with sig1:
        st.markdown('<div class="sh">🚦 MASTER SIGNAL</div>', unsafe_allow_html=True)
        components.html(traffic_signal_html(sig_phase, sig_cd, ti), height=320)

        st.markdown('<div class="sh" style="margin-top:12px;">⚙️ SIGNAL CONFIG</div>', unsafe_allow_html=True)
        cycle_len = st.slider("Cycle Length (s)", 30, 180, 90)
        green_pct = st.slider("Green Phase %", 20, 70, 50)
        adaptive  = st.toggle("Adaptive Timing", value=True)
        if adaptive:
            st.markdown(f'<div class="b b-go">AUTO-ADJUSTED TO TI {ti}</div>', unsafe_allow_html=True)

    with sig2:
        st.markdown('<div class="sh">🔁 ALL INTERSECTION STATUS</div>', unsafe_allow_html=True)
        sc_cols = st.columns(3)
        for idx, inter in enumerate(traffic["intersections"]):
            p = inter["phase"]
            pc = {"RED":"#ff3060","YELLOW":"#ffaa00","GREEN":"#00ff88"}[p]
            sc_cols[idx % 3].markdown(f"""
            <div class="nx-card" style="padding:12px;text-align:center;margin-bottom:8px;">
              <div style="width:36px;height:36px;border-radius:50%;background:{pc};
                          margin:0 auto 8px;box-shadow:0 0 15px {pc}88,0 0 30px {pc}44;"></div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#aaccdd;margin-bottom:4px;">{inter['name']}</div>
              <div style="font-size:.68rem;color:{pc};font-weight:700;">{p}</div>
              <div style="font-size:.62rem;color:var(--lo);margin-top:2px;">{inter['congestion']}% · {inter['wait_time']}s wait</div>
            </div>""", unsafe_allow_html=True)

        # Phase timeline
        st.markdown('<div class="sh" style="margin-top:12px;">⏱️ SIGNAL CYCLE VISUALIZATION</div>', unsafe_allow_html=True)
        phases_d  = [green_pct, 11, 100-green_pct-11]
        phases_l  = ["GREEN", "YELLOW", "RED"]
        phases_c  = ["#00ff88", "#ffaa00", "#ff3060"]
        fig_ph = go.Figure(go.Bar(
            x=phases_d, y=["Signal Cycle"]*3,
            orientation="h",
            marker_color=phases_c,
            text=[f"{p}: {d}s" for p,d in zip(phases_l,[int(cycle_len*p/100) for p in phases_d])],
            textfont=dict(family="JetBrains Mono",size=10,color="#000"),
            hovertemplate="%{text}<extra></extra>"
        ))
        fig_ph.update_layout(**PLOT_LAYOUT, height=120, barmode="stack",
            xaxis=dict(showgrid=False, zeroline=False, range=[0,100])
            yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(family="JetBrains Mono",size=9,color="#556677"), showticklabels=False),
            showlegend=False, margin=dict(l=0,r=0,t=10,b=30))
        st.plotly_chart(fig_ph, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="sh">📊 SIGNAL ANALYTICS</div>', unsafe_allow_html=True)
        total_vol = sum(i["volume"] for i in traffic["intersections"])
        avg_wait  = int(np.mean([i["wait_time"] for i in traffic["intersections"]]))
        green_int = sum(1 for i in traffic["intersections"] if i["phase"]=="GREEN")

        for label, val, sub in [
            ("Total Volume", f"{total_vol:,}", "vehicles/hour"),
            ("Avg Wait Time", f"{avg_wait}s", "per intersection"),
            ("Green Signals", f"{green_int}/{len(traffic['intersections'])}", "currently green"),
            ("Cycle Length", f"{cycle_len}s", "configured"),
        ]:
            st.markdown(f"""
            <div class="nx-card" style="padding:12px 14px;margin-bottom:10px;">
              <div class="kpi-lbl">{label}</div>
              <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:700;
                          background:linear-gradient(135deg,#00ffe1,#0090ff);
                          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{val}</div>
              <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

        # Throughput optimization score
        opt_score = max(0, 100 - ti + (green_pct - 50) * 0.5)
        st.markdown(f"""
        <div class="nx-card green" style="padding:14px;text-align:center;">
          <div class="kpi-lbl">OPTIMIZATION SCORE</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:2.5rem;font-weight:900;color:var(--green);">{opt_score:.0f}</div>
          <div class="kpi-sub">Signal efficiency index</div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7: CITY COMPARE
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    if not compare_mode or not city2:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;">
          <div style="font-size:3rem;margin-bottom:14px;">🆚</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;letter-spacing:3px;color:var(--c);">COMPARE MODE</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:var(--lo);margin-top:10px;">
            Enable "City Comparison" in the sidebar to compare two cities side-by-side.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        weather2  = fetch_weather(lat2, lon2)
        aq2       = fetch_air_quality(lat2, lon2)
        if weather2:
            cur2  = weather2["current"]
            temp2 = cur2.get("temperature_2m",0); wind2 = cur2.get("wind_speed_10m",0)
            precip2=cur2.get("precipitation",0); w2code=cur2.get("weather_code",0); vis2=cur2.get("visibility",10000)
        else:
            temp2=wind2=precip2=0; w2code=0; vis2=10000
        aqi2     = aq2["current"].get("us_aqi") if aq2 and "current" in aq2 else None
        traffic2 = simulate_traffic(lat2, lon2, w2code, precip2, wind2, aqi2)
        ti2      = traffic2["index"]

        st.markdown(f'<div class="sh">🆚 {city.upper()} vs {city2.upper()}</div>', unsafe_allow_html=True)
        
        cmp_items = [
            ("Traffic Index",  ti,                      ti2,             "%",    True),
            ("Temperature",    f"{temp:.0f}",            f"{temp2:.0f}",  "°C",   False),
            ("Wind Speed",     f"{wind_speed:.0f}",      f"{wind2:.0f}",  "km/h", True),
            ("Precipitation",  f"{precip:.1f}",          f"{precip2:.1f}","mm",   True),
            ("AQI",            str(aqi_val or "N/A"),    str(aqi2 or "N/A"),"",   True),
            ("Visibility",     f"{visibility/1000:.1f}", f"{vis2/1000:.1f}","km", False),
            ("Incidents",      len(traffic["incidents"]),len(traffic2["incidents"]),"",True),
        ]
        cmp_cols = st.columns(7)
        for col, (label, v1, v2, unit, lower_better) in zip(cmp_cols, cmp_items):
            try:
                n1, n2 = float(str(v1)), float(str(v2))
                c1 = "var(--green)" if (n1 < n2 if lower_better else n1 > n2) else "var(--red)"
                c2 = "var(--green)" if (n2 < n1 if lower_better else n2 > n1) else "var(--red)"
            except:
                c1 = c2 = "var(--c)"
            col.markdown(f"""
            <div class="nx-card" style="padding:12px;text-align:center;">
              <div class="kpi-lbl">{label}</div>
              <div style="font-family:'Orbitron',sans-serif;font-size:1.4rem;font-weight:700;color:{c1};margin-bottom:4px;">{v1}{unit}</div>
              <div style="font-size:.6rem;color:var(--lo);margin-bottom:8px;">{city.split(',')[0]}</div>
              <div style="height:1px;background:rgba(0,255,225,.08);"></div>
              <div style="font-family:'Orbitron',sans-serif;font-size:1.4rem;font-weight:700;color:{c2};margin-top:8px;margin-bottom:4px;">{v2}{unit}</div>
              <div style="font-size:.6rem;color:var(--lo);">{city2.split(',')[0]}</div>
            </div>""", unsafe_allow_html=True)

        # 24H comparison chart
        st.markdown('<div class="sh" style="margin-top:16px;">📈 24H CONGESTION COMPARISON</div>', unsafe_allow_html=True)
        h1 = traffic["history"]; h2 = traffic2["history"]
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Scatter(x=[h["hour"] for h in h1], y=[h["congestion"] for h in h1],
            name=city.split(",")[0], line=dict(color="#00ffe1",width=2.5),
            fill="tozeroy",fillcolor="rgba(0,255,225,0.06)",
            hovertemplate="<b>%{x}</b> — %{y}%<extra>"+city.split(',')[0]+"</extra>"))
        fig_cmp.add_trace(go.Scatter(x=[h["hour"] for h in h2], y=[h["congestion"] for h in h2],
            name=city2.split(",")[0], line=dict(color="#ff3060",width=2.5),
            fill="tozeroy",fillcolor="rgba(255,48,96,0.06)",
            hovertemplate="<b>%{x}</b> — %{y}%<extra>"+city2.split(',')[0]+"</extra>"))
        fig_cmp.update_layout(**PLOT_LAYOUT, height=300,
            legend=dict(orientation="h",y=1.1,font=dict(size=10,color="#667788")),
            xaxis=NOGRID(nticks=12),
            yaxis=GRID(range=[0,115]))
        st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar": False})

        # Radar comparison
        cc1, cc2 = st.columns(2)
        for col, city_n, tr in zip([cc1,cc2],[city,city2],[traffic,traffic2]):
            with col:
                st.markdown(f'<div class="sh">{city_n.split(",")[0].upper()}</div>', unsafe_allow_html=True)
                seed_rc = int(CITIES[city_n][0]*100+CITIES[city_n][1]*100+datetime.now().hour)
                rv = [random.Random(seed_rc+i).randint(20,90) for i in range(8)]
                dirs = ["N","NE","E","SE","S","SW","W","NW"]
                fig_rc = go.Figure(go.Scatterpolar(r=rv+[rv[0]],theta=dirs+[dirs[0]],fill="toself",
                    line=dict(color="#00ffe1" if col==cc1 else "#ff3060",width=2),
                    fillcolor="rgba(0,255,225,0.08)" if col==cc1 else "rgba(255,48,96,0.08)"))
                fig_rc.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    polar=dict(bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(range=[0,100],tickfont=dict(size=7,color="#445566"),gridcolor="rgba(0,255,225,0.06)"),
                        angularaxis=dict(tickfont=dict(size=9,color="#667788",family="JetBrains Mono"),gridcolor="rgba(0,255,225,0.06)")),
                    margin=dict(l=20,r=20,t=20,b=20),height=250,showlegend=False)
                st.plotly_chart(fig_rc, use_container_width=True, config={"displayModeBar": False})

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8: HISTORICAL
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown('<div class="sh">📅 HISTORICAL TRAFFIC ANALYSIS</div>', unsafe_allow_html=True)

    # Weekly heatmap
    h1, h2 = st.columns(2)
    with h1:
        st.markdown('<div class="sh">📅 7-DAY CONGESTION HEATMAP</div>', unsafe_allow_html=True)
        days = list(traffic["weekly"].keys())
        heat_hours = [f"{h:02d}:00" for h in range(24)]
        heat_data = [traffic["weekly"][d] for d in days]
        fig_hm = go.Figure(go.Heatmap(
            z=heat_data, x=heat_hours, y=days,
            colorscale=[[0,"#050e1a"],[0.25,"#00ff88"],[0.55,"#ffaa00"],[1,"#ff3060"]],
            zmin=0, zmax=100,
            hovertemplate="<b>%{y} %{x}</b><br>Congestion: %{z}%<extra></extra>",
            colorbar=dict(tickfont=dict(family="JetBrains Mono",size=8,color="#667788"))
        ))
        fig_hm.update_layout(**PLOT_LAYOUT, height=280,
            xaxis=NOGRID(nticks=12),
            yaxis=NOGRID())
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

    with h2:
        st.markdown('<div class="sh">📈 30-DAY MONTHLY TREND</div>', unsafe_allow_html=True)
        df_mt = pd.DataFrame(traffic["monthly"])
        fig_mt = go.Figure()
        fig_mt.add_trace(go.Scatter(x=df_mt["day"],y=df_mt["avg_congestion"],name="Avg Congestion",
            line=dict(color="#00ffe1",width=2),fill="tozeroy",fillcolor="rgba(0,255,225,0.06)",
            hovertemplate="Day %{x}: Avg %{y}%<extra></extra>"))
        fig_mt.add_trace(go.Scatter(x=df_mt["day"],y=df_mt["peak_congestion"],name="Peak",
            line=dict(color="#ff3060",width=1.5,dash="dot"),
            hovertemplate="Day %{x}: Peak %{y}%<extra></extra>"))
        fig_mt.add_trace(go.Bar(x=df_mt["day"],y=df_mt["incidents"],name="Incidents",
            marker_color="rgba(255,170,0,0.35)",yaxis="y2",
            hovertemplate="Day %{x}: %{y} incidents<extra></extra>"))
        fig_mt.update_layout(**PLOT_LAYOUT, height=280,
            legend=dict(orientation="h",y=1.1,font=dict(size=9,color="#667788")),
            xaxis=NOGRID(title="Day of Month",title_font=dict(size=9,color="#445566")),
            yaxis=GRID(range=[0,110]),
            yaxis2=dict(overlaying="y",side="right",showgrid=False,tickfont=dict(family="JetBrains Mono",size=9,color="#556677"),range=[0,50]))
        st.plotly_chart(fig_mt, use_container_width=True, config={"displayModeBar": False})

    # Day-of-week analysis
    st.markdown('<div class="sh">📊 DAY-OF-WEEK AVERAGE CONGESTION</div>', unsafe_allow_html=True)
    dow_avgs = {day: int(np.mean(vals)) for day, vals in traffic["weekly"].items()}
    dow_peaks = {day: max(vals) for day, vals in traffic["weekly"].items()}
    fig_dow = go.Figure()
    fig_dow.add_trace(go.Bar(x=list(dow_avgs.keys()), y=list(dow_avgs.values()), name="Daily Average",
        marker=dict(color=list(dow_avgs.values()),
            colorscale=[[0,"#00ff88"],[0.4,"#ffaa00"],[1,"#ff3060"]],cmin=0,cmax=80,
            line=dict(color="rgba(0,0,0,.3)",width=1)),
        text=[f"{v}%" for v in dow_avgs.values()],textposition="outside",
        textfont=dict(family="JetBrains Mono",size=10,color="#667788"),
        hovertemplate="<b>%{x}</b><br>Avg: %{y}%<extra></extra>"))
    fig_dow.add_trace(go.Scatter(x=list(dow_peaks.keys()),y=list(dow_peaks.values()),name="Daily Peak",
        mode="markers+lines",line=dict(color="#ff3060",width=1.5,dash="dot"),
        marker=dict(size=8,color="#ff3060"),
        hovertemplate="<b>%{x}</b><br>Peak: %{y}%<extra></extra>"))
    fig_dow.update_layout(**PLOT_LAYOUT, height=270,
        legend=dict(orientation="h",y=1.08,font=dict(size=9,color="#667788")),
        xaxis=NOGRID(),
        yaxis=GRID(range=[0,110]),
        showlegend=True)
    st.plotly_chart(fig_dow, use_container_width=True, config={"displayModeBar": False})

    # Hour-by-hour table for selected day
    st.markdown('<div class="sh">🔍 HOURLY DETAIL</div>', unsafe_allow_html=True)
    sel_day = st.selectbox("Select Day", list(traffic["weekly"].keys()), index=datetime.now().weekday() % 7)
    day_data = []
    for h_idx, cng in enumerate(traffic["weekly"][sel_day]):
        spd = max(8, 90 - int(cng * 0.82))
        day_data.append({"Hour": f"{h_idx:02d}:00", "Congestion": cng, "Avg Speed": spd,
                         "Status": ti_label(cng), "Volume Est.": int(500+cng*20)})
    df_day = pd.DataFrame(day_data)
    st.dataframe(
        df_day.style
            .background_gradient(subset=["Congestion"], cmap="RdYlGn_r", vmin=0, vmax=100)
            .background_gradient(subset=["Avg Speed"], cmap="RdYlGn", vmin=10, vmax=90),
        use_container_width=True, height=300,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 9: ALERTS & LOGS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    al1, al2 = st.columns([1.6, 1])

    with al1:
        st.markdown('<div class="sh">🔔 ACTIVE ALERTS</div>', unsafe_allow_html=True)
        
        alerts = []
        if ti >= ti_crit:
            alerts.append(("CRITICAL", "🚨", f"Traffic Index {ti} — Critical congestion city-wide", "red", datetime.now().strftime("%H:%M:%S")))
        elif ti >= ti_warn:
            alerts.append(("WARNING", "⚠️", f"Traffic Index {ti} — Elevated congestion", "amber", datetime.now().strftime("%H:%M:%S")))
        if (aqi_val or 0) > 150:
            alerts.append(("CRITICAL", "😷", f"AQI {aqi_val} — Unhealthy air quality", "red", datetime.now().strftime("%H:%M:%S")))
        if precip > 5:
            alerts.append(("WARNING", "🌧️", f"Heavy precipitation {precip:.1f}mm/hr", "amber", datetime.now().strftime("%H:%M:%S")))
        for inc in traffic["incidents"]:
            if inc["severity"] == "High":
                alerts.append(("INCIDENT", "🚗", f"{inc['type']} on {inc['road']} — +{inc['delay']}min", "red", inc["reported"]))
        if not alerts:
            alerts.append(("INFO", "✅", "All systems nominal — No active alerts", "green", datetime.now().strftime("%H:%M:%S")))

        for severity, icon, msg, cls, ts in alerts:
            cls_map2 = {"red":"alert-crit","amber":"alert-warn","green":"alert-info"}
            sc_map = {"CRITICAL":"b-stop","WARNING":"b-slow","INCIDENT":"b-stop","INFO":"b-go"}
            st.markdown(f"""
            <div class="alert {cls_map2.get(cls,'alert-info')}" style="margin-bottom:8px;">
              <span style="font-size:1.2rem;">{icon}</span>
              <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;font-weight:700;color:{'var(--red)' if cls=='red' else 'var(--amber)' if cls=='amber' else 'var(--green)'};">
                    {msg}
                  </div>
                  <span class="b {sc_map.get(severity,'b-info')}" style="font-size:.58rem;white-space:nowrap;margin-left:8px;">{severity}</span>
                </div>
                <div style="font-size:.62rem;color:rgba(150,180,200,.4);margin-top:3px;font-family:'JetBrains Mono',monospace;">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Incident timeline
        st.markdown('<div class="sh" style="margin-top:16px;">📋 INCIDENT LOG</div>', unsafe_allow_html=True)
        df_inc = pd.DataFrame(traffic["incidents"])
        if not df_inc.empty:
            df_inc["time"] = [f"{random.Random(i).randint(0,59):02d}:{random.Random(i+1).randint(0,59):02d}" for i in range(len(df_inc))]
            st.dataframe(df_inc[["type","road","severity","delay","reported","time"]].rename(columns={
                "type":"Incident","road":"Road","severity":"Severity","delay":"Delay (min)","reported":"Reported","time":"Time"
            }), use_container_width=True, height=250)

    with al2:
        st.markdown('<div class="sh">📊 ALERT STATISTICS</div>', unsafe_allow_html=True)
        
        sev_counts = {"High":0,"Medium":0,"Low":0}
        for inc in traffic["incidents"]:
            sev_counts[inc["severity"]] = sev_counts.get(inc["severity"],0) + 1
        
        fig_sev = go.Figure(go.Pie(
            values=list(sev_counts.values()),
            labels=list(sev_counts.keys()),
            hole=0.55,
            marker=dict(colors=["#ff3060","#ffaa00","#00ff88"],line=dict(color="#040810",width=3)),
            textfont=dict(family="JetBrains Mono",size=9),
            hovertemplate="%{label}: %{value}<extra></extra>"
        ))
        fig_sev.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=0,b=0),height=180,
            legend=dict(orientation="h",y=-0.1,font=dict(size=8,color="#667788",family="JetBrains Mono")),
            annotations=[dict(text="SEVERITY",x=0.5,y=0.5,font=dict(size=9,color="#667788",family="JetBrains Mono"),showarrow=False)])
        st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="sh">🚨 INCIDENT TYPE BREAKDOWN</div>', unsafe_allow_html=True)
        type_counts = {}
        for inc in traffic["incidents"]:
            t = inc["type"].split(" ",1)[1] if " " in inc["type"] else inc["type"]
            type_counts[t] = type_counts.get(t,0) + 1
        fig_tc = go.Figure(go.Bar(
            x=list(type_counts.values()), y=list(type_counts.keys()),
            orientation="h",
            marker=dict(color=list(type_counts.values()),
                colorscale=[[0,"#004488"],[1,"#ff3060"]],
                line=dict(color="rgba(0,0,0,.3)",width=1)),
            hovertemplate="%{y}: %{x}<extra></extra>"
        ))
        fig_tc.update_layout(**PLOT_LAYOUT,height=220,
            xaxis=NOGRID(),
            yaxis=NOGRID(),
            showlegend=False)
        st.plotly_chart(fig_tc, use_container_width=True, config={"displayModeBar": False})

        # System status
        st.markdown('<div class="sh">🖥️ SYSTEM STATUS</div>', unsafe_allow_html=True)
        systems = [
            ("Weather API", "ONLINE", "green"),
            ("Air Quality API", "ONLINE" if aq_data else "DEGRADED", "green" if aq_data else "amber"),
            ("Traffic Engine", "ONLINE", "green"),
            ("AI Module", "ONLINE", "green"),
            ("TomTom Live", "OFFLINE" if not tomtom_key else "ONLINE", "red" if not tomtom_key else "green"),
            ("Alert System", "ONLINE", "green"),
        ]
        for sys_n, status, cls in systems:
            sc = {"green":"var(--green)","amber":"var(--amber)","red":"var(--red)"}[cls]
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;
                        border-bottom:1px solid rgba(0,255,225,0.06);
                        font-family:'JetBrains Mono',monospace;font-size:.68rem;">
              <span style="color:#aaccdd;">{sys_n}</span>
              <span style="color:{sc};font-weight:700;">{status}</span>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 10: CONFIG & EXPORT
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[9]:
    cfg1, cfg2, cfg3 = st.columns(3)

    with cfg1:
        st.markdown('<div class="sh">📊 24H TRAFFIC HISTORY EXPORT</div>', unsafe_allow_html=True)
        df_exp = pd.DataFrame(traffic["history"])
        df_exp.insert(0,"city",city); df_exp.insert(1,"date",datetime.now().strftime("%Y-%m-%d"))
        st.dataframe(df_exp.style.background_gradient(subset=["congestion"],cmap="RdYlGn_r"),
            use_container_width=True, height=260)
        csv1 = df_exp.to_csv(index=False).encode()
        st.download_button("⬇️ Download Traffic History CSV", csv1,
            f"nexus_traffic_{city.split(',')[0].lower()}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",
            use_container_width=True)

    with cfg2:
        st.markdown('<div class="sh">🛣️ ROAD NETWORK EXPORT</div>', unsafe_allow_html=True)
        df_rf_exp = pd.DataFrame(traffic["road_flows"])
        df_rf_exp.insert(0,"city",city); df_rf_exp.insert(1,"timestamp",datetime.now().strftime("%Y-%m-%d %H:%M"))
        st.dataframe(df_rf_exp, use_container_width=True, height=260)
        csv2 = df_rf_exp.to_csv(index=False).encode()
        st.download_button("⬇️ Download Road Network CSV", csv2,
            f"nexus_roads_{city.split(',')[0].lower()}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",
            use_container_width=True)

    with cfg3:
        st.markdown('<div class="sh">⚠️ INCIDENTS EXPORT</div>', unsafe_allow_html=True)
        df_inc_exp = pd.DataFrame(traffic["incidents"])
        df_inc_exp.insert(0,"city",city); df_inc_exp.insert(1,"timestamp",datetime.now().strftime("%Y-%m-%d %H:%M"))
        st.dataframe(df_inc_exp, use_container_width=True, height=260)
        csv3 = df_inc_exp.to_csv(index=False).encode()
        st.download_button("⬇️ Download Incidents CSV", csv3,
            f"nexus_incidents_{city.split(',')[0].lower()}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",
            use_container_width=True)

    # Full JSON export
    st.markdown('<div class="sh" style="margin-top:16px;">📦 FULL DATA EXPORT (JSON)</div>', unsafe_allow_html=True)
    export_payload = {
        "meta": {"city": city, "lat": lat, "lon": lon, "timestamp": datetime.now().isoformat(), "version": "3.0"},
        "traffic": {"index": ti, "label": ti_label(ti), "incidents": traffic["incidents"],
                    "road_flows": traffic["road_flows"], "intersections": traffic["intersections"]},
        "weather": {"temperature": temp, "feels_like": feels_like, "humidity": humidity,
                    "wind_speed": wind_speed, "precipitation": precip, "description": weather_desc, "visibility": visibility},
        "air_quality": {"us_aqi": aqi_val, "pm25": pm25, "pm10": pm10, "no2": no2, "ozone": ozone},
        "eta": {"distance_km": route_dist, "base_min": eta_base, "delay_min": eta_delay, "total_min": eta_base+eta_delay},
    }
    json_exp = json.dumps(export_payload, indent=2, default=str)
    st.download_button("⬇️ Download Full JSON Report", json_exp.encode(),
        f"nexus_report_{city.split(',')[0].lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.json","application/json",
        use_container_width=False)

    # Session summary
    st.markdown('<div class="sh" style="margin-top:16px;">📋 SESSION SUMMARY</div>', unsafe_allow_html=True)
    sum_cols = st.columns(4)
    summary = [
        ("City", city, ""),
        ("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"), ""),
        ("Traffic Index", f"{ti}/100", "red" if ti>ti_crit else "amber" if ti>ti_warn else "green"),
        ("Traffic Status", ti_label(ti), ""),
        ("Active Incidents", str(len(traffic["incidents"])), ""),
        ("Peak Hour Today", max(traffic["history"],key=lambda x:x["congestion"])["hour"], ""),
        ("Max Congestion", f"{max(h['congestion'] for h in traffic['history'])}%", ""),
        ("Avg Speed", f"{int(np.mean([h['speed'] for h in traffic['history']]))} km/h", ""),
        ("AQI", str(aqi_val or "N/A"), ""),
        ("PM2.5", f"{pm25:.1f} µg/m³", ""),
        ("ETA ({route_dist}km)", f"{eta_base+eta_delay} min", ""),
        ("Data Sources Active", "3/4" if not tomtom_key else "4/4", ""),
    ]
    sc_cols = st.columns(6)
    for i, (label, val, cls) in enumerate(summary):
        vc = {"red":"var(--red)","amber":"var(--amber)","green":"var(--green)"}.get(cls,"#00ffe1")
        sc_cols[i%6].markdown(f"""
        <div class="nx-card" style="padding:10px 12px;margin-bottom:8px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:.55rem;color:var(--lo);letter-spacing:2px;margin-bottom:3px;">{label}</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:.95rem;font-weight:600;color:{vc};">{val}</div>
        </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:30px;padding:14px 0;border-top:1px solid rgba(0,255,225,0.08);
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:rgba(180,210,240,.25);letter-spacing:2px;">
    NEXUS TRAFFIC COMMAND · v3.0 · OPEN-METEO · AI-POWERED · {datetime.now().year}
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:rgba(180,210,240,.25);">
    {lat:.4f}°N · {lon:.4f}°E · NEXT REFRESH IN {refresh_rate}s
  </div>
</div>
""", unsafe_allow_html=True)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
