import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from config import COLORS, FONTS, SHADOWS, RADIUS
from database import Database
import math

class AuthWindow:
    def __init__(self, parent, on_login_success):
        self.parent = parent
        self.on_login_success = on_login_success
        
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Owner credentials
        self.owner_username = "FP"
        self.owner_password = "1539"
        
        # Initialize database
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db = Database(self.base_dir)
        
        # Create main container
        self.main_container = tk.Frame(self.parent, bg=COLORS['bg'])
        self.main_container.pack(fill='both', expand=True)
        
        # Configure grid for responsive design
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create widgets
        self.create_widgets()
    
    def destroy(self):
        """Clean up"""
        if hasattr(self, 'main_container'):
            self.main_container.destroy()
    
    def create_widgets(self):
        """Create modern authentication interface"""
        # Main frame with padding
        main_frame = tk.Frame(self.main_container, bg=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configure grid for responsive design
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel - Hero section
        left_panel = tk.Frame(main_frame, bg=COLORS['bg'])
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Right panel - Auth forms
        right_panel = tk.Frame(main_frame, bg=COLORS['bg'])
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Configure panels for responsiveness
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Create hero section
        self.create_hero_section(left_panel)
        
        # Create auth forms
        self.create_auth_forms(right_panel)
    
    def create_hero_section(self, parent):
        """Create hero section with vinyl animation"""
        # Hero container with centered content
        hero_container = tk.Frame(parent, bg=COLORS['bg'])
        hero_container.pack(fill='both', expand=True)
        
        hero_container.grid_rowconfigure(0, weight=1)
        hero_container.grid_rowconfigure(1, weight=0)
        hero_container.grid_rowconfigure(2, weight=1)
        hero_container.grid_columnconfigure(0, weight=1)
        
        # Top spacer
        top_spacer = tk.Frame(hero_container, bg=COLORS['bg'], height=20)
        top_spacer.grid(row=0, column=0, sticky="nsew")
        
        # Content frame (centered)
        content_frame = tk.Frame(hero_container, bg=COLORS['bg'])
        content_frame.grid(row=1, column=0, sticky="nsew")
        
        # Center content in content_frame
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=0)
        content_frame.grid_rowconfigure(2, weight=0)
        content_frame.grid_rowconfigure(3, weight=0)
        content_frame.grid_rowconfigure(4, weight=0)
        content_frame.grid_rowconfigure(5, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Vinyl animation (centered)
        vinyl_frame = tk.Frame(content_frame, bg=COLORS['bg'])
        vinyl_frame.grid(row=1, column=0, pady=(0, 20))
        self.create_vinyl_animation(vinyl_frame)
        
        # Title (centered)
        title_label = tk.Label(content_frame,
                             text="VinylFlow",
                             font=FONTS['h1'],
                             bg=COLORS['bg'],
                             fg=COLORS['fg'])
        title_label.grid(row=2, column=0, pady=(0, 10))
        
        # Subtitle (centered)
        subtitle_label = tk.Label(content_frame,
                                text="Your Digital Record Collection",
                                font=FONTS['body_large'],
                                bg=COLORS['bg'],
                                fg=COLORS['secondary'])
        subtitle_label.grid(row=3, column=0, pady=(0, 30))
        
        # Features frame
        features_frame = tk.Frame(content_frame, bg=COLORS['bg'])
        features_frame.grid(row=4, column=0)
        
        features = [
            "🎵  Curate your vinyl collection",
            "📊  Track inventory & sales",
            "🛒  Easy customer shopping",
            "📈  Advanced analytics",
            "🔐  Secure management"
        ]
        
        for i, feature in enumerate(features):
            feature_label = tk.Label(features_frame,
                                   text=feature,
                                   font=FONTS['body'],
                                   bg=COLORS['bg'],
                                   fg=COLORS['fg'])
            feature_label.grid(row=i, column=0, sticky="w", pady=5)
        
        # Stats
        try:
            stats = self.db.get_statistics()
            if stats:
                stats_frame = tk.Frame(content_frame, bg=COLORS['bg'])
                stats_frame.grid(row=5, column=0, pady=(30, 0))
                
                stats_text = f"📦 {stats.get('total_records', 0):,} Records • 💰 ${stats.get('total_value', 0):,.0f} Value"
                stats_label = tk.Label(stats_frame,
                                     text=stats_text,
                                     font=FONTS['caption'],
                                     bg=COLORS['card_bg'],
                                     fg=COLORS['secondary'],
                                     padx=20,
                                     pady=10)
                stats_label.pack()
        except:
            pass
    
    def create_vinyl_animation(self, parent):
        """Create vinyl record animation"""
        self.canvas = tk.Canvas(parent, width=200, height=200, bg=COLORS['bg'], highlightthickness=0)
        self.canvas.pack()
        
        # Draw vinyl record
        center_x, center_y = 100, 100
        radius = 80
        
        # Outer ring
        self.canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               fill='#222222', outline='#444444', width=2)
        
        # Grooves
        for i in range(10, 80, 5):
            self.canvas.create_oval(center_x - i, center_y - i,
                                   center_x + i, center_y + i,
                                   outline='#333333', width=1)
        
        # Label area
        label_radius = 30
        self.canvas.create_oval(center_x - label_radius, center_y - label_radius,
                               center_x + label_radius, center_y + label_radius,
                               fill='#1e293b', outline='#475569', width=2)
        
        # Center hole
        self.canvas.create_oval(center_x - 5, center_y - 5,
                               center_x + 5, center_y + 5,
                               fill='#ffffff', outline='#cbd5e1')
        
        # Start rotation animation
        self.rotation_angle = 0
        self.animate_vinyl()
    
    def animate_vinyl(self):
        """Animate vinyl rotation"""
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.rotation_angle += 5
            if self.rotation_angle >= 360:
                self.rotation_angle = 0
            
            # Rotate the canvas
            self.canvas.delete("all")
            
            center_x, center_y = 100, 100
            radius = 80
            
            # Calculate rotation
            rad_angle = math.radians(self.rotation_angle)
            cos_a = math.cos(rad_angle)
            sin_a = math.sin(rad_angle)
            
            # Outer ring
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                   center_x + radius, center_y + radius,
                                   fill='#222222', outline='#444444', width=2)
            
            # Grooves with rotation effect
            for i in range(10, 80, 5):
                # Create slightly offset grooves for rotation effect
                offset = math.sin(rad_angle + i/20) * 2
                self.canvas.create_oval(center_x - i + offset, center_y - i,
                                       center_x + i + offset, center_y + i,
                                       outline='#333333', width=1)
            
            # Label area
            label_radius = 30
            self.canvas.create_oval(center_x - label_radius, center_y - label_radius,
                                   center_x + label_radius, center_y + label_radius,
                                   fill='#1e293b', outline='#475569', width=2)
            
            # VinylFlow text on label
            self.canvas.create_text(center_x, center_y,
                                  text="VF",
                                  font=('Inter', 10, 'bold'),
                                  fill=COLORS['primary'])
            
            # Center hole
            self.canvas.create_oval(center_x - 5, center_y - 5,
                                   center_x + 5, center_y + 5,
                                   fill='#ffffff', outline='#cbd5e1')
            
            # Continue animation
            self.parent.after(50, self.animate_vinyl)
    
    def create_auth_forms(self, parent):
        """Create modern auth forms"""
        # Container for forms
        form_container = tk.Frame(parent, bg=COLORS['bg'])
        form_container.pack(fill='both', expand=True)
        
        # Configure grid for responsive design
        form_container.grid_rowconfigure(0, weight=0)
        form_container.grid_rowconfigure(1, weight=1)
        form_container.grid_columnconfigure(0, weight=1)
        
        # Title (centered)
        title_frame = tk.Frame(form_container, bg=COLORS['bg'])
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(title_frame,
                             text="Welcome Back",
                             font=FONTS['h3'],
                             bg=COLORS['bg'],
                             fg=COLORS['fg'])
        title_label.grid(row=0, column=0)
        
        # Notebook frame
        notebook_frame = tk.Frame(form_container, bg=COLORS['bg'])
        notebook_frame.grid(row=1, column=0, sticky="nsew")
        notebook_frame.grid_rowconfigure(0, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Configure notebook style
        style = ttk.Style()
        style.configure('Custom.TNotebook', background=COLORS['bg'], borderwidth=0)
        style.configure('Custom.TNotebook.Tab', 
                       background=COLORS['card_bg'],
                       foreground=COLORS['fg'],
                       padding=[20, 10],
                       font=FONTS['button'])
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', COLORS['primary'])],
                 foreground=[('selected', COLORS['white'])])
        
        self.notebook.configure(style='Custom.TNotebook')
        
        # Create tabs
        self.create_customer_tab()
        self.create_owner_tab()
        
        # Set initial tab
        self.notebook.select(0)
    
    def create_customer_tab(self):
        """Create customer login/signup tab"""
        tab = tk.Frame(self.notebook, bg=COLORS['bg'])
        self.notebook.add(tab, text="👤 Customers")
        
        # Configure grid for responsive design
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        
        # Split into login and signup
        login_frame = self.create_card(tab)
        login_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        signup_frame = self.create_card(tab)
        signup_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Configure frames for responsiveness
        login_frame.grid_rowconfigure(0, weight=1)
        login_frame.grid_columnconfigure(0, weight=1)
        signup_frame.grid_rowconfigure(0, weight=1)
        signup_frame.grid_columnconfigure(0, weight=1)
        
        # Create login form
        self.create_login_form(login_frame)
        
        # Create signup form
        self.create_signup_form(signup_frame)
    
    def create_owner_tab(self):
        """Create owner login tab"""
        tab = tk.Frame(self.notebook, bg=COLORS['bg'])
        self.notebook.add(tab, text="🔐 Store Owner")
        
        # Configure grid for centered content
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        # Owner form container (centered)
        form_frame = self.create_card(tab)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        
        # Configure form frame for centered content
        form_frame.grid_rowconfigure(0, weight=1)
        form_frame.grid_rowconfigure(1, weight=0)
        form_frame.grid_rowconfigure(2, weight=0)
        form_frame.grid_rowconfigure(3, weight=0)
        form_frame.grid_rowconfigure(4, weight=0)
        form_frame.grid_rowconfigure(5, weight=0)
        form_frame.grid_rowconfigure(6, weight=0)
        form_frame.grid_rowconfigure(7, weight=0)
        form_frame.grid_rowconfigure(8, weight=0)
        form_frame.grid_rowconfigure(9, weight=0)
        form_frame.grid_rowconfigure(10, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Icon (centered)
        icon_label = tk.Label(form_frame,
                            text="👑",
                            font=('Segoe UI Emoji', 48),
                            bg=COLORS['card_bg'],
                            fg=COLORS['primary'])
        icon_label.grid(row=1, column=0, pady=(30, 10))
        
        # Title (centered)
        title_label = tk.Label(form_frame,
                             text="Owner Portal",
                             font=FONTS['h4'],
                             bg=COLORS['card_bg'],
                             fg=COLORS['fg'])
        title_label.grid(row=2, column=0, pady=(0, 5))
        
        # Description (centered)
        desc_label = tk.Label(form_frame,
                            text="Full access to inventory & management",
                            font=FONTS['body_small'],
                            bg=COLORS['card_bg'],
                            fg=COLORS['secondary'])
        desc_label.grid(row=3, column=0, pady=(0, 30))
        
        # Username
        tk.Label(form_frame,
                text="Username",
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        self.owner_username_entry = tk.Entry(form_frame,
                                     font=FONTS['body'],
                                     bg=COLORS['entry_bg'],
                                     fg=COLORS['fg'],
                                     relief='flat',
                                     insertbackground=COLORS['fg'])
        self.owner_username_entry.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        self.owner_username_entry.insert(0, "FP")
        
        # Password
        tk.Label(form_frame,
                text="Password",
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).grid(row=6, column=0, sticky="w", pady=(0, 5))
        
        self.owner_password_entry = tk.Entry(form_frame,
                                     font=FONTS['body'],
                                     bg=COLORS['entry_bg'],
                                     fg=COLORS['fg'],
                                     relief='flat',
                                     show="●",
                                     insertbackground=COLORS['fg'])
        self.owner_password_entry.grid(row=7, column=0, sticky="ew", pady=(0, 30))
        self.owner_password_entry.insert(0, "1539")
        
        # Login button
        login_btn = tk.Button(form_frame,
                            text="Login as Owner",
                            font=FONTS['button'],
                            bg=COLORS['primary'],
                            fg=COLORS['white'],
                            relief='flat',
                            command=self.owner_login,
                            cursor='hand2',
                            padx=30,
                            pady=12)
        login_btn.grid(row=8, column=0, sticky="ew", pady=(0, 20))
        
        # Guest option
        guest_btn = tk.Button(form_frame,
                            text="Continue as Guest",
                            font=FONTS['button_small'],
                            bg=COLORS['card_bg'],
                            fg=COLORS['secondary'],
                            relief='flat',
                            command=lambda: self.on_login_success(is_owner=False, user={'username': 'guest'}),
                            cursor='hand2')
        guest_btn.grid(row=9, column=0)
        
        # Error label
        self.owner_error = tk.Label(form_frame,
                                  text="",
                                  font=FONTS['caption_small'],
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['danger'])
        self.owner_error.grid(row=10, column=0, pady=(10, 0))
    
    def create_card(self, parent):
        """Create a modern card container"""
        card = tk.Frame(parent,
                       bg=COLORS['card_bg'],
                       padx=30,
                       pady=30,
                       relief='flat',
                       borderwidth=0)
        
        return card
    
    def create_login_form(self, parent):
        """Create customer login form"""
        # Configure grid for responsive design
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Content frame
        content_frame = tk.Frame(parent, bg=COLORS['card_bg'])
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure content frame
        content_frame.grid_rowconfigure(0, weight=0)
        content_frame.grid_rowconfigure(1, weight=0)
        content_frame.grid_rowconfigure(2, weight=0)
        content_frame.grid_rowconfigure(3, weight=0)
        content_frame.grid_rowconfigure(4, weight=0)
        content_frame.grid_rowconfigure(5, weight=0)
        content_frame.grid_rowconfigure(6, weight=0)
        content_frame.grid_rowconfigure(7, weight=0)
        content_frame.grid_rowconfigure(8, weight=0)
        content_frame.grid_rowconfigure(9, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(content_frame,
                             text="Login",
                             font=FONTS['h5'],
                             bg=COLORS['card_bg'],
                             fg=COLORS['fg'])
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Username
        tk.Label(content_frame,
                text="Username",
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.cust_username = tk.Entry(content_frame,
                                     font=FONTS['body'],
                                     bg=COLORS['entry_bg'],
                                     fg=COLORS['fg'],
                                     relief='flat',
                                     insertbackground=COLORS['fg'])
        self.cust_username.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        # Password
        tk.Label(content_frame,
                text="Password",
                font=FONTS['caption'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        self.cust_password = tk.Entry(content_frame,
                                     font=FONTS['body'],
                                     bg=COLORS['entry_bg'],
                                     fg=COLORS['fg'],
                                     relief='flat',
                                     show="●",
                                     insertbackground=COLORS['fg'])
        self.cust_password.grid(row=4, column=0, sticky="ew", pady=(0, 25))
        
        # Login button
        login_btn = tk.Button(content_frame,
                            text="Login to Account",
                            font=FONTS['button'],
                            bg=COLORS['primary'],
                            fg=COLORS['white'],
                            relief='flat',
                            command=self.customer_login,
                            cursor='hand2',
                            padx=20,
                            pady=12)
        login_btn.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        
        # Quick login buttons frame
        quick_frame = tk.Frame(content_frame, bg=COLORS['card_bg'])
        quick_frame.grid(row=6, column=0, sticky="ew", pady=(0, 20))
        
        quick_frame.grid_columnconfigure(0, weight=1)
        quick_frame.grid_columnconfigure(1, weight=1)
        
        # Sample user 1
        user1_btn = tk.Button(quick_frame,
                            text="Demo User 1",
                            font=FONTS['button_small'],
                            bg=COLORS['light_gray'],
                            fg=COLORS['fg'],
                            relief='flat',
                            command=lambda: self.quick_login("Tiernan123", "123456"),
                            cursor='hand2',
                            padx=15,
                            pady=8)
        user1_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Sample user 2
        user2_btn = tk.Button(quick_frame,
                            text="Demo User 2",
                            font=FONTS['button_small'],
                            bg=COLORS['light_gray'],
                            fg=COLORS['fg'],
                            relief='flat',
                            command=lambda: self.quick_login("kokilumi", "Shea123"),
                            cursor='hand2',
                            padx=15,
                            pady=8)
        user2_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Guest option
        guest_btn = tk.Button(content_frame,
                            text="Continue as Guest",
                            font=FONTS['button_small'],
                            bg=COLORS['card_bg'],
                            fg=COLORS['secondary'],
                            relief='flat',
                            command=lambda: self.on_login_success(is_owner=False, user={'username': 'guest'}),
                            cursor='hand2')
        guest_btn.grid(row=7, column=0, sticky="ew")
        
        # Error label
        self.login_error = tk.Label(content_frame,
                                  text="",
                                  font=FONTS['caption_small'],
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['danger'])
        self.login_error.grid(row=8, column=0, pady=(10, 0))
    
    def create_signup_form(self, parent):
        """Create customer signup form"""
        # Configure grid for responsive design
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Main container with scrollbar
        main_container = tk.Frame(parent, bg=COLORS['card_bg'])
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_container, bg=COLORS['card_bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['card_bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure scrollable frame
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(scrollable_frame,
                             text="Sign Up",
                             font=FONTS['h5'],
                             bg=COLORS['card_bg'],
                             fg=COLORS['fg'])
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Form fields
        fields = [
            ("Username", "signup_username", False),
            ("Email", "signup_email", False),
            ("Full Name", "signup_name", False),
            ("Password", "signup_password", True),
            ("Confirm Password", "signup_confirm", True),
            ("Address", "signup_address", False),
            ("Phone", "signup_phone", False),
        ]
        
        self.signup_entries = {}
        
        for i, (label, field_name, is_password) in enumerate(fields):
            row = i * 2 + 1
            
            # Label
            tk.Label(scrollable_frame,
                    text=label,
                    font=FONTS['caption'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['fg']).grid(row=row, column=0, sticky="w", pady=(10, 5))
            
            # Entry field
            if is_password:
                entry = tk.Entry(scrollable_frame,
                               font=FONTS['body'],
                               bg=COLORS['entry_bg'],
                               fg=COLORS['fg'],
                               relief='flat',
                               show="●",
                               insertbackground=COLORS['fg'])
            else:
                entry = tk.Entry(scrollable_frame,
                               font=FONTS['body'],
                               bg=COLORS['entry_bg'],
                               fg=COLORS['fg'],
                               relief='flat',
                               insertbackground=COLORS['fg'])
            
            entry.grid(row=row + 1, column=0, sticky="ew", pady=(0, 5))
            self.signup_entries[field_name] = entry
        
        # Terms checkbox
        self.terms_var = tk.BooleanVar()
        terms_frame = tk.Frame(scrollable_frame, bg=COLORS['card_bg'])
        terms_frame.grid(row=len(fields) * 2 + 1, column=0, sticky="ew", pady=15)
        
        terms_check = tk.Checkbutton(terms_frame,
                                   text="I agree to Terms & Privacy",
                                   variable=self.terms_var,
                                   font=FONTS['caption_small'],
                                   bg=COLORS['card_bg'],
                                   fg=COLORS['fg'],
                                   selectcolor=COLORS['primary'],
                                   activebackground=COLORS['card_bg'],
                                   activeforeground=COLORS['fg'])
        terms_check.pack(anchor='w')
        
        # Error label
        self.signup_error = tk.Label(scrollable_frame,
                                   text="",
                                   font=FONTS['caption_small'],
                                   bg=COLORS['card_bg'],
                                   fg=COLORS['danger'])
        self.signup_error.grid(row=len(fields) * 2 + 2, column=0, pady=(10, 0))
        
        # Signup button
        signup_btn = tk.Button(scrollable_frame,
                             text="Create Account",
                             font=FONTS['button'],
                             bg=COLORS['success'],
                             fg=COLORS['white'],
                             relief='flat',
                             command=self.customer_signup,
                             cursor='hand2',
                             padx=20,
                             pady=12)
        signup_btn.grid(row=len(fields) * 2 + 3, column=0, sticky="ew", pady=(20, 30))
    
    def quick_login(self, username, password):
        """Quick login for demo users"""
        self.cust_username.delete(0, tk.END)
        self.cust_username.insert(0, username)
        self.cust_password.delete(0, tk.END)
        self.cust_password.insert(0, password)
        self.customer_login()
    
    def customer_login(self):
        """Handle customer login"""
        username = self.cust_username.get().strip()
        password = self.cust_password.get().strip()
        
        if not username or not password:
            self.show_error(self.login_error, "Please enter username and password")
            return
        
        try:
            # Authenticate
            customer = self.db.authenticate_customer(username, password)
            
            if customer:
                self.on_login_success(is_owner=False, user=customer)
            else:
                self.show_error(self.login_error, "Invalid credentials")
        except Exception as e:
            self.show_error(self.login_error, f"Error: {str(e)}")
    
    def customer_signup(self):
        """Handle customer signup"""
        # Get form data
        data = {
            'username': self.signup_entries['signup_username'].get().strip(),
            'email': self.signup_entries['signup_email'].get().strip(),
            'full_name': self.signup_entries['signup_name'].get().strip(),
            'password': self.signup_entries['signup_password'].get().strip(),
            'confirm_password': self.signup_entries['signup_confirm'].get().strip(),
            'address': self.signup_entries['signup_address'].get().strip(),
            'phone': self.signup_entries['signup_phone'].get().strip(),
        }
        
        # Validation
        errors = []
        
        if not all([data['username'], data['email'], data['password']]):
            errors.append("Required fields: username, email, password")
        
        if data['password'] != data['confirm_password']:
            errors.append("Passwords don't match")
        
        if len(data['password']) < 6:
            errors.append("Password must be 6+ characters")
        
        if data['email'] and not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors.append("Invalid email format")
        
        if not self.terms_var.get():
            errors.append("Must agree to terms")
        
        if errors:
            self.show_error(self.signup_error, "\n".join(errors))
            return
        
        try:
            # Register customer
            customer_id = self.db.register_customer({
                'username': data['username'],
                'password': data['password'],
                'email': data['email'],
                'full_name': data['full_name'],
                'address': data['address'],
                'phone': data['phone']
            })
            
            # Get customer record
            customer = self.db.get_customer_by_username(data['username'])
            if customer and 'password_hash' in customer:
                del customer['password_hash']
            
            messagebox.showinfo("Success", "Account created successfully!")
            self.on_login_success(is_owner=False, user=customer)
            
        except ValueError as e:
            self.show_error(self.signup_error, str(e))
        except Exception as e:
            self.show_error(self.signup_error, f"Error: {str(e)}")
    
    def owner_login(self):
        """Handle owner login"""
        username = self.owner_username_entry.get().strip()
        password = self.owner_password_entry.get().strip()
        
        if username == self.owner_username and password == self.owner_password:
            self.on_login_success(is_owner=True, user={'username': 'owner'})
        else:
            self.show_error(self.owner_error, "Invalid owner credentials")
    
    def show_error(self, label_widget, message):
        """Show error message"""
        label_widget.config(text=message)
        # Clear after 5 seconds
        self.parent.after(5000, lambda: label_widget.config(text=""))