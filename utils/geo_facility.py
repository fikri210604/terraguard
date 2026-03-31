import requests
import math

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Menghitung jarak lurus (km) antara dua koordinat GPS menggunakan Haversine Formula."""
    R = 6371.0  # Radius bumi dalam kilometer
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return round(distance, 1)

def fetch_nearby_facilities(lat, lon, radius_meters=10000):
    """
    Mengambil data fasilitas umum terdekat (RS, Polisi, Damkar) via Overpass API.
    radius_meters default 10km.
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Query untuk mencari Hospital, Police, dan Fire Station dalam radius tertentu
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius_meters},{lat},{lon});
      node["amenity"="clinic"](around:{radius_meters},{lat},{lon});
      node["amenity"="police"](around:{radius_meters},{lat},{lon});
      node["amenity"="fire_station"](around:{radius_meters},{lat},{lon});
    );
    out body;
    """
    
    facilities = {
        "hospital": {"name": None, "distance": float('inf')},
        "police": {"name": None, "distance": float('inf')},
        "fire_station": {"name": None, "distance": float('inf')}
    }
    
    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            for element in data.get('elements', []):
                f_lat = element.get('lat')
                f_lon = element.get('lon')
                amenity = element.get('tags', {}).get('amenity')
                name = element.get('tags', {}).get('name', 'Fasilitas Tanpa Nama')
                
                if f_lat and f_lon and amenity:
                    dist = calculate_haversine_distance(lat, lon, f_lat, f_lon)
                    
                    # Grouping clinic as hospital for simplicity if hospital is not found
                    key = "hospital" if amenity in ["hospital", "clinic"] else amenity
                    
                    if key in facilities and dist < facilities[key]['distance']:
                        facilities[key]['distance'] = dist
                        facilities[key]['name'] = name
                        
        # Bersihkan inf menjadi None
        for k in facilities:
            if facilities[k]['distance'] == float('inf'):
                facilities[k]['distance'] = None
                
        return facilities

    except Exception as e:
        print(f"Overpass API Error: {e}")
        return {
            "hospital": {"name": None, "distance": None},
            "police": {"name": None, "distance": None},
            "fire_station": {"name": None, "distance": None}
        }
