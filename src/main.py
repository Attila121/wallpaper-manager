import tkinter as tk
from pathlib import Path
from wallpaper_manager import WallpaperManager

class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Wallpaper Manager')
        self.wallpaper_manager = WallpaperManager()
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(expand=True, fill='both')
        
        # Title label
        title = tk.Label(main_frame, text='Wallpaper Manager', font=('Helvetica', 16))
        title.pack(pady=10)
        
        # Buttons
        tk.Button(main_frame, text='Download New Wallpaper', command=self.download_wallpaper).pack(pady=5)
        tk.Button(main_frame, text='Set Random Wallpaper', command=self.set_random_wallpaper).pack(pady=5)
    
    def download_wallpaper(self):
        # TODO: Implement wallpaper download
        pass
    
    def set_random_wallpaper(self):
        # TODO: Implement random wallpaper setting
        pass

def main():
    root = tk.Tk()
    app = WallpaperApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()