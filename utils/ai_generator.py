import pickle
import os
import pandas as pd
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def predict_disaster_probability(features_df):
    """
    Menjalankan inferensi menggunakan model Logistic Regression yang telah dilatih.
    Mengambil baris terakhir (data terkini) untuk prediksi bulan depan.
    """
    if features_df.empty:
        return 0.0

    model_path = os.path.join('models', 'predictive_risk_model.pkl')
    
    if not os.path.exists(model_path):
        return round(float(min(100, features_df['total_rain_mm'].iloc[-1] / 10)), 1)

    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        scaler = model_data['scaler']
        feature_names = model_data['features']
        
        latest_row = features_df.iloc[-1:].copy()
        latest_row.fillna(0, inplace=True)
        
        X = latest_row[feature_names]
        X_scaled = scaler.transform(X)
        proba = model.predict_proba(X_scaled)[0][1]
        
        return round(float(proba * 100), 1)
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0.0

def get_gemini_recommendation(risk_score, lokasi_nama, weather_summary, elevation, geo_type, facilities=None, eq_data=None, dem_slope=None):
    """
    Meminta rekomendasi mitigasi dari Gemini berdasarkan probabilitas risiko,
    elevasi lahan, ringkasan cuaca, TIPE GEOGRAFI, fasilitas, risiko seismik, dan slope.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Tambahan konteks jika kawasan khusus
        geo_context = ""
        if elevation > 1200:
            geo_context = f"""
        ⚠️ PERINGATAN KRITIS: Lokasi berada di KETINGGIAN EKSTREM ({elevation} mdpl). 
        Topografi seperti ini biasanya memiliki kemiringan curam (>40%) yang sangat rawan LONGSOR. 
        Membangun di sini sangat berbahaya dan mahal secara logistik. 
        Saran Anda HARUS: "JANGAN MEMBELI LAHAN INI".
            """
        elif elevation > 800:
             geo_context = f"""
        ⚠️ PERINGATAN: Lokasi berada di dataran tinggi ({elevation} mdpl). 
        Walaupun probabilitas hujan rendah, waspadai stabilitas tanah dan potensi longsor jangka panjang.
            """

        if geo_type in ["Kawasan Konservasi / Taman Nasional", "Kawasan Hutan"]:
            geo_context = f"""
        ⚠️ PERINGATAN KRITIS: Lokasi ini terdeteksi sebagai "{geo_type}" oleh OpenStreetMap. 
        Anda WAJIB memasukkan peringatan HUKUM: mendirikan bangunan tanpa izin alih fungsi lahan 
        di kawasan ini melanggar UU No. 5/1990 tentang Konservasi dan/atau UU No. 41/1999 tentang Kehutanan.
        Keputusan Anda HARUS: "JANGAN MEMBELI LAHAN INI" terlepas dari probabilitas bencana.
            """
        elif "Sungai" in geo_type or "Danau" in geo_type:
            geo_context = """
        ⚠️ PERINGATAN: Lokasi dekat badan air (sungai/danau). 
        Pertimbangkan regulasi sempadan sungai (min 15-100m tergantung lebar sungai) 
        berdasarkan PP No. 38/2011 tentang Sungai.
            """

        # Konteks Infrastruktur
        infra_context = ""
        if facilities:
            hosp = facilities.get('hospital', {}).get('distance')
            pol = facilities.get('police', {}).get('distance')
            if hosp and hosp < 10:
                infra_context += f"- Akses Kesehatan: RS/Klinik berjarak {hosp:.1f} km.\n"
            else:
                infra_context += "- Akses Kesehatan: Jauh (>10 km).\n"

        # Konteks Gempa
        seismic_context = ""
        if eq_data and eq_data.get('distance_km') is not None:
            dist = eq_data['distance_km']
            if dist < 150:
                seismic_context = f"\n⚠️ PERINGATAN SEISMIK: Lokasi ini berjarak hanya {dist:.1f} km dari pusat Gempa M {eq_data['magnitude']} terbaru. Anda WAJIB menyarankan konstruksi ASLI tahan gempa (misal: struktur beton bertulang, pondasi cakar ayam, kayu fleksibel)."

        # Konteks Slope
        slope_context = ""
        if dem_slope is not None:
            if dem_slope > 30:
                 slope_context = f"\n⚠️ PERINGATAN KEMIRINGAN EKSTREM: Lahan ini sangat curam ({dem_slope}%). Anda WAJIB MEREKOMENDASIKAN UNTUK TIDAK MEMBANGUN RUMAH di sini karena risiko longsor struktural sangat tinggi, ATAU sarankan dinding penahan tanah (retaining wall) masif."
            elif dem_slope > 15:
                 slope_context = f"\n⚠️ PERINGATAN KEMIRINGAN: Lahan ini cukup miring ({dem_slope}%). Sarankan perkuatan fondasi split level atau terasering."
            else:
                 slope_context = f"\n✅ Info Topografi: Lahan landai ({dem_slope}%). Relatif mendukung konstruksi standar."

        prompt = f"""
        Anda adalah Konsultan Arsitek dan Pakar Kelayakan Properti terkemuka di Indonesia.
        Tugas Anda: memberikan saran KEPUTUSAN INVESTASI LAHAN kepada calon pembeli.
        
        Lokasi: {lokasi_nama}
        Tipe Lahan (OSM): {geo_type}
        
        Data Analisis Lahan (Hasil Prediksi AI):
        - Probabilitas Bencana Alam Bulan Depan: {risk_score}%
        - Ketinggian Lahan (Elevasi): {elevation} mdpl
        - Curah Hujan Bulan Ini: {weather_summary['total_rain_mm']:.1f} mm
        - Jumlah Hari Hujan: {int(weather_summary['rainy_days'])} hari
        {infra_context}
        {geo_context}
        {seismic_context}
        {slope_context}
        
        Instruksi Keputusan (jika tidak ada override kawasan khusus):
        1. Jika Probabilitas > 60% ATAU Kemiringan Lahan > 30%: "JANGAN MEMBELI LAHAN INI"
        2. Jika Probabilitas 30-60%: "HATI-HATI MEMBELI" (butuh anggaran ekstra mitigasi)
        3. Jika Probabilitas < 30%: "AMAN UNTUK DIBELI"

        Anda HARUS merespons HANYA dalam format JSON dengan skema berikut:
        {{
            "investment_logic": "Alasan keputusan berdasarkan data di atas (hubungkan elevasi, cuaca, infrastruktur, topografi, dan seismik). Minimal 2 paragraf.",
            "engineering_specs": "2-3 rekomendasi arsitektur bangunan (pondasi, atap, drainase) secara singkat namun teknis berupa bullet point (tambahkan <li> jika HTML)",
            "legal_constraints": "1-2 saran administratif/legal (IMB, SHM, sempadan, dll) atau peringatan kawasan secara spesifik."
        }}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def generate_ai_recommendation(risk_score, lokasi_nama, weather_summary, elevation, geo_type="Lahan Darat", facilities=None, eq_data=None, dem_slope=None):
    """
    Fungsi wrapper untuk mendapatkan rekomendasi AI (Gemini atau Fallback).
    """
    # Coba Gemini
    gemini_saran = get_gemini_recommendation(risk_score, lokasi_nama, weather_summary, elevation, geo_type, facilities, eq_data, dem_slope)
    if gemini_saran:
        return gemini_saran

    # Fallback Logic
    if geo_type in ["Kawasan Konservasi / Taman Nasional", "Kawasan Hutan"]:
        keputusan = "🔴 **JANGAN MEMBELI (KAWASAN LINDUNG)**"
        detail = f"Lokasi terdeteksi sebagai **{geo_type}**. Mendirikan bangunan di sini melanggar UU Konservasi/Kehutanan."
    elif risk_score > 60:
        keputusan = "🔴 **JANGAN MEMBELI LAHAN INI**"
        detail = f"Probabilitas bencana **{risk_score}%** — terlalu tinggi untuk investasi properti."
    elif risk_score > 30:
        keputusan = "🟡 **HATI-HATI MEMBELI (Butuh Anggaran Ekstra)**"
        detail = f"Probabilitas bencana **{risk_score}%** — lahan perlu penguatan pondasi dan drainase sebelum dibangun."
    else:
        keputusan = "🟢 **AMAN UNTUK DIBELI**"
        detail = f"Probabilitas bencana **{risk_score}%** — kondisi mendukung pembangunan konvensional."

    saran_fallback = {
        "investment_logic": f"<p style='color: var(--primary); font-weight: bold;'>Keputusan Offline Mode:</p><p>{keputusan}</p><p>{detail}</p><p><i>{key_warning}</i></p>",
        "engineering_specs": "<li>Pastikan elevasi lantai utama bangunan berada di atas titik tertinggi banjir historis.</li><li>Lakukan uji boring (tanah) sebelum memulai pondasi.</li>",
        "legal_constraints": "Pastikan SHM (Sertifikat Hak Milik) tidak berada di jalur hijau/sempadan sungai."
    }
    
    return saran_fallback
