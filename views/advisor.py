import streamlit as st
from templates.ui_advisor import render_advisor_page

if st.button("⬅ KEMBALI KE LAPORAN"):
    st.switch_page("views/report.py")

ai_dict = st.session_state.get('ai_report', {})
render_advisor_page(ai_dict)
