import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np

def get_lampung_kabupaten():
    """
    Mengembalikan daftar 15 kabupaten/kota di Lampung dengan koordinat pusatnya.
    [DEPRECATED] - Disimpan untuk kompatibilitas jika fitur dropdown ingin dikembalikan.
    """
    return [
        {"kabupaten": "Bandar Lampung", "lat": -5.4297, "lon": 105.2625},
        {"kabupaten": "Lampung Selatan", "lat": -5.5861, "lon": 105.5186},
        {"kabupaten": "Lampung Tengah", "lat": -4.9818, "lon": 105.0766},
        {"kabupaten": "Lampung Utara", "lat": -4.8398, "lon": 104.8967},
        {"kabupaten": "Lampung Barat", "lat": -5.0084, "lon": 104.0321},
        {"kabupaten": "Tulang Bawang", "lat": -4.4379, "lon": 105.7876},
        {"kabupaten": "Tanggamus", "lat": -5.3524, "lon": 104.6247},
        {"kabupaten": "Lampung Timur", "lat": -5.1054, "lon": 105.6766},
        {"kabupaten": "Way Kanan", "lat": -4.4447, "lon": 104.5367},
        {"kabupaten": "Pesawaran", "lat": -5.4646, "lon": 105.0487},
        {"kabupaten": "Pringsewu", "lat": -5.3541, "lon": 104.9754},
        {"kabupaten": "Mesuji", "lat": -4.0156, "lon": 105.4167},
        {"kabupaten": "Tulang Bawang Barat", "lat": -4.4578, "lon": 105.1267},
        {"kabupaten": "Pesisir Barat", "lat": -5.1978, "lon": 103.9567},
        {"kabupaten": "Metro", "lat": -5.1128, "lon": 105.3067}
    ]

def fetch_recent_weather(lat, lon):
    """
    Mengambil data cuaca harian 90 hari terakhir menggunakan Open-Meteo Forecast API.
    Mengembalikan Tuple (DataFrame cuaca, Dictionary metadata termasuk elevasi).
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "past_days": 92, # Ambil ~3 bulan ke belakang
        "forecast_days": 1, 
        "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum", "relative_humidity_2m_max"],
        "timezone": "Asia/Bangkok"
    }
    
    metadata = {"elevation": 0}
    
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            json_res = r.json()
            metadata["elevation"] = json_res.get("elevation", 0)
            
            data = json_res["daily"]
            df = pd.DataFrame(data)
            df.rename(columns={
                "time": "date",
                "temperature_2m_max": "temperature_max",
                "temperature_2m_min": "temperature_min",
                "rain_sum": "rain_sum",
                "relative_humidity_2m_max": "humidity_max"
            }, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            # Hanya ambil data masa lalu (past)
            today = datetime.now().date()
            df = df[df['date'].dt.date < today].copy()
            
            return df, metadata
        else:
            print(f"Weather API Error: {r.status_code}")
    except Exception as e:
        print(f"Error fetching weather: {e}")
    
    return pd.DataFrame(), metadata

def prepare_prediction_features(weather_df):
    """
    Mengubah data harian menjadi fitur bulanan sesuai pipeline model:
    total_rain_mm, rainy_days, lag, rolling, seasonality.
    """
    if weather_df.empty:
        return pd.DataFrame()

    # 1. Agregasi Bulanan
    weather_df['year'] = weather_df['date'].dt.year
    weather_df['month'] = weather_df['date'].dt.month
    
    monthly = weather_df.groupby(['year', 'month']).agg(
        total_rain_mm = ('rain_sum', 'sum'),
        max_rain_mm   = ('rain_sum', 'max'),
        rainy_days    = ('rain_sum', lambda x: (x > 1).sum()),
        avg_temp_max  = ('temperature_max', 'mean'),
        avg_humidity  = ('humidity_max', 'mean')
    ).reset_index()
    
    # Sort temporal
    monthly.sort_values(['year', 'month'], inplace=True)
    
    # 2. Hitung Fitur Lag & Rolling
    if len(monthly) < 2:
        return pd.DataFrame()

    monthly['total_rain_mm_lag1'] = monthly['total_rain_mm'].shift(1)
    monthly['total_rain_mm_roll3_mean'] = monthly['total_rain_mm'].rolling(3, min_periods=1).mean()
    monthly['total_rain_mm_roll3_std'] = monthly['total_rain_mm'].rolling(3, min_periods=1).std().fillna(0)
    monthly['rainy_days_roll3_mean'] = monthly['rainy_days'].rolling(3, min_periods=1).mean()
    monthly['avg_humidity_roll3_mean'] = monthly['avg_humidity'].rolling(3, min_periods=1).mean()
    
    # 3. Seasonality
    monthly['month_sin'] = np.sin(2 * np.pi * monthly['month'] / 12)
    monthly['month_cos'] = np.cos(2 * np.pi * monthly['month'] / 12)
    
    return monthly

def get_disaster_stats(kab_name):
    """
    Memuat data historis bencana BNPB dan memfilter berdasarkan nama kabupaten.
    kab_name bisa berisi format "Kec. X, Kabupaten Y" - akan diekstrak otomatis.
    Mengembalikan (df_by_type, df_by_year, total_events, last_year).
    """
    csv_path = "data/raw/data_bencana.csv"
    
    try:
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Filter Lampung
        df = df[df['Provinsi'] == 'Lampung'].copy()
        df['kabupaten_clean'] = df['Kabupaten'].str.replace('Kota ', '', regex=False).str.strip()
        
        # Ekstrak nama kabupaten dari string "Kec. X, Kabupaten Lampung Selatan"
        # Ambil bagian setelah koma terakhir: "Lampung Selatan"
        kab_search = kab_name
        if ',' in kab_name:
            kab_search = kab_name.split(',')[-1].strip()
        
        # Fuzzy match: cari kabupaten yang mengandung kata kunci
        kab_words = [w for w in kab_search.split() if len(w) > 3]
        
        matched = pd.DataFrame()
        for word in kab_words:
            mask = df['kabupaten_clean'].str.contains(word, case=False, na=False)
            if mask.sum() > 0:
                matched = df[mask].copy()
                break
        
        if matched.empty:
            return None, None, 0, None
        
        # Filter tipe bencana relevan
        target_types = ['Banjir', 'Tanah Longsor', 'Longsor', 'Cuaca ekstrem', 'Puting Beliung']
        matched = matched[matched['Jenis Bencana'].isin(target_types)].copy()
        
        if matched.empty:
            return None, None, 0, None
        
        # Agregasi per Jenis Bencana
        df_by_type = matched.groupby('Jenis Bencana').size().reset_index(name='jumlah')
        df_by_type = df_by_type.sort_values('jumlah', ascending=False)
        
        # Agregasi per Tahun
        df_by_year = matched.groupby('Tahun').size().reset_index(name='jumlah')
        df_by_year = df_by_year.sort_values('Tahun')
        
        total_events = len(matched)
        last_year = int(matched['Tahun'].max()) if not matched.empty else None
        
        return df_by_type, df_by_year, total_events, last_year
        
    except Exception as e:
        print(f"Disaster data error: {e}")
        return None, None, 0, None
