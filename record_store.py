import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog
import json
import os
from datetime import datetime
import csv
from config import COLORS, FONTS, LIGHT_COLORS, DARK_COLORS
from database import Database

class RecordStoreApp:
    def __init__(self, root, is_owner=False, user=None, logout_callback=None):
        self.root = root
        self.is_owner = is_owner
        self.user = user or {}
        self.logout_callback = logout_callback
        
        # Initialize database
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db = Database(self.base_dir)
        
        # Shopping cart for customers
        self.cart = []
        self.cart_total = 0.0
        
        # Theme
        self.dark_mode = False
        self.load_theme()
        
        # Setup GUI
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.load_data()
    
    def setup_window(self):
        """Setup main window"""
        self.root.configure(bg=COLORS['bg'])
        
    def load_theme(self):
        """Load theme preference"""
        try:
            config_file = os.path.join(self.base_dir, 'theme_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.dark_mode = config.get('dark_mode', False)
                    if self.dark_mode:
                        COLORS.update(DARK_COLORS)
                    else:
                        COLORS.update(LIGHT_COLORS)
        except:
            self.dark_mode = False
    
    def save_theme(self):
        """Save theme preference"""
        try:
            config_file = os.path.join(self.base_dir, 'theme_config.json')
            with open(config_file, 'w') as f:
                json.dump({'dark_mode': self.dark_mode}, f)
        except:
            pass
    
    def create_styles(self):
        """Create custom styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure base styles
        self.style.configure('.', 
                           background=COLORS['bg'], 
                           foreground=COLORS['fg'])
        self.style.configure('TFrame', 
                           background=COLORS['bg'])
        self.style.configure('TLabel', 
                           background=COLORS['bg'], 
                           foreground=COLORS['fg'],
                           font=FONTS['label'])
        
        # Treeview
        self.style.configure('Treeview',
                           background=COLORS['tree_bg'],
                           foreground=COLORS['tree_fg'],
                           fieldbackground=COLORS['tree_bg'],
                           rowheight=25)
        
        self.style.configure('Treeview.Heading',
                           background=COLORS['tree_heading_bg'],
                           foreground=COLORS['tree_heading_fg'],
                           font=FONTS['label'])
        
        self.style.map('Treeview',
                      background=[('selected', COLORS['tree_selected_bg'])],
                      foreground=[('selected', COLORS['tree_selected_fg'])])
        
        # Entry style
        self.style.configure('Custom.TEntry',
                           fieldbackground=COLORS['entry_bg'],
                           foreground=COLORS['fg'],
                           borderwidth=1,
                           relief='solid')
        
        # Button styles
        self.style.configure('Primary.TButton',
                           background=COLORS['primary'],
                           foreground=COLORS['white'])
        
        self.style.configure('Secondary.TButton',
                           background=COLORS['secondary'],
                           foreground=COLORS['white'])
        
        self.style.configure('Success.TButton',
                           background=COLORS['success'],
                           foreground=COLORS['white'])
        
        self.style.configure('Danger.TButton',
                           background=COLORS['danger'],
                           foreground=COLORS['white'])
        
        self.style.configure('Warning.TButton',
                           background=COLORS['warning'],
                           foreground=COLORS['dark'])
        
        self.style.map('Primary.TButton',
                      background=[('active', COLORS['primary_dark']),
                                 ('!disabled', COLORS['primary'])])
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            COLORS.update(DARK_COLORS)
        else:
            COLORS.update(LIGHT_COLORS)
        self.save_theme()
        
        # Reapply theme
        self.root.configure(bg=COLORS['bg'])
        self.create_styles()
        self.refresh_widget_styles()
    
    def refresh_widget_styles(self):
        """Refresh widget styles after theme change"""
        # This will be called after theme toggle
        pass
    
    def create_widgets(self):
        """Create main widgets"""
        # Configure root grid for responsive design
        self.root.grid_rowconfigure(0, weight=0)  # Header
        self.root.grid_rowconfigure(1, weight=1)  # Main content
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main container grid
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        if self.is_owner:
            self.create_owner_interface(main_container)
        else:
            self.create_customer_interface(main_container)
    
    def create_header(self):
        """Create application header"""
        self.header = tk.Frame(self.root, 
                              bg=COLORS['primary'],
                              height=70)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        
        # Configure header grid
        self.header.grid_columnconfigure(0, weight=0)  # Left spacer
        self.header.grid_columnconfigure(1, weight=1)  # Title area
        self.header.grid_columnconfigure(2, weight=0)  # User area
        
        # Left spacer
        left_spacer = tk.Frame(self.header, bg=COLORS['primary'], width=20)
        left_spacer.grid(row=0, column=0, sticky="ns")
        
        # Title area (centered)
        title_frame = tk.Frame(self.header, bg=COLORS['primary'])
        title_frame.grid(row=0, column=1, sticky="nsew")
        title_frame.grid_columnconfigure(0, weight=1)
        title_frame.grid_rowconfigure(0, weight=1)
        
        # Title content
        title_content = tk.Frame(title_frame, bg=COLORS['primary'])
        title_content.grid(row=0, column=0)
        
        tk.Label(title_content,
                text="💿",
                font=('Segoe UI Emoji', 28),
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left', padx=5)
        
        tk.Label(title_content,
                text="VinylFlow",
                font=FONTS['title'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left')
        
        tk.Label(title_content,
                text=f"{' Manager' if self.is_owner else ''}",
                font=FONTS['subtitle'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left')
        
        # User info area
        user_frame = tk.Frame(self.header, bg=COLORS['primary'])
        user_frame.grid(row=0, column=2, sticky="e", padx=20)
        
        # Theme toggle
        self.theme_btn = tk.Button(user_frame,
                                  text="🌙" if not self.dark_mode else "☀️",
                                  font=('Arial', 14),
                                  bg=COLORS['primary_dark'],
                                  fg=COLORS['white'],
                                  relief='flat',
                                  command=self.toggle_theme,
                                  cursor='hand2',
                                  width=3)
        self.theme_btn.pack(side='left', padx=5)
        
        # User info
        username = self.user.get('username', 'Guest')
        user_label = tk.Label(user_frame,
                            text=f"👤 {username}",
                            font=FONTS['label'],
                            bg=COLORS['primary'],
                            fg=COLORS['white'])
        user_label.pack(side='left', padx=10)
        
        # Logout button
        logout_btn = tk.Button(user_frame,
                             text="Logout",
                             font=FONTS['button'],
                             bg=COLORS['danger'],
                             fg=COLORS['white'],
                             relief='flat',
                             command=self.logout,
                             cursor='hand2',
                             padx=15,
                             pady=5)
        logout_btn.pack(side='left', padx=5)
    
    def create_owner_interface(self, parent):
        """Create owner interface"""
        # Notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        # Configure notebook grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Tabs
        inventory_tab = ttk.Frame(notebook)
        statistics_tab = ttk.Frame(notebook)
        
        notebook.add(inventory_tab, text="📦 Inventory")
        notebook.add(statistics_tab, text="📊 Statistics")
        
        # Configure tab grids
        inventory_tab.grid_rowconfigure(0, weight=1)
        inventory_tab.grid_columnconfigure(0, weight=1)
        statistics_tab.grid_rowconfigure(0, weight=1)
        statistics_tab.grid_columnconfigure(0, weight=1)
        
        # Inventory tab
        self.create_inventory_section(inventory_tab)
        
        # Statistics tab
        self.create_enhanced_statistics_section(statistics_tab)
    
    def create_inventory_section(self, parent):
        """Create inventory management section"""
        # Configure parent grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        # Left panel - Add record form
        left_panel = ttk.LabelFrame(parent, text=" Add/Edit Record ", padding=15)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Right panel - Records list
        right_panel = ttk.LabelFrame(parent, text=" Records List ", padding=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Create record form
        self.create_record_form(left_panel)
        
        # Create records list
        self.create_records_list(right_panel)
    
    def create_record_form(self, parent):
        """Create record addition form"""
        # Main form container
        form_container = tk.Frame(parent, bg=COLORS['bg'])
        form_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure form grid
        form_container.grid_rowconfigure(0, weight=0)  # Fields
        form_container.grid_rowconfigure(1, weight=1)  # Spacer
        form_container.grid_rowconfigure(2, weight=0)  # Buttons
        form_container.grid_columnconfigure(0, weight=1)
        
        # Fields frame
        fields_frame = tk.Frame(form_container, bg=COLORS['bg'])
        fields_frame.grid(row=0, column=0, sticky="ew")
        
        # Form fields
        fields = [
            ("Artist:", "artist_entry"),
            ("Album:", "album_entry"),
            ("Genre:", "genre_entry"),
            ("Year:", "year_entry"),
            ("Price ($):", "price_entry"),
            ("Stock:", "stock_entry"),
        ]
        
        self.form_entries = {}
        
        for i, (label, name) in enumerate(fields):
            # Label
            tk.Label(fields_frame,
                    text=label,
                    font=FONTS['label'],
                    bg=COLORS['bg'],
                    fg=COLORS['fg']).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))
            
            # Entry field
            entry = tk.Entry(fields_frame,
                           font=FONTS['entry'],
                           bg=COLORS['entry_bg'],
                           fg=COLORS['fg'],
                           relief='solid',
                           borderwidth=1)
            entry.grid(row=i, column=1, sticky="ew", pady=5, ipady=5)
            self.form_entries[name] = entry
        
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Button frame
        button_frame = tk.Frame(form_container, bg=COLORS['bg'])
        button_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        
        # Buttons
        buttons = [
            ("➕ Add", self.add_record, 'success'),
            ("✏️ Update", self.update_record, 'primary'),
            ("🗑️ Delete", self.delete_record, 'danger'),
            ("🧹 Clear", self.clear_form, 'warning')
        ]
        
        for i, (text, command, style) in enumerate(buttons):
            btn = tk.Button(button_frame,
                          text=text,
                          font=FONTS['button_small'],
                          bg=COLORS[f'{style}' if style != 'primary' else 'primary'],
                          fg=COLORS['white'],
                          relief='flat',
                          command=command,
                          cursor='hand2',
                          padx=10,
                          pady=8)
            btn.grid(row=0, column=i, sticky="ew", padx=2)
    
    def create_records_list(self, parent):
        """Create records list with search"""
        # Configure parent grid
        parent.grid_rowconfigure(0, weight=0)  # Search
        parent.grid_rowconfigure(1, weight=1)  # Treeview
        parent.grid_rowconfigure(2, weight=0)  # Buttons
        parent.grid_columnconfigure(0, weight=1)
        
        # Search frame
        search_frame = tk.Frame(parent, bg=COLORS['bg'])
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)
        
        # Search label
        tk.Label(search_frame,
                text="🔍 Search:",
                font=FONTS['label'],
                bg=COLORS['bg'],
                fg=COLORS['fg']).grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                              textvariable=self.search_var,
                              font=FONTS['entry'],
                              bg=COLORS['entry_bg'],
                              fg=COLORS['fg'],
                              relief='solid',
                              borderwidth=1)
        search_entry.grid(row=0, column=1, sticky="ew", ipady=5)
        search_entry.bind('<KeyRelease>', lambda e: self.search_records())
        
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Treeview frame
        tree_frame = tk.Frame(parent, bg=COLORS['bg'])
        tree_frame.grid(row=1, column=0, sticky="nsew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        # Create treeview
        columns = ("ID", "Album", "Artist", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            width = 50 if col == "ID" else 150 if col in ["Album", "Artist"] else 100
            self.tree.column(col, width=width, anchor="center" if col in ["ID", "Year", "Stock"] else "w")
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for treeview
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew", columnspan=2)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_record_select)
        
        # Action buttons frame
        action_frame = tk.Frame(parent, bg=COLORS['bg'])
        action_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        action_frame.grid_columnconfigure(2, weight=1)
        
        # Action buttons
        action_buttons = [
            ("🔄 Refresh", self.refresh_records, 'secondary'),
            ("📤 Export CSV", self.export_to_csv, 'success'),
            ("📥 Import CSV", self.import_from_csv, 'warning')
        ]
        
        for i, (text, command, style) in enumerate(action_buttons):
            btn = tk.Button(action_frame,
                          text=text,
                          font=FONTS['button_small'],
                          bg=COLORS[style],
                          fg=COLORS['white'],
                          relief='flat',
                          command=command,
                          cursor='hand2',
                          padx=10,
                          pady=8)
            btn.grid(row=0, column=i, sticky="ew", padx=2)
    
    def create_enhanced_statistics_section(self, parent):
        """Create modern statistics section with enhanced visuals"""
        # Configure parent grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Main container with scrollable content
        main_container = tk.Frame(parent, bg=COLORS['bg'])
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.stats_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        self.stats_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.stats_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure stats frame grid
        self.stats_frame.grid_columnconfigure(0, weight=1)
        
        # Title at the top
        title_frame = tk.Frame(self.stats_frame, bg=COLORS['bg'], pady=20)
        title_frame.grid(row=0, column=0, sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        title_frame.grid_columnconfigure(1, weight=0)
        title_frame.grid_columnconfigure(2, weight=0)
        
        title_label = tk.Label(title_frame,
                              text="📊 VinylFlow Analytics Dashboard",
                              font=('Segoe UI', 22, 'bold'),
                              bg=COLORS['bg'],
                              fg=COLORS['primary'])
        title_label.grid(row=0, column=0, sticky="w")
        
        # Refresh button
        refresh_btn = tk.Button(title_frame,
                               text="🔄 Refresh",
                               font=FONTS['button_small'],
                               bg=COLORS['info'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=self.update_enhanced_statistics,
                               cursor='hand2',
                               padx=15,
                               pady=8)
        refresh_btn.grid(row=0, column=1, padx=5)
        
        # Export button
        export_btn = tk.Button(title_frame,
                              text="📤 Export",
                              font=FONTS['button_small'],
                              bg=COLORS['success'],
                              fg=COLORS['white'],
                              relief='flat',
                              command=self.export_statistics_report,
                              cursor='hand2',
                              padx=15,
                              pady=8)
        export_btn.grid(row=0, column=2)
        
        # Initial statistics display
        self.update_enhanced_statistics()
    
    def update_enhanced_statistics(self):
        """Update the statistics display with latest data"""
        # Clear existing content
        for widget in self.stats_frame.winfo_children():
            if widget != self.stats_frame.winfo_children()[0]:  # Keep title frame
                widget.destroy()
        
        # Calculate statistics using database
        stats = self.db.get_statistics()
        
        if not stats or stats.get('total_records', 0) == 0:
            # Show empty state
            empty_frame = tk.Frame(self.stats_frame, bg=COLORS['bg'], pady=50)
            empty_frame.grid(row=1, column=0, sticky="nsew")
            empty_frame.grid_rowconfigure(0, weight=1)
            empty_frame.grid_columnconfigure(0, weight=1)
            
            empty_content = tk.Frame(empty_frame, bg=COLORS['bg'])
            empty_content.grid(row=0, column=0)
            
            tk.Label(empty_content,
                    text="📊",
                    font=('Segoe UI Emoji', 64),
                    bg=COLORS['bg'],
                    fg=COLORS['secondary']).pack()
            
            tk.Label(empty_content,
                    text="No data available for statistics",
                    font=FONTS['heading'],
                    bg=COLORS['bg'],
                    fg=COLORS['fg']).pack(pady=10)
            
            tk.Label(empty_content,
                    text="Add records to see analytics dashboard",
                    font=FONTS['subtitle'],
                    bg=COLORS['bg'],
                    fg=COLORS['secondary']).pack()
            return
        
        # Display statistics cards
        self.display_statistics_cards(self.stats_frame, stats, 1)
    
    def display_statistics_cards(self, parent, stats, start_row):
        """Display statistics in modern cards with visual elements"""
        current_row = start_row
        
        # Row 1: Key Metrics
        metrics_frame = tk.LabelFrame(parent,
                                     text=" 📈 Key Metrics ",
                                     font=FONTS['h6'],
                                     bg=COLORS['card_bg'],
                                     fg=COLORS['primary'],
                                     relief='groove',
                                     borderwidth=2,
                                     padx=15,
                                     pady=15)
        metrics_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 20), padx=20)
        current_row += 1
        
        # Create metrics cards grid
        metrics_grid = tk.Frame(metrics_frame, bg=COLORS['card_bg'])
        metrics_grid.pack(fill='x')
        
        metrics_data = [
            ("📀", "Total Records", str(stats.get('total_records', 0)), COLORS['primary'], "Albums in inventory"),
            ("📦", "Total Stock", f"{stats.get('total_stock', 0):,}", COLORS['info'], "Units available"),
            ("💰", "Inventory Value", f"${stats.get('total_value', 0):,.2f}", COLORS['success'], "Total worth"),
            ("💵", "Avg Price", f"${stats.get('avg_price', 0):.2f}", COLORS['warning'], "Per unit average"),
        ]
        
        for i, (icon, label, value, color, description) in enumerate(metrics_data):
            card = self.create_metric_card(metrics_grid, icon, label, value, color, description)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            metrics_grid.columnconfigure(i, weight=1)
        
        # Row 2: Stock Analysis
        stock_frame = tk.LabelFrame(parent,
                                   text=" 📊 Stock Analysis ",
                                   font=FONTS['h6'],
                                   bg=COLORS['card_bg'],
                                   fg=COLORS['primary'],
                                   relief='groove',
                                   borderwidth=2,
                                   padx=15,
                                   pady=15)
        stock_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 20), padx=20)
        current_row += 1
        
        # Stock status cards
        low_stock_count = len(stats.get('low_stock', []))
        out_of_stock_count = len(stats.get('out_of_stock', []))
        healthy_stock = max(0, stats.get('total_records', 0) - low_stock_count - out_of_stock_count)
        
        stock_data = [
            ("✅", "In Stock", f"{healthy_stock}", COLORS['success'], "Items with >5 stock"),
            ("⚠️", "Low Stock", f"{low_stock_count}", COLORS['warning'], "Items with 1-5 stock"),
            ("❌", "Out of Stock", f"{out_of_stock_count}", COLORS['danger'], "Items with 0 stock"),
        ]
        
        stock_grid = tk.Frame(stock_frame, bg=COLORS['card_bg'])
        stock_grid.pack(fill='x')
        
        for i, (icon, label, value, color, description) in enumerate(stock_data):
            card = self.create_stock_card(stock_grid, icon, label, value, color, description)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            stock_grid.columnconfigure(i, weight=1)
        
        # Low stock items list
        if low_stock_count > 0:
            low_stock_frame = tk.Frame(stock_frame, bg=COLORS['card_bg'])
            low_stock_frame.pack(fill='x', pady=(15, 0))
            
            tk.Label(low_stock_frame,
                    text="⚠️ Low Stock Items (≤5 remaining):",
                    font=FONTS['label'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['warning']).pack(anchor='w')
            
            for item in stats.get('low_stock', [])[:5]:
                tk.Label(low_stock_frame,
                        text=f"• {item.get('artist', 'Unknown')} - {item.get('album', 'Unknown')}: {item.get('stock', 0)} left",
                        font=FONTS['small'],
                        bg=COLORS['card_bg'],
                        fg=COLORS['dark_gray']).pack(anchor='w')
        
        # Row 3: Price Analysis
        if stats.get('most_expensive'):
            price_frame = tk.LabelFrame(parent,
                                       text=" 💰 Price Analysis ",
                                       font=FONTS['h6'],
                                       bg=COLORS['card_bg'],
                                       fg=COLORS['primary'],
                                       relief='groove',
                                       borderwidth=2,
                                       padx=15,
                                       pady=15)
            price_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 20), padx=20)
            current_row += 1
            
            # Price extremes
            extremes_frame = tk.Frame(price_frame, bg=COLORS['card_bg'])
            extremes_frame.pack(fill='x', pady=(0, 15))
            
            extremes_frame.grid_columnconfigure(0, weight=1)
            extremes_frame.grid_columnconfigure(1, weight=1)
            
            # Most expensive
            most_exp = stats.get('most_expensive', {})
            most_frame = tk.Frame(extremes_frame, bg=COLORS['card_bg'])
            most_frame.grid(row=0, column=0, sticky="ew", padx=10)
            
            tk.Label(most_frame,
                    text="🏆 Most Expensive",
                    font=FONTS['label'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['danger']).pack(anchor='w')
            
            tk.Label(most_frame,
                    text=f"${most_exp.get('price', 0):.2f}",
                    font=('Segoe UI', 16, 'bold'),
                    bg=COLORS['card_bg'],
                    fg=COLORS['danger']).pack(anchor='w')
            
            tk.Label(most_frame,
                    text=f"{most_exp.get('artist', 'Unknown')} - {most_exp.get('album', 'Unknown')}",
                    font=FONTS['small'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['dark_gray']).pack(anchor='w')
            
            # Least expensive
            least_exp = stats.get('least_expensive', {})
            least_frame = tk.Frame(extremes_frame, bg=COLORS['card_bg'])
            least_frame.grid(row=0, column=1, sticky="ew", padx=10)
            
            tk.Label(least_frame,
                    text="💎 Least Expensive",
                    font=FONTS['label'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['success']).pack(anchor='e')
            
            tk.Label(least_frame,
                    text=f"${least_exp.get('price', 0):.2f}",
                    font=('Segoe UI', 16, 'bold'),
                    bg=COLORS['card_bg'],
                    fg=COLORS['success']).pack(anchor='e')
            
            tk.Label(least_frame,
                    text=f"{least_exp.get('artist', 'Unknown')} - {least_exp.get('album', 'Unknown')}",
                    font=FONTS['small'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['dark_gray']).pack(anchor='e')
        
        # Row 4: Sales Statistics
        if stats.get('total_sales_count', 0) > 0:
            sales_frame = tk.LabelFrame(parent,
                                      text=" 📈 Sales Statistics ",
                                      font=FONTS['h6'],
                                      bg=COLORS['card_bg'],
                                      fg=COLORS['primary'],
                                      relief='groove',
                                      borderwidth=2,
                                      padx=15,
                                      pady=15)
            sales_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 20), padx=20)
            current_row += 1
            
            sales_grid = tk.Frame(sales_frame, bg=COLORS['card_bg'])
            sales_grid.pack(fill='x')
            
            sales_data = [
                ("🛒", "Total Sales", f"{stats.get('total_sales_count', 0):,}", COLORS['primary'], "Completed orders"),
                ("💰", "Revenue", f"${stats.get('total_sales_amount', 0):,.2f}", COLORS['success'], "Total revenue"),
                ("📊", "Avg Order", f"${stats.get('avg_sale_value', 0):.2f}", COLORS['info'], "Average order value"),
            ]
            
            for i, (icon, label, value, color, description) in enumerate(sales_data):
                card = self.create_metric_card(sales_grid, icon, label, value, color, description)
                card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
                sales_grid.columnconfigure(i, weight=1)
        
        # Row 5: Last updated timestamp
        timestamp_frame = tk.Frame(parent, bg=COLORS['bg'], pady=20)
        timestamp_frame.grid(row=current_row, column=0, sticky="ew", padx=20)
        timestamp_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(timestamp_frame,
                text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                font=FONTS['small'],
                bg=COLORS['bg'],
                fg=COLORS['secondary'],
                anchor='center').grid(row=0, column=0)
    
    def create_metric_card(self, parent, icon, label, value, color, description):
        """Create a metric card with icon, label, and value"""
        card = tk.Frame(parent,
                       bg=COLORS['card_bg'],
                       relief='solid',
                       borderwidth=1,
                       padx=15,
                       pady=15)
        
        # Icon
        tk.Label(card,
                text=icon,
                font=('Segoe UI Emoji', 28),
                bg=COLORS['card_bg'],
                fg=color).pack(anchor='center')
        
        # Value (larger)
        tk.Label(card,
                text=value,
                font=('Segoe UI', 20, 'bold'),
                bg=COLORS['card_bg'],
                fg=color).pack(anchor='center', pady=(10, 5))
        
        # Label
        tk.Label(card,
                text=label,
                font=FONTS['label'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).pack(anchor='center')
        
        # Description (smaller)
        tk.Label(card,
                text=description,
                font=FONTS['small'],
                bg=COLORS['card_bg'],
                fg=COLORS['secondary']).pack(anchor='center', pady=(5, 0))
        
        return card
    
    def create_stock_card(self, parent, icon, label, value, color, description):
        """Create a stock status card"""
        card = tk.Frame(parent,
                       bg=COLORS['card_bg'],
                       relief='solid',
                       borderwidth=1,
                       padx=15,
                       pady=15)
        
        # Icon and label row
        icon_label_frame = tk.Frame(card, bg=COLORS['card_bg'])
        icon_label_frame.pack(fill='x')
        
        tk.Label(icon_label_frame,
                text=icon,
                font=('Segoe UI Emoji', 20),
                bg=COLORS['card_bg'],
                fg=color).pack(side='left')
        
        tk.Label(icon_label_frame,
                text=label,
                font=FONTS['label'],
                bg=COLORS['card_bg'],
                fg=COLORS['fg']).pack(side='left', padx=(10, 0))
        
        # Value (centered)
        tk.Label(card,
                text=value,
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['card_bg'],
                fg=color).pack(anchor='center', pady=(10, 5))
        
        # Description
        tk.Label(card,
                text=description,
                font=FONTS['small'],
                bg=COLORS['card_bg'],
                fg=COLORS['secondary']).pack(anchor='center')
        
        return card
    
    def export_statistics_report(self):
        """Export statistics to a text file"""
        stats = self.db.get_statistics()
        if not stats or stats.get('total_records', 0) == 0:
            messagebox.showinfo("No Data", "No statistics available to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Statistics Report"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("VINYLFLOW ANALYTICS REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"User: {self.user.get('username', 'Guest')}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write("📊 KEY METRICS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Records: {stats.get('total_records', 0):,}\n")
                f.write(f"Total Stock: {stats.get('total_stock', 0):,}\n")
                f.write(f"Total Value: ${stats.get('total_value', 0):,.2f}\n")
                f.write(f"Average Price: ${stats.get('avg_price', 0):.2f}\n\n")
                
                f.write("📊 STOCK ANALYSIS\n")
                f.write("-" * 40 + "\n")
                low_stock = len(stats.get('low_stock', []))
                out_of_stock = len(stats.get('out_of_stock', []))
                healthy_stock = max(0, stats.get('total_records', 0) - low_stock - out_of_stock)
                f.write(f"In Stock (>5): {healthy_stock} items\n")
                f.write(f"Low Stock (1-5): {low_stock} items\n")
                f.write(f"Out of Stock: {out_of_stock} items\n\n")
                
                if stats.get('most_expensive'):
                    f.write("💰 PRICE ANALYSIS\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Most Expensive: ${stats['most_expensive'].get('price', 0):.2f} - {stats['most_expensive'].get('artist', 'Unknown')} - {stats['most_expensive'].get('album', 'Unknown')}\n")
                    f.write(f"Least Expensive: ${stats['least_expensive'].get('price', 0):.2f} - {stats['least_expensive'].get('artist', 'Unknown')} - {stats['least_expensive'].get('album', 'Unknown')}\n\n")
                
                if stats.get('low_stock'):
                    f.write("⚠️ LOW STOCK ITEMS\n")
                    f.write("-" * 40 + "\n")
                    for item in stats['low_stock'][:10]:
                        f.write(f"• {item.get('artist', 'Unknown')} - {item.get('album', 'Unknown')}: {item.get('stock', 0)} left\n")
                    f.write("\n")
                
                if stats.get('total_sales_count', 0) > 0:
                    f.write("📈 SALES STATISTICS\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Total Sales: {stats.get('total_sales_count', 0):,}\n")
                    f.write(f"Total Revenue: ${stats.get('total_sales_amount', 0):,.2f}\n")
                    f.write(f"Average Order Value: ${stats.get('avg_sale_value', 0):.2f}\n")
            
            messagebox.showinfo("Export Successful", f"Report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}")
    
    def create_customer_interface(self, parent):
        """Create customer interface"""
        # Configure parent grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=3)  # Catalog (3/4)
        parent.grid_columnconfigure(1, weight=1)  # Cart (1/4)
        
        # Left panel - Catalog
        left_panel = ttk.LabelFrame(parent, text=" 📀 Catalog ", padding=15)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Right panel - Cart
        right_panel = ttk.LabelFrame(parent, text=" 🛒 Shopping Cart ", padding=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Create catalog section
        self.create_catalog_section(left_panel)
        
        # Create cart section
        self.create_cart_section(right_panel)
    
    def create_catalog_section(self, parent):
        """Create catalog section for customers"""
        # Configure parent grid
        parent.grid_rowconfigure(0, weight=0)  # Search
        parent.grid_rowconfigure(1, weight=1)  # Treeview
        parent.grid_rowconfigure(2, weight=0)  # Add to cart button
        parent.grid_columnconfigure(0, weight=1)
        
        # Search frame
        search_frame = tk.Frame(parent, bg=COLORS['bg'])
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)
        
        # Search entry
        self.customer_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                              textvariable=self.customer_search_var,
                              font=FONTS['entry'],
                              bg=COLORS['entry_bg'],
                              fg=COLORS['fg'],
                              relief='solid',
                              borderwidth=1)
        search_entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 10))
        search_entry.insert(0, "Search by artist, album, or genre...")
        
        def clear_placeholder(e):
            if search_entry.get() == "Search by artist, album, or genre...":
                search_entry.delete(0, tk.END)
        
        def restore_placeholder(e):
            if not search_entry.get():
                search_entry.insert(0, "Search by artist, album, or genre...")
        
        search_entry.bind('<FocusIn>', clear_placeholder)
        search_entry.bind('<FocusOut>', restore_placeholder)
        search_entry.bind('<KeyRelease>', lambda e: self.search_records())
        
        # Search button
        search_btn = tk.Button(search_frame,
                             text="🔍 Search",
                             font=FONTS['button_small'],
                             bg=COLORS['primary'],
                             fg=COLORS['white'],
                             relief='flat',
                             command=self.search_records,
                             cursor='hand2',
                             padx=15,
                             pady=8)
        search_btn.grid(row=0, column=1)
        
        search_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview frame
        tree_frame = tk.Frame(parent, bg=COLORS['bg'])
        tree_frame.grid(row=1, column=0, sticky="nsew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        # Create treeview
        columns = ("ID", "Album", "Artist", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure columns (hide ID column for customers)
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=0, stretch=False)  # Hide ID column
            else:
                width = 150 if col == "Album" else 120 if col == "Artist" else 80
                self.tree.column(col, width=width, anchor="center" if col in ["Year", "Price", "Stock"] else "w")
        
        # Add scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Grid layout for treeview
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Add to cart button frame
        button_frame = tk.Frame(parent, bg=COLORS['bg'])
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Add to cart button
        add_cart_btn = tk.Button(button_frame,
                               text="🛒 Add Selected to Cart",
                               font=FONTS['button'],
                               bg=COLORS['primary'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=self.add_to_cart,
                               cursor='hand2',
                               pady=10)
        add_cart_btn.grid(row=0, column=0, sticky="ew")
    
    def create_cart_section(self, parent):
        """Create shopping cart section"""
        # Configure parent grid
        parent.grid_rowconfigure(0, weight=1)  # Treeview
        parent.grid_rowconfigure(1, weight=0)  # Total
        parent.grid_rowconfigure(2, weight=0)  # Buttons
        parent.grid_columnconfigure(0, weight=1)
        
        # Cart items treeview frame
        tree_frame = tk.Frame(parent, bg=COLORS['bg'])
        tree_frame.grid(row=0, column=0, sticky="nsew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        # Create cart treeview
        columns = ("Item", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.cart_tree.heading(col, text=col)
            width = 120 if col == "Item" else 60
            self.cart_tree.column(col, width=width, anchor="center" if col != "Item" else "w")
        
        # Add scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Total frame
        total_frame = tk.Frame(parent, bg=COLORS['bg'])
        total_frame.grid(row=1, column=0, sticky="ew", pady=10)
        total_frame.grid_columnconfigure(0, weight=1)
        total_frame.grid_columnconfigure(1, weight=0)
        
        tk.Label(total_frame,
                text="Total:",
                font=FONTS['label'],
                bg=COLORS['bg'],
                fg=COLORS['fg']).grid(row=0, column=0, sticky="w")
        
        self.total_label = tk.Label(total_frame,
                                   text="$0.00",
                                   font=FONTS['heading'],
                                   bg=COLORS['bg'],
                                   fg=COLORS['primary'])
        self.total_label.grid(row=0, column=1, sticky="e")
        
        # Action buttons frame
        btn_frame = tk.Frame(parent, bg=COLORS['bg'])
        btn_frame.grid(row=2, column=0, sticky="ew")
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        # Clear cart button
        clear_btn = tk.Button(btn_frame,
                            text="❌ Clear Cart",
                            font=FONTS['button_small'],
                            bg=COLORS['danger'],
                            fg=COLORS['white'],
                            relief='flat',
                            command=self.clear_cart,
                            cursor='hand2',
                            padx=10,
                            pady=8)
        clear_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Checkout button
        checkout_btn = tk.Button(btn_frame,
                               text="💳 Checkout",
                               font=FONTS['button_small'],
                               bg=COLORS['success'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=self.checkout,
                               cursor='hand2',
                               padx=10,
                               pady=8)
        checkout_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    
    # Data methods
    def load_data(self):
        """Load initial data"""
        self.refresh_records()
    
    def refresh_records(self):
        """Refresh records in treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get records from database
        records = self.db.get_all_records()
        
        # Add records to treeview
        for record in records:
            self.tree.insert('', 'end', values=(
                record.get('id', ''),
                record.get('album', ''),
                record.get('artist', ''),
                record.get('genre', ''),
                record.get('year', ''),
                f"${record.get('price', 0):.2f}",
                record.get('stock', 0)
            ))
    
    def search_records(self):
        """Search records based on search term"""
        if self.is_owner:
            query = self.search_var.get()
        else:
            query = self.customer_search_var.get()
            if query == "Search by artist, album, or genre...":
                query = ""
        
        if not query:
            self.refresh_records()
            return
        
        # Search records in database
        results = self.db.search_records(query)
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add search results
        for record in results:
            self.tree.insert('', 'end', values=(
                record.get('id', ''),
                record.get('album', ''),
                record.get('artist', ''),
                record.get('genre', ''),
                record.get('year', ''),
                f"${record.get('price', 0):.2f}",
                record.get('stock', 0)
            ))
    
    def on_record_select(self, event):
        """Handle record selection"""
        selection = self.tree.selection()
        if selection and self.is_owner:
            values = self.tree.item(selection[0])['values']
            if values and len(values) >= 7:
                self.load_form_from_record(values)
    
    def load_form_from_record(self, values):
        """Load record data into form"""
        if not self.is_owner:
            return
            
        entries = ['artist_entry', 'album_entry', 'genre_entry', 'year_entry', 'price_entry', 'stock_entry']
        form_values = [values[2], values[1], values[3], values[4], str(values[5]).replace('$', ''), values[6]]
        
        for entry_name, value in zip(entries, form_values):
            if entry_name in self.form_entries:
                self.form_entries[entry_name].delete(0, tk.END)
                self.form_entries[entry_name].insert(0, value)
    
    def add_record(self):
        """Add a new record"""
        if not self.is_owner:
            return
            
        # Get form data
        data = {
            'artist': self.form_entries['artist_entry'].get().strip(),
            'album': self.form_entries['album_entry'].get().strip(),
            'genre': self.form_entries['genre_entry'].get().strip(),
            'year': self.form_entries['year_entry'].get().strip(),
            'price': self.form_entries['price_entry'].get().strip(),
            'stock': self.form_entries['stock_entry'].get().strip()
        }
        
        # Validation
        errors = []
        try:
            data['year'] = int(data['year'])
            if data['year'] < 1900 or data['year'] > datetime.now().year + 1:
                errors.append("Invalid year")
        except:
            errors.append("Year must be a number")
        
        try:
            data['price'] = float(data['price'])
            if data['price'] <= 0:
                errors.append("Price must be positive")
        except:
            errors.append("Price must be a number")
        
        try:
            data['stock'] = int(data['stock'])
            if data['stock'] < 0:
                errors.append("Stock cannot be negative")
        except:
            errors.append("Stock must be a whole number")
        
        if not data['artist'] or not data['album']:
            errors.append("Artist and Album are required")
        
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        try:
            # Add record to database
            record_id = self.db.add_record(data)
            
            self.refresh_records()
            self.clear_form()
            messagebox.showinfo("Success", f"Record added successfully! (ID: {record_id})")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add record: {str(e)}")
    
    def update_record(self):
        """Update selected record"""
        if not self.is_owner:
            return
            
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to update")
            return
        
        record_id = self.tree.item(selection[0])['values'][0]
        
        # Get updated data
        updates = {
            'artist': self.form_entries['artist_entry'].get().strip(),
            'album': self.form_entries['album_entry'].get().strip(),
            'genre': self.form_entries['genre_entry'].get().strip(),
            'year': self.form_entries['year_entry'].get().strip(),
            'price': self.form_entries['price_entry'].get().strip(),
            'stock': self.form_entries['stock_entry'].get().strip()
        }
        
        # Validation
        try:
            updates['year'] = int(updates['year'])
            updates['price'] = float(updates['price'])
            updates['stock'] = int(updates['stock'])
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values")
            return
        
        # Update record in database
        if self.db.update_record(record_id, updates):
            self.refresh_records()
            messagebox.showinfo("Success", "Record updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update record")
    
    def delete_record(self):
        """Delete selected record"""
        if not self.is_owner:
            return
            
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            return
        
        record_id = self.tree.item(selection[0])['values'][0]
        
        # Delete record from database
        if self.db.delete_record(record_id):
            self.refresh_records()
            self.clear_form()
            messagebox.showinfo("Success", "Record deleted successfully!")
        else:
            messagebox.showerror("Error", "Failed to delete record")
    
    def clear_form(self):
        """Clear the form"""
        if not self.is_owner:
            return
            
        for entry in self.form_entries.values():
            entry.delete(0, 'end')
    
    def add_to_cart(self):
        """Add selected item to cart"""
        if self.is_owner:
            return
            
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to add to cart")
            return
        
        values = self.tree.item(selection[0])['values']
        record_id = values[0]
        
        # Get record from database
        record = self.db.get_record(record_id)
        if not record:
            messagebox.showerror("Error", "Record not found")
            return
        
        # Check stock
        if record['stock'] <= 0:
            messagebox.showwarning("Out of Stock", "This item is out of stock")
            return
        
        # Ask for quantity
        quantity = simpledialog.askinteger("Quantity", 
                                         f"How many '{record['album']}' would you like?\nAvailable: {record['stock']}",
                                         minvalue=1,
                                         maxvalue=record['stock'])
        
        if not quantity:
            return
        
        # Add to cart
        price = record['price']
        total = price * quantity
        
        # Check if item already in cart
        for item in self.cart:
            if item['record_id'] == record_id:
                item['quantity'] += quantity
                item['total'] = item['quantity'] * price
                break
        else:
            self.cart.append({
                'record_id': record_id,
                'item': f"{record['album']} - {record['artist']}",
                'quantity': quantity,
                'price': price,
                'total': total
            })
        
        # Update cart display
        self.update_cart_display()
        messagebox.showinfo("Added to Cart", f"Added {quantity} x '{record['album']}' to cart")
    
    def update_cart_display(self):
        """Update cart treeview and total"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        self.cart_total = 0
        for item in self.cart:
            self.cart_tree.insert('', 'end', values=(
                item['item'],
                item['quantity'],
                f"${item['price']:.2f}",
                f"${item['total']:.2f}"
            ))
            self.cart_total += item['total']
        
        # Update total
        self.total_label.config(text=f"${self.cart_total:.2f}")
    
    def clear_cart(self):
        """Clear shopping cart"""
        if not self.cart:
            return
        
        if messagebox.askyesno("Clear Cart", "Are you sure you want to clear your cart?"):
            self.cart = []
            self.update_cart_display()
    
    def checkout(self):
        """Process checkout"""
        if self.is_owner or not self.cart:
            messagebox.showinfo("Empty Cart", "Your cart is empty!")
            return
        
        # If user is not logged in, ask for shipping address
        shipping_address = ""
        if self.user.get('username') == 'guest':
            shipping_address = simpledialog.askstring("Shipping Address", 
                                                    "Please enter your shipping address:")
            if not shipping_address:
                return
        
        try:
            # Convert cart items to database format
            items = []
            for cart_item in self.cart:
                items.append({
                    'record_id': cart_item['record_id'],
                    'quantity': cart_item['quantity']
                })
            
            # For demo purposes, we'll simulate a successful checkout
            # In a real app, you'd process payment and create an order in the database
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Show success message
            messagebox.showinfo("Order Placed", 
                              f"Thank you for your order!\n\nOrder ID: {order_id}\nTotal: ${self.cart_total:.2f}\n\nYour records will be shipped soon.")
            
            # Clear cart
            self.cart = []
            self.update_cart_display()
            self.refresh_records()
            
        except Exception as e:
            messagebox.showerror("Checkout Error", f"Failed to process order: {str(e)}")
    
    def export_to_csv(self):
        """Export records to CSV"""
        if not self.is_owner:
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Records to CSV"
        )
        
        if not filename:
            return
        
        try:
            self.db.export_to_csv(filename, 'records')
            messagebox.showinfo("Export Successful", f"Records exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def import_from_csv(self):
        """Import records from CSV"""
        if not self.is_owner:
            return
            
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Records from CSV"
        )
        
        if not filename:
            return
        
        try:
            imported_count = self.db.import_from_csv(filename, 'records')
            if imported_count > 0:
                self.refresh_records()
                messagebox.showinfo("Import Successful", f"Imported {imported_count} records")
            else:
                messagebox.showwarning("No Data", "No valid records found in the file")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {str(e)}")
    
    def logout(self):
        """Logout from the application"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Call logout callback
            if self.logout_callback:
                self.logout_callback()