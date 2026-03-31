import streamlit as st
from utils.data_loader import fetch_recent_weather, prepare_prediction_features, get_disaster_stats, fetch_latest_earthquake
from utils.geo_facility import fetch_nearby_facilities
from utils.dem_loader import fetch_demnas_slope
from utils.ai_generator import predict_disaster_probability, generate_ai_recommendation
from utils.geo_utils import detect_geo_type
from templates.loading_state import AuraLoader
from templates.ui_report import (
    render_dashboard_header, render_location_summary, render_decision_box,
    render_blocked_box, render_slope_analysis_bento, render_weather_insights,
    render_infrastructure_card, render_disaster_history
)

# --- 3. INITIAL DEFAULTS ---
if 'target_lat' not in st.session_state:
    st.session_state.target_lat = -5.4297
if 'target_lon' not in st.session_state:
    st.session_state.target_lon = 105.2625

if 'analysis_results' not in st.session_state:
    with AuraLoader("Mengaktifkan TerraGuard AI Core...") as loader:
        loader.update(f"Mendeteksi Wilayah di Koordinat {st.session_state.target_lat:.4f}, {st.session_state.target_lon:.4f}...")
        lokasi, geo_type, geo_warning = detect_geo_type(st.session_state.target_lat, st.session_state.target_lon)
        
        st.session_state.basic_geo = {'lokasi': lokasi, 'geo_type': geo_type, 'geo_warning': geo_warning}
        
        if geo_warning and "[TERLARANG]" in geo_warning:
            pass
        else:
            loader.update(f"Menarik Data Cuaca dari BMKG & Open Meteo...")
            weather_data, metadata = fetch_recent_weather(st.session_state.target_lat, st.session_state.target_lon)
            
            if weather_data.empty:
                st.error("API Error: Gagal mengambil data cuaca.")
                st.stop()
            
            loader.update("Memproses Fitur Prediksi Bulanan...")
            features_df = prepare_prediction_features(weather_data)
            
            if features_df.empty:
                st.error("Data Error: Data historis tidak mencukupi.")
                st.stop()

            loader.update("Memindai Fasilitas Publik Terdekat...")
            facilities = fetch_nearby_facilities(st.session_state.target_lat, st.session_state.target_lon)
            
            loader.update("Mengambil Data Gempa Terkini...")
            eq_data = fetch_latest_earthquake(st.session_state.target_lat, st.session_state.target_lon)
            
            loader.update("Menganalisis Topografi & Slope (DEMNAS)...")
            dem_elev, dem_slope = fetch_demnas_slope(st.session_state.target_lat, st.session_state.target_lon)
            
            loader.update("Menghitung Skor Risiko Machine Learning...")
            prob_score = predict_disaster_probability(features_df)
            
            final_elevation = dem_elev if dem_elev is not None else metadata.get('elevation', 0)

            st.session_state.analysis_results = {
                'weather_data': weather_data,
                'features_df': features_df,
                'facilities': facilities,
                'eq_data': eq_data,
                'dem_elev': dem_elev,
                'dem_slope': dem_slope,
                'prob_score': prob_score,
                'final_elevation': final_elevation
            }
            loader.update("Menyusun Laporan Dashboard...")
    st.rerun()

# --- 5. STATE RETRIEVAL & ERROR HANDLING ---
geo = st.session_state.basic_geo
lokasi = geo['lokasi']
geo_type = geo['geo_type']
geo_warning = geo['geo_warning']

if geo_warning and "[TERLARANG]" in geo_warning:
    render_blocked_box(geo_warning.replace("[TERLARANG] ", ""))
    if st.button("⬅ KEMBALI KE PETA"):
        del st.session_state.basic_geo
        st.switch_page("views/map.py")
    st.stop()

# Retrieve results from state
res = st.session_state.analysis_results
weather_data = res['weather_data']
features_df = res['features_df']
facilities = res['facilities']
eq_data = res['eq_data']
dem_elev = res['dem_elev']
dem_slope = res['dem_slope']
prob_score = res['prob_score']
final_elevation = res['final_elevation']

# --- 5. RESULT DASHBOARD ---
if st.button("⬅ KEMBALI KE PETA"):
    # Clear results when going back so new analysis can be triggered
    del st.session_state.analysis_results
    st.switch_page("views/map.py")
    
render_dashboard_header(lokasi)
        
