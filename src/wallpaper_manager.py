from pathlib import Path
import requests
from PIL import Image
import ctypes
import os

class WallpaperManager:
    def __init__(self):
        self.wallpaper_dir = Path.home() / 'Pictures' / 'Wallpapers'
        self.wallpaper_dir.mkdir(parents=True, exist_ok=True)
    
    def download_wallpaper(self, url):
        """Download wallpaper from URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Generate filename from URL
            filename = Path(url).name
            save_path = self.wallpaper_dir / filename
            
            # Save the image
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return save_path
        except Exception as e:
            print(f'Error downloading wallpaper: {e}')
            return None
    
    def set_wallpaper(self, image_path):
        """Set wallpaper on Windows"""
        try:
            # Convert path to absolute path
            abs_path = str(Path(image_path).resolve())
            
            # Windows specific wallpaper setting
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
            
            return True
        except Exception as e:
            print(f'Error setting wallpaper: {e}')
            return False