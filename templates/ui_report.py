import streamlit as st

def render_decision_box(risk_score, geo_type, elevation):
    """
    Menentukan kategori dan merender box keputusan.
    """
    if risk_score > 60:
        status_text = "🔴 JANGAN DIBELI"
        box_class = "nobuy-box"
        saran = "Risiko bencana ALAM sangat tinggi di lokasi ini. Sangat tidak disarankan untuk investasi properti jangka panjang."
    elif risk_score > 30:
        status_text = "🟡 HATI-HATI"
        box_class = "warn-box"
        saran = "Lokasi memiliki tingkat kerentanan sedang. Boleh dibeli dengan syarat anggaran ekstra untuk mitigasi tata letak dan konstruksi khusus."
    else:
        status_text = "🟢 AMAN DIBELI"
        box_class = "buy-box"
        saran = "Kondisi lahan memiliki probabilitas bencana terendah. Relatif sangat aman untuk didirikan bangunan konvensional."

    # --- TOPOGRAPHIC OVERRIDES (PEGUNUNGAN) ---
    if elevation > 1200:
        status_text = "🔴 JANGAN DIBELI (ELEVASI EKSTREM)"
        box_class = "nobuy-box"
        saran = f"⚠️ Lokasi berada di ketinggian ekstrem ({elevation} mdpl). Risiko longsor, keterbatasan akses, dan cuaca ekstrem sangat tinggi. Tidak disarankan untuk hunian."
    elif elevation > 800 and status_text == "🟢 AMAN DIBELI":
        status_text = "🟡 HATI-HATI (DATARAN TINGGI)"
        box_class = "warn-box"
        saran = f"⚠️ Meskipun probabilitas bencana dari cuaca rendah, lokasi berada di dataran tinggi ({elevation} mdpl) yang rawan terhadap pergerakan tanah/longsor jika terjadi anomali cuaca."

    # Override kawasan lindung
    if geo_type in ["Kawasan Konservasi / Taman Nasional", "Kawasan Hutan"]:
        status_text = "🔴 TIDAK DISARANKAN (KAWASAN LINDUNG)"
        box_class = "nobuy-box"
        saran = f"⚠️ Lokasi terdeteksi sebagai {geo_type}. Meskipun probabilitas rendah, mendirikan bangunan kemungkinan MELANGGAR HUKUM."

    st.markdown(f"""
    <div class="decision-box {box_class}">
        <h3>Keputusan TerraGuard: {status_text}</h3>
        <p>{saran}</p>
    </div>
    """, unsafe_allow_html=True)
    
    return status_text # Return for metric delta

def render_blocked_box(warning):
    st.markdown(f"""
    <div class="decision-box blocked-box">
        <h3>⛔ ANALISIS DIBATALKAN</h3>
        <p>{warning}</p>
        <p style="margin-top:8px; font-size:0.85rem;">Silakan pilih titik koordinat lain yang berada di daratan.</p>
    </div>
    """, unsafe_allow_html=True)

def render_disaster_history(df_by_type, df_by_year, total_events, last_year, kab_name):
    """Menampilkan ringkasan sejarah bencana historis berdasarkan data BNPB."""
    st.markdown("#### 🗂️ Jejak Rekam Bencana Historis (BNPB)")
    
    if total_events == 0 or df_by_type is None:
        st.info(f"ℹ️ Tidak ada catatan bencana besar yang ditemukan untuk area **{kab_name}** dalam database BNPB.")
        return
    
    # Summary metrics
    col_a, col_b, col_c = st.columns(3)
    most_common = df_by_type.iloc[0]['Jenis Bencana'] if not df_by_type.empty else "N/A"
    col_a.metric("Total Kejadian Tercatat", f"{total_events} kejadian")
    col_b.metric("Jenis Bencana Terbesar", most_common)
    col_c.metric("Terakhir Tercatat", str(last_year) if last_year else "N/A")
    
    # Charts side by side
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**Berdasarkan Jenis Bencana**")
        st.bar_chart(df_by_type.set_index('Jenis Bencana')['jumlah'])
    
    with col_chart2:
        st.markdown("**Berdasarkan Tahun Kejadian**")
        st.line_chart(df_by_year.set_index('Tahun')['jumlah'])
    
    st.caption("Sumber: Data BNPB (Badan Nasional Penanggulangan Bencana), diolah 2024.")

