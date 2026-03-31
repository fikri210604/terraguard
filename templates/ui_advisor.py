import streamlit as st

def render_advisor_page(ai_dict, case_id="TG-LMP-2024-0892"):
    if not isinstance(ai_dict, dict):
        ai_dict = {
            "investment_logic": "AI gagal merespons atau sedang offline.",
            "engineering_specs": "Sistem gagal memuat data.",
            "legal_constraints": "Sistem gagal memuat data."
        }
        
    # Sanitize and format outputs to prevent Markdown parsing breaks
    logic_text = ai_dict.get('investment_logic', 'No data available.')
    if isinstance(logic_text, list):
        logic_text = "<br><br>".join(str(item) for item in logic_text)
    else:
        logic_text = str(logic_text).replace('\n', '<br>')
        
    eng_text = ai_dict.get('engineering_specs', '<li>No specifications provided.</li>')
    if isinstance(eng_text, list):
        eng_text = "".join(f"<li style='margin-bottom: 0.5rem;'>{item}</li>" for item in eng_text)
    else:
        eng_text = str(eng_text).replace('\n', '<br>')
        
    leg_text = ai_dict.get('legal_constraints', 'No immediate constraints identified.')
    if isinstance(leg_text, list):
        leg_text = "<br><br>".join(f"• {item}" for item in leg_text)
    else:
        leg_text = str(leg_text).replace('\n', '<br>')
    
    st.markdown(f"""
<div class="max-w-5xl mx-auto space-y-8" style="padding: 1rem;">
<!-- Header Section -->
<div style="display: flex; flex-direction: column; md:flex-row; justify-content: space-between; align-items: flex-end; gap: 1rem; border-bottom: 1px solid rgba(65, 72, 75, 0.1); padding-bottom: 1.5rem;">
    <div>
        <span style="color: var(--primary); font-family: 'Inter', sans-serif; font-size: 0.75rem; letter-spacing: 0.3em; text-transform: uppercase; margin-bottom: 0.5rem; display: block;">Analytical Intelligence</span>
        <h1 style="font-size: 3rem; font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: var(--on-surface); letter-spacing: -0.025em; line-height: 1; margin: 0;">Aura Sentinel Expert Advisor</h1>
    </div>
    <div style="text-align: right;">
        <p style="color: rgba(220, 225, 251, 0.5); font-size: 0.75rem; font-family: monospace; margin: 0;">MODEL_VERSION: GEMINI_2.5_FLASH</p>
        <p style="color: rgba(220, 225, 251, 0.5); font-size: 0.75rem; font-family: monospace; text-transform: uppercase; margin: 0;">REGION: LAMPUNG_SOUTH_COAST</p>
    </div>
</div>
<!-- Central Frosted Panel: Professional Report -->
<div class="glass-panel" style="border-radius: 1rem; padding: 3rem; background: linear-gradient(135deg, rgba(25, 31, 49, 0.6) 0%, rgba(21, 27, 45, 0.4) 100%); box-shadow: 0 0 60px rgba(139, 92, 246, 0.15); position: relative; border: 1px solid rgba(65, 72, 75, 0.05);">
    <div style="position: absolute; top: 1rem; right: 1rem; display: flex; gap: 0.5rem;">
        <div style="width: 0.5rem; height: 0.5rem; border-radius: 9999px; background: var(--primary);"></div>
        <div style="width: 0.5rem; height: 0.5rem; border-radius: 9999px; background: rgba(0, 218, 243, 0.4);"></div>
    </div>
    <div style="display: flex; flex-direction: column; gap: 3rem; max-width: 48rem; margin: 0 auto;">
        <!-- Report Header -->
        <div style="text-align: center; display: flex; flex-direction: column; gap: 0.5rem;">
            <h2 style="font-size: 1.875rem; font-family: 'Space Grotesk', sans-serif; font-style: italic; font-weight: 300; letter-spacing: 0.025em; color: var(--on-surface); margin: 0;">Official Architectural & Risk Report</h2>
            <div style="height: 1px; width: 6rem; background: linear-gradient(to right, transparent, rgba(0, 218, 243, 0.4), transparent); margin: 0 auto;"></div>
            <p style="color: rgba(220, 225, 251, 0.6); font-size: 0.875rem; font-family: 'Inter', sans-serif; text-transform: uppercase; letter-spacing: 0.1em; margin: 0;">Case ID: {case_id}</p>
        </div>
        <!-- 1. Reasoning-Based Advice -->
        <section style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: var(--primary); font-size: 1.875rem;" class="material-symbols-outlined">insights</span>
                <h3 style="font-size: 1.25rem; font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: var(--primary); letter-spacing: -0.025em; margin: 0;">Investment Reasoning & Strategic Logic</h3>
            </div>
            <div style="display: grid; grid-template-columns: 1fr; gap: 2rem; align-items: start;">
                <div style="color: rgba(220, 225, 251, 0.8); line-height: 1.625; font-size: 1.125rem;">
                    {logic_text}
                </div>
            </div>
        </section>
        <!-- 2. Engineering Insights -->
        <section style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: var(--primary); font-size: 1.875rem;" class="material-symbols-outlined">architecture</span>
                <h3 style="font-size: 1.25rem; font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: var(--primary); letter-spacing: -0.025em; margin: 0;">Technical Engineering Specifications</h3>
            </div>
            <div style="background: rgba(46, 52, 71, 0.2); padding: 1.5rem; border-radius: 0.75rem; border: 1px solid rgba(65, 72, 75, 0.1);">
                <ul style="color: rgba(220, 225, 251, 0.8); line-height: 1.625; margin: 0; padding-left: 1.2rem;">
                    {eng_text}
                </ul>
            </div>
        </section>
        <!-- 3. Legal & Safety Safeguard -->
        <section style="background: rgba(57, 33, 0, 0.3); border: 1px solid rgba(255, 185, 95, 0.2); padding: 2rem; border-radius: 1rem; display: flex; flex-direction: column; gap: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; color: var(--tertiary);">
                <span class="material-symbols-outlined">gavel</span>
                <h3 style="font-size: 1.125rem; font-family: 'Space Grotesk', sans-serif; font-weight: 700; text-transform: uppercase; letter-spacing: 0.025em; margin: 0;">Legal Constraints & Safety Mandate</h3>
            </div>
            <div style="color: rgba(220, 225, 251, 0.8); font-size: 1rem;">
                {leg_text}
            </div>
        </section>
        <!-- Follow-up Interaction Area Placeholder -->
        <div class="glass-panel" style="border-radius: 1rem; padding: 1.5rem; border: 1px solid rgba(0, 218, 243, 0.2); box-shadow: 0 0 40px rgba(0, 218, 243, 0.1); margin-top: 2rem;">
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0 0.5rem;">
                    <span class="material-symbols-outlined" style="color: var(--primary);">chat_bubble</span>
                    <span style="font-size: 0.75rem; font-family: 'Inter', sans-serif; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(220, 225, 251, 0.6);">Inquiry: Follow-up Analysis</span>
                </div>
                <p style="color: var(--on-surface-variant); font-size: 0.875rem; padding-left: 0.5rem; margin: 0;">Gunakan sidebar atau fitur di bawah untuk bertanya secara interaktif.</p>
            </div>
        </div>
    </div>
</div>
</div>
    """, unsafe_allow_html=True)
