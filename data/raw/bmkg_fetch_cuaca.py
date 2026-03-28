"""
BMKG Weather Data Fetcher untuk Lampung
Mengambil data prakiraan cuaca real-time dari BMKG
dan menyimpannya ke CSV untuk semua kabupaten/kota di Lampung.
"""

import requests
import json
import time
import pandas as pd
import os
from datetime import datetime

# Load kode adm4 yang sudah ditemukan
CODES_FILE = os.path.join(os.path.dirname(__file__), "lampung_adm4_codes.json")


def load_adm4_codes():
    with open(CODES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_cuaca(adm4_code, kabupaten_name):
    """Fetch data cuaca dari BMKG dan parse ke list of records."""
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4_code}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"  ✗ {kabupaten_name}: HTTP {r.status_code}")
            return []
        data = r.json()
    except Exception as e:
        print(f"  ✗ {kabupaten_name}: {e}")
        return []

    lokasi = data.get("lokasi", {})
    records = []

    for hari_data in data.get("data", []):
        for slot_list in hari_data.get("cuaca", []):
            if not isinstance(slot_list, list):
                continue
            for slot in slot_list:
                records.append({
                    # Identitas wilayah
                    "kabupaten":        kabupaten_name,
                    "adm4":             adm4_code,
                    "provinsi":         lokasi.get("provinsi", "Lampung"),
                    "kota_kabupaten":   lokasi.get("kotkab", ""),
                    "kecamatan":        lokasi.get("kecamatan", ""),
                    "desa":             lokasi.get("desa", ""),
                    "lat":              lokasi.get("lat", None),
                    "lon":              lokasi.get("lon", None),
                    # Waktu
                    "utc_datetime":     slot.get("utc_datetime", ""),
                    "local_datetime":   slot.get("local_datetime", ""),
                    "analysis_date":    slot.get("analysis_date", ""),
                    # Data cuaca
                    "suhu_c":           slot.get("t", None),
                    "kelembapan_pct":   slot.get("hu", None),
                    "curah_hujan_mm":   slot.get("tp", None),      # ⭐ Curah hujan
                    "tutupan_awan_pct": slot.get("tcc", None),
                    "kecepatan_angin":  slot.get("ws", None),
                    "arah_angin":       slot.get("wd", None),
                    "jarak_pandang":    slot.get("vs_text", None),
                    "kondisi_cuaca":    slot.get("weather_desc", None),
                    "kondisi_cuaca_en": slot.get("weather_desc_en", None),
                    "icon_cuaca":       slot.get("weather_icon", None),
                })
    return records


def main():
    print("=" * 60)
    print("BMKG Lampung Weather Fetcher")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Load kode adm4
    codes = load_adm4_codes()
    print(f"\nMengambil data cuaca untuk {len(codes)} kabupaten/kota...\n")

    all_records = []

    for kab_name, info in codes.items():
        adm4 = info["adm4"]
        records = fetch_cuaca(adm4, kab_name)
        if records:
            all_records.extend(records)
            print(f"  ✅ {kab_name:<25} → {len(records)} slot prakiraan")
        time.sleep(0.5)

    if not all_records:
        print("\n✗ Tidak ada data yang berhasil diambil!")
        return

    df = pd.DataFrame(all_records)

    # Parse waktu
    df["local_datetime"] = pd.to_datetime(df["local_datetime"], errors="coerce")

    # Simpan ke CSV
    output_path = os.path.join(os.path.dirname(__file__), "bmkg_lampung_cuaca.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\n{'='*60}")
    print(f"✅ SELESAI!")
    print(f"   Total record  : {len(df):,}")
    print(f"   Kabupaten     : {df['kabupaten'].nunique()}")
    print(f"   Rentang waktu : {df['local_datetime'].min()} s/d {df['local_datetime'].max()}")
    print(f"   File output   : {output_path}")
    print(f"{'='*60}")

    # Preview
    print("\nPreview data cuaca:")
    preview_cols = ["kabupaten", "local_datetime", "suhu_c", "kelembapan_pct", 
                    "curah_hujan_mm", "kondisi_cuaca"]
    print(df[preview_cols].head(10).to_string(index=False))

    # Summary per kabupaten (rata-rata curah hujan prakiraan)
    print("\n--- Rata-rata curah hujan prakiraan per kabupaten ---")
    summary = (
        df.groupby("kabupaten")["curah_hujan_mm"]
        .agg(["mean", "max", "sum"])
        .round(2)
        .rename(columns={"mean": "Rata2 (mm)", "max": "Maks (mm)", "sum": "Total (mm)"})
        .sort_values("Rata2 (mm)", ascending=False)
    )
    print(summary.to_string())


if __name__ == "__main__":
    main()
