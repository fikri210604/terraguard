"""
Script riset BMKG API untuk Lampung
1. Cek satu sampel untuk melihat struktur data
2. Test semua kode kabupaten/kota Lampung
3. Analisis field yang tersedia
"""

import requests
import json
import time
import pandas as pd
from pprint import pprint

# Kode adm4 (kelurahan level) untuk ibukota tiap kabupaten/kota di Lampung
# Format: XX.YY.ZZ.WWWW (Provinsi.Kab.Kec.Kel)
# Lampung = kode provinsi 18

LAMPUNG_ADM4_CODES = {
    "Bandar Lampung":       "18.71.01.1001",  # Tanjung Karang Pusat
    "Metro":                "18.72.01.1001",  # Metro Pusat
    "Lampung Selatan":      "18.01.01.2001",  # Kalianda
    "Lampung Tengah":       "18.02.01.2001",  # Gunung Sugih
    "Lampung Utara":        "18.03.01.1001",  # Kotabumi
    "Lampung Barat":        "18.04.01.2001",  # Liwa
    "Tulang Bawang":        "18.05.01.2001",  # Menggala
    "Tanggamus":            "18.06.01.2001",  # Kota Agung
    "Way Kanan":            "18.08.01.2001",  # Blambangan Umpu
    "Lampung Timur":        "18.07.01.2001",  # Sukadana
    "Pesawaran":            "18.09.01.2001",  # Gedong Tataan
    "Pringsewu":            "18.10.01.2001",  # Pringsewu
    "Mesuji":               "18.11.01.2001",  # Mesuji
    "Tulang Bawang Barat":  "18.12.01.2001",  # Panaragan Jaya
    "Pesisir Barat":        "18.13.01.2001",  # Krui
}


def fetch_bmkg_weather(adm4_code):
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4_code}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": r.status_code}
    except Exception as e:
        return {"error": str(e)}


# ── Step 1: Cek satu sampel untuk melihat struktur data
print("=" * 60)
print("STEP 1: Analisis Struktur Response BMKG")
print("=" * 60)
sample_code = "18.71.01.1001"
sample = fetch_bmkg_weather(sample_code)

if "error" in sample:
    print(f"GAGAL: {sample}")
else:
    print(json.dumps(sample, indent=2, ensure_ascii=False)[:3000])

time.sleep(1)

# ── Step 2: Coba semua kode & catat mana yang berhasil
print("\n" + "=" * 60)
print("STEP 2: Test Semua Kode Kabupaten/Kota Lampung")
print("=" * 60)

results = []
for kab, code in LAMPUNG_ADM4_CODES.items():
    data = fetch_bmkg_weather(code)
    
    if "error" in data:
        status = f"GAGAL ({data['error']})"
        n_records = 0
        lokasi_name = "-"
    else:
        try:
            lokasi_info = data.get("lokasi", {})
            lokasi_name = lokasi_info.get("desa", lokasi_info.get("kecamatan", "?"))
            n_records = len(data.get("data", [{}])[0].get("cuaca", []))
            status = "OK"
        except Exception as e:
            status = f"PARSE ERROR: {e}"
            n_records = 0
            lokasi_name = "-"

    results.append({
        "Kabupaten": kab,
        "ADM4 Code": code,
        "Nama Lokasi API": lokasi_name,
        "Status": status,
        "N Data Hari": n_records,
    })
    print(f"  [{status}] {kab} ({code}) → {lokasi_name}")
    time.sleep(0.5)

df_result = pd.DataFrame(results)
print("\n--- SUMMARY ---")
print(df_result.to_string(index=False))

# ── Step 3: Analisis field yang tersedia dari satu sampel berhasil
print("\n" + "=" * 60)
print("STEP 3: Analisis Field Cuaca yang Tersedia")
print("=" * 60)
ok_rows = [r for r in results if r["Status"] == "OK"]
if ok_rows:
    sample_data = fetch_bmkg_weather(ok_rows[0]["ADM4 Code"])
    try:
        cuaca_first = sample_data["data"][0]["cuaca"][0][0]
        print(f"Field-field yang tersedia untuk 1 record prakiraan:")
        for k, v in cuaca_first.items():
            print(f"  {k:<30} = {v}")
    except Exception as e:
        print(f"Gagal parse field: {e}")
else:
    print("Tidak ada data yang berhasil diambil")

print("\n" + "=" * 60)
print("SELESAI")
print("=" * 60)