def render_weather_insights(features_df, weather_data):
    """Menampilkan card tren cuaca menggunakan bento box stylings."""
    
    st.markdown("""
    <div class="glass-panel" style="padding: 2rem; margin-bottom: 1rem; margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <div>
                <h2 class="text-headline-lg" style="margin: 0;">Weather Trends</h2>
                <p style="color: var(--on-surface-variant); font-size: 0.875rem; margin-top: 4px;">90-Day precipitation & humidity via Open-Meteo</p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span style="padding: 6px 16px; background: var(--surface-container-high); border-radius: 9999px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border: 1px solid rgba(65,72,75,0.2);">30 Days</span>
                <span class="glow-primary" style="padding: 6px 16px; background: var(--primary); color: var(--on-primary); border-radius: 9999px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">90 Days</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Real Streamlit Chart inside the HTML sandwich
    # We use weather_data for the chart, index represents dates
    st.bar_chart(weather_data.set_index('date')['rain_sum'], color="#00daf3", height=220)

    # Calculate real stats
    avg_precip = weather_data['rain_sum'].mean()
    
    # For humidity, let's grab it if available in weather_data, otherwise from features_df
    avg_humid = weather_data['relative_humidity_2m_max'].mean() if 'relative_humidity_2m_max' in weather_data.columns else (features_df['avg_humidity'].mean() if 'avg_humidity' in features_df.columns else 78.5)
    
    peak_rain = weather_data['rain_sum'].max()
    peak_date_idx = weather_data['rain_sum'].idxmax()
    peak_forecast = "Peak Date"
    if str(peak_date_idx).isdigit(): # If it's just an int index
        # peak_date_idx won't be date
        pass 

    st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin-top: 1.5rem; padding-top: 2rem; border-top: 1px solid rgba(65, 72, 75, 0.2);">
            <div style="display: flex; gap: 1rem; align-items: center;">
                <span class="material-symbols-outlined nav-icon" style="color: var(--secondary); font-size: 2rem;">rainy</span>
                <div>
                    <p style="font-size: 10px; text-transform: uppercase; color: var(--on-surface-variant); font-weight: 700; letter-spacing: 1px; margin-bottom: 4px;">Avg Precipitation</p>
                    <p style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700; margin: 0;">{avg_precip:.1f}mm</p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <span class="material-symbols-outlined nav-icon" style="color: var(--primary); font-size: 2rem;">humidity_percentage</span>
                <div>
                    <p style="font-size: 10px; text-transform: uppercase; color: var(--on-surface-variant); font-weight: 700; letter-spacing: 1px; margin-bottom: 4px;">Humidity Avg</p>
                    <p style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700; margin: 0;">{avg_humid:.1f}%</p>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <span class="material-symbols-outlined nav-icon" style="color: var(--tertiary); font-size: 2rem;">warning</span>
                <div>
                    <p style="font-size: 10px; text-transform: uppercase; color: var(--on-surface-variant); font-weight: 700; letter-spacing: 1px; margin-bottom: 4px;">Peak Rain</p>
                    <p style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700; margin: 0;">{peak_rain:.1f} mm</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_infrastructure_card(facilities):
    """Menampilkan card jarak ke fasilitas umum (RS, Polisi, Damkar)."""
    st.markdown("#### 🏥 Aksesibilitas Fasilitas Publik (Radius 10km)")
    
    col1, col2, col3 = st.columns(3)
    
    # Hospital
    hosp_dist = facilities.get('hospital', {}).get('distance')
    hosp_name = facilities.get('hospital', {}).get('name')
    if hosp_dist is not None:
        col1.metric("RS/Klinik Terdekat", f"{hosp_dist:.1f} km", delta=hosp_name, delta_color="off")
    else:
        col1.metric("RS/Klinik Terdekat", "Tidak Ditemukan", delta="> 10 km", delta_color="inverse")
        
    # Police
    pol_dist = facilities.get('police', {}).get('distance')
    pol_name = facilities.get('police', {}).get('name')
    if pol_dist is not None:
        col2.metric("Kantor Polisi Terdekat", f"{pol_dist:.1f} km", delta=pol_name, delta_color="off")
    else:
        col2.metric("Kantor Polisi Terdekat", "Tidak Ditemukan", delta="> 10 km", delta_color="inverse")
        
    # Fire Station
    fire_dist = facilities.get('fire_station', {}).get('distance')
    fire_name = facilities.get('fire_station', {}).get('name')
    if fire_dist is not None:
        col3.metric("Pemadam Kebakaran", f"{fire_dist:.1f} km", delta=fire_name, delta_color="off")
    else:
        col3.metric("Pemadam Kebakaran", "Tidak Ditemukan", delta="> 10 km", delta_color="inverse")
        
    st.caption("Sumber Data: OpenStreetMap (Overpass API). Jarak dihitung lurus (Haversine).")

def render_seismic_warning(eq_data):
    """Menampilkan banner peringatan gempa jika jarak episentrum < 150km."""
    if not eq_data:
        return
        
    dist = eq_data['distance_km']
    
    if dist < 150:
        st.error(f"**⚠️ PERINGATAN SEISMIK AKTUAL (Jarak: {dist:.1f} km dari Episentrum)**\n\nLokasi lahan Anda berada sangat dekat dengan pusat Gempa Bumi M {eq_data['magnitude']} yang terjadi pada {eq_data['date']} di {eq_data['location']}. Potensi: {eq_data['potensi']}. \n\n**SANGAT DISARANKAN MENGGUNAKAN KONSTRUKSI ANTI-GEMPA.**")
    elif dist < 300:
        st.warning(f"**⚡ Info Seismik (Jarak: {dist:.1f} km dari Episentrum)**\n\nTercatat Gempa Bumi M {eq_data['magnitude']} di {eq_data['location']} pada {eq_data['date']}. Lahan Anda berpotensi merasakan guncangan ringan-sedang jika terjadi gempa serupa.")
    else:
        st.success(f"**✅ Aman dari Gempa Terkini (Jarak: {dist:.1f} km dari Episentrum)**\n\nPusat Gempa Bumi terbaru (M {eq_data['magnitude']} di {eq_data['location']}) berada cukup jauh dan minim dampak destruktif langsung ke lahan Anda.")

def render_dashboard_header(lokasi):
    st.markdown(f"""
    <div class="dashboard-header">
        <div style="display: flex; gap: 12px; align-items: center;">
            <span style="background: var(--primary-container); color: var(--primary); padding: 4px 12px; border-radius: 9999px; font-size: 10px; font-weight: 700; text-transform: uppercase;">AI Analysis Active</span>
            <span class="report-id">TG-LMP-2024-001</span>
        </div>
        <h1 class="text-display-lg" style="margin:0;">Risk Analysis <span style="color:var(--primary);">Report</span>.</h1>
    </div>
    """, unsafe_allow_html=True)

def render_location_summary(lokasi, lat, lon, elevation):
    st.markdown(f"""
    <div class="glass-panel bento-container" style="height: 100%; display: flex; flex-direction: column; gap: 1.5rem; padding: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h2 class="text-headline-lg" style="margin: 0;">Location Summary</h2>
                <p style="color: var(--on-surface-variant); font-size: 0.875rem; margin-top: 4px;">{lokasi}</p>
            </div>
            <span class="material-symbols-outlined nav-icon" style="color: var(--primary);">location_on</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="bg-surface-container-low" style="padding: 1rem; border-radius: 8px;">
                <p style="font-size: 10px; text-transform: uppercase; color: var(--on-surface-variant); font-weight: 700; letter-spacing: 1px; margin-bottom: 4px;">Coordinates</p>
                <p style="font-family: monospace; font-size: 0.875rem; color: var(--primary); margin:0;">{lat:.4f}°, {lon:.4f}°</p>
            </div>
            <div class="bg-surface-container-low" style="padding: 1rem; border-radius: 8px;">
                <p style="font-size: 10px; text-transform: uppercase; color: var(--on-surface-variant); font-weight: 700; letter-spacing: 1px; margin-bottom: 4px;">Elevation</p>
                <p style="font-family: monospace; font-size: 0.875rem; color: var(--primary); margin:0;">{round(elevation)}m MSL</p>
            </div>
        </div>
        <div class="bento-img-container" style="margin-top: auto;">
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuDwnFVnORTBmQiypZMOnupzpoXQ0z6KXzvW4ASIO2Sud3uAYHp9pZpUJlKhLdsgUA61DbqHyDotWp7PmpCn8-RVvMlinCx8xUvpxMwU0-D9IlRkSpsqx5eo1vXggfGbgBf_m-yJVelIeibnB1qKgUCbFPeNI5VZBO1geT0yt40gIIZETjx7hVSqc8HirwTq6OpkoPm_o1N_fIO_dOrzgmuYjMACg2dn1mydC6f_2lFJESl4JPvZ_sI1nmdIgx7_w27-wa2a1D9zPffc" alt="Map Preview">
            <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 100px; background: linear-gradient(to top, var(--surface), transparent); opacity: 0.6;"></div>
            <div style="position: absolute; bottom: 16px; left: 16px; display: flex; align-items: center; gap: 8px;">
                <div class="ping-core" style="width: 8px; height: 8px; border-radius: 50%; background: var(--secondary);"></div>
                <span style="font-size: 10px; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;">Live Satellite Feed</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_risk_gauges(landslide_pct, flood_pct, seismic_pct):
    def get_color(pct):
        if pct < 30: return "var(--secondary)", "Low"
        if pct < 60: return "var(--tertiary)", "Moderate"
        return "var(--error)", "High"

    l_color, l_label = get_color(landslide_pct)
    f_color, f_label = get_color(flood_pct)
    s_color, s_label = get_color(seismic_pct)
    
    circumference = 314.159
    l_offset = circumference - (landslide_pct / 100) * circumference
    f_offset = circumference - (flood_pct / 100) * circumference
    s_offset = circumference - (seismic_pct / 100) * circumference

    st.markdown(f"""
    <div class="glass-panel" style="padding: 2rem;">
        <div style="margin-bottom: 2rem;">
            <h2 class="text-headline-lg" style="margin: 0;">Disaster Risk Gauges</h2>
            <p style="color: var(--on-surface-variant); font-size: 0.875rem; margin-top: 4px;">Real-time risk assessment based on multispectral data</p>
        </div>
        <div style="display: flex; flex-wrap: wrap; justify-content: space-around; gap: 2rem;">
            <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
                <div class="radial-gauge">
                    <svg style="width: 100%; height: 100%; transform: rotate(-90deg);">
                        <circle cx="60" cy="60" r="50" fill="transparent" stroke="var(--outline-variant)" stroke-width="8" opacity="0.3"></circle>
                        <circle class="glow-primary gauge-value-stroke" cx="60" cy="60" r="50" fill="transparent" stroke="{l_color}" stroke-width="8" stroke-dasharray="314.159" stroke-dashoffset="{l_offset}"></circle>
                    </svg>
                    <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700;">{int(landslide_pct)}%</span>
                        <span style="font-size: 8px; text-transform: uppercase; letter-spacing: 1px; color: {l_color}; font-weight:700;">{l_label}</span>
                    </div>
                </div>
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--on-surface-variant); font-weight:700;">Landslide</span>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
                <div class="radial-gauge">
                    <svg style="width: 100%; height: 100%; transform: rotate(-90deg);">
                        <circle cx="60" cy="60" r="50" fill="transparent" stroke="var(--outline-variant)" stroke-width="8" opacity="0.3"></circle>
                        <circle class="glow-primary gauge-value-stroke" cx="60" cy="60" r="50" fill="transparent" stroke="{f_color}" stroke-width="8" stroke-dasharray="314.159" stroke-dashoffset="{f_offset}"></circle>
                    </svg>
                    <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700;">{int(flood_pct)}%</span>
                        <span style="font-size: 8px; text-transform: uppercase; letter-spacing: 1px; color: {f_color}; font-weight:700;">{f_label}</span>
                    </div>
                </div>
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--on-surface-variant); font-weight:700;">Flood</span>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
                <div class="radial-gauge">
                    <svg style="width: 100%; height: 100%; transform: rotate(-90deg);">
                        <circle cx="60" cy="60" r="50" fill="transparent" stroke="var(--outline-variant)" stroke-width="8" opacity="0.3"></circle>
                        <circle class="glow-primary gauge-value-stroke" cx="60" cy="60" r="50" fill="transparent" stroke="{s_color}" stroke-width="8" stroke-dasharray="314.159" stroke-dashoffset="{s_offset}"></circle>
                    </svg>
                    <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700;">{int(seismic_pct)}%</span>
                        <span style="font-size: 8px; text-transform: uppercase; letter-spacing: 1px; color: {s_color}; font-weight:700;">{s_label}</span>
                    </div>
                </div>
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--on-surface-variant); font-weight:700;">Seismic</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_slope_analysis_bento(dem_slope):
    slope_val = f"{dem_slope}%" if dem_slope is not None else "Unknown"
    is_steep = dem_slope is not None and dem_slope > 25
    st.markdown(f"""
    <div class="glass-panel" style="padding: 2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center; background: rgba(35, 41, 60, 0.4);">
        <div>
            <h2 class="text-headline-lg" style="margin: 0;">Slope Analysis</h2>
            <p style="color: var(--on-surface-variant); font-size: 0.875rem; margin-top: 1rem; line-height: 1.5;">
                DEMNAS 8m resolution processing indicates a maximum measured slope of <b>{slope_val}</b>. 
                {'High-risk steepness detected, requiring retaining walls.' if is_steep else 'Gradient is relatively stable across the primary zones.'}
            </p>
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 12px; height: 12px; border-radius: 4px; background: var(--secondary);"></div>
                    <span style="font-size: 10px; text-transform: uppercase; font-weight: 700; color: var(--on-surface-variant); letter-spacing: 1px;">Stable</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 12px; height: 12px; border-radius: 4px; background: var(--tertiary);"></div>
                    <span style="font-size: 10px; text-transform: uppercase; font-weight: 700; color: var(--on-surface-variant); letter-spacing: 1px;">Critical</span>
                </div>
            </div>
        </div>
        <div style="position: relative; height: 180px; background: var(--surface-container); border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
            <img style="position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0.5; mix-blend-mode: overlay;" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAiCjaf76zu0h6clvpQdmbIh_AAnF4RNkxsbouW0A4-AeYPrScPs_dbhsl4cXBViAlcDj-Fx3wvxwjgXXMRsCBlgU5iBFMIomyO85-PshFpFHJL6yiKfMsiRmjvOxFZftGoGPtNMLnbEMVmX5FzFY5r3Nw5WKQItVSBlGHtNKQtgn2B-p_QPJJ2AoZslE2YRp1VAodaDC611Ni5WtX37AqrYm7CAHsXadF6-3Bb6Me9VDtG3m15e_J3r0jZtHyEARmRU0Iq6f0XZOHG" alt="3D Topo Render">
            <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                <span class="material-symbols-outlined" style="color: var(--primary); font-size: 3rem; opacity: 0.4;">terrain</span>
                <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--primary); margin-top: 8px;">3D Render Engine Active</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
