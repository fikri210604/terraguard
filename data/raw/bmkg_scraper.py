"""
Script untuk mencari adm4 codes yang valid untuk Lampung dari BMKG API
Strategi: scan kode kecamatan per kabupaten, coba beberapa kode kelurahan
"""
import requests
import json
import time
import os

# Kode kabupaten/kota Lampung (2 digit terakhir kode BPS per kabupaten)
# Format adm4 BMKG: 18.KK.CC.DDDD
# 18 = Lampung (kode provisi)
# KK = kode kabupaten (2 digit)
# CC = kode kecamatan (2 digit)
# DDDD = kode desa/kelurahan (4 digit, biasanya 1001 atau 2001+)

KABUPATEN_LAMPUNG = {
    "01": "Lampung Selatan",
    "02": "Lampung Tengah",
    "03": "Lampung Utara",
    "04": "Lampung Barat",
    "05": "Tulang Bawang",
    "06": "Tanggamus",
    "07": "Lampung Timur",
    "08": "Way Kanan",
    "09": "Pesawaran",
    "10": "Pringsewu",
    "11": "Mesuji",
    "12": "Tulang Bawang Barat",
    "13": "Pesisir Barat",
    "71": "Bandar Lampung",
    "72": "Metro",
}

def try_adm4(kab_code, kec_code, kel_code):
    """Coba kombinasi kode adm4"""
    adm4 = f"18.{kab_code}.{kec_code:02d}.{kel_code}"
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return adm4, r.json()
        return None, None
    except:
        return None, None

def run_discovery():
    # Cari satu kode valid per kabupaten
    print("Mencari kode adm4 valid untuk tiap kabupaten/kota Lampung...\n")

    VALID_CODES = {}
    
    # Ensure directory exists
    os.makedirs("data/raw", exist_ok=True)

    for kab_code, kab_name in KABUPATEN_LAMPUNG.items():
        found = False
        # Scan kecamatan 01-05, kelurahan 1001/2001/1002/2002
        for kec in range(1, 6):
            for kel in ["1001", "2001", "1002", "2002", "1003", "2003"]:
                adm4, data = try_adm4(kab_code, kec, kel)
                if data:
                    lokasi = data.get("lokasi", {})
                    nama = lokasi.get("desa", lokasi.get("kecamatan", "?"))
                    kecamatan = lokasi.get("kecamatan", "?")
                    kota = lokasi.get("kotkab", "?")
                    VALID_CODES[kab_name] = {
                        "adm4": adm4,
                        "desa": nama,
                        "kecamatan": kecamatan,
                        "kabupaten": kota,
                    }
                    print(f"  ✅ {kab_name:<25} → {adm4}  ({nama}, {kecamatan})")
                    found = True
                    break
                time.sleep(0.3)
            if found:
                break

        if not found:
            print(f"  ❌ {kab_name:<25} → Tidak ditemukan")
        time.sleep(0.5)

    # Tampilkan hasil lengkap
    print(f"\n{'='*60}")
    print(f"HASIL: {len(VALID_CODES)}/15 kabupaten/kota berhasil")
    print(f"{'='*60}\n")

    # Simpan ke JSON untuk digunakan di app
    output_path = "data/raw/lampung_adm4_codes.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(VALID_CODES, f, ensure_ascii=False, indent=2)
    print(f"Disimpan ke {output_path}")

    # Analisis 1 sample lengkap
    if VALID_CODES:
        first_kab = list(VALID_CODES.keys())[0]
        first_code = VALID_CODES[first_kab]["adm4"]
        print(f"\n{'='*60}")
        print(f"CONTOH DATA CUACA: {first_kab}")
        print(f"{'='*60}")
        r = requests.get(f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={first_code}", timeout=10)
        data = r.json()
        
        # Parse data cuaca
        cuaca_hari = data.get("data", [])
        print(f"Jumlah hari prakiraan: {len(cuaca_hari)}")
        
        for hari in cuaca_hari:
            tanggal = hari.get("lokasi", {}).get("tanggal", "?") if "lokasi" in hari else "?"
            slot_per_hari = len(hari.get("cuaca", []))
            print(f"\nHari: {tanggal} → {slot_per_hari} slot waktu")
            
            for slot_list in hari.get("cuaca", []):
                if isinstance(slot_list, list):
                    for slot in slot_list[:2]:  # 2 sampel per hari
                        print(f"  ⏱ {slot.get('local_datetime','?')} | Suhu: {slot.get('t','?')}°C | Cuaca: {slot.get('weather_desc','?')} | Hujan: {slot.get('tp','?')}mm | Angin: {slot.get('ws','?')} km/j [{slot.get('wd','?')}]")

if __name__ == "__main__":
    run_discovery()