# CSS flex layout emulation with Streamlit columns
col_left, col_right = st.columns([5, 7], gap="large")
    
with col_left:
    render_location_summary(lokasi, st.session_state.target_lat, st.session_state.target_lon, final_elevation)
        
with col_right:
    # Original Decision Box & Metrics (Restored)
    status_text = render_decision_box(prob_score, geo_type, final_elevation)

    col_met1, col_met2, col_met3 = st.columns(3)
    col_met1.metric("Probabilitas Bencana", f"{prob_score}%", delta=status_text, delta_color="inverse" if prob_score > 30 else "normal")
    col_met2.metric("Hujan Terkini", f"{features_df['total_rain_mm'].iloc[-1]:.1f} mm")
        
    slope_label = f"{dem_slope}% (DEMNAS)" if dem_slope is not None else "- (Simulasi)"
    col_met3.metric("Lahan & Slope", f"{round(final_elevation)} mdpl", delta=f"{slope_label}", delta_color="inverse" if dem_slope and dem_slope > 30 else "normal")
        
    st.markdown("<br>", unsafe_allow_html=True)
    render_slope_analysis_bento(dem_slope)

# Full width weather
render_weather_insights(features_df, weather_data)

# --- 6. CTA / AI ADVISOR ---
st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; padding: 2rem 0; margin-top: 2rem;">
    <div class="glass-panel" style="padding: 4px; border-color: rgba(0, 218, 243, 0.2); border-radius: 1rem; max-width: 42rem; width: 100%; box-shadow: 0 0 20px rgba(0,218,243,0.1);">
        <div style="background: rgba(0, 44, 50, 0.3); border-radius: 0.75rem; padding: 3rem; display: flex; flex-direction: column; align-items: center; text-align: center; gap: 1.5rem;">
            <div style="width: 64px; height: 64px; border-radius: 50%; background: rgba(0, 218, 243, 0.1); display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                <span class="material-symbols-outlined" style="color: var(--primary); font-size: 2rem; font-variation-settings: 'FILL' 1;">bolt</span>
            </div>
            <div>
                <p class="loader-subtext">TerraGuard AI Engine Active<span class="flashing-dots"></span></p>
                <h3 class="text-headline-lg" style="margin: 0; margin-bottom: 0.5rem;">Ready for mitigation strategies?</h3>
                <p style="color: var(--on-surface-variant); font-size: 0.875rem; max-width: 28rem; margin: 0 auto; line-height: 1.6;">Our specialized AI can cross-reference these risks with infrastructure blueprints and regional safety protocols.</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    
col_btn1, col_btn2, col_btn3 = st.columns([1,1,1])
with col_btn2:
    generate_ai_btn = st.button("Consult Gemini Advisor ➞", type="primary", use_container_width=True)
    
if generate_ai_btn:
    with AuraLoader("Inisialisasi Gemini Advisor...") as loader:
        loader.update("Menyusun Konteks Geospasial & Lingkungan...")
        
        # Simulasi sedikit waktu agar pesan terbaca (opsional, tapi bagus untuk UX)
        import time
        time.sleep(0.5)
        
        loader.update("Menganalisis Parameter Risiko Seismik & Topografi...")
        time.sleep(0.5)
        
        loader.update("Menghubungkan ke TerraGuard Gemini AI Interface...")
        
        ai_dict = generate_ai_recommendation(
            prob_score, lokasi, features_df.iloc[-1], final_elevation, geo_type,
            facilities, eq_data, dem_slope
        )
            
        loader.update("Menghasilkan Laporan Investasi & Mitigasi...")
        time.sleep(0.3)
        
        st.session_state.ai_report = ai_dict
        st.switch_page("views/advisor.py")

# --- 7. EXTRA INSIGHTS (Optional Tabbed) ---
st.markdown("---")
with st.expander("📊 Lihat Data Dukung & Sejarah BNPB"):
    # Infrastruktur Sosio-Ekonomi
    render_infrastructure_card(facilities)
    st.markdown("---")
    # BNPB Historical Records
    with st.spinner("Memuat catatan sejarah bencana..."):
        df_by_type, df_by_year, total_events, last_year = get_disaster_stats(lokasi)
    render_disaster_history(df_by_type, df_by_year, total_events, last_year, lokasi)
    # Raw Model Features
    st.dataframe(features_df.tail(3).T, use_container_width=True)
