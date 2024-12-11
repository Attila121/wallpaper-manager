import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from wallpaper_manager import WallpaperManager
from PIL import Image, ImageTk
import threading
from utils.logger import WallpaperLogger
import traceback

class ModernWallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Wallpaper Manager')
        self.root.geometry('1024x768')
        self.wallpaper_manager = WallpaperManager()
        self.logger = WallpaperLogger(__name__)
        
        # State variables
        self.current_wallpaper_info = None
        self.download_in_progress = False
        
        # Configure style
        self.setup_styles()
        
        # Setup UI
        self.setup_ui()
        
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        
        # Configure main styles
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'))
        style.configure('Subheader.TLabel', font=('Segoe UI', 12))
        style.configure('Info.TLabel', font=('Segoe UI', 10))
        style.configure('Action.TButton', font=('Segoe UI', 10), padding=10)
        
        # Configure frames
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        
    def setup_ui(self):
        # Main container with padding
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        title = ttk.Label(header_frame, text='Wallpaper Manager', style='Header.TLabel')
        title.pack(side="left")
        
        # Action buttons in header
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side="right")
        
        self.download_btn = ttk.Button(
            button_frame, 
            text='Download New APOD', 
            style='Action.TButton',
            command=self.download_wallpaper
        )
        self.download_btn.pack(side="left", padx=5)
        
        self.random_btn = ttk.Button(
            button_frame, 
            text='Set Random Wallpaper', 
            style='Action.TButton',
            command=self.set_random_wallpaper
        )
        self.random_btn.pack(side="left", padx=5)
        
        # Preview section
        preview_frame = ttk.LabelFrame(self.main_frame, text='Preview', padding="10")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(expand=True, fill="both")
        
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.main_frame,
            length=300,
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.progress.grid_remove()  # Hide initially
        
        # Information section
        info_frame = ttk.LabelFrame(self.main_frame, text='Wallpaper Information', padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        # Title and date in info frame
        title_date_frame = ttk.Frame(info_frame)
        title_date_frame.pack(fill="x", pady=(0, 10))
        
        self.title_label = ttk.Label(
            title_date_frame, 
            text='No wallpaper selected', 
            style='Subheader.TLabel',
            wraplength=900
        )
        self.title_label.pack(side="left")
        
        self.date_label = ttk.Label(
            title_date_frame, 
            text='', 
            style='Info.TLabel'
        )
        self.date_label.pack(side="right")
        
        # Explanation text
        self.explanation_text = tk.Text(
            info_frame, 
            height=6, 
            wrap=tk.WORD, 
            font=('Segoe UI', 10),
            padx=10,
            pady=10
        )
        self.explanation_text.pack(fill="both", expand=True)
        
        # Add scrollbar to explanation text
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.explanation_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.explanation_text.configure(yscrollcommand=scrollbar.set)
        
        # Make text readonly
        self.explanation_text.configure(state='disabled')
        
    def show_progress(self):
        """Show progress bar"""
        self.progress.grid()
        self.progress.start()
        
    def hide_progress(self):
        """Hide progress bar"""
        self.progress.stop()
        self.progress.grid_remove()
        
    def update_preview(self, image_path: str):
        """Update the preview with the given image"""
        try:
            with Image.open(image_path) as img:
                # Calculate resize dimensions keeping aspect ratio
                max_size = (800, 400)
                img.thumbnail(max_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.preview_label.configure(image=photo)
                self.preview_label.image = photo
        except Exception as e:
            self.logger.exception("Error updating preview")
            raise Exception(f"Failed to load preview: {str(e)}")
    
    def update_info(self, info: dict):
        """Update the information display"""
        try:
            if info:
                self.title_label.config(text=info.get('title', 'N/A'))
                self.date_label.config(text=f"Date: {info.get('date', 'N/A')}")
                
                # Update explanation text
                self.explanation_text.configure(state='normal')
                self.explanation_text.delete('1.0', tk.END)
                self.explanation_text.insert('1.0', info.get('explanation', 'No explanation available.'))
                self.explanation_text.configure(state='disabled')
            else:
                self.title_label.config(text="No information available")
                self.date_label.config(text="")
                self.explanation_text.configure(state='normal')
                self.explanation_text.delete('1.0', tk.END)
                self.explanation_text.configure(state='disabled')
        except Exception as e:
            self.logger.exception("Error updating info display")
            raise Exception(f"Failed to update information display: {str(e)}")
    
    def show_error(self, error_message: str, error_details: str = None):
        """Show error message to user with optional details"""
        if error_details:
            detailed_message = f"{error_message}\n\nDetails:\n{error_details}"
        else:
            detailed_message = error_message
        
        messagebox.showerror("Error", detailed_message)
    
    def download_wallpaper(self):
        if self.download_in_progress:
            return
        
        def download_thread():
            self.download_in_progress = True
            self.root.after(0, self.show_progress)
            
            try:
                info = self.wallpaper_manager.get_daily_apod_wallpaper()
                if info:
                    path_str = str(info['path'])
                    
                    def update_ui():
                        try:
                            self.update_preview(path_str)
                            self.update_info(info)
                            messagebox.showinfo("Success", "New wallpaper downloaded successfully!")
                        except Exception as ui_error:
                            self.logger.exception("Error updating UI")
                            self.show_error("Failed to update display", str(ui_error))
                    
                    self.root.after(0, update_ui)
                else:
                    self.root.after(0, lambda: self.show_error("Failed to download wallpaper"))
            
            except Exception as e:
                error_message = str(e)
                error_details = traceback.format_exc()
                self.logger.exception("Error in download_wallpaper")
                
                def show_error():
                    self.show_error(
                        "Failed to download wallpaper",
                        f"Error: {error_message}\n\nDetails: {error_details}"
                    )
                
                self.root.after(0, show_error)
            
            finally:
                self.download_in_progress = False
                self.root.after(0, self.hide_progress)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def set_random_wallpaper(self):
        try:
            wallpapers = list(Path(self.wallpaper_manager.wallpaper_dir).glob('*.*'))
            
            if not wallpapers:
                messagebox.showinfo("Info", "No wallpapers available. Download some first!")
                return
            
            import random
            wallpaper = random.choice(wallpapers)
            
            if self.wallpaper_manager.set_wallpaper(wallpaper):
                self.update_preview(str(wallpaper))
                messagebox.showinfo("Success", "Wallpaper changed successfully!")
            else:
                self.show_error("Failed to set wallpaper")
        
        except Exception as e:
            self.logger.exception("Error in set_random_wallpaper")
            self.show_error("Failed to set wallpaper", str(e))

def main():
    try:
        root = tk.Tk()
        app = ModernWallpaperApp(root)
        root.mainloop()
    except Exception as e:
        logger = WallpaperLogger(__name__)
        logger.exception("Fatal error in main")
        messagebox.showerror(
            "Fatal Error", 
            f"Application failed to start: {str(e)}\n\n"
            f"Please check the logs for details."
        )

if __name__ == '__main__':
    main()