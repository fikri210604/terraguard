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
        url_geo = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=18"
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
                    geo_warning = "[TERLARANG] 🌊 Lokasi ini berada di wilayah perairan lepas. Anda tidak bisa mendirikan bangunan di atas laut."
                    lokasi_nama = res_geo.get("display_name", "Perairan")
                    return lokasi_nama, geo_type, geo_warning
            
            # --- DETEKSI SUNGAI / DANAU ---
            if osm_type in ["river", "stream", "lake", "reservoir", "water"] or osm_class == "waterway":
                geo_type = "Perairan (Sungai/Danau)"
                geo_warning = "[TERLARANG] 🏞️ Lokasi ini tepat berada di badan air (sungai/danau/waduk). Investasi lahan di sini tidak dimungkinkan karena merupakan milik negara."
                lokasi_nama = res_geo.get("display_name", "Badan Air")
                return lokasi_nama, geo_type, geo_warning
                
            # --- DETEKSI INFRASTRUKTUR PUBLIK (JALAN & REL) ---
            if osm_class == "highway":
                geo_type = "Infrastruktur (Jalan Raya)"
                geo_warning = "[TERLARANG] 🛣️ Lahan ini berada tepat di atas atau memotong Jalur Jalan Raya / Tol. Lahan tidak bisa disertifikasi / dibangun rumah pribadi."
                lokasi_nama = res_geo.get("display_name", "Jalan Utama")
                return lokasi_nama, geo_type, geo_warning
                
            if osm_class == "railway":
                geo_type = "Infrastruktur (Rel Kereta)"
                geo_warning = "[TERLARANG] 🚂 Lahan ini persis berada di atas Jalur Rel Kereta Api (Aset PT KAI). Membangun rumah di sini melanggar undang-undang perkeretaapian."
                lokasi_nama = res_geo.get("display_name", "Rel Kereta Api")
                return lokasi_nama, geo_type, geo_warning
            
            # --- DETEKSI KAWASAN LINDUNG ---
            protected_keywords = ["taman nasional", "national park", "cagar alam", "nature reserve", 
                                  "hutan lindung", "protected forest", "suaka margasatwa", "wildlife"]
            if any(kw in display_name.lower() for kw in protected_keywords):
                geo_type = "Kawasan Konservasi / Taman Nasional"
                geo_warning = "🌲 Lokasi ini berada di dalam / dekat Kawasan Konservasi. Mendirikan bangunan masif kemungkinan melanggar hukum kehutanan."
            
            # --- DETEKSI HUTAN ---
            elif osm_type in ["forest", "wood"] or (osm_class == "landuse" and "hutan" in display_name.lower()):
                if not geo_warning:
                    geo_type = "Kawasan Hutan"
                    geo_warning = "🌳 Lokasi terdeteksi sebagai zona vegetasi / hutan. Pastikan izin alih fungsi lahan (IPL) telah diperoleh."
                    
            # --- DETEKSI PERUMAHAN & ALAM LAINNYA ---
            elif osm_class == "landuse" and osm_type == "residential":
                geo_type = "Kawasan Pemukiman (Residential)"
                geo_warning = "🏡 Lahan ini berada di dalam batas pemukiman/perumahan padat. Sangat cocok dan legal untuk pembangunan rumah baru."
                
            elif osm_class == "natural" and osm_type in ["peak", "hill", "volcano", "ridge", "cliff"]:
                geo_type = "Kawasan Perbukitan / Dataran Tinggi"
                geo_warning = "⛰️ Lokasi berada di kawasan perbukitan puncak. Hati-hati dengan biaya pembangunan (*cut and fill*) yang ekstrem."

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
