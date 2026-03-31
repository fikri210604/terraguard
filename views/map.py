import streamlit as st
import folium
from streamlit_folium import st_folium
from utils.geo_utils import detect_geo_type
from templates.ui_map import render_floating_ui

# Activate Fullscreen CSS targeting for this page only
st.markdown('<div class="map-fullscreen-flag"></div>', unsafe_allow_html=True)

# Pastikan default target_lat dan target_lon ada
if 'target_lat' not in st.session_state:
    st.session_state.target_lat = -5.4297
if 'target_lon' not in st.session_state:
    st.session_state.target_lon = 105.2625

lokasi, geo_type, geo_warning = detect_geo_type(st.session_state.target_lat, st.session_state.target_lon)

# Render Floating Overlay UI
render_floating_ui(st.session_state.target_lat, st.session_state.target_lon, lokasi, geo_type, geo_warning)

# Render Full Width Interactive Map
m = folium.Map(location=[-4.9818, 105.0766], zoom_start=8, tiles="CartoDB positron")

# Layer Sesar Semangko
sesar_coords = [
    [-4.95, 103.95], [-5.15, 104.15], [-5.25, 104.28], 
    [-5.45, 104.50], [-5.52, 104.60], [-5.75, 104.75]
]
folium.PolyLine(
    locations=sesar_coords, color="#dc2626", weight=4, dash_array='5, 5', tooltip="Sistem Sesar Sumatera (Segmen Semangko)"
).add_to(m)

# Pin Lokasi Pengguna
folium.Marker(
    [st.session_state.target_lat, st.session_state.target_lon], popup="📌 Lokasi Lahan Incaran", icon=folium.Icon(color="blue", icon="home", prefix='fa')
).add_to(m)

# Tampilkan Peta (Mengisi seluruh layar melalui CSS Ultra-Fullscreen)
map_data = st_folium(m, width="100%", height=800, returned_objects=["last_clicked"])

# Render Floating Action Bar (Precision & Stability) inside the Map
# This replaces the hidden global one to maintain edge-to-edge look
st.markdown("""
<div style="position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%); z-index: 1001; display: flex; gap: 8px; pointer-events: none;">
    <div style="background: rgba(25, 31, 49, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 10px 20px; border-radius: 9999px; border: 1px solid rgba(0, 218, 243, 0.3); display: flex; align-items: center; gap: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--primary); box-shadow: 0 0 10px var(--primary);"></span>
            <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--on-surface-variant);">Precision: <span style="color: var(--on-surface);">0.02m</span></span>
        </div>
        <div style="height: 16px; width: 1px; background: rgba(65, 72, 75, 0.5);"></div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--secondary); box-shadow: 0 0 10px var(--secondary);"></span>
            <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--on-surface-variant);">Stability: <span style="color: var(--on-surface);">99.4%</span></span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Render Floating Action Button (FAB)
if st.button("Generate Risk Report", type="primary"):
    st.switch_page("views/report.py")

# Update State on Click
if map_data and map_data.get("last_clicked"):
    new_lat, new_lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    if new_lat != st.session_state.target_lat or new_lon != st.session_state.target_lon:
        st.session_state.target_lat, st.session_state.target_lon = new_lat, new_lon
        st.rerun()
