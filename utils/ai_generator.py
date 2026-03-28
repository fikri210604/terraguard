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

def get_gemini_recommendation(risk_score, lokasi_nama, weather_summary, elevation, geo_type):
    """
    Meminta rekomendasi mitigasi dari Gemini berdasarkan probabilitas risiko,
    elevasi lahan, ringkasan cuaca, dan TIPE GEOGRAFI lokasi.
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
        {geo_context}
        
        Instruksi Keputusan (jika tidak ada override kawasan khusus):
        1. Jika Probabilitas > 60%: "JANGAN MEMBELI LAHAN INI"
        2. Jika Probabilitas 30-60%: "HATI-HATI MEMBELI" (butuh anggaran ekstra mitigasi)
        3. Jika Probabilitas < 30%: "AMAN UNTUK DIBELI"

        Penjelasan Teknis (Format Markdown):
        - Alasan keputusan berdasarkan data di atas (hubungkan elevasi, curah hujan, dan geo_type)
        - 2-3 rekomendasi arsitektur bangunan (pondasi, atap, drainase)
        - 1 saran administratif/legal (IMB, SHM, sempadan, alih fungsi lahan)
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def generate_ai_recommendation(risk_score, lokasi_nama, weather_summary, elevation, geo_type="Lahan Darat"):
    """
    Fungsi wrapper untuk mendapatkan rekomendasi AI (Gemini atau Fallback).
    """
    # Coba Gemini
    gemini_saran = get_gemini_recommendation(risk_score, lokasi_nama, weather_summary, elevation, geo_type)
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

    saran_fallback = f"""
### Keputusan TerraGuard (Sistem Offline)
{keputusan}

{detail}

**Elevasi Lahan:** {elevation} mdpl | **Tipe Lahan:** {geo_type}

*Rekomendasi Dasar:*
1. Pastikan elevasi lantai utama bangunan berada di atas titik tertinggi banjir historis.
2. Lakukan uji boring (tanah) sebelum memulai pondasi.
3. Pastikan SHM (Sertifikat Hak Milik) tidak berada di jalur hijau/sempadan sungai.
    """
    return saran_fallback
