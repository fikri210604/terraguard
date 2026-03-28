import requests

def detect_geo_type(lat, lon):
    """
    Menggunakan Nominatim reverse geocoding untuk mendeteksi jenis lokasi:
    Laut, Sungai, Danau, Hutan Lindung, Taman Nasional, atau Lahan Darat biasa.
    Mengembalikan (lokasi_nama, geo_type, geo_warning).
    """
    lokasi_nama = "Titik Koordinat Kustom"
    geo_type = "Lahan Darat"
    geo_warning = None

    try:
        url_geo = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=14"
        headers = {'User-Agent': 'TerraGuardAI/1.0'}
        r_geo = requests.get(url_geo, headers=headers, timeout=5)
        
        if r_geo.status_code == 200:
            res_geo = r_geo.json()
            
            osm_type = res_geo.get("type", "").lower()
            osm_class = res_geo.get("class", "").lower()
            display_name = res_geo.get("display_name", "").lower()
            place_rank = res_geo.get("place_rank", 30)
            address = res_geo.get("address", {})
            
            # --- LOGIKA DETEKSI LAUT (OFFSHORE) ---
            # Jika Nominatim hanya mengembalikan level Kota/Provinsi (Rank rendah < 15)
            # Dan tidak ada detail jalan/kecamatan/desa, kemungkinan besar itu di perairan
            is_generic_boundary = place_rank < 18 and not any(k in address for k in ["road", "suburb", "village", "neighbourhood", "hamlet"])
            
            water_keywords = ["ocean", "sea", "laut", "samudra", "selat", "teluk", "bay", "strait"]
            
            if (osm_class in ["natural", "waterway", "water"] or osm_type in ["water", "ocean", "sea", "coastline"]) or is_generic_boundary:
                if any(kw in display_name.lower() for kw in water_keywords) or is_generic_boundary:
                    geo_type = "Perairan (Laut/Samudra)"
                    geo_warning = "🌊 Lokasi ini berada di wilayah perairan atau sangat jauh dari pemukiman. Tidak mungkin mendirikan bangunan di sini."
                    lokasi_nama = res_geo.get("display_name", "Perairan")
                    return lokasi_nama, geo_type, geo_warning
            
            # --- DETEKSI SUNGAI / DANAU ---
            river_keywords = ["sungai", "river", "danau", "lake", "waduk", "reservoir", "rawa", "marsh"]
            if osm_type in ["river", "stream", "lake", "reservoir", "water"] or osm_class == "waterway":
                geo_type = "Perairan (Sungai/Danau)"
                geo_warning = "🏞️ Lokasi ini berada di badan air (sungai/danau/waduk). Tidak bisa didirikan bangunan."
                lokasi_nama = res_geo.get("display_name", "Badan Air")
                return lokasi_nama, geo_type, geo_warning
            
            # --- DETEKSI KAWASAN LINDUNG ---
            protected_keywords = ["taman nasional", "national park", "cagar alam", "nature reserve", 
                                  "hutan lindung", "protected forest", "suaka margasatwa", "wildlife"]
            if any(kw in display_name.lower() for kw in protected_keywords):
                geo_type = "Kawasan Konservasi / Taman Nasional"
                geo_warning = "🌲 Lokasi ini berada di dalam atau dekat kawasan konservasi/taman nasional. Mendirikan bangunan di sini kemungkinan besar melanggar hukum."
            
            # --- DETEKSI HUTAN ---
            if osm_type in ["forest", "wood"] or (osm_class == "landuse" and "hutan" in display_name.lower()):
                if not geo_warning:
                    geo_type = "Kawasan Hutan"
                    geo_warning = "🌳 Lokasi ini terdeteksi sebagai kawasan hutan. Pastikan izin alih fungsi lahan (IPL) telah diperoleh."

            # Ekstrak Nama
            if 'address' in res_geo:
                addr = res_geo['address']
                kec_part = addr.get('village', addr.get('suburb', addr.get('county', addr.get('city_district', ''))))
                kab_part = addr.get('city', addr.get('state_district', 'Lampung'))
                lokasi_nama = f"{kec_part}, {kab_part}".strip(", ")
            else:
                lokasi_nama = res_geo.get("display_name", lokasi_nama)
                
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return lokasi_nama, geo_type, geo_warning
