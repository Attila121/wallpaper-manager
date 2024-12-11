# Wallpaper Manager

A wallpaper management application that allows you to download, organize, and automatically set wallpapers on your Windows system. Built with Python and Tkinter, featuring NASA's Astronomy Picture of the Day (APOD) integration.

## Features

### Current Features
- ✓ User-friendly interface with split-view design
- ✓ NASA APOD integration for daily wallpapers
- ✓ Searchable wallpaper library
- ✓ Real-time wallpaper preview
- ✓ Random wallpaper selection
- ✓ Manual wallpaper selection
- ✓ Automatic wallpaper downloading
- ✓ Comprehensive error handling and logging
- ✓ Detailed wallpaper information display

### Planned Features
- Automatic wallpaper rotation
- Wallpaper scheduling
- Category-based organization
- Favorite wallpapers collection
- Multi-monitor support
- Android support (via BeeWare)
- Additional wallpaper sources

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Conda (recommended) or pip
- Windows operating system (currently)
- NASA API key for APOD features

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Attila121/wallpaper-manager.git
cd wallpaper-manager
```

2. Set up Conda environment (recommended):
```bash
conda create -n wallpaper-manager python=3.8
conda activate wallpaper-manager
conda install --file requirements.txt
```

   Or with pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure NASA API Key:
   - Get your API key from [NASA API Portal](https://api.nasa.gov/)
   - Either:
     - Create `src/config_local.py` with: `NASA_API_KEY = "your-api-key"`
     - Set environment variable: `NASA_API_KEY=your-api-key`

### Running the Application

```bash
python src/main.py
```

## Usage

1. **Download New Wallpaper**:
   - Click "Download New APOD" to get today's NASA astronomy picture
   - View image details in the information panel

2. **Select Wallpaper**:
   - Browse your wallpaper collection in the left panel
   - Use the search box to filter wallpapers
   - Click any wallpaper to preview it
   - Click "Set Selected Wallpaper" to apply it

3. **Random Wallpaper**:
   - Click "Set Random Wallpaper" to randomly select and apply a wallpaper

4. **Managing Wallpapers**:
   - All wallpapers are stored in the `Wallpapers/` directory
   - Use the refresh button to update the wallpaper list
   - Preview shows the full image with proper aspect ratio

## Project Structure

```
wallpaper-manager/
├── requirements.txt (Project dependencies)
├── Wallpapers/ (Local wallpaper storage)
└── src/
    ├── main.py (GUI application)
    ├── wallpaper_manager.py (Core functionality)
    ├── apod_client.py (NASA APOD API integration)
    ├── config.py (Configuration management)
    └── utils/
        └── logger.py (Logging functionality)
```

## Development

This project is under active development. Here's our roadmap:

1. Windows Version (Current Phase)
   - Core functionality implementation
   - GUI development
   - API integration

2. Cross-Platform Preparation
   - Code reorganization
   - BeeWare integration

3. Android Development
   - Android-specific features
   - Testing and optimization

4. Distribution
   - Windows installer
   - Android APK
   - App store deployment

### Logging

- Logs are stored in the `logs/` directory
- Check error.log for detailed error information
- Debug.log contains development-related information

## Acknowledgments

- NASA for providing the APOD API
- The Python community for the excellent libraries
- Contributors and users of the project

