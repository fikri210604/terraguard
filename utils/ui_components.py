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
