import streamlit as st
import time

def render_custom_loader(message="Processing data...", is_overlay=True, return_html=False):
    """
    Menampilkan animasi loading kustom bergaya Glassmorphism/Sci-Fi.
    Jika is_overlay=True, loader akan menutupi seluruh layar (global).
    """
    overlay_style = """
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle at center, rgba(13, 17, 28, 0.95) 0%, rgba(5, 7, 12, 1) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    """ if is_overlay else ""

    container_style = """
        padding: 4rem 2rem;
        background: rgba(25, 31, 49, 0.6);
        border-radius: 1.5rem;
        border: 1px solid rgba(0, 218, 243, 0.2);
        box-shadow: 0 0 50px rgba(0, 218, 243, 0.1);
        max-width: 32rem;
        margin: 2rem auto;
        text-align: center;
    """ if not is_overlay else "text-align: center;"

    html_code = f"""
    <div style="{overlay_style}">
        <style>
            .loader-content-container {{
                {container_style}
            }}
            /* ... (stay same) ... */
            .css-animation-container {{
                position: relative;
                width: 100px;
                height: 100px;
                margin: 0 auto 2rem auto;
            }}
            .pulse-ring {{
                position: absolute;
                inset: 0;
                border-radius: 50%;
                border: 2px solid transparent;
                border-top-color: #00daf3;
                border-right-color: #00daf3;
                animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
            }}
            .pulse-ring:nth-child(2) {{
                inset: 10px;
                border-top-color: #4edea3;
                border-right-color: #4edea3;
                animation-duration: 1.5s;
                animation-direction: reverse;
            }}
            .pulse-ring:nth-child(3) {{
                inset: 20px;
                border-top-color: #ffb95f;
                border-right-color: #ffb95f;
                animation-duration: 2s;
            }}
            .core-dot {{
                position: absolute;
                inset: 40px;
                background: #00daf3;
                border-radius: 50%;
                box-shadow: 0 0 20px #00daf3;
                animation: pulse-glow 2s ease-in-out infinite;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            @keyframes pulse-glow {{ 0%, 100% {{ transform: scale(1); opacity: 0.8; }} 50% {{ transform: scale(1.5); opacity: 1; box-shadow: 0 0 40px #00daf3; }} }}
            .loader-text {{ font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700; color: #dce1fb; letter-spacing: 0.05em; margin: 0; margin-bottom: 0.75rem; }}
            .loader-subtext {{ font-family: 'Inter', sans-serif; font-size: 0.875rem; color: #00daf3; letter-spacing: 0.2em; text-transform: uppercase; margin: 0; font-weight: 700; opacity: 0.8; }}
            .flashing-dots::after {{ content: '...'; animation: dots 1.5s steps(4, end) infinite; }}
            @keyframes dots {{ 0%, 20% {{ color: rgba(0,0,0,0); text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }} 40% {{ color: #00daf3; text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }} 60% {{ text-shadow: .25em 0 0 #00daf3, .5em 0 0 rgba(0,0,0,0); }} 80%, 100% {{ text-shadow: .25em 0 0 #00daf3, .5em 0 0 #00daf3; }} }}
        </style>
        <div class="loader-content-container">
            <div class="css-animation-container">
                <div class="pulse-ring"></div>
                <div class="pulse-ring"></div>
                <div class="pulse-ring"></div>
                <div class="core-dot"></div>
            </div>
            <h3 class="loader-text">{message}</h3>
            <p class="loader-subtext">TerraGuard AI Engine Active<span class="flashing-dots"></span></p>
        </div>
    </div>
    """
    if return_html:
        return html_code
    st.markdown(html_code, unsafe_allow_html=True)

class AuraLoader:
    """Context manager untuk memudahkan penggunaan global loading dengan pesan dinamis."""
    def __init__(self, message="Processing..."):
        self.message = message
        self.placeholder = st.empty()

    def update(self, new_message):
        """Memperbarui pesan pada loader yang sedang berjalan."""
        self.message = new_message
        html = render_custom_loader(self.message, is_overlay=True, return_html=True)
        self.placeholder.markdown(html, unsafe_allow_html=True)

    def __enter__(self):
        # Render HTML langsung ke placeholder
        self.update(self.message)
        # Beri jeda kecil agar Streamlit sempat mem-push HTML ke browser 
        time.sleep(0.1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.placeholder.empty()
