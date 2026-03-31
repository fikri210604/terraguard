import streamlit as st

# --- 1. CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(
    page_title="TerraGuard AI — Property Risk Assessor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    from templates.ui_common import (
        render_custom_css, render_meta, render_top_nav, render_footer
    )
except Exception as e:
    import traceback
    st.error("IMPORT ERROR:")
    st.error(traceback.format_exc())
    st.stop()

# --- 2. GLOBAL STYLES & HEADER ---
render_custom_css()
render_meta()
render_top_nav()

# --- 3. PAGE DEFINITIONS ---
map_page = st.Page("views/map.py", title="Peta Interaktif", icon="📍", default=True)
report_page = st.Page("views/report.py", title="Hasil Analisis", icon="📊")
advisor_page = st.Page("views/advisor.py", title="Gemini Advisor", icon="🤖")

# --- 4. NAVIGATION SETUP ---
pg = st.navigation(
    {
        "Menu Utama": [map_page, report_page, advisor_page]
    }
)

# --- 5. SIDEBAR & BRANDING ---

with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid rgba(65, 72, 75, 0.2); margin-bottom: 1rem;">
        <h2 style="font-family: 'Space Grotesk', sans-serif; color: var(--primary); font-size: 1.25rem; font-weight: 700; margin-bottom: 0;">Lampung Edition</h2>
        <p style="font-size: 10px; color: var(--on-surface-variant); text-transform: uppercase; letter-spacing: 2px; font-weight: 400; opacity: 0.7;">Regional Risk Assessor</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Pilih menu di atas untuk melakukan analisis lahan secara otomatis.")

# --- 6. RUN ACTIVE PAGE ---
pg.run()

# --- 7. GLOBAL FOOTER ---
st.markdown("""
<div class="global-floating-stats" style="position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; gap: 8px;">
    <div style="background: rgba(25, 31, 49, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 8px 16px; border-radius: 9999px; border: 1px solid rgba(65, 72, 75, 0.3); display: flex; align-items: center; gap: 24px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--primary);"></span>
            <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--on-surface-variant);">Precision: <span style="color: var(--on-surface);">0.02m</span></span>
        </div>
        <div style="height: 16px; width: 1px; background: rgba(65, 72, 75, 0.5);"></div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--secondary);"></span>
            <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--on-surface-variant);">Stability: <span style="color: var(--on-surface);">99.4%</span></span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
render_footer()
