import os
from rasterio.merge import merge
import rasterio
import numpy as np

def fetch_demnas_slope(lat, lon):
    """
    Mencoba membaca elevasi dan slope dari file DEMNAS_Gabungan.tif lokal.
    Jika file tidak ada (misal di cloud), gagal secara aman (return None).
    """
    dem_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'denmas', 'DEMNAS_Gabungan.tif')
    
    if not os.path.exists(dem_path):
        return None, None
        
    try:
        with rasterio.open(dem_path) as src:
            if lat < src.bounds.bottom or lat > src.bounds.top or lon < src.bounds.left or lon > src.bounds.right:
                return None, None
                
            vals = src.sample([(lon, lat)])
            elevation_meters = next(vals)[0]
            
            row, col = src.index(lon, lat)
            window = rasterio.windows.Window(col - 1, row - 1, 3, 3)
            
            data = src.read(1, window=window)
            if data.shape != (3, 3):
                return elevation_meters, None
                
            dx = ((data[0][2] + 2*data[1][2] + data[2][2]) - (data[0][0] + 2*data[1][0] + data[2][0])) / 8
            dy = ((data[2][0] + 2*data[2][1] + data[2][2]) - (data[0][0] + 2*data[0][1] + data[0][2])) / 8
            
            cell_size_m = 8.2 
            dist_x = dx / cell_size_m
            dist_y = dy / cell_size_m
            
            slope_percent = np.sqrt(dist_x**2 + dist_y**2) * 100
            return elevation_meters, round(slope_percent, 1)
            
    except Exception as e:
        print(f"DEMNAS Reading Error: {e}")
        return None, None
