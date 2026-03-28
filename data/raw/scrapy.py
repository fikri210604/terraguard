import requests
import pandas as pd
import json
import time
import os

# ============================================================
# DIBI BNPB Superset API Scraper
# Mengambil data bencana dari https://dibi.bnpb.go.id
# Strategi: pagination per tahun untuk bypass row_limit 50K
# ============================================================

API_URL = "https://dibi.bnpb.go.id/api/v1/chart/data"
FORM_DATA_PARAMS = "?form_data=%7B%22slice_id%22%3A51%7D&dashboard_id=2"
FULL_URL = API_URL + FORM_DATA_PARAMS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://dibi.bnpb.go.id/superset/dashboard/2/",
    "Origin": "https://dibi.bnpb.go.id",
}

KATEGORI_BENCANA = [
    "Banjir",
    "Longsor",
    "Cuaca ekstrem",
    "Gelombang pasang / Abrasi",
    "Erupsi gunung api",
    "Gempabumi",
    "Kekeringan",
    "Kebakaran hutan dan lahan",
    "Tsunami",
]

# Kolom yang diminta (sesuai payload asli dari Network tab)
COLUMNS = [
    "id",
    {"expressionType": "SQL", "label": "Tanggal / Waktu Kejadian", "sqlExpression": "dt"},
    {"expressionType": "SQL", "label": "Minggu", "sqlExpression": "minggu"},
    {"expressionType": "SQL", "label": "Bulan", "sqlExpression": "bulan"},
    {"expressionType": "SQL", "label": "Tahun", "sqlExpression": "tahun"},
    {"expressionType": "SQL", "label": "Kode Provinsi", "sqlExpression": "id_provinsi_sdi"},
    {"expressionType": "SQL", "label": "Provinsi", "sqlExpression": "provinsi"},
    {"expressionType": "SQL", "label": "Kode Kabupaten", "sqlExpression": "id_kab_sdi"},
    {"expressionType": "SQL", "label": "Kabupaten", "sqlExpression": "kabupaten"},
    {"expressionType": "SQL", "label": "Kode Jenis Kejadian", "sqlExpression": "id_tipe_bencana"},
    {"expressionType": "SQL", "label": "Nama Kejadian", "sqlExpression": "jenis_bencana"},
    {"expressionType": "SQL", "label": "Jenis Bencana", "sqlExpression": "kategori_bencana"},
    "is_bencana",
    {"expressionType": "SQL", "label": "Jumlah Kejadian", "sqlExpression": "jumlah_kejadian"},
    {"expressionType": "SQL", "label": "Meninggal", "sqlExpression": "meninggal"},
    {"expressionType": "SQL", "label": "Hilang", "sqlExpression": "hilang"},
    {"expressionType": "SQL", "label": "Luka / Sakit", "sqlExpression": "luka_sakit"},
    {"expressionType": "SQL", "label": "Menderita", "sqlExpression": "menderita"},
    {"expressionType": "SQL", "label": "Mengungsi", "sqlExpression": "mengungsi"},
    {"expressionType": "SQL", "label": "Rumah Rusak Berat", "sqlExpression": "rumah_rusak_berat"},
    {"expressionType": "SQL", "label": "Rumah Rusak Sedang", "sqlExpression": "rumah_rusak_sedang"},
    {"expressionType": "SQL", "label": "Rumah Rusak Ringan", "sqlExpression": "rumah_rusak_ringan"},
    {"expressionType": "SQL", "label": "Rumah Terendam", "sqlExpression": "rumah_terendam"},
    {"expressionType": "SQL", "label": "Satuan Pendidikan Rusak", "sqlExpression": "pendidikan_rusak"},
    {"expressionType": "SQL", "label": "Rumah Ibadat Rusak", "sqlExpression": "rumah_ibadat_rusak"},
    {"expressionType": "SQL", "label": "Fasilitas Pelayanan Kesehatan Rusak", "sqlExpression": "fasyankes_rusak"},
    {"expressionType": "SQL", "label": "Kantor Rusak", "sqlExpression": "kantor_rusak"},
    {"expressionType": "SQL", "label": "Jembatan Rusak", "sqlExpression": "jembatan_rusak"},
]


def build_payload(year_start=None, year_end=None, row_limit=50000):
    """Buat payload request. Jika year diberikan, filter berdasarkan TEMPORAL_RANGE."""

    # Tentukan time filter
    if year_start and year_end:
        time_val = f"{year_start}-01-01 : {year_end}-12-31"
    else:
        time_val = "No filter"

    payload = {
        "datasource": {"id": 1, "type": "table"},
        "force": False,
        "queries": [
            {
                "filters": [
                    {"col": "kategori_bencana", "op": "IN", "val": KATEGORI_BENCANA},
                    {"col": "is_bencana", "op": "IN", "val": [True]},
                    {"col": "dt", "op": "TEMPORAL_RANGE", "val": time_val},
                ],
                "extras": {"having": "", "where": ""},
                "applied_time_extras": {},
                "columns": COLUMNS,
                "orderby": [["dt", False], ["id_kab_bps", True]],
                "annotation_layers": [],
                "row_limit": row_limit,
                "series_limit": 0,
                "order_desc": True,
                "url_params": {},
                "custom_params": {},
                "custom_form_data": {},
                "post_processing": [],
                "time_offsets": [],
            }
        ],
        "form_data": {
            "datasource": "1__table",
            "viz_type": "table",
            "slice_id": 51,
            "query_mode": "raw",
            "all_columns": COLUMNS,
            "order_by_cols": ['["dt", false]', '["id_kab_bps", true]'],
            "row_limit": row_limit,
            "order_desc": True,
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "comparator": time_val,
                    "expressionType": "SIMPLE",
                    "operator": "TEMPORAL_RANGE",
                    "subject": "dt",
                }
            ],
            "extra_filters": [],
            "extra_form_data": {
                "filters": [
                    {"col": "kategori_bencana", "op": "IN", "val": KATEGORI_BENCANA},
                    {"col": "is_bencana", "op": "IN", "val": [True]},
                ]
            },
            "dashboardId": 2,
            "force": False,
            "result_format": "json",
            "result_type": "full",
        },
        "result_format": "json",
        "result_type": "full",
    }
    return payload


