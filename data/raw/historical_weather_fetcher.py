"""
Script to fetch historical weather data (5 years) for Lampung from Open-Meteo API.
Matches coordinates with the discovered BMKG adm4 codes.
"""

import requests
import json
import time
import pandas as pd
import os
from datetime import datetime, timedelta

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODES_FILE = os.path.join(BASE_DIR, "lampung_adm4_codes.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "historical_weather_lampung.csv")

def get_coordinates(adm4_code):
    """Fetch coordinates from BMKG API for a given adm4 code."""
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4_code}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lokasi = r.json().get("lokasi", {})
            return lokasi.get("lat"), lokasi.get("lon")
    except:
        pass
    return None, None

def fetch_openmeteo_history(kab_name, lat, lon, start_date, end_date):
    """Fetch historical weather data from Open-Meteo API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum", "relative_humidity_2m_max"],
        "timezone": "Asia/Bangkok"
    }
    
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        data = r.json().get("daily", {})
        
        df = pd.DataFrame({
            "kabupaten": kab_name,
            "date": data.get("time", []),
            "temperature_max": data.get("temperature_2m_max", []),
            "temperature_min": data.get("temperature_2m_min", []),
            "rain_sum_mm": data.get("rain_sum", []),
            "humidity_max": data.get("relative_humidity_2m_max", [])
        })
        return df
    except Exception as e:
        print(f"  ✗ Error fetching Open-Meteo for {kab_name}: {e}")
        return pd.DataFrame()

def main():
    print("=" * 60)
    print("LAMUNG HISTORICAL WEATHER ACQUISITION (2010-2026)")
    print("=" * 60)
    
    # 1. Load codes
    if not os.path.exists(CODES_FILE):
        print(f"Error: {CODES_FILE} not found. Run discovery script first.")
        return
        
    with open(CODES_FILE, "r") as f:
        kab_codes = json.load(f)
    
    # Dates
    start_date = "2010-01-01"
    end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d") # Open-Meteo archive lags ~2 days
    
    all_dfs = []
    fetched_kabs = []
    if os.path.exists(OUTPUT_FILE):
        existing_df = pd.read_csv(OUTPUT_FILE)
        if not existing_df.empty:
            fetched_kabs = existing_df['kabupaten'].unique().tolist()
            all_dfs.append(existing_df)
            print(f"Skipping already fetched: {fetched_kabs}")
    # 2. Process each kabupaten
    for kab_name, info in kab_codes.items():
        if kab_name in fetched_kabs:
            continue
            
        print(f"\nProcessing {kab_name} ({info['adm4']})...")
        
        # Step A: Get coordinates
        lat, lon = get_coordinates(info['adm4'])
        if lat is None:
            print(f"  ✗ Could not fetch coordinates for {kab_name}")
            continue
        print(f"  ✓ Coordinates: {lat}, {lon}")
        
        # Step B: Fetch Open-Meteo
        print(f"  Fetching history from {start_date} to {end_date}...")
        df = fetch_openmeteo_history(kab_name, lat, lon, start_date, end_date)
        
        if not df.empty:
            all_dfs.append(df)
            print(f"  ✓ Fetched {len(df)} days of data.")
        
        time.sleep(5) # Be nice to Open-Meteo
        
    # 3. Concatenate and save
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS!")
        print(f"   Total records : {len(final_df):,}")
        print(f"   Saved to      : {OUTPUT_FILE}")
        print(f"{'='*60}")
        
        # Quick summary
        print("\nSummary (Sum of Rainfall 2021-2026):")
        summary = final_df.groupby("kabupaten")["rain_sum_mm"].sum().sort_values(ascending=False)
        print(summary)
    else:
        print("\n✗ Failed to acquire any historical data.")

if __name__ == "__main__":
    main()
