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

def render_top_nav():
    html = get_html_template()
    if html:
        part = html.split("<!-- HERO SECTION -->")[1] if "<!-- HERO SECTION -->" in html else ""
        st.markdown(part, unsafe_allow_html=True)

def render_footer():
    html = get_html_template()
    if html:
        part = html.split("<!-- FOOTER SECTION -->")[1] if "<!-- FOOTER SECTION -->" in html else ""
        st.markdown(part, unsafe_allow_html=True)
