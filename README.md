# 🌍 TerraGuard AI (Lampung Edition)
### Hybrid AI: Predictive Disaster Model + Generative Expert Advisor (2.5 Flash)

---

## 📌 Latar Belakang
**TerraGuard AI** adalah platform *Property Advisor* masa depan yang menggabungkan kekuatan **Big Data Meteorologi** dengan **Kecerdasan Buatan (AI)**. Proyek ini memecahkan kebuntuan informasi bagi calon pembeli lahan di Lampung yang sering kali tidak tahu risiko bencana tersembunyi di balik sebuah lokasi GPS.

## 🤖 Keunggulan Utama: Integrasi Gemini AI
Proyek ini menonjolkan penggunaan **Google Gemini 2.5 Flash** bukan sekadar sebagai chatbot, melainkan sebagai **Expert Decision Maker**:

*   **Reasoning-Based Advice**: Gemini menerima input data "kering" dari Machine Learning (probabilitas %), data topografi (elevasi), dan jenis geografi (hutan/dekat sungai) untuk dirangkum menjadi keputusan investasi yang manusiawi dan logis.
*   **Engineering Insights**: Gemini memberikan saran teknis konstruksi (misal: penggunaan pondasi cakar ayam, peninggian lantai utama, atau sistem drainase khusus) yang disesuaikan dengan profil risiko lokasi tersebut.
*   **Legal & Safety Safeguard**: AI memberikan peringatan hukum jika lokasi berada di jalur hijau atau kawasan lindung, yang sering kali terlewatkan oleh pembeli awam.

---

## ✨ Fitur Inovatif
*   **📍 Precision Pin-Drop**: Navigasi peta interaktif untuk pemilihan titik lahan secara akurat.
*   **⛰️ Topographic Intelligence**: Analisis otomatis risiko longsor berdasarkan ketinggian lahan (mdpl).
*   **📊 BNPB Historical Deep-Dive**: Menyajikan data sejarah bencana nyata 15 tahun terakhir di lokasi terpilih.
*   **⚡ Real-Time Weather Routing**: Mengambil data meteorologi 90 hari terakhir secara dinamis via API.
*   **🤖 Gemini Expert Tab**: Dedicated space untuk konsultasi hasil analisis dalam format laporan profesional.

---

## 🛠️ Teknologi Stack
*   **AI/ML Core**: Logistic Regression (Predictive) + **Google Gemini 2.5 Flash (Generative)**.
*   **Framework**: Streamlit (Backend & UI).
*   **Geospatial**: Folium, Leaflet, & Nominatim API.
*   **Data Source**: Open-Meteo & BNPB Indonesia.

---

## 📂 Struktur Proyek Modular
```text
├── app.py                # Main Orchestrator
├── templates/
│   ├── ui_components.py  # Visual Branding & UI Rendering
│   └── index.html        # HTML Meta & Layout Fragments
├── utils/
│   ├── ai_generator.py   # Core Logic: ML Inference & Gemini Expert
│   ├── data_loader.py    # Data Pipeline (Weather & BNPB)
│   └── geo_utils.py      # Geographic Intelligence
├── static/
│   └── style.css         # Premium Glassmorphism Design
└── scripts/
    └── test_gemini.py    # Gemini Connectivity Diagnostic Tool
```

---

## 🛠️ Cara Menjalankan
1.  Install dependencies: `pip install -r requirements.txt`
2.  Setup `.env`: `GOOGLE_API_KEY=AIza...`
3.  Run: `streamlit run app.py`

---

## 📬 Kontak
**Email**: afh.fikri2106@gmail.com
**IDCamp 2026 Project Submission**

---
*Powered by Google Gemini 2.5 AI & Scikit-Learn*
