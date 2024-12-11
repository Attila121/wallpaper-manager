import requests
from datetime import datetime
from typing import Optional, Dict, Any
import os

class APODClient:
    """Client for NASA's Astronomy Picture of the Day API"""
    
    BASE_URL = "https://api.nasa.gov/planetary/apod"
    
    def __init__(self, api_key: str):
        """
        Initialize the APOD client
        
        Args:
            api_key (str): NASA API key from api.nasa.gov
        """
        self.api_key = api_key
        
    def get_apod(self, date: Optional[datetime] = None) -> Dict[Any, Any]:
        """
        Get the Astronomy Picture of the Day
        
        Args:
            date (datetime, optional): Specific date for APOD. Defaults to today.
            
        Returns:
            dict: APOD data including URL, title, explanation, etc.
        """
        params = {
            'api_key': self.api_key,
            'date': date.strftime('%Y-%m-%d') if date else None,
            'hd': True  # Request HD image if available
        }
        
        response = requests.get(self.BASE_URL, params={k: v for k, v in params.items() if v is not None})
        response.raise_for_status()
        
        return response.json()
    
    def download_image(self, url: str, save_path: str) -> str:
        """
        Download an image from the given URL
        
        Args:
            url (str): URL of the image to download
            save_path (str): Directory to save the image
            
        Returns:
            str: Path to the downloaded image
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract filename from URL or use date if not possible
        filename = url.split('/')[-1]
        if not filename or '?' in filename:
            filename = f"apod_{datetime.now().strftime('%Y%m%d')}.jpg"
            
        full_path = os.path.join(save_path, filename)
        
        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return full_path

# Example usage
if __name__ == "__main__":
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    client = APODClient(api_key)
    
    # Get today's APOD
    apod_data = client.get_apod()
    
    # Download the image
    if apod_data.get('hdurl'):
        image_path = client.download_image(
            apod_data['hdurl'],
            os.path.join(os.path.dirname(__file__), 'downloads')
        )
        print(f"Downloaded image to: {image_path}")
        print(f"Title: {apod_data['title']}")
        print(f"Explanation: {apod_data['explanation']}")
