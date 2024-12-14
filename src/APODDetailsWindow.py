import tkinter as tk
from tkinter import ttk

class APODDetailsWindow:
    def __init__(self, parent, info):
        self.window = tk.Toplevel(parent)
        self.window.title("APOD Details")
        self.window.geometry("800x600")
        
        # Configure the window style
        self.window.configure(bg='#f0f0f0')
        self.setup_ui(info)
        
        # Make the window modal
        self.window.transient(parent)
        self.window.grab_set()
        
    def setup_ui(self, info):
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=info.get('title', 'No title'),
            font=('Segoe UI', 16, 'bold'),
            wraplength=760
        )
        title_label.pack(anchor='w', pady=(0, 5))
        
        # Metadata frame
        meta_frame = ttk.Frame(main_frame)
        meta_frame.pack(fill='x', pady=(0, 15))
        
        # Date and copyright info
        date_text = f"Date: {info.get('date', 'Unknown')}"
        if 'copyright' in info:
            date_text += f" © {info['copyright']}"
        
        date_label = ttk.Label(
            meta_frame,
            text=date_text,
            font=('Segoe UI', 10),
            foreground='#666666'
        )
        date_label.pack(anchor='w')
        
        # Media type info
        media_label = ttk.Label(
            meta_frame,
            text=f"Media Type: {info.get('media_type', 'Unknown')}",
            font=('Segoe UI', 10),
            foreground='#666666'
        )
        media_label.pack(anchor='w')
        
        # Links frame for HD URL if available
        if info.get('hdurl'):
            link_frame = ttk.Frame(meta_frame)
            link_frame.pack(anchor='w', pady=(5, 0))
            
            link_label = ttk.Label(
                link_frame,
                text="HD Version available at: ",
                font=('Segoe UI', 10),
                foreground='#666666'
            )
            link_label.pack(side='left')
            
            url_label = ttk.Label(
                link_frame,
                text=info['hdurl'],
                font=('Segoe UI', 10),
                foreground='#0066cc',
                cursor='hand2'
            )
            url_label.pack(side='left')
            
            # Make URL clickable
            url_label.bind("<Button-1>", lambda e: self.open_url(info['hdurl']))
        
        # Explanation
        explanation_frame = ttk.LabelFrame(main_frame, text="Explanation", padding=10)
        explanation_frame.pack(fill='both', expand=True)
        
        # Create Text widget with scrollbar for explanation
        text_frame = ttk.Frame(explanation_frame)
        text_frame.pack(fill='both', expand=True)
        
        scroll = ttk.Scrollbar(text_frame)
        scroll.pack(side='right', fill='y')
        
        explanation_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            padx=10,
            pady=10,
            height=15
        )
        explanation_text.pack(side='left', fill='both', expand=True)
        
        # Configure scrollbar
        scroll.config(command=explanation_text.yview)
        explanation_text.config(yscrollcommand=scroll.set)
        
        # Insert explanation text
        explanation_text.insert('1.0', info.get('explanation', 'No explanation available.'))
        explanation_text.config(state='disabled')
        
        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.window.destroy,
            padding=(20, 5)
        )
        close_btn.pack(pady=(15, 0))
        
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)