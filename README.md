# 🌍 TerraGuard AI (Lampung Edition)
### Asisten Cerdas Prediksi Risiko Bencana Lahan & Properti

---

## 📌 Latar Belakang & Fokus Wilayah
Indonesia adalah negara rawan bencana. **TerraGuard AI** hadir sebagai *predictive system* dan **alat bantu keputusan investasi properti** bagi calon pembeli lahan/rumah di Provinsi Lampung. Aplikasi ini membantu pengguna memperkirakan probabilitas bencana dalam 30 hari ke depan di titik lokasi spesifik (berbasis koordinat GPS).

## 🤖 Integrasi AI (Predictive + Generative)
1.  **Predictive Model (Time-Series Logistic Regression)**: 
    Memprediksi probabilitas (0-100%) terjadinya bencana (banjir/longsor) di suatu wilayah dalam **30 hari ke depan**. Model dilatih menggunakan *temporal splitting* dan *lag/rolling features* dari 16 tahun sejarah cuaca Open-Meteo dan insiden BNPB (DIBI) — memastikan validitas saintifik.
2.  **Expert Recommendation (Google Gemini 1.5 Flash)**: 
    Bertindak sebagai konsultan tata ruang. Gemini akan menerima probabilitas bencana dari ML dan langsung memberikan **keputusan tegas untuk pembeli lahan** (Membeli vs Jangan Membeli) lengkap dengan syarat mitigasi konstruksinya.

## ✨ Fitur Utama
*   **📍 Interactive Pin-Drop Map**: Pengguna dapat mencari dan menandai (klik) titik lahan yang ingin mereka beli langsung di peta.
*   **📡 Dynamic Weather Routing**: Sistem otomatis menarik data cuaca 90 hari terakhir (Via Open-Meteo Forecast API) spesifik pada titik koordinat (Lat/Lon) yang dipilih pengguna.
*   **🏢 Property Investment Advisor**: Rekomendasi "Go/No-Go" berbasis AI untuk kelayakan lahan secara meteorologis dan geologis.

---

## 📊 Sumber Data

| Sumber | Deskripsi | File |
|---|---|---|
| **BNPB DIBI** | Insiden bencana historis (2010–2026) | `data/raw/data_bencana.csv` |
| **Open-Meteo** | Data cuaca harian historis (2010–2026) Lampung | `data/raw/historical_weather_lampung.csv` |
| **Open-Meteo Forecast** | Real-time weather API (90 hari lalu & 1 ke depan) | Terhubung di `utils/data_loader.py` |

---

## 🧠 Pipeline Training Klasifikasi (Validasi ketat Time-Series)

### Alur Notebook: `notebooks/model_bnpb.ipynb`

```
┌──────────────────┐     ┌───────────────────────┐
│   Data Bencana   │     │ Cuaca (Open-Meteo)    │
│   (BNPB)         │     │                       │
└────────┬─────────┘     └───────────┬───────────┘
         │                           │
         ▼                           ▼
┌──────────────────┐     ┌───────────────────────┐
│ Agregasi Bulanan │     │ Agregasi Bulanan      │
│ per Kabupaten    │     │ per Kabupaten         │
│ (n_bencana)      │     │ (avg_rain, max_rain,  │
│                  │     │ rainy_days, dll)      │
└────────┬─────────┘     └───────────┬───────────┘
         │                           │
         └─────────────┬─────────────┘
                       ▼
            ┌─────────────────────┐
            │  MERGE BULANAN      │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │ TARGET SHIFT (y)    │
            │ = n_bencana > 0     │
            │ di BULAN DEPAN      │
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │ TIME-SERIES FEATURE │
            │ ENGINEERING         │
            │ • Lag 1             │
            │ • Rolling 3 Mean/Std│
            │ • Seasonal Sin/Cos  │
            └──────────┬──────────┘
                       ▼
            ┌──────────────────────┐
            │ TIME-BASED SPLIT     │
            │ Train: 2010-2023     │
            │ Test : 2024-2026     │
            └──────────┬───────────┘
                       ▼
            ┌──────────────────────┐
            │ Logistic Regression  │
            │ (Scale + Predict)    │
            │ Metrik: ROC-AUC > 0.6│
            └──────────────────────┘
```

---

## 📚 Teknologi
*   **Frontend**: Streamlit, Folium (Interactive Maps)
*   **ML**: Scikit-Learn (Logistic Regression, StandardScaler)
*   **Data Prep**: Pandas, NumPy (Shift, Rolling Window)
*   **API Data**: Open-Meteo API
*   **LLM**: Google Gemini 1.5 Flash API

---

## 🛠️ Panduan Menjalankan Secara Lokal

1. **Clone repository ini:**
   ```bash
   git clone https://github.com/USERNAME/terraguard-ai.git
   cd terraguard-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```

3. **Setup API Key:**
   ```bash
   # Buat file .env
   GOOGLE_API_KEY=AIza...
   ```

4. **Training model prediktif (Opsional, Model siap di models/):**
   ```bash
   jupyter notebook notebooks/model_bnpb.ipynb
   ```

5. **Jalankan aplikasi:**
   ```bash
   streamlit run app.py
   ```
# terraguard
