import streamlit as st
import random
import time
import requests
from datetime import datetime

# ════════════════════════════════════════════════════════════════════════════
# DEMO MODE CONFIGURATION
# Set to True  → uses simulated data (always works, no hardware needed)
# Set to False → reads real gas sensor data from Firebase (ESP32 hardware)
# ════════════════════════════════════════════════════════════════════════════
DEMO_MODE = False

# Paste your Firebase Realtime Database URL here (no trailing slash)
FIREBASE_URL = "https://vanguard-gas-detector-default-rtdb.asia-southeast1.firebasedatabase.app"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Venguard – Gas & Fire Monitor",
    page_icon="🛡️",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────────────────────
# BRAND PALETTE
# #4075c4  — Brand Blue       (primary accent, buttons, highlights)
# #212529  — Deep Charcoal    (main text, headings)
# #708090  — Slate Gray       (secondary text, borders, muted labels)
# #dfe0df  — Light Gray       (page background, card backgrounds)
# #ffc107  — Amber Yellow     (warning state)
# #dc3545  — Alert Red        (danger state, emergency)
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Rajdhani:wght@500;600;700&family=DM+Sans:wght@400;500;600&family=Merriweather:wght@400;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #dfe0df;
    color: #212529;
    font-size: 15px;
}

/* ── Header ── */
.header-bar {
    background: linear-gradient(135deg, #4075c4 0%, #2d5aa0 60%, #1e3f7a 100%);
    border: none;
    border-radius: 16px;
    padding: 26px 36px;
    margin-bottom: 28px;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    box-shadow: 0 4px 20px rgba(64,117,196,0.3);
}
.header-brand {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 72px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    margin: 0 !important;
    line-height: 1 !important;
    display: block !important;
}
.header-motto {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: #dfe0df;
    letter-spacing: 1.5px;
    margin: 10px 0 0 2px;
}
.header-product {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: rgba(255,255,255,0.5);
    margin: 6px 0 0 2px;
}
.header-time    { font-family: 'Rajdhani', sans-serif; font-size: 18px; color: #dfe0df; text-align: right; }
.header-refresh { font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 4px; text-align: right; }

/* ── Metric Cards ── */
.metric-card {
    background: #ffffff;
    border: 1px solid #c8c9c8;
    border-radius: 14px;
    padding: 24px 20px 20px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(33,37,41,0.08);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #4075c4, #2d5aa0);
    border-radius: 14px 14px 0 0;
}
.metric-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #708090;
    margin-bottom: 12px;
}
.metric-value {
    font-family: 'Montserrat', sans-serif;
    font-size: 62px;
    font-weight: 900;
    line-height: 1;
    color: #212529;
}
.metric-value-sm {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 800;
    line-height: 1.2;
    padding-top: 8px;
    color: #212529;
}
.metric-unit   { font-size: 14px; color: #708090; margin-top: 8px; font-weight: 500; }
.metric-source { font-size: 13px; color: #4075c4; margin-top: 8px; font-weight: 600; }

/* Status colors */
.metric-safe   { color: #198754; }
.metric-warn   { color: #ffc107; }
.metric-danger { color: #dc3545; }

/* ── Badges ── */
.badge { display:inline-block; padding:5px 14px; border-radius:20px; font-size:12px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; }
.badge-online  { background:#d1e7dd; color:#0a5c36; border:1px solid #a3cfbb; }
.badge-offline { background:#f8d7da; color:#842029; border:1px solid #f1aeb5; }

/* ── Alert Banners ── */
.alert-danger {
    background: linear-gradient(135deg, #dc3545, #a71d2a);
    border: none;
    border-radius: 12px; padding: 16px 24px;
    font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700;
    color: #ffffff; text-align: center; letter-spacing: 1.5px;
    box-shadow: 0 4px 16px rgba(220,53,69,0.4);
    animation: pulse-red 1.5s infinite;
}
.alert-warn {
    background: linear-gradient(135deg, #ffc107, #d39e00);
    border: none;
    border-radius: 12px; padding: 16px 24px;
    font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700;
    color: #212529; text-align: center; letter-spacing: 1.5px;
    box-shadow: 0 4px 16px rgba(255,193,7,0.35);
}
.alert-safe {
    background: linear-gradient(135deg, #198754, #0d6640);
    border: none;
    border-radius: 12px; padding: 16px 24px;
    font-size: 15px; font-weight: 600;
    color: #ffffff; text-align: center;
    box-shadow: 0 4px 16px rgba(25,135,84,0.25);
}
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220,53,69,0.5); }
    50%       { box-shadow: 0 0 0 12px rgba(220,53,69,0); }
}

/* ── Device Rows ── */
.device-row {
    background: #ffffff;
    border: 1px solid #c8c9c8;
    border-radius: 12px;
    padding: 14px 20px; margin-bottom: 10px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 1px 6px rgba(33,37,41,0.06);
}
.device-name     { font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 600; color: #212529; }
.device-location { font-family: 'Merriweather', serif; font-size: 14px; font-weight: 600; color: #212529; margin-top: 4px; }
.device-readings { font-size: 13px; color: #708090; margin-top: 4px; }

/* ── Section Headers ── */
.section-header {
    font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 700;
    color: #ffffff; text-transform: uppercase; letter-spacing: 2.5px;
    border-left: 4px solid #4075c4; padding-left: 12px; margin: 22px 0 14px 0;
}

/* ── Activity Log ── */
.log-entry {
    font-size: 13px; color: #708090; padding: 7px 0;
    border-bottom: 1px solid #c8c9c8; font-family: 'Courier New', monospace;
}
.log-entry span.warn { color: #b8860b; font-weight: 600; }
.log-entry span.safe { color: #198754; font-weight: 600; }
.log-entry span.crit { color: #dc3545; font-weight: bold; }

/* ── Threshold Rows ── */
.thresh-row { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #dfe0df; font-size:14px; }
.thresh-row:last-child { border-bottom:none; }

/* ── Emergency Box ── */
.emergency-box {
    background: linear-gradient(135deg, #fff5f5, #ffe0e3);
    border: 2px solid #dc3545;
    border-radius: 14px; padding: 20px; text-align: center; margin-bottom: 14px;
    box-shadow: 0 2px 12px rgba(220,53,69,0.15);
}

/* ── Threshold Box ── */
.thresh-box {
    background: #ffffff;
    border: 1px solid #c8c9c8;
    border-radius: 12px; padding: 16px 18px;
    box-shadow: 0 1px 6px rgba(33,37,41,0.06);
}

/* ── Streamlit Button ── */
.stButton > button {
    background: linear-gradient(135deg, #dc3545, #a71d2a) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important; font-weight: 700 !important;
    font-size: 17px !important; letter-spacing: 1px !important;
    padding: 12px 20px !important; width: 100% !important;
    box-shadow: 0 3px 12px rgba(220,53,69,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #bb2d3b, #8b1520) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(220,53,69,0.4) !important;
}
div[data-testid="stMetric"] { display: none; }

/* ── Responsive: Tablet ── */
@media (max-width: 900px) {
    .header-brand    { font-size: 52px !important; letter-spacing: 3px !important; }
    .header-motto    { font-size: 13px !important; }
    .header-bar      { grid-template-columns: 1fr !important; text-align: center !important; padding: 18px 20px !important; }
    .header-time, .header-refresh { text-align: center !important; }
    .metric-value    { font-size: 48px !important; }
    .metric-value-sm { font-size: 26px !important; }
    .metric-label    { font-size: 12px !important; }
    .metric-source   { font-size: 12px !important; }
    .device-name     { font-size: 15px !important; }
    .section-header  { font-size: 15px !important; }
    .alert-danger, .alert-warn, .alert-safe { font-size: 16px !important; padding: 12px 14px !important; }
}

/* ── Responsive: Mobile ── */
@media (max-width: 600px) {
    html, body, [class*="css"] { font-size: 13px !important; }
    .header-brand    { font-size: 38px !important; letter-spacing: 2px !important; }
    .header-motto    { font-size: 12px !important; letter-spacing: 1px !important; }
    .header-product  { font-size: 11px !important; }
    .header-bar      { padding: 14px 12px !important; }
    .header-time     { font-size: 14px !important; }
    .metric-card     { padding: 16px 12px !important; border-radius: 10px !important; }
    .metric-value    { font-size: 42px !important; }
    .metric-value-sm { font-size: 22px !important; }
    .metric-label    { font-size: 11px !important; letter-spacing: 1px !important; }
    .metric-unit     { font-size: 12px !important; }
    .metric-source   { font-size: 11px !important; }
    .device-row      { flex-direction: column !important; align-items: flex-start !important; gap: 8px !important; }
    .device-name     { font-size: 14px !important; }
    .device-location { font-size: 11px !important; }
    .device-readings { font-size: 11px !important; }
    .section-header  { font-size: 13px !important; letter-spacing: 1.5px !important; }
    .alert-danger, .alert-warn, .alert-safe { font-size: 13px !important; padding: 10px 12px !important; }
    .log-entry       { font-size: 11px !important; }
    .thresh-row      { font-size: 12px !important; }
    .badge           { font-size: 11px !important; padding: 4px 10px !important; }
    .stButton > button { font-size: 15px !important; padding: 10px 14px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Device definitions ─────────────────────────────────────────────────────────
DEVICES = [
    {"id": "DEV-001", "name": "Kitchen Sensor",     "location": "House – Mirpur",        "status": "online"},
    {"id": "DEV-002", "name": "Kitchen Sensor",        "location": "Restaurant – Dhanmondi","status": "online"},
    {"id": "DEV-003", "name": "Storage Sensor",      "location": "Restaurant – Gulshan",  "status": "offline"},
    {"id": "DEV-004", "name": "Living Room Sensor",  "location": "House – Uttara",        "status": "online"},
]

def sim_device_readings(devices):
    readings = []
    for d in devices:
        if d["status"] == "online":
            base_gas  = random.choice([42, 58, 310, 680])
            gas_ppm   = max(0, min(1000, base_gas + random.randint(-25, 25)))
            smoke_pct = round(random.uniform(0, 30), 1)
        else:
            gas_ppm   = None
            smoke_pct = None
        readings.append({**d, "gas_ppm": gas_ppm, "smoke_pct": smoke_pct})
    return readings

def firebase_device_readings(devices):
    """
    Reads real sensor data from Firebase (sent by the Slave ESP32).
    Falls back to simulated data if Firebase is unreachable —
    so the dashboard never breaks even if hardware/internet fails.
    """
    try:
        url = f"{FIREBASE_URL}/gasStatus.json"
        response = requests.get(url, timeout=3)
        data = response.json()

        if data is None:
            raise ValueError("No data in Firebase yet")

        gas_danger = data.get("gasDanger", False)

        # Convert the simple true/false signal into PPM-style numbers
        # so it fits the existing card/coloring logic
        if gas_danger:
            gas_ppm   = 650   # above danger threshold (500+)
            smoke_pct = 28.0
        else:
            gas_ppm   = 50    # safe baseline
            smoke_pct = 5.0

        readings = []
        for d in devices:
            if d["id"] == "DEV-001":  # the device connected to real hardware
                if d["status"] == "online":
                    readings.append({**d, "gas_ppm": gas_ppm, "smoke_pct": smoke_pct})
                else:
                    readings.append({**d, "gas_ppm": None, "smoke_pct": None})
            else:
                # Other devices remain simulated for demo richness
                if d["status"] == "online":
                    base_gas = random.choice([42, 58])
                    readings.append({**d,
                        "gas_ppm": base_gas + random.randint(-10, 10),
                        "smoke_pct": round(random.uniform(0, 15), 1)})
                else:
                    readings.append({**d, "gas_ppm": None, "smoke_pct": None})
        return readings

    except Exception as e:
        st.session_state.firebase_error = str(e)
        return sim_device_readings(devices)

def gas_cls(ppm):
    if ppm is None: return "metric-safe", "–"
    if ppm < 200:   return "metric-safe",  "SAFE"
    if ppm < 500:   return "metric-warn",  "WARNING"
    return "metric-danger", "DANGER"

def smoke_cls(pct):
    if pct is None: return "metric-safe", "–"
    if pct < 10:    return "metric-safe",  "SAFE"
    if pct < 25:    return "metric-warn",  "WARNING"
    return "metric-danger", "DANGER"

# ── Session state ──────────────────────────────────────────────────────────────
if "alert_log"      not in st.session_state: st.session_state.alert_log      = []
if "device_data"    not in st.session_state: st.session_state.device_data    = sim_device_readings(DEVICES)
if "last_refresh"   not in st.session_state: st.session_state.last_refresh   = time.time()
if "firebase_error" not in st.session_state: st.session_state.firebase_error = None

# Demo mode refreshes every 30s (slow, for showing variety)
# Live mode refreshes every 2s (fast, for real-time sensor response)
REFRESH_INTERVAL = 30 if DEMO_MODE else 2

elapsed = time.time() - st.session_state.last_refresh
if elapsed >= REFRESH_INTERVAL:
    if DEMO_MODE:
        st.session_state.device_data = sim_device_readings(DEVICES)
    else:
        st.session_state.device_data = firebase_device_readings(DEVICES)
    st.session_state.last_refresh = time.time()
    elapsed = 0

device_data  = st.session_state.device_data
now          = datetime.now().strftime("%d %b %Y  |  %H:%M:%S")
next_refresh = max(0, int(REFRESH_INTERVAL - elapsed))

# ── Aggregates ─────────────────────────────────────────────────────────────────
online_data   = [d for d in device_data if d["status"] == "online"]
online_count  = len(online_data)
worst_gas     = max(online_data, key=lambda d: d["gas_ppm"])   if online_data else None
worst_smoke   = max(online_data, key=lambda d: d["smoke_pct"]) if online_data else None
top_gas_ppm   = worst_gas["gas_ppm"]     if worst_gas   else 0
top_smoke_pct = worst_smoke["smoke_pct"] if worst_smoke else 0
top_gas_src   = f"{worst_gas['id']} · {worst_gas['name']}"     if worst_gas   else "No devices online"
top_smoke_src = f"{worst_smoke['id']} · {worst_smoke['name']}" if worst_smoke else "No devices online"
top_gas_c,   top_gas_l   = gas_cls(top_gas_ppm)
top_smoke_c, top_smoke_l = smoke_cls(top_smoke_pct)
fire_active  = top_gas_ppm >= 500 or top_smoke_pct >= 25

# ── Activity log ───────────────────────────────────────────────────────────────
if top_gas_ppm >= 500:
    st.session_state.alert_log.insert(0, f'<span class="crit">[{now}] CRITICAL: Gas {top_gas_ppm} PPM @ {top_gas_src}</span>')
elif top_gas_ppm >= 200:
    st.session_state.alert_log.insert(0, f'<span class="warn">[{now}] WARNING: Gas {top_gas_ppm} PPM @ {top_gas_src}</span>')
else:
    st.session_state.alert_log.insert(0, f'<span class="safe">[{now}] OK – Gas {top_gas_ppm} PPM | Smoke {top_smoke_pct}%</span>')
st.session_state.alert_log = st.session_state.alert_log[:20]

# ══════════════════════════════ RENDER ════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
mode_label = "🟡 DEMO MODE" if DEMO_MODE else ("🟢 LIVE" if not st.session_state.firebase_error else "🟠 LIVE (fallback)")
st.markdown(f"""
<div class="header-bar" style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;">
  <div></div>
  <div style="text-align:center;">
    <p class="header-brand">VENGUARD</p>
    <p class="header-motto">Protecting lives before danger strikes</p>
    <p class="header-product">Gas Leak & Fire Safety Monitoring — Dhaka, Bangladesh</p>
  </div>
  <div style="text-align:right;">
    <div class="header-time">🕐 {now}</div>
    <div class="header-refresh">{mode_label} &nbsp;·&nbsp; refresh in {next_refresh}s</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Metric Cards ──────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">⚠ Highest Gas Reading</div>
      <div class="metric-value {top_gas_c}">{top_gas_ppm}</div>
      <div class="metric-unit">PPM &nbsp;·&nbsp; <span class="{top_gas_c}" style="font-weight:700;">{top_gas_l}</span></div>
      <div class="metric-source">📡 {top_gas_src}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">⚠ Highest Smoke Reading</div>
      <div class="metric-value {top_smoke_c}">{top_smoke_pct}<span style="font-size:28px;">%</span></div>
      <div class="metric-unit">Density &nbsp;·&nbsp; <span class="{top_smoke_c}" style="font-weight:700;">{top_smoke_l}</span></div>
      <div class="metric-source">📡 {top_smoke_src}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    fire_label = "ACTIVE 🔴" if fire_active else "Clear ✅"
    fire_c     = "metric-danger" if fire_active else "metric-safe"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">🔥 Fire Alert</div>
      <div class="metric-value-sm {fire_c}">{fire_label}</div>
      <div class="metric-unit">System status</div>
      <div class="metric-source">Based on all online sensors</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">📶 Devices Online</div>
      <div class="metric-value metric-safe">{online_count}<span style="font-size:26px;color:#708090;">/{len(DEVICES)}</span></div>
      <div class="metric-unit">Active sensors</div>
      <div class="metric-source">{len(DEVICES)-online_count} device(s) offline</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Alert Banner ───────────────────────────────────────────────────────────────
if top_gas_ppm >= 500:
    st.markdown(f'<div class="alert-danger">⚠️ CRITICAL GAS LEAK — {top_gas_ppm} PPM @ {top_gas_src} — EVACUATE IMMEDIATELY</div>', unsafe_allow_html=True)
elif top_gas_ppm >= 200:
    st.markdown(f'<div class="alert-warn">⚠️ GAS WARNING — {top_gas_ppm} PPM @ {top_gas_src} — Check appliances</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="alert-safe">✅ All readings normal — Highest Gas: {top_gas_ppm} PPM | Highest Smoke: {top_smoke_pct}% | No active alerts</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Bottom Section ────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="section-header">Device Status</div>', unsafe_allow_html=True)
    for d in device_data:
        badge = '<span class="badge badge-online">● Online</span>' if d["status"] == "online" \
                else '<span class="badge badge-offline">● Offline</span>'
        if d["status"] == "online":
            g_c, g_l = gas_cls(d["gas_ppm"])
            s_c, s_l = smoke_cls(d["smoke_pct"])
            readings_html = f"""<div class="device-readings">
              Gas: <span class="{g_c}" style="font-weight:600;">{d['gas_ppm']} PPM ({g_l})</span>
              &nbsp;|&nbsp;
              Smoke: <span class="{s_c}" style="font-weight:600;">{d['smoke_pct']}% ({s_l})</span>
            </div>"""
        else:
            readings_html = '<div class="device-readings" style="color:#708090;">No data — device offline</div>'
        st.markdown(f"""
        <div class="device-row">
          <div>
            <div class="device-name">{d['id']} — {d['name']}</div>
            <div class="device-location">📍 {d['location']}</div>
            {readings_html}
          </div>
          {badge}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:28px;">Recent Activity Log</div>', unsafe_allow_html=True)
    log_entries = "".join([f'<div class="log-entry">{e}</div>' for e in st.session_state.alert_log])
    st.markdown(f'<div style="background:#ffffff;border:1px solid #c8c9c8;border-radius:12px;padding:14px 18px;box-shadow:0 1px 6px rgba(33,37,41,0.06);">{log_entries}</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-header">Emergency</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="emergency-box">
      <div style="font-size:40px;margin-bottom:10px;">🚨</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:18px;color:#dc3545;font-weight:700;letter-spacing:1px;">One-Tap Emergency Alert</div>
      <div style="font-size:13px;color:#708090;margin-top:8px;line-height:1.6;">
        Instantly notifies your emergency contacts & nearest fire station in Dhaka
      </div>
    </div>""", unsafe_allow_html=True)

    if st.button("🚨 SEND EMERGENCY ALERT"):
        st.markdown("""
        <div style="background:#d1e7dd;border:1px solid #a3cfbb;border-radius:10px;
                    padding:14px;text-align:center;font-size:14px;color:#0a5c36;line-height:1.8;margin-top:10px;">
          ✅ Alert sent to 3 emergency contacts<br>
          🚒 Nearest fire station notified<br>
          <span style="font-size:12px;color:#198754;">Dhaka Fire Service – Mirpur Unit</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:28px;">Thresholds</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="thresh-box">
      <div class="thresh-row"><span style="color:#708090;">Gas – Safe</span>     <span style="color:#198754;font-weight:600;">0 – 200 PPM</span></div>
      <div class="thresh-row"><span style="color:#708090;">Gas – Warning</span>  <span style="color:#b8860b;font-weight:600;">200 – 500 PPM</span></div>
      <div class="thresh-row"><span style="color:#708090;">Gas – Danger</span>   <span style="color:#dc3545;font-weight:600;">500+ PPM</span></div>
      <div class="thresh-row"><span style="color:#708090;">Smoke – Safe</span>   <span style="color:#198754;font-weight:600;">&lt; 10%</span></div>
      <div class="thresh-row"><span style="color:#708090;">Smoke – Warning</span><span style="color:#b8860b;font-weight:600;">10 – 25%</span></div>
      <div class="thresh-row"><span style="color:#708090;">Smoke – Danger</span> <span style="color:#dc3545;font-weight:600;">25%+</span></div>
    </div>""", unsafe_allow_html=True)

# ── Footer + Manual Refresh ────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, mid, _ = st.columns([1, 1, 1])
with mid:
    if st.button("🔄 Refresh Now"):
        st.session_state.device_data  = sim_device_readings(DEVICES)
        st.session_state.last_refresh = time.time()
        st.rerun()

st.markdown(f"""
<div style="text-align:center;font-size:12px;color:#708090;margin-top:20px;
            padding-top:16px;border-top:2px solid #c8c9c8;">
  <span style="color:#4075c4;font-weight:700;">VANGUARD</span>
  &nbsp;·&nbsp; Gas & Fire Safety Monitor &nbsp;·&nbsp; Dhaka, Bangladesh
  &nbsp;·&nbsp; Simulated Data Mode &nbsp;·&nbsp; Auto-refresh every 30s
</div>""", unsafe_allow_html=True)

# ── Auto-rerun every second ────────────────────────────────────────────────────
time.sleep(1)
st.rerun()
