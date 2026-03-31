import streamlit as st
import textwrap

def render_floating_ui(lat, lon, lokasi, geo_type, geo_warning):
    """Render floating UI components (Cards & Search Bar) over the full-screen map."""
    
    # Determine status styling
    is_safe = not bool(geo_warning)
    status_icon = "shield" if is_safe else "warning"
    status_color = "#4edea3" if is_safe else "#ffb95f"
    
    if geo_warning and "[TERLARANG]" in geo_warning:
        status_icon = "gpp_bad"
        status_color = "#ffb4ab"
        
    status_title = "Safe Zone Detected" if is_safe else "Warning / Restricted"
    status_desc = "Clearance verified. Lahan siap untuk dianalisis mendalam." if is_safe else geo_warning.replace("[TERLARANG] ", "")

    short_lokasi = lokasi.split(',')[0]
    short_type = geo_type.split(' ')[0] if ' ' in geo_type else geo_type

    html_code = textwrap.dedent(f"""
    <div style="position: absolute; top: 2rem; left: 2.5rem; z-index: 999; display: flex; flex-direction: column; gap: 1rem; pointer-events: none;">
        <div class="glass-panel" style="pointer-events: auto; padding: 1.5rem; width: 320px; background: rgba(18, 22, 33, 0.85); border: 1px solid rgba(65, 72, 75, 0.3); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; font-weight: 700; color: var(--primary); letter-spacing: 1.5px;">TARGET ANALYSIS</span>
                <span class="material-symbols-outlined" style="color:var(--primary); font-size: 1rem;">gps_fixed</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(65, 72, 75, 0.2); padding-bottom: 0.75rem;">
                <div>
                    <div style="font-size: 8px; color: var(--on-surface-variant); text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;">LATITUDE</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: var(--on-surface);">{lat:.4f}° S</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 8px; color: var(--on-surface-variant); text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;">LONGITUDE</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: var(--on-surface);">{lon:.4f}° E</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                <div style="background: rgba(35, 41, 60, 0.5); padding: 10px; border-radius: 6px;">
                    <div style="font-size: 8px; color: #00daf3; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 4px;">LOKASI</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; font-weight: 500; color: var(--on-surface); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{lokasi}">{short_lokasi}</div>
                </div>
                <div style="background: rgba(35, 41, 60, 0.5); padding: 10px; border-radius: 6px;">
                    <div style="font-size: 8px; color: #ffb95f; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 4px;">TIPE</div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; font-weight: 500; color: var(--on-surface); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{geo_type}">{short_type}</div>
                </div>
            </div>
        </div>
        <div class="glass-panel" style="pointer-events: auto; padding: 1rem; width: 320px; background: rgba(18, 22, 33, 0.85); border: 1px solid rgba(65, 72, 75, 0.3); border-left: 4px solid {status_color}; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="display: flex; gap: 0.75rem; align-items: center;">
                <div style="background: {status_color}22; padding: 8px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                    <span class="material-symbols-outlined" style="color: {status_color}; font-variation-settings: 'FILL' 1; font-size: 1.1rem;">{status_icon}</span>
                </div>
                <div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; font-weight: 700; color: {status_color};">{status_title}</div>
                    <div style="font-size: 10px; color: var(--on-surface-variant); font-family: 'Inter', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px;">{status_desc}</div>
                </div>
            </div>
        </div>
    </div>
    </div>
    """)
    
    st.markdown(html_code, unsafe_allow_html=True)
