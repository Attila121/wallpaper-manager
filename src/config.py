import os
from pathlib import Path

# Try to get API key from environment variable first
NASA_API_KEY = os.getenv('NASA_API_KEY', None)

# If no environment variable, try to read from config_local.py
if NASA_API_KEY is None:
    try:
        from config_local import NASA_API_KEY
    except ImportError:
        NASA_API_KEY = None

# If still no API key, provide instructions
if NASA_API_KEY is None:
    print("""
    ⚠️ NASA API key not found!
    
    To use the APOD feature, you need to:
    1. Get an API key from https://api.nasa.gov/
    2. Either:
        a) Create a file 'config_local.py' in the same directory with:
           NASA_API_KEY = "your-api-key-here"
        b) Set an environment variable:
           set NASA_API_KEY=your-api-key-here (on Windows)
           export NASA_API_KEY=your-api-key-here (on Linux/Mac)
    """)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
WALLPAPER_DIR = PROJECT_ROOT / 'Wallpapers'