def fetch_data(session, year_start=None, year_end=None, row_limit=50000):
    """Fetch data dari API untuk rentang tahun tertentu."""
    payload = build_payload(year_start, year_end, row_limit)

    label = f"tahun {year_start}-{year_end}" if year_start else "semua tahun"
    print(f"  Fetching data {label} (row_limit={row_limit})...")

    try:
        response = session.post(FULL_URL, json=payload, headers=HEADERS, timeout=120)
        response.raise_for_status()

        data = response.json()

        # Superset API mengembalikan data di result[0].data
        if "result" in data and len(data["result"]) > 0:
            records = data["result"][0].get("data", [])
            row_count = data["result"][0].get("rowcount", len(records))
            print(f"  ✓ Dapat {row_count} baris data")
            return records, row_count
        else:
            print(f"  ✗ Tidak ada data dalam response")
            return [], 0

    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP Error: {e}")
        print(f"    Response: {response.text[:500]}")
        return [], 0
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Request Error: {e}")
        return [], 0
    except (KeyError, json.JSONDecodeError) as e:
        print(f"  ✗ Parse Error: {e}")
        return [], 0


def scrape_all_data():
    """
    Strategi scraping:
    1. Coba ambil semua data sekaligus (tanpa filter tahun)
    2. Jika hasilnya mentok di row_limit (50K), pecah per rentang tahun
    """
    session = requests.Session()

    # Step 1: Akses dashboard dulu untuk dapat cookies/session
    print("=" * 60)
    print("DIBI BNPB Data Scraper")
    print("=" * 60)
    print("\n[1/3] Mengakses dashboard untuk inisialisasi session...")
    try:
        init_resp = session.get(
            "https://dibi.bnpb.go.id/superset/dashboard/2/",
            headers={"User-Agent": HEADERS["User-Agent"]},
            timeout=30,
        )
        print(f"  ✓ Dashboard diakses (status: {init_resp.status_code})")
    except Exception as e:
        print(f"  ⚠ Gagal akses dashboard: {e}")
        print("  Melanjutkan tanpa session cookies...")

    time.sleep(2)

    # Step 2: Coba fetch semua data sekaligus
    print(f"\n[2/3] Mencoba fetch semua data sekaligus...")
    all_records, total_rows = fetch_data(session, row_limit=50000)

    if total_rows >= 50000:
        # Data kemungkinan terpotong, pecah per rentang tahun
        print(f"\n  ⚠ Data mencapai limit 50K! Menggunakan pagination per tahun...")
        all_records = []

        # Pecah per rentang tahun (sesuaikan rentang jika perlu)
        year_ranges = [
            (1815, 1999),  # Data historis
            (2000, 2005),
            (2006, 2010),
            (2011, 2015),
            (2016, 2018),
            (2019, 2020),
            (2021, 2022),
            (2023, 2024),
            (2025, 2026),
        ]

        for start, end in year_ranges:
            records, count = fetch_data(session, start, end, row_limit=50000)
            if records:
                all_records.extend(records)
            time.sleep(3)  # Jeda antar request agar tidak kena rate limit

            # Jika satu rentang juga mentok 50K, perlu dipecah lebih kecil lagi
            if count >= 50000:
                print(f"  ⚠ Rentang {start}-{end} juga mentok 50K!")
                print(f"    Memecah lagi per tahun...")
                # Hapus records yang sudah ditambahkan tadi
                all_records = all_records[: -len(records)] if records else all_records
                for year in range(start, end + 1):
                    sub_records, sub_count = fetch_data(
                        session, year, year, row_limit=50000
                    )
                    if sub_records:
                        all_records.extend(sub_records)
                    time.sleep(2)

    # Step 3: Simpan ke CSV
    print(f"\n[3/3] Menyimpan data...")
    if all_records:
        df = pd.DataFrame(all_records)

        # Hapus duplikat berdasarkan kolom 'id' jika ada
        if "id" in df.columns:
            before = len(df)
            df = df.drop_duplicates(subset=["id"])
            after = len(df)
            if before != after:
                print(f"  Menghapus {before - after} duplikat")

        # Simpan
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "data_bencana.csv")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"\n{'=' * 60}")
        print(f"✅ SELESAI!")
        print(f"   Total baris  : {len(df):,}")
        print(f"   Total kolom  : {len(df.columns)}")
        print(f"   File output  : {output_path}")
        print(f"   Ukuran file  : {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        print(f"{'=' * 60}")

        # Preview data
        print(f"\nPreview 5 baris pertama:")
        print(df.head().to_string())
        print(f"\nKolom: {list(df.columns)}")
    else:
        print("  ✗ Tidak ada data yang berhasil diambil!")


if __name__ == "__main__":
    scrape_all_data()