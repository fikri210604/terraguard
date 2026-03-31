import streamlit as st
import textwrap

def render_sidebar():
    """Renders the native Streamlit sidebar with professional branding."""
    with st.sidebar:
        # Branding Header
        st.markdown(textwrap.dedent("""
            <div style="padding: 0.5rem 0 1.5rem 0; text-align: center;">
                <h1 style="font-family: 'Space Grotesk', sans-serif; color: #00daf3; font-size: 20px; font-weight: 800; margin: 0; text-shadow: 0 0 20px rgba(0, 218, 243, 0.4);">TerraGuard AI</h1>
                <p style="font-size: 11px; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 3px; font-weight: 500; margin: 0;">Command Center v2.0</p>
            </div>
        """).strip(), unsafe_allow_html=True)
        # Region Info Card
        st.markdown(textwrap.dedent("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 1.25rem; border-radius: 16px; margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span class="material-symbols-outlined" style="color: #00daf3; font-size: 18px;">location_on</span>
                    <span style="font-weight: 700; color: #fff; font-size: 14px;">Wilayah Operasional</span>
                </div>
                <p style="font-size: 13px; color: rgba(255,255,255,0.7); margin: 0; line-height: 1.5;">
                    Provinsi Lampung, Indonesia<br>
                    <span style="font-size: 11px; color: #00daf3; opacity: 0.8;">Monitoring DEMNAS & BMKG Aktif</span>
                </p>
            </div>
        """).strip(), unsafe_allow_html=True)
        st.info("Pilih menu navigasi di atas untuk melakukan analisis lahan secara otomatis.")

def render_navbar():
    """Renders a status bar with brand title, letting native Streamlit handle the sidebar."""
    st.markdown(textwrap.dedent("""
        <div style="position: fixed; top: 0; left: 0; right: 0; height: 60px; background: rgba(18, 22, 33, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(0, 218, 243, 0.15); display: flex; justify-content: space-between; align-items: center; padding: 0 1.5rem; z-index: 999900; pointer-events: none;">
            <div style="display: flex; align-items: center; gap: 1rem; pointer-events: auto; margin-left: 40px;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #00daf3; font-size: 1.2rem; letter-spacing: -0.5px;">TerraGuard AI</span>
            </div>
            <div style="display: flex; align-items: center; gap: 1.5rem; pointer-events: auto;">
                <div style="background: rgba(0, 218, 243, 0.1); border: 1px solid rgba(0, 218, 243, 0.2); padding: 4px 12px; border-radius: 999px; display: flex; align-items: center; gap: 8px;">
                    <span style="width: 8px; height: 8px; background: #00daf3; border-radius: 50%; box-shadow: 0 0 10px #00daf3;"></span>
                    <span style="font-size: 10px; color: #00daf3; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">BMKG Connected</span>
                </div>
                <div style="display: flex; gap: 12px; color: rgba(255,255,255,0.6);">
                    <span class="material-symbols-outlined nav-icon-native" style="font-size: 20px;">sensors</span>
                    <span class="material-symbols-outlined nav-icon-native" style="font-size: 20px;">push_pin</span>
                </div>
                <div style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid #00daf3; display: flex; align-items: center; justify-content: center; background: rgba(0, 218, 243, 0.1);">
                    <span class="material-symbols-outlined" style="color: #00daf3; font-size: 20px;">account_circle</span>
                </div>
            </div>
        </div>
        <div style="height: 12px;"></div>
    """).strip(), unsafe_allow_html=True)

def render_footer():
    """Renders the precision status bar and the legal footer."""
    st.markdown(textwrap.dedent("""
        <div class="global-floating-stats" style="position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; gap: 8px; pointer-events: none;">
            <div style="background: rgba(25, 31, 49, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 8px 16px; border-radius: 9999px; border: 1px solid rgba(0, 218, 243, 0.15); display: flex; align-items: center; gap: 24px; pointer-events: auto;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #00daf3;"></span>
                    <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.6);">Precision: <span style="color: #fff;">0.02m</span></span>
                </div>
                <div style="height: 16px; width: 1px; background: rgba(255, 255, 255, 0.1);"></div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #4edea3;"></span>
                    <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.6);">Stability: <span style="color: #fff;">99.4%</span></span>
                </div>
            </div>
        </div>
        <footer style="margin-top: 4rem; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 1px;">
            <div>© 2026 TerraGuard AI. Data: BMKG, Open-Meteo, BIG.</div>
            <div style="display: flex; gap: 1.5rem;">
                <a href="#" style="color: inherit; text-decoration: none;">Disclaimers</a>
                <a href="#" style="color: inherit; text-decoration: none;">Privacy</a>
                <a href="#" style="color: inherit; text-decoration: none;">Terms</a>
            </div>
        </footer>
    """).strip(), unsafe_allow_html=True)