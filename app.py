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
        render_custom_css, render_meta
    )
    from templates.layouts import render_sidebar, render_navbar, render_footer
except Exception as e:
    import traceback
    st.error("IMPORT ERROR:")
    st.error(traceback.format_exc())
    st.stop()

# --- 2. GLOBAL STYLES & LAYOUT ---
render_custom_css()
render_meta()
render_navbar()
render_sidebar()

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

# --- 5. RUN ACTIVE PAGE ---
pg.run()

# --- 6. GLOBAL FOOTER ---
render_footer()
