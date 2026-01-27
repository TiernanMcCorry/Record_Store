import tkinter as tk
from tkinter import ttk, messagebox
from config import FONTS, COLORS, set_theme
import json
import os

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        
        # Load theme preference
        self.load_theme_preference()
        
        # Setup window
        self.setup_window()
        self.create_widgets()
    
    def load_theme_preference(self):
        """Load theme preference from config file"""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vinylflow_config.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    dark_mode = config.get('dark_mode', False)
                    set_theme('dark' if dark_mode else 'light')
        except:
            set_theme('light')
    
    def setup_window(self):
        """Setup the login window"""
        self.window = tk.Toplevel(self.root)
        self.window.title("VinylFlow - Login")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS['bg'])
        
        # Center window
        self.center_window(self.window)
        
        # Make window modal
        self.window.transient(self.root)
        self.window.grab_set()
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.owner_login())
    
    def center_window(self, window):
        """Center window on screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all widgets for the login window"""
        # Main container with padding
        main_frame = tk.Frame(self.window, bg=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header with logo
        self.create_header(main_frame)
        
        # Login form
        self.create_login_form(main_frame)
        
        # Footer with options
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Create the header section with logo"""
        header_frame = tk.Frame(parent, bg=COLORS['bg'])
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Vinyl icon
        icon_label = tk.Label(
            header_frame,
            text="💿",
            font=('Segoe UI Emoji', 48),
            bg=COLORS['bg'],
            fg=COLORS['primary']
        )
        icon_label.pack()
        
        # App title
        title_label = tk.Label(
            header_frame,
            text="VinylFlow",
            font=FONTS['title'],
            bg=COLORS['bg'],
            fg=COLORS['primary']
        )
        title_label.pack(pady=(10, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Record Store Management System",
            font=FONTS['subtitle'],
            bg=COLORS['bg'],
            fg=COLORS['fg']
        )
        subtitle_label.pack()
    
    def create_login_form(self, parent):
        """Create the login form"""
        form_frame = tk.Frame(parent, bg=COLORS['bg'])
        form_frame.pack(fill='x', pady=(0, 30))
        
        # Username field
        tk.Label(
            form_frame,
            text="Username",
            font=FONTS['label'],
            bg=COLORS['bg'],
            fg=COLORS['fg']
        ).pack(anchor='w', pady=(10, 5))
        
        self.username_entry = self.create_entry(form_frame, "Enter username...")
        self.username_entry.pack(fill='x', pady=(0, 15))
        
        # Password field
        tk.Label(
            form_frame,
            text="Password",
            font=FONTS['label'],
            bg=COLORS['bg'],
            fg=COLORS['fg']
        ).pack(anchor='w', pady=(5, 5))
        
        self.password_entry = self.create_entry(form_frame, "Enter password...", show="●")
        self.password_entry.pack(fill='x', pady=(0, 25))
        
        # Login buttons frame
        button_frame = tk.Frame(form_frame, bg=COLORS['bg'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Owner login button (left side)
        owner_btn = tk.Button(
            button_frame,
            text="Login as Owner",
            font=FONTS['button'],
            bg=COLORS['primary'],
            fg=COLORS['white'],
            relief='flat',
            command=self.owner_login,
            cursor='hand2',
            padx=20,
            pady=10
        )
        owner_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Customer login button (right side)
        customer_btn = tk.Button(
            button_frame,
            text="Continue as Customer",
            font=FONTS['button'],
            bg=COLORS['secondary'],
            fg=COLORS['white'],
            relief='flat',
            command=self.customer_login,
            cursor='hand2',
            padx=20,
            pady=10
        )
        customer_btn.pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        # Focus on username field
        self.username_entry.focus()
    
    def create_entry(self, parent, placeholder, show=""):
        """Create a styled entry field with placeholder"""
        entry = tk.Entry(
            parent,
            font=FONTS['entry'],
            bg=COLORS['entry_bg'],
            fg=COLORS['fg'],
            relief='solid',
            borderwidth=1,
            show=show
        )
        
        # Add placeholder functionality
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=COLORS['dark_gray'])
            
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=COLORS['fg'])
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=COLORS['dark_gray'])
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        return entry
    
    def create_footer(self, parent):
        """Create footer with additional options"""
        footer_frame = tk.Frame(parent, bg=COLORS['bg'])
        footer_frame.pack(fill='x', pady=(20, 0))
        
        # Demo credentials
        demo_frame = tk.Frame(footer_frame, bg=COLORS['light_gray'])
        demo_frame.pack(fill='x', pady=(0, 20))
        
        demo_text = "Demo Owner Credentials:\nUsername: FP | Password: 1539"
        demo_label = tk.Label(
            demo_frame,
            text=demo_text,
            font=FONTS['small'],
            bg=COLORS['light_gray'],
            fg=COLORS['dark_gray'],
            justify='center',
            padx=10,
            pady=10
        )
        demo_label.pack()
        
        # Quick info
        info_text = tk.Label(
            footer_frame,
            text="• Owner login for inventory management\n• Customer login for shopping only",
            font=FONTS['small'],
            bg=COLORS['bg'],
            fg=COLORS['secondary'],
            justify='left'
        )
        info_text.pack(anchor='w', pady=(10, 0))
    
    def owner_login(self):
        """Handle owner login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Remove placeholder if still present
        if username == "Enter username...":
            username = ""
        if password == "Enter password...":
            password = ""
        
        # Hardcoded owner credentials
        owner_credentials = {
            'username': 'FP',
            'password': '1539'
        }
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        if username == owner_credentials['username'] and password == owner_credentials['password']:
            self.window.destroy()
            self.on_login_success(is_owner=True, user={'username': 'owner', 'is_owner': True})
        else:
            self.show_error("Invalid owner credentials. Please try again.")
    
    def customer_login(self):
        """Handle customer login (continue without authentication)"""
        self.window.destroy()
        self.on_login_success(is_owner=False, user={'username': 'guest', 'is_owner': False})
    
    def show_error(self, message):
        """Show error message with animation"""
        # Remove any existing error message
        for widget in self.window.winfo_children():
            if hasattr(widget, 'error_label'):
                widget.error_label.destroy()
        
        # Create error message
        error_frame = tk.Frame(self.window, bg=COLORS['bg'])
        error_frame.pack(fill='x', padx=40, pady=(10, 0))
        
        error_label = tk.Label(
            error_frame,
            text=message,
            font=FONTS['small'],
            bg=COLORS['bg'],
            fg=COLORS['danger'],
            wraplength=400
        )
        error_label.pack()
        error_label.error_label = True  # Mark as error label
        
        # Shake animation for password field
        self.shake_widget(self.password_entry)
    
    def shake_widget(self, widget):
        """Add a shake animation to widget"""
        x = widget.winfo_x()
        for _ in range(3):
            for dx in [5, -5, 5, -5, 0]:
                widget.place(x=x + dx)
                widget.update()
                self.window.after(30)