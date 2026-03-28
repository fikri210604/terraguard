import streamlit as st
import folium
from streamlit_folium import st_folium

# Import Utilities
from utils.data_loader import fetch_recent_weather, prepare_prediction_features, get_disaster_stats
from utils.ai_generator import predict_disaster_probability, generate_ai_recommendation
from utils.geo_utils import detect_geo_type
from templates.ui_components import (
    render_custom_css, render_meta, render_hero, render_footer, 
    render_glass_card, render_decision_box, render_blocked_box,
    render_disaster_history, render_weather_insights
)

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="TerraGuard AI - Property Risk Assessor", 
    layout="wide", 
    page_icon="🌍",
    initial_sidebar_state="collapsed"
)

# Render Styles & Header
render_custom_css()
render_meta()
render_hero()

# --- 2. STATE MANAGEMENT ---
if 'target_lat' not in st.session_state:
    st.session_state.target_lat = -5.4297
if 'target_lon' not in st.session_state:
    st.session_state.target_lon = 105.2625
if 'should_analyze' not in st.session_state:
    st.session_state.should_analyze = False

# --- 3. MAP SELECTION ---
st.markdown('<p class="section-title">📍 Peta Interaktif — Pilih Lokasi Lahan</p>', unsafe_allow_html=True)
st.markdown('<p class="section-subtitle">Klik pada peta untuk memindahkan pin ke lokasi lahan yang ingin Anda analisis.</p>', unsafe_allow_html=True)

col_map, col_info = st.columns([3, 1])

with col_map:
    # Render Interactive Map
    m = folium.Map(location=[-4.9818, 105.0766], zoom_start=8, tiles="CartoDB positron")
    folium.Marker(
        [st.session_state.target_lat, st.session_state.target_lon],
        popup="📌 Lokasi Lahan Incaran",
        icon=folium.Icon(color="blue", icon="home", prefix='fa')
    ).add_to(m)

    map_data = st_folium(m, width="100%", height=420, returned_objects=["last_clicked"])

    # Update State on Click
    if map_data and map_data.get("last_clicked"):
        new_lat, new_lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        if new_lat != st.session_state.target_lat or new_lon != st.session_state.target_lon:
            st.session_state.target_lat, st.session_state.target_lon = new_lat, new_lon
            st.session_state.should_analyze = False
            st.rerun()

with col_info:
    # Geo Detection
    lokasi, geo_type, geo_warning = detect_geo_type(st.session_state.target_lat, st.session_state.target_lon)
    
    # Render Info Card
    render_glass_card(st.session_state.target_lat, st.session_state.target_lon, lokasi, geo_type)
    
    if geo_warning:
        st.warning(geo_warning)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Analisis Lahan Ini", type="primary", use_container_width=True):
        st.session_state.should_analyze = True

# --- 4. ANALYSIS PROCESS ---
if st.session_state.should_analyze:
    # Check if building is possible
    if geo_type.startswith("Perairan") and geo_warning and ("mungkin" in geo_warning or "bisa" in geo_warning):
        render_blocked_box(geo_warning)
    else:
        with st.status(f"Menganalisis Lahan di {lokasi}...", expanded=True) as status:
            st.write("🛰️ Mengambil data iklim (90 Hari) & topografi...")
            weather_data, metadata = fetch_recent_weather(st.session_state.target_lat, st.session_state.target_lon)
            
            if weather_data.empty:
                status.update(label="API Error: Gagal mengambil data cuaca.", state="error")
            else:
                st.write("⚙️ Mengekstraksi Fitur ML (Lags, Rolling Trends)...")
                features_df = prepare_prediction_features(weather_data)
                
                if features_df.empty:
                    status.update(label="Data Error: Data historis tidak mencukupi.", state="error")
                else:
                    st.write("🧠 Menjalankan Inferensi Logistic Regression...")
                    prob_score = predict_disaster_probability(features_df)
                    
                    status.update(label=f"Analisis Selesai! (Elevasi: {metadata.get('elevation')} mdpl)", state="complete", expanded=False)

                    # --- 5. RESULT DASHBOARD ---
                    # Decision Box & Category
                    status_text = render_decision_box(prob_score, geo_type, metadata.get('elevation', 0))

                    col_met1, col_met2, col_met3 = st.columns(3)
                    col_met1.metric("Probabilitas Bencana", f"{prob_score}%", delta=status_text, delta_color="inverse" if prob_score > 30 else "normal")
                    col_met2.metric("Curah Hujan Terkini", f"{features_df['total_rain_mm'].iloc[-1]:.1f} mm")
                    col_met3.metric("Ketinggian Lahan", f"{metadata.get('elevation', 0)} mdpl")

                    # Deep Insights
                    tab_ai, tab_data = st.tabs(["🤖 Konsultan Arsitek AI (Gemini)", "📊 Analisis Detail"])
                    
                    with tab_ai:
                        with st.spinner("AI sedang merumuskan desain konstruksi..."):
                            ai_report = generate_ai_recommendation(
                                prob_score, lokasi, features_df.iloc[-1], metadata.get('elevation', 0), geo_type
                            )
                        st.markdown(ai_report)
                    
                    with tab_data:
                        # 1. Weather Trends & Features
                        st.markdown("#### 📈 Tren Curah Hujan Harian")
                        st.line_chart(weather_data.set_index('date')['rain_sum'], color="#0ea5e9")
                        st.caption("Curah hujan harian yang digunakan sebagai input model ML.")
                        
                        st.markdown("---")
                        render_weather_insights(features_df)
                        
                        st.markdown("---")
                        # 2. BNPB Historical Records
                         # Muat dan tampilkan sejarah bencana BNPB
                        with st.spinner("Memuat catatan sejarah bencana..."):
                            df_by_type, df_by_year, total_events, last_year = get_disaster_stats(lokasi)
                        render_disaster_history(df_by_type, df_by_year, total_events, last_year, lokasi)
                        
                        # 3. Raw Model Features
                        with st.expander("🔎 Lihat Fitur Model Terproses (Raw Dataframe)"):
                             st.dataframe(features_df.tail(3).T, use_container_width=True)

# Footer
st.markdown("---")
render_footer()
