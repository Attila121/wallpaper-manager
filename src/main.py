import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from wallpaper_manager import WallpaperManager
from PIL import Image, ImageTk
import threading
from utils.logger import WallpaperLogger
import traceback
from datetime import datetime
from APODDetailsWindow import APODDetailsWindow
class ModernWallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Wallpaper Manager')
        self.root.geometry('1200x800')
        self.root.configure(bg='#f0f0f0')
        
        self.wallpaper_manager = WallpaperManager()
        self.logger = WallpaperLogger(__name__)
        
        # State variables
        self.current_wallpaper_info = None
        self.download_in_progress = False
        self.wallpapers_list = []
        
        self.setup_styles()
        self.setup_ui()
        self.load_wallpapers()
    
    def setup_styles(self):
        """Configure modern styles using ttk"""
        style = ttk.Style()
        
        # Configure colors
        self.colors = {
            'primary': '#2563eb',  # Blue
            'primary_hover': '#1d4ed8',
            'bg': '#f0f0f0',  # Light gray
            'card': '#ffffff',  # White
            'text': '#1f2937',  # Dark gray
            'text_secondary': '#6b7280'  # Medium gray
        }
        
        # Configure fonts
        self.fonts = {
            'heading': ('Segoe UI', 24, 'bold'),
            'subheading': ('Segoe UI', 16),
            'body': ('Segoe UI', 10),
            'small': ('Segoe UI', 9)
        }
        
        # Configure common styles
        style.configure('Modern.TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['card'])
        
        style.configure('Modern.TLabel', 
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=self.fonts['body'])
        
        style.configure('Heading.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=self.fonts['heading'])
        
        style.configure('Modern.TButton',
                       font=self.fonts['body'],
                       padding=10)
        
        # Configure button hover effect
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_hover'])],
                 foreground=[('active', 'white')])
    
    def setup_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Modern.TFrame', padding=20)
        self.main_frame.pack(fill='both', expand=True)
        
        # Header section
        self.setup_header()
        
        # Content section
        self.content_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        self.content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Split view
        self.setup_split_view()
        
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.main_frame,
            length=300,
            variable=self.progress_var,
            mode='indeterminate'
        )
        
    def setup_header(self):
        header_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        title_frame.pack(side='left')
        
        title = ttk.Label(title_frame, 
                         text='Wallpaper Manager',
                         style='Heading.TLabel')
        title.pack(anchor='w')
        
        subtitle = ttk.Label(title_frame,
                           text='Manage and organize your wallpapers',
                           style='Modern.TLabel',
                           foreground=self.colors['text_secondary'])
        subtitle.pack(anchor='w')
        
        # Action buttons
        button_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        button_frame.pack(side='right')
        
        self.download_btn = ttk.Button(
            button_frame,
            text='Download New APOD',
            style='Modern.TButton',
            command=self.download_wallpaper
        )
        self.download_btn.pack(side='left', padx=5)
        
        self.random_btn = ttk.Button(
            button_frame,
            text='Set Random Wallpaper',
            style='Modern.TButton',
            command=self.set_random_wallpaper
        )
        self.random_btn.pack(side='left', padx=5)
    
    def setup_split_view(self):
        # Left panel (Wallpaper list)
        left_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=15)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Search bar
        search_frame = ttk.Frame(left_frame, style='Card.TFrame')
        search_frame.pack(fill='x', pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_wallpapers)
        
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.search_var,
                               font=self.fonts['body'])
        search_entry.pack(side='left', fill='x', expand=True)
        
        refresh_btn = ttk.Button(
            search_frame,
            text='↻',
            width=3,
            command=self.load_wallpapers
        )
        refresh_btn.pack(side='right', padx=(5, 0))
        
        # Wallpaper list
        list_frame = ttk.Frame(left_frame, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True)
        
        self.wallpaper_list = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=self.fonts['body'],
            bg=self.colors['card'],
            fg=self.colors['text'],
            selectbackground=self.colors['primary'],
            selectforeground='white',
            borderwidth=0,
            highlightthickness=0
        )
        self.wallpaper_list.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical',
                                command=self.wallpaper_list.yview)
        scrollbar.pack(side='right', fill='y')
        self.wallpaper_list.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.wallpaper_list.bind('<<ListboxSelect>>', self.on_wallpaper_select)
        
        # Right panel (Preview and info)
        right_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=15)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Preview section
        preview_label = ttk.Label(right_frame,
                                text='Preview',
                                style='Modern.TLabel',
                                font=self.fonts['subheading'])
        preview_label.pack(anchor='w', pady=(0, 10))
        
        self.preview_frame = ttk.Frame(right_frame, style='Card.TFrame')
        self.preview_frame.pack(fill='both', expand=True)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True)
        
        # Set wallpaper button
        self.set_btn = ttk.Button(
            right_frame,
            text='Set as Wallpaper',
            style='Modern.TButton',
            command=self.set_selected_wallpaper
        )
        self.set_btn.pack(pady=10)
        buttons_frame = ttk.Frame(right_frame, style='Card.TFrame')
        buttons_frame.pack(pady=10)
        
        self.set_btn = ttk.Button(
            buttons_frame,
            text='Set as Wallpaper',
            style='Modern.TButton',
            command=self.set_selected_wallpaper
        )
        self.set_btn.pack(side='left', padx=5)
        
        self.details_btn = ttk.Button(
            buttons_frame,
            text='Show Details',
            style='Modern.TButton',
            command=self.show_details
        )
        self.details_btn.pack(side='left', padx=5)
        
        # Information section
        info_frame = ttk.Frame(right_frame, style='Card.TFrame', padding=10)
        info_frame.pack(fill='x', pady=(10, 0))
        
        self.title_label = ttk.Label(
            info_frame,
            text='No wallpaper selected',
            style='Modern.TLabel',
            font=self.fonts['subheading']
        )
        self.title_label.pack(anchor='w')
        
        self.date_label = ttk.Label(
            info_frame,
            text='',
            style='Modern.TLabel',
            foreground=self.colors['text_secondary']
        )
        self.date_label.pack(anchor='w')
        
        self.explanation_text = tk.Text(
            info_frame,
            height=4,
            wrap=tk.WORD,
            font=self.fonts['body'],
            bg=self.colors['card'],
            fg=self.colors['text'],
            borderwidth=0,
            padx=0,
            pady=10
        )
        self.explanation_text.pack(fill='both', expand=True)
        self.explanation_text.configure(state='disabled')

    def load_wallpapers(self):
        """Load existing wallpapers into the list"""
        try:
            self.wallpapers_list = list(Path(self.wallpaper_manager.wallpaper_dir).glob('*.*'))
            self.wallpaper_list.delete(0, tk.END)
            
            for wallpaper in sorted(self.wallpapers_list, key=lambda x: x.stat().st_mtime, reverse=True):
                self.wallpaper_list.insert(tk.END, wallpaper.name)
                
        except Exception as e:
            self.logger.exception("Error loading wallpapers")
            self.show_error("Failed to load wallpapers", str(e))
    
    def filter_wallpapers(self, *args):
        """Filter wallpapers based on search text"""
        search_text = self.search_var.get().lower()
        self.wallpaper_list.delete(0, tk.END)
        
        for wallpaper in self.wallpapers_list:
            if search_text in wallpaper.name.lower():
                self.wallpaper_list.insert(tk.END, wallpaper.name)
    
    def update_preview(self, image_path: str):
        """Update the preview with the given image"""
        try:
            with Image.open(image_path) as img:
                # Calculate resize dimensions keeping aspect ratio
                preview_width = 600
                preview_height = 400
                img.thumbnail((preview_width, preview_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.preview_label.configure(image=photo)
                self.preview_label.image = photo  # Keep a reference
        except Exception as e:
            self.logger.exception("Error updating preview")
            raise Exception(f"Failed to load preview: {str(e)}")
    
    def show_error(self, title: str, message: str = None):
        """Show error message with modern styling"""
        messagebox.showerror(title, message or title)
    
    def download_wallpaper(self):
        """Download new wallpaper from APOD"""
        if self.download_in_progress:
            return
        
        def download_thread():
            self.download_in_progress = True
            self.progress.pack(pady=10)
            self.progress.start()
            
            try:
                info = self.wallpaper_manager.get_daily_apod_wallpaper()
                if info:
                    def update_ui():
                        self.current_wallpaper_info = info
                        self.update_preview(str(info['path']))
                        # Update the explanation and other metadata
                        self.title_label.config(text=info.get('title', 'No title'))
                        self.date_label.config(text=f"Date: {info.get('date', 'Unknown')}")
                        
                        # Update explanation text
                        self.explanation_text.configure(state='normal')
                        self.explanation_text.delete('1.0', tk.END)
                        self.explanation_text.insert('1.0', info.get('explanation', 'No explanation available.'))
                        self.explanation_text.configure(state='disabled')
                        
                        self.load_wallpapers()  # Refresh list
                        messagebox.showinfo("Success", "New wallpaper downloaded successfully!")
                    self.root.after(0, update_ui)
                else:
                    self.show_error("Download Failed", "Could not download wallpaper")
            except Exception as e:
                self.logger.exception("Download error")
                self.show_error("Download Error", str(e))
            finally:
                self.download_in_progress = False
                self.progress.stop()
                self.progress.pack_forget()
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def set_selected_wallpaper(self):
        """Set the currently selected wallpaper"""
        selection = self.wallpaper_list.curselection()
        if not selection:
            messagebox.showinfo("Select Wallpaper", "Please select a wallpaper first!")
            return
        
        wallpaper_name = self.wallpaper_list.get(selection[0])
        wallpaper_path = self.wallpaper_manager.wallpaper_dir / wallpaper_name
        
        try:
            if self.wallpaper_manager.set_wallpaper(wallpaper_path):
                messagebox.showinfo("Success", "Wallpaper set successfully!")
            else:
                self.show_error("Failed to set wallpaper")
        except Exception as e:
            self.logger.exception("Error setting wallpaper")
            self.show_error("Error", f"Failed to set wallpaper: {str(e)}")

    def on_wallpaper_select(self, event):
        """Handle wallpaper selection"""
        selection = self.wallpaper_list.curselection()
        if not selection:
            return
            
        wallpaper_name = self.wallpaper_list.get(selection[0])
        wallpaper_path = self.wallpaper_manager.wallpaper_dir / wallpaper_name
        
        try:
            self.update_preview(str(wallpaper_path))
            
            # Get metadata if available
            metadata = self.wallpaper_manager.get_wallpaper_metadata(wallpaper_path)
            if metadata:
                self.current_wallpaper_info = metadata
                self.title_label.config(text=metadata.get('title', wallpaper_name))
                self.date_label.config(
                    text=f"Date: {metadata.get('date', 'Unknown')}"
                )
                # Update other UI elements with metadata
            else:
                # Fallback to basic file info
                stats = wallpaper_path.stat()
                self.current_wallpaper_info = None
                self.title_label.config(text=wallpaper_name)
                self.date_label.config(
                    text=f"Added: {datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')}"
                )
                
        except Exception as e:
            self.logger.exception("Error updating preview")
            self.show_error("Preview Error", str(e))

    def set_random_wallpaper(self):
        """Set a random wallpaper from the collection"""
        try:
            if not self.wallpapers_list:
                messagebox.showinfo("No Wallpapers", "Please download some wallpapers first!")
                return
            
            import random
            wallpaper = random.choice(self.wallpapers_list)
            
            if self.wallpaper_manager.set_wallpaper(wallpaper):
                self.update_preview(str(wallpaper))
                messagebox.showinfo("Success", "Random wallpaper set successfully!")
            else:
                self.show_error("Failed to set wallpaper")
        except Exception as e:
            self.logger.exception("Error setting random wallpaper")
            self.show_error("Error", str(e))
    
    def show_details(self):
        """Show APOD details in a popup window"""
        if self.current_wallpaper_info:
            APODDetailsWindow(self.root, self.current_wallpaper_info)
        else:
            messagebox.showinfo("No Details", "Please select or download an APOD wallpaper first.")


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