from pathlib import Path
import requests
from PIL import Image
import ctypes
import os
from typing import Optional, Dict, Any
from datetime import datetime

from apod_client import APODClient
from config import NASA_API_KEY, WALLPAPER_DIR
from utils.logger import (
    WallpaperLogger, 
    log_operation, 
    DownloadError, 
    WallpaperSetError, 
    APIError
)

class WallpaperManager:
    def __init__(self, api_key: str = NASA_API_KEY):
        """
        Initialize WallpaperManager
        
        Args:
            api_key (str, optional): NASA API key for APOD service.
            Defaults to value from config.py.
        """
        self.logger = WallpaperLogger(__name__)
        self.wallpaper_dir = WALLPAPER_DIR
        self.wallpaper_dir.mkdir(parents=True, exist_ok=True)

        if not api_key:
            self.logger.warning("No API key provided. APOD features will be disabled.")
        self.apod_client = APODClient(api_key) if api_key else None
        
        # Set initial context for logging
        self.logger.set_context(
            wallpaper_dir=str(self.wallpaper_dir),
            apod_enabled=bool(self.apod_client)
        )

    @log_operation()
    def download_wallpaper(self, url: str) -> Path:
        """
        Download wallpaper from URL
        
        Args:
            url (str): URL to download wallpaper from
            
        Returns:
            Path: Path to downloaded wallpaper
            
        Raises:
            DownloadError: If download fails
        """
        try:
            self.logger.info(f"Downloading wallpaper from {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Generate filename from URL and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{Path(url).name}"
            save_path = self.wallpaper_dir / filename
            
            # Download with progress tracking
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                        self.logger.debug(f"Download progress: {progress:.1f}%")
            
            self.logger.info(f"Download completed: {save_path}")
            return save_path
            
        except requests.RequestException as e:
            raise DownloadError(
                f"Failed to download wallpaper: {str(e)}", 
                details={
                    'url': url,
                    'status_code': getattr(e.response, 'status_code', None),
                    'response_text': getattr(e.response, 'text', None)
                }
            )
        except OSError as e:
            raise DownloadError(
                f"Failed to save wallpaper: {str(e)}",
                details={'url': url, 'save_path': str(save_path)}
            )

    @log_operation()
    def set_wallpaper(self, image_path: Path) -> bool:
        """
        Set wallpaper on Windows
        
        Args:
            image_path (Path): Path to wallpaper image
            
        Returns:
            bool: True if successful
            
        Raises:
            WallpaperSetError: If setting wallpaper fails
        """
        try:
            # Validate image before setting
            self._validate_image(image_path)
            
            # Convert path to absolute path
            abs_path = str(Path(image_path).resolve())
            
            # Windows specific wallpaper setting
            result = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
            
            if not result:
                raise WallpaperSetError(
                    "Failed to set wallpaper through Windows API",
                    details={'image_path': str(image_path)}
                )
            
            self.logger.info(f"Successfully set wallpaper: {image_path}")
            return True
            
        except OSError as e:
            raise WallpaperSetError(
                f"Failed to access wallpaper file: {str(e)}",
                details={'image_path': str(image_path)}
            )
        except Exception as e:
            raise WallpaperSetError(
                f"Unexpected error setting wallpaper: {str(e)}",
                details={'image_path': str(image_path)}
            )

    @log_operation()
    def get_daily_apod_wallpaper(self) -> Dict[str, Any]:
        """
        Downloads and sets today's APOD as wallpaper
        
        Returns:
            dict: Information about the wallpaper including path and metadata
            
        Raises:
            APIError: If APOD API request fails
            DownloadError: If wallpaper download fails
        """
        if not self.apod_client:
            raise APIError(
                "NASA API key not provided. Cannot fetch APOD.",
                details={'api_enabled': False}
            )
            
        try:
            # Get APOD data
            self.logger.info("Fetching APOD data")
            apod_data = self.apod_client.get_apod()
            
            # Download the image
            image_url = apod_data.get('hdurl') or apod_data['url']
            image_path = self.download_wallpaper(image_url)
            
            result = {
                'path': image_path,
                'title': apod_data['title'],
                'explanation': apod_data['explanation'],
                'date': apod_data['date']
            }
            
            self.logger.info("Successfully retrieved APOD wallpaper", 
                           wallpaper_info=result)
            return result
            
        except requests.RequestException as e:
            raise APIError(
                f"APOD API request failed: {str(e)}",
                details={
                    'status_code': getattr(e.response, 'status_code', None),
                    'response_text': getattr(e.response, 'text', None)
                }
            )

    def _validate_image(self, image_path: Path) -> None:
        """
        Validate image file before setting as wallpaper
        
        Args:
            image_path (Path): Path to image file
            
        Raises:
            WallpaperSetError: If image is invalid
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception as e:
            raise WallpaperSetError(
                f"Invalid image file: {str(e)}",
                details={'image_path': str(image_path)}
            )