import streamlit as st
import os

def load_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def render_custom_css():
    css_content = load_file("static/style.css")
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def render_meta():
    html = get_html_template()
    if html:
        part = html.split("<!-- META SECTION -->")[1] if "<!-- META SECTION -->" in html else ""
        st.markdown(part, unsafe_allow_html=True)

def get_html_template():
    return load_file("templates/index.html")

def render_hero():
    html = get_html_template()
    if html:
        part = html.split("<!-- HERO SECTION -->")[1] if "<!-- HERO SECTION -->" in html else ""
        st.markdown(part, unsafe_allow_html=True)

def render_footer():
    html = get_html_template()
    if html:
        part = html.split("<!-- FOOTER SECTION -->")[1] if "<!-- FOOTER SECTION -->" in html else ""
        st.markdown(part, unsafe_allow_html=True)

def render_glass_card(lat, lon, lokasi, geo_type):
    st.markdown(f"""
    <div class="glass-card">
        <h4>📌 Koordinat Terpilih</h4>
        <div class="coord-code">
            Lat: {lat:.5f}<br>
            Lon: {lon:.5f}
        </div>
        <br>
        <div class="geo-label">Area Terdeteksi</div>
        <div class="geo-value">{lokasi}</div>
        <br>
        <div class="geo-label">Tipe Lahan</div>
        <div class="geo-value">{geo_type}</div>
    </div>
    """, unsafe_allow_html=True)

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

def render_weather_insights(monthly_df):
    """Menampilkan card informasi cuaca bulanan (Hujan, Lembap, Suhu)."""
    st.markdown("#### ☁️ Wawasan Fitur Cuaca Bulanan (3 Bulan Terakhir)")
    
    if monthly_df.empty:
        st.warning("Data fitur bulanan tidak tersedia.")
        return

    # Ambil data bulan terakhir
    latest = monthly_df.iloc[-1]
    prev = monthly_df.iloc[-2] if len(monthly_df) > 1 else latest

    col1, col2, col3 = st.columns(3)
    
    # Card 1: Rainy Days
    delta_days = int(latest['rainy_days'] - prev['rainy_days'])
    col1.metric("Hari Hujan / Bulan", f"{int(latest['rainy_days'])} hari", 
                delta=f"{delta_days} hari" if len(monthly_df) > 1 else None)
    
    # Card 2: Average Humidity
    delta_hum = float(latest['avg_humidity'] - prev['avg_humidity'])
    col2.metric("Kelembaban Rata-rata", f"{latest['avg_humidity']:.1f}%", 
                delta=f"{delta_hum:.1f}%" if len(monthly_df) > 1 else None)
    
    # Card 3: Average Temp Max
    delta_temp = float(latest['avg_temp_max'] - prev['avg_temp_max'])
    col3.metric("Suhu Max Rata-rata", f"{latest['avg_temp_max']:.1f}°C", 
                delta=f"{delta_temp:.1f}°C" if len(monthly_df) > 1 else None)

    # Trend Chart for Features
    st.markdown("**Tren Parameter Lingkungan (Monthly)**")
    
    # Kita gabungkan fitur untuk chart
    trend_data = monthly_df[['year', 'month', 'avg_humidity', 'avg_temp_max']].copy()
    trend_data['period'] = trend_data['year'].astype(str) + "-" + trend_data['month'].astype(str)
    
    st.line_chart(trend_data.set_index('period')[['avg_humidity', 'avg_temp_max']], color=["#0ea5e9", "#f59e0b"])
    st.caption("Grafik perbandingan kelembaban (Biru) dan suhu udara (Oranye).")
