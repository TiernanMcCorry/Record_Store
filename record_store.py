import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog
import json
import os
from datetime import datetime
import csv
from config import COLORS, FONTS, LIGHT_COLORS, DARK_COLORS

class RecordStoreApp:
    def __init__(self, root, is_owner=False, user=None, logout_callback=None):
        self.root = root
        self.is_owner = is_owner
        self.user = user or {}
        self.logout_callback = logout_callback
        
        # Data storage
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.records_file = os.path.join(self.base_dir, "records_inventory.json")
        self.records = self.load_records()
        
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
        
        # Update theme button
        if hasattr(self, 'theme_btn'):
            self.theme_btn.config(text="☀️" if self.dark_mode else "🌙",
                                bg=COLORS['primary_dark'] if self.dark_mode else COLORS['primary'])
        
        # Reapply theme
        self.root.configure(bg=COLORS['bg'])
        self.create_styles()
        self.refresh_widget_styles()
    
    def refresh_widget_styles(self):
        """Refresh widget styles after theme change"""
        # Update header
        if hasattr(self, 'header'):
            self.header.configure(bg=COLORS['primary'])
        
        # Update treeview
        if hasattr(self, 'tree'):
            self.tree.configure(style='Treeview')
    
    def create_widgets(self):
        """Create main widgets"""
        # Header
        self.create_header()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        if self.is_owner:
            self.create_owner_interface(main_container)
        else:
            self.create_customer_interface(main_container)
    
    def create_header(self):
        """Create application header"""
        self.header = tk.Frame(self.root, 
                              bg=COLORS['primary'],
                              height=80)
        self.header.pack(fill='x', side='top')
        self.header.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(self.header, bg=COLORS['primary'])
        title_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(title_frame,
                text="💿",
                font=('Segoe UI Emoji', 28),
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left', padx=5)
        
        tk.Label(title_frame,
                text="VinylFlow",
                font=FONTS['title'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left')
        
        tk.Label(title_frame,
                text=f"{' Manager' if self.is_owner else ''}",
                font=FONTS['subtitle'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left')
        
        # User info
        user_frame = tk.Frame(self.header, bg=COLORS['primary'])
        user_frame.place(relx=0.95, rely=0.5, anchor='e')
        
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
        user_type = "Owner" if self.is_owner else "Customer"
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
        notebook.pack(fill='both', expand=True)
        
        # Tabs
        inventory_tab = ttk.Frame(notebook)
        statistics_tab = ttk.Frame(notebook)
        
        notebook.add(inventory_tab, text="📦 Inventory")
        notebook.add(statistics_tab, text="📊 Statistics")
        
        # Inventory tab
        self.create_inventory_section(inventory_tab)
        
        # Statistics tab
        self.create_enhanced_statistics_section(statistics_tab)
    
    def create_inventory_section(self, parent):
        """Create inventory management section"""
        # Split into left and right panels
        left_panel = ttk.Frame(parent)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_panel = ttk.Frame(parent)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Left panel - Add record form
        self.create_record_form(left_panel)
        
        # Right panel - Records list
        self.create_records_list(right_panel)
    
    def create_record_form(self, parent):
        """Create record addition form"""
        # Form frame
        form_frame = ttk.LabelFrame(parent, text=" Add/Edit Record ", padding=15)
        form_frame.pack(fill='both', expand=True)
        
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
        
        for label, name in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', pady=5)
            
            ttk.Label(frame, text=label, width=12, anchor='w').pack(side='left')
            
            entry = ttk.Entry(frame, font=FONTS['entry'], width=30, style='Custom.TEntry')
            entry.pack(side='left', fill='x', expand=True)
            
            self.form_entries[name] = entry
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame,
                  text="➕ Add Record",
                  command=self.add_record,
                  style='Success.TButton').pack(side='left', padx=(0, 5))
        
        ttk.Button(btn_frame,
                  text="✏️ Update",
                  command=self.update_record,
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="🗑️ Delete",
                  command=self.delete_record,
                  style='Danger.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="🧹 Clear",
                  command=self.clear_form,
                  style='Warning.TButton').pack(side='left', padx=5)
    
    def create_records_list(self, parent):
        """Create records list with search"""
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Search:").pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                               font=FONTS['entry'], style='Custom.TEntry')
        search_entry.pack(side='left', fill='x', expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self.search_records())
        
        # Treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True)
        
        # Create treeview
        columns = ("ID", "Album", "Artist", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_configs = {
            "ID": {"width": 50, "anchor": "center"},
            "Album": {"width": 200, "anchor": "w"},
            "Artist": {"width": 150, "anchor": "w"},
            "Genre": {"width": 100, "anchor": "center"},
            "Year": {"width": 70, "anchor": "center"},
            "Price": {"width": 80, "anchor": "e"},
            "Stock": {"width": 70, "anchor": "center"}
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, **column_configs[col])
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_record_select)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill='x', pady=10)
        
        ttk.Button(action_frame,
                  text="🔄 Refresh",
                  command=self.refresh_records,
                  style='Secondary.TButton').pack(side='left', padx=5)
        
        ttk.Button(action_frame,
                  text="📤 Export CSV",
                  command=self.export_to_csv,
                  style='Success.TButton').pack(side='left', padx=5)
        
        ttk.Button(action_frame,
                  text="📥 Import CSV",
                  command=self.import_from_csv,
                  style='Warning.TButton').pack(side='left', padx=5)
    
    def create_enhanced_statistics_section(self, parent):
        """Create modern statistics section with enhanced visuals"""
        # Main container with scrollable content
        main_container = tk.Frame(parent, bg=COLORS['bg'])
        main_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.stats_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        self.stats_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.stats_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")
        
        # Title at the top
        title_frame = tk.Frame(self.stats_frame, bg=COLORS['bg'], pady=10)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(title_frame,
                              text="📊 VinylFlow Analytics Dashboard",
                              font=('Segoe UI', 22, 'bold'),
                              bg=COLORS['bg'],
                              fg=COLORS['primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame,
                                 text="Real-time inventory insights and statistics",
                                 font=FONTS['subtitle'],
                                 bg=COLORS['bg'],
                                 fg=COLORS['secondary'])
        subtitle_label.pack(pady=(5, 20))
        
        # Refresh button in title
        refresh_btn = tk.Button(title_frame,
                               text="🔄 Refresh Dashboard",
                               font=FONTS['button'],
                               bg=COLORS['info'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=self.update_enhanced_statistics,
                               cursor='hand2',
                               padx=20,
                               pady=10)
        refresh_btn.pack(side='right', padx=20)
        
        # Export button
        export_btn = tk.Button(title_frame,
                              text="📤 Export Report",
                              font=FONTS['button'],
                              bg=COLORS['success'],
                              fg=COLORS['white'],
                              relief='flat',
                              command=self.export_statistics_report,
                              cursor='hand2',
                              padx=20,
                              pady=10)
        export_btn.pack(side='left', padx=20)
        
        # Initial statistics display
        self.update_enhanced_statistics()
    
    def update_enhanced_statistics(self):
        """Update the statistics display with latest data"""
        # Clear existing content (except title)
        for widget in self.stats_frame.winfo_children():
            if widget != self.stats_frame.winfo_children()[0]:  # Keep the title frame
                widget.destroy()
        
        # Calculate statistics
        stats = self.calculate_comprehensive_stats()
        
        if not stats:
            # Show empty state
            empty_frame = tk.Frame(self.stats_frame, bg=COLORS['bg'], pady=50)
            empty_frame.pack(fill='both', expand=True)
            
            tk.Label(empty_frame,
                    text="📊",
                    font=('Segoe UI Emoji', 64),
                    bg=COLORS['bg'],
                    fg=COLORS['secondary']).pack()
            
            tk.Label(empty_frame,
                    text="No data available for statistics",
                    font=FONTS['heading'],
                    bg=COLORS['bg'],
                    fg=COLORS['fg']).pack(pady=10)
            
            tk.Label(empty_frame,
                    text="Add records to see analytics dashboard",
                    font=FONTS['subtitle'],
                    bg=COLORS['bg'],
                    fg=COLORS['secondary']).pack()
            return
        
        # Display statistics cards
        self.display_statistics_cards(self.stats_frame, stats)
    
    def calculate_comprehensive_stats(self):
        """Calculate comprehensive statistics with enhanced metrics"""
        stats = {}
        
        if not self.records:
            return stats
        
        # Basic metrics
        stats['total_records'] = len(self.records)
        stats['total_stock'] = sum(record.get('stock', 0) for record in self.records)
        stats['total_value'] = sum(record.get('price', 0) * record.get('stock', 0) for record in self.records)
        stats['avg_price'] = stats['total_value'] / stats['total_stock'] if stats['total_stock'] > 0 else 0
        
        # Stock analysis
        stats['low_stock'] = [r for r in self.records if 0 < r.get('stock', 0) <= 5]
        stats['out_of_stock'] = [r for r in self.records if r.get('stock', 0) == 0]
        stats['in_stock'] = [r for r in self.records if r.get('stock', 0) > 0]
        stats['healthy_stock'] = [r for r in self.records if r.get('stock', 0) > 5]
        
        # Genre analysis
        genres = {}
        for record in self.records:
            genre = record.get('genre', 'Unknown')
            genres[genre] = genres.get(genre, 0) + 1
        stats['genres'] = genres
        
        # Year analysis
        years = {}
        for record in self.records:
            year = record.get('year', 'Unknown')
            years[year] = years.get(year, 0) + 1
        stats['years'] = years
        
        # Price analysis
        if self.records:
            stats['most_expensive'] = max(self.records, key=lambda x: x.get('price', 0))
            stats['least_expensive'] = min(self.records, key=lambda x: x.get('price', 0))
            stats['highest_stock'] = max(self.records, key=lambda x: x.get('stock', 0))
            stats['lowest_stock'] = min(self.records, key=lambda x: x.get('stock', 0))
            
            # Calculate price ranges
            prices = [r.get('price', 0) for r in self.records]
            stats['price_min'] = min(prices)
            stats['price_max'] = max(prices)
            stats['price_avg'] = sum(prices) / len(prices)
            
            # Price distribution categories
            price_categories = {
                'Under $10': 0,
                '$10-$20': 0,
                '$20-$30': 0,
                '$30-$50': 0,
                'Over $50': 0
            }
            
            for price in prices:
                if price < 10:
                    price_categories['Under $10'] += 1
                elif price < 20:
                    price_categories['$10-$20'] += 1
                elif price < 30:
                    price_categories['$20-$30'] += 1
                elif price < 50:
                    price_categories['$30-$50'] += 1
                else:
                    price_categories['Over $50'] += 1
            
            stats['price_distribution'] = price_categories
        
        return stats
    
    def display_statistics_cards(self, parent, stats):
        """Display statistics in modern cards with visual elements"""
        # Container for all statistics
        container = tk.Frame(parent, bg=COLORS['bg'])
        container.pack(fill='x', padx=20, pady=10)
        
        # Row 1: Key Metrics
        metrics_frame = tk.LabelFrame(container,
                                     text=" 📈 Key Metrics ",
                                     font=('Segoe UI', 14, 'bold'),
                                     bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                                     fg=COLORS['primary'],
                                     relief='groove',
                                     borderwidth=2,
                                     padx=15,
                                     pady=15)
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        # Create metrics cards grid
        metrics_grid = tk.Frame(metrics_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
        metrics_grid.pack(fill='x')
        
        metrics_data = [
            ("📀", "Total Records", str(stats['total_records']), COLORS['primary'], "Albums in inventory"),
            ("📦", "Total Stock", f"{stats['total_stock']:,}", COLORS['info'], "Units available"),
            ("💰", "Inventory Value", f"${stats['total_value']:,.2f}", COLORS['success'], "Total worth"),
            ("💵", "Avg Price", f"${stats['avg_price']:.2f}", COLORS['warning'], "Per unit average"),
        ]
        
        for i, (icon, label, value, color, description) in enumerate(metrics_data):
            card = self.create_metric_card(metrics_grid, icon, label, value, color, description)
            card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            metrics_grid.columnconfigure(i, weight=1)
        
        # Row 2: Stock Analysis
        stock_frame = tk.LabelFrame(container,
                                   text=" 📊 Stock Analysis ",
                                   font=('Segoe UI', 14, 'bold'),
                                   bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                                   fg=COLORS['primary'],
                                   relief='groove',
                                   borderwidth=2,
                                   padx=15,
                                   pady=15)
        stock_frame.pack(fill='x', pady=(0, 20))
        
        # Stock status cards
        stock_data = [
            ("✅", "In Stock", f"{len(stats['healthy_stock'])}", COLORS['success'], "Items with >5 stock"),
            ("⚠️", "Low Stock", f"{len(stats['low_stock'])}", COLORS['warning'], "Items with 1-5 stock"),
            ("❌", "Out of Stock", f"{len(stats['out_of_stock'])}", COLORS['danger'], "Items with 0 stock"),
        ]
        
        stock_grid = tk.Frame(stock_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
        stock_grid.pack(fill='x')
        
        for i, (icon, label, value, color, description) in enumerate(stock_data):
            card = self.create_stock_card(stock_grid, icon, label, value, color, description)
            card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            stock_grid.columnconfigure(i, weight=1)
        
        # Low stock items list
        if stats['low_stock']:
            low_stock_frame = tk.Frame(stock_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
            low_stock_frame.pack(fill='x', pady=(15, 0))
            
            tk.Label(low_stock_frame,
                    text="⚠️ Low Stock Items (≤5 remaining):",
                    font=FONTS['label'],
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['warning']).pack(anchor='w')
            
            for item in stats['low_stock'][:5]:  # Show top 5
                tk.Label(low_stock_frame,
                        text=f"• {item.get('artist', 'Unknown')} - {item.get('album', 'Unknown')}: {item.get('stock', 0)} left",
                        font=FONTS['small'],
                        bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                        fg=COLORS['dark_gray']).pack(anchor='w')
        
        # Row 3: Genre Distribution
        genre_frame = tk.LabelFrame(container,
                                   text=" 🎵 Genre Distribution ",
                                   font=('Segoe UI', 14, 'bold'),
                                   bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                                   fg=COLORS['primary'],
                                   relief='groove',
                                   borderwidth=2,
                                   padx=15,
                                   pady=15)
        genre_frame.pack(fill='x', pady=(0, 20))
        
        if stats.get('genres'):
            # Find most popular genre
            popular_genre = max(stats['genres'].items(), key=lambda x: x[1]) if stats['genres'] else ('None', 0)
            
            # Genre header with popular genre
            genre_header = tk.Frame(genre_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
            genre_header.pack(fill='x', pady=(0, 10))
            
            tk.Label(genre_header,
                    text=f"Most Popular: {popular_genre[0]} ({popular_genre[1]} records)",
                    font=FONTS['label'],
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['primary']).pack(side='left')
            
            # Genre bars
            total_records = stats['total_records']
            for genre, count in sorted(stats['genres'].items(), key=lambda x: x[1], reverse=True)[:8]:  # Top 8
                percentage = (count / total_records) * 100
                self.create_genre_bar(genre_frame, genre, count, percentage, total_records)
        
        # Row 4: Price Analysis
        if stats.get('most_expensive'):
            price_frame = tk.LabelFrame(container,
                                       text=" 💰 Price Analysis ",
                                       font=('Segoe UI', 14, 'bold'),
                                       bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                                       fg=COLORS['primary'],
                                       relief='groove',
                                       borderwidth=2,
                                       padx=15,
                                       pady=15)
            price_frame.pack(fill='x', pady=(0, 20))
            
            # Price extremes
            extremes_frame = tk.Frame(price_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
            extremes_frame.pack(fill='x', pady=(0, 15))
            
            # Most expensive
            most_exp = stats['most_expensive']
            most_frame = tk.Frame(extremes_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
            most_frame.pack(side='left', fill='x', expand=True, padx=10)
            
            tk.Label(most_frame,
                    text="🏆 Most Expensive",
                    font=FONTS['label'],
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['danger']).pack(anchor='w')
            
            tk.Label(most_frame,
                    text=f"${most_exp.get('price', 0):.2f}",
                    font=('Segoe UI', 16, 'bold'),
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['danger']).pack(anchor='w')
            
            tk.Label(most_frame,
                    text=f"{most_exp.get('artist', 'Unknown')} - {most_exp.get('album', 'Unknown')}",
                    font=FONTS['small'],
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['dark_gray']).pack(anchor='w')
            
            # Least expensive
            least_exp = stats['least_expensive']
            least_frame = tk.Frame(extremes_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
            least_frame.pack(side='right', fill='x', expand=True, padx=10)
            
            tk.Label(least_frame,
                    text="💎 Least Expensive",
                    font=FONTS['label'],
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['success']).pack(anchor='e')
            
            tk.Label(least_frame,
                    text=f"${least_exp.get('price', 0):.2f}",
                    font=('Segoe UI', 16, 'bold'),
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['success']).pack(anchor='e')
            
            tk.Label(least_frame,
                    text=f"{least_exp.get('artist', 'Unknown')} - {least_exp.get('album', 'Unknown')}",
                    font=FONTS['small'],
                    bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                    fg=COLORS['dark_gray']).pack(anchor='e')
            
            # Price distribution
            if stats.get('price_distribution'):
                price_dist_frame = tk.Frame(price_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
                price_dist_frame.pack(fill='x', pady=(10, 0))
                
                tk.Label(price_dist_frame,
                        text="📊 Price Distribution:",
                        font=FONTS['label'],
                        bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                        fg=COLORS['fg']).pack(anchor='w', pady=(0, 10))
                
                for category, count in stats['price_distribution'].items():
                    if count > 0:
                        percentage = (count / stats['total_records']) * 100
                        self.create_price_distribution_bar(price_dist_frame, category, count, percentage)
        
        # Row 5: Year Analysis (if data exists)
        if stats.get('years') and len(stats['years']) > 1:
            year_frame = tk.LabelFrame(container,
                                      text=" 📅 Year Analysis ",
                                      font=('Segoe UI', 14, 'bold'),
                                      bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                                      fg=COLORS['primary'],
                                      relief='groove',
                                      borderwidth=2,
                                      padx=15,
                                      pady=15)
            year_frame.pack(fill='x', pady=(0, 20))
            
            # Get top 5 years
            sorted_years = sorted(stats['years'].items(), key=lambda x: x[1], reverse=True)[:5]
            
            year_grid = tk.Frame(year_frame, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'])
            year_grid.pack(fill='x')
            
            for i, (year, count) in enumerate(sorted_years):
                percentage = (count / stats['total_records']) * 100
                card = self.create_year_card(year_grid, year, count, percentage)
                card.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
                year_grid.columnconfigure(i, weight=1)
        
        # Last updated timestamp
        timestamp_frame = tk.Frame(container, bg=COLORS['bg'], pady=20)
        timestamp_frame.pack(fill='x')
        
        tk.Label(timestamp_frame,
                text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                font=FONTS['small'],
                bg=COLORS['bg'],
                fg=COLORS['secondary'],
                anchor='center').pack()
    
    def create_metric_card(self, parent, icon, label, value, color, description):
        """Create a metric card with icon, label, and value"""
        card = tk.Frame(parent,
                       bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                       relief='solid',
                       borderwidth=1,
                       padx=15,
                       pady=15)
        
        # Icon
        tk.Label(card,
                text=icon,
                font=('Segoe UI Emoji', 28),
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=color).pack(anchor='center')
        
        # Value (larger)
        tk.Label(card,
                text=value,
                font=('Segoe UI', 20, 'bold'),
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=color).pack(anchor='center', pady=(10, 5))
        
        # Label
        tk.Label(card,
                text=label,
                font=FONTS['label'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['fg']).pack(anchor='center')
        
        # Description (smaller)
        tk.Label(card,
                text=description,
                font=FONTS['small'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['secondary']).pack(anchor='center', pady=(5, 0))
        
        return card
    
    def create_stock_card(self, parent, icon, label, value, color, description):
        """Create a stock status card"""
        card = tk.Frame(parent,
                       bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                       relief='solid',
                       borderwidth=1,
                       padx=15,
                       pady=15)
        
        # Icon and label row
        icon_label_frame = tk.Frame(card, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'])
        icon_label_frame.pack(fill='x')
        
        tk.Label(icon_label_frame,
                text=icon,
                font=('Segoe UI Emoji', 20),
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=color).pack(side='left')
        
        tk.Label(icon_label_frame,
                text=label,
                font=FONTS['label'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['fg']).pack(side='left', padx=(10, 0))
        
        # Value (centered)
        tk.Label(card,
                text=value,
                font=('Segoe UI', 24, 'bold'),
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=color).pack(anchor='center', pady=(10, 5))
        
        # Description
        tk.Label(card,
                text=description,
                font=FONTS['small'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['secondary']).pack(anchor='center')
        
        return card
    
    def create_genre_bar(self, parent, genre, count, percentage, total):
        """Create a visual bar for genre distribution"""
        bar_frame = tk.Frame(parent, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'], height=35)
        bar_frame.pack(fill='x', pady=3)
        bar_frame.pack_propagate(False)
        
        # Genre label
        genre_label = tk.Label(bar_frame,
                              text=f"{genre}:",
                              font=FONTS['small'],
                              bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                              fg=COLORS['fg'],
                              width=20,
                              anchor='w')
        genre_label.place(x=0, y=0, relheight=1)
        
        # Progress bar background
        progress_bg = tk.Frame(bar_frame,
                              bg=COLORS['light_gray'],
                              height=25)
        progress_bg.place(x=150, y=5, relwidth=0.6)
        
        # Progress bar fill with gradient effect
        progress_width = min(percentage, 100) / 100 * 0.6
        progress_fill = tk.Frame(bar_frame,
                                bg=COLORS['primary'],
                                height=25)
        progress_fill.place(x=150, y=5, relwidth=progress_width)
        
        # Count and percentage label
        count_label = tk.Label(bar_frame,
                              text=f"{count} ({percentage:.1f}%)",
                              font=FONTS['small'],
                              bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                              fg=COLORS['fg'])
        count_label.place(relx=0.85, y=0, relheight=1)
    
    def create_price_distribution_bar(self, parent, category, count, percentage):
        """Create a price distribution bar"""
        bar_frame = tk.Frame(parent, bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'], height=30)
        bar_frame.pack(fill='x', pady=2)
        
        # Category label
        tk.Label(bar_frame,
                text=category,
                font=FONTS['small'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                fg=COLORS['fg'],
                width=15,
                anchor='w').pack(side='left')
        
        # Progress bar background
        progress_bg = tk.Frame(bar_frame,
                              bg=COLORS['light_gray'],
                              height=20)
        progress_bg.pack(side='left', fill='x', expand=True, padx=10)
        
        # Progress bar fill
        progress_width = min(percentage, 100) / 100
        progress_fill = tk.Frame(progress_bg,
                                bg=COLORS['warning'],
                                height=20)
        progress_fill.place(relwidth=progress_width)
        
        # Count label with percentage
        tk.Label(bar_frame,
                text=f"{count} ({percentage:.1f}%)",
                font=FONTS['small'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['bg'],
                fg=COLORS['fg'],
                width=15,
                anchor='e').pack(side='right')
    
    def create_year_card(self, parent, year, count, percentage):
        """Create a year analysis card"""
        card = tk.Frame(parent,
                       bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                       relief='solid',
                       borderwidth=1,
                       padx=15,
                       pady=15)
        
        # Year with icon
        tk.Label(card,
                text=f"📅 {year}",
                font=FONTS['label'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['primary']).pack()
        
        # Count (large)
        tk.Label(card,
                text=f"{count}",
                font=('Segoe UI', 18, 'bold'),
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['fg']).pack(pady=(10, 5))
        
        # Percentage
        tk.Label(card,
                text=f"{percentage:.1f}%",
                font=FONTS['small'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['secondary']).pack()
        
        # Label
        tk.Label(card,
                text="records",
                font=FONTS['small'],
                bg=COLORS['card_bg'] if 'card_bg' in COLORS else COLORS['light_gray'],
                fg=COLORS['dark_gray']).pack(pady=(5, 0))
        
        return card
    
    def export_statistics_report(self):
        """Export statistics to a text file"""
        from datetime import datetime
        
        stats = self.calculate_comprehensive_stats()
        if not stats:
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
                f.write(f"Total Records: {stats['total_records']:,}\n")
                f.write(f"Total Stock: {stats['total_stock']:,}\n")
                f.write(f"Total Value: ${stats['total_value']:,.2f}\n")
                f.write(f"Average Price: ${stats['avg_price']:.2f}\n\n")
                
                f.write("📊 STOCK ANALYSIS\n")
                f.write("-" * 40 + "\n")
                f.write(f"In Stock (>5): {len(stats['healthy_stock'])} items\n")
                f.write(f"Low Stock (1-5): {len(stats['low_stock'])} items\n")
                f.write(f"Out of Stock: {len(stats['out_of_stock'])} items\n\n")
                
                if stats.get('genres'):
                    f.write("🎵 GENRE DISTRIBUTION\n")
                    f.write("-" * 40 + "\n")
                    for genre, count in sorted(stats['genres'].items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / stats['total_records']) * 100
                        f.write(f"{genre}: {count} ({percentage:.1f}%)\n")
                    f.write("\n")
                
                if stats.get('most_expensive'):
                    f.write("💰 PRICE ANALYSIS\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Most Expensive: ${stats['most_expensive'].get('price', 0):.2f} - {stats['most_expensive'].get('artist', 'Unknown')} - {stats['most_expensive'].get('album', 'Unknown')}\n")
                    f.write(f"Least Expensive: ${stats['least_expensive'].get('price', 0):.2f} - {stats['least_expensive'].get('artist', 'Unknown')} - {stats['least_expensive'].get('album', 'Unknown')}\n\n")
                
                if stats.get('price_distribution'):
                    f.write("📊 PRICE DISTRIBUTION\n")
                    f.write("-" * 40 + "\n")
                    for category, count in stats['price_distribution'].items():
                        if count > 0:
                            percentage = (count / stats['total_records']) * 100
                            f.write(f"{category}: {count} ({percentage:.1f}%)\n")
                    f.write("\n")
                
                if stats['low_stock']:
                    f.write("⚠️ LOW STOCK ITEMS\n")
                    f.write("-" * 40 + "\n")
                    for item in stats['low_stock'][:10]:  # Top 10
                        f.write(f"• {item.get('artist', 'Unknown')} - {item.get('album', 'Unknown')}: {item.get('stock', 0)} left\n")
                    f.write("\n")
                
                if stats.get('years'):
                    f.write("📅 YEAR DISTRIBUTION (Top 5)\n")
                    f.write("-" * 40 + "\n")
                    for year, count in sorted(stats['years'].items(), key=lambda x: x[1], reverse=True)[:5]:
                        percentage = (count / stats['total_records']) * 100
                        f.write(f"{year}: {count} ({percentage:.1f}%)\n")
            
            messagebox.showinfo("Export Successful", f"Report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}")
    
    def create_customer_interface(self, parent):
        """Create customer interface"""
        # Split into left (catalog) and right (cart)
        left_panel = ttk.Frame(parent)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_panel = ttk.Frame(parent, width=350)
        right_panel.pack(side='right', fill='both')
        right_panel.pack_propagate(False)
        
        # Left panel - Catalog
        self.create_catalog_section(left_panel)
        
        # Right panel - Shopping cart
        self.create_cart_section(right_panel)
    
    def create_catalog_section(self, parent):
        """Create catalog section for customers"""
        # Search bar
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', pady=(0, 10))
        
        self.customer_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.customer_search_var,
                               font=FONTS['entry'],
                               style='Custom.TEntry')
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
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
        
        ttk.Button(search_frame,
                  text="🔍 Search",
                  command=self.search_records,
                  style='Primary.TButton').pack(side='left')
        
        # Records treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True)
        
        # Create treeview
        columns = ("Album", "Artist", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_configs = {
            "Album": {"width": 200, "anchor": "w"},
            "Artist": {"width": 150, "anchor": "w"},
            "Genre": {"width": 100, "anchor": "center"},
            "Year": {"width": 70, "anchor": "center"},
            "Price": {"width": 80, "anchor": "e"},
            "Stock": {"width": 70, "anchor": "center"}
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, **column_configs[col])
        
        # Add scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        # Add to cart button
        add_cart_btn = tk.Button(parent,
                               text="🛒 Add to Cart",
                               font=FONTS['button'],
                               bg=COLORS['primary'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=self.add_to_cart)
        add_cart_btn.pack(pady=10)
    
    def create_cart_section(self, parent):
        """Create shopping cart section"""
        cart_frame = ttk.LabelFrame(parent, text=" 🛒 Shopping Cart ", padding=15)
        cart_frame.pack(fill='both', expand=True)
        
        # Cart items treeview
        columns = ("Item", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=80 if col != "Item" else 150)
        
        self.cart_tree.pack(fill='both', expand=True)
        
        # Total frame
        total_frame = ttk.Frame(cart_frame)
        total_frame.pack(fill='x', pady=10)
        
        ttk.Label(total_frame, text="Total:", font=FONTS['label']).pack(side='left')
        self.total_label = ttk.Label(total_frame, 
                                   text="$0.00", 
                                   font=FONTS['heading'],
                                   foreground=COLORS['primary'])
        self.total_label.pack(side='right')
        
        # Action buttons
        btn_frame = ttk.Frame(cart_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame,
                  text="❌ Clear Cart",
                  command=self.clear_cart,
                  style='Danger.TButton').pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(btn_frame,
                  text="💳 Checkout",
                  command=self.checkout,
                  style='Success.TButton').pack(side='right', fill='x', expand=True)
    
    # Data methods
    def load_records(self):
        """Load records from JSON file"""
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_records(self):
        """Save records to JSON file"""
        with open(self.records_file, 'w') as f:
            json.dump(self.records, f, indent=4)
    
    def load_data(self):
        """Load initial data"""
        self.refresh_records()
    
    def refresh_records(self):
        """Refresh records in treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add records
        for record in self.records:
            if self.is_owner:
                self.tree.insert('', 'end', values=(
                    record['id'],
                    record['album'],
                    record['artist'],
                    record['genre'],
                    record['year'],
                    f"${record['price']:.2f}",
                    record['stock']
                ))
            else:
                self.tree.insert('', 'end', values=(
                    record['album'],
                    record['artist'],
                    record['genre'],
                    record['year'],
                    f"${record['price']:.2f}",
                    record['stock']
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
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search and add matching records
        for record in self.records:
            if (query.lower() in record["artist"].lower() or
                query.lower() in record["album"].lower() or
                query.lower() in record["genre"].lower()):
                
                if self.is_owner:
                    self.tree.insert('', 'end', values=(
                        record['id'],
                        record['album'],
                        record['artist'],
                        record['genre'],
                        record['year'],
                        f"${record['price']:.2f}",
                        record['stock']
                    ))
                else:
                    self.tree.insert('', 'end', values=(
                        record['album'],
                        record['artist'],
                        record['genre'],
                        record['year'],
                        f"${record['price']:.2f}",
                        record['stock']
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
        self.form_entries['artist_entry'].delete(0, 'end')
        self.form_entries['artist_entry'].insert(0, values[2])
        
        self.form_entries['album_entry'].delete(0, 'end')
        self.form_entries['album_entry'].insert(0, values[1])
        
        self.form_entries['genre_entry'].delete(0, 'end')
        self.form_entries['genre_entry'].insert(0, values[3])
        
        self.form_entries['year_entry'].delete(0, 'end')
        self.form_entries['year_entry'].insert(0, values[4])
        
        self.form_entries['price_entry'].delete(0, 'end')
        self.form_entries['price_entry'].insert(0, str(values[5]).replace('$', ''))
        
        self.form_entries['stock_entry'].delete(0, 'end')
        self.form_entries['stock_entry'].insert(0, values[6])
    
    def add_record(self):
        """Add a new record"""
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
        
        # Create record
        record = {
            'id': len(self.records) + 1,
            'artist': data['artist'],
            'album': data['album'],
            'genre': data['genre'],
            'year': data['year'],
            'price': data['price'],
            'stock': data['stock'],
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to records
        self.records.append(record)
        self.save_records()
        self.refresh_records()
        self.clear_form()
        messagebox.showinfo("Success", "Record added successfully!")
    
    def update_record(self):
        """Update selected record"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to update")
            return
        
        record_id = self.tree.item(selection[0])['values'][0]
        
        # Find and update record
        for record in self.records:
            if record['id'] == record_id:
                # Get updated data
                record['artist'] = self.form_entries['artist_entry'].get().strip()
                record['album'] = self.form_entries['album_entry'].get().strip()
                record['genre'] = self.form_entries['genre_entry'].get().strip()
                
                try:
                    record['year'] = int(self.form_entries['year_entry'].get().strip())
                    record['price'] = float(self.form_entries['price_entry'].get().strip())
                    record['stock'] = int(self.form_entries['stock_entry'].get().strip())
                except ValueError:
                    messagebox.showerror("Error", "Invalid numeric values")
                    return
                
                self.save_records()
                self.refresh_records()
                messagebox.showinfo("Success", "Record updated successfully!")
                return
        
        messagebox.showerror("Error", "Record not found")
    
    def delete_record(self):
        """Delete selected record"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            return
        
        record_id = self.tree.item(selection[0])['values'][0]
        
        # Find and delete record
        for i, record in enumerate(self.records):
            if record['id'] == record_id:
                del self.records[i]
                self.save_records()
                self.refresh_records()
                self.clear_form()
                messagebox.showinfo("Success", "Record deleted successfully!")
                return
        
        messagebox.showerror("Error", "Record not found")
    
    def clear_form(self):
        """Clear the form"""
        for entry in self.form_entries.values():
            entry.delete(0, 'end')
    
    def add_to_cart(self):
        """Add selected item to cart"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to add to cart")
            return
        
        values = self.tree.item(selection[0])['values']
        
        # Find the actual record
        album = values[0]
        artist = values[1]
        
        record = None
        for r in self.records:
            if r['album'] == album and r['artist'] == artist:
                record = r
                break
        
        if not record:
            messagebox.showerror("Error", "Record not found")
            return
        
        # Check stock
        if record['stock'] <= 0:
            messagebox.showwarning("Out of Stock", "This item is out of stock")
            return
        
        # Ask for quantity
        quantity = simpledialog.askinteger("Quantity", 
                                         f"How many '{album}' would you like?\nAvailable: {record['stock']}",
                                         minvalue=1,
                                         maxvalue=record['stock'])
        
        if not quantity:
            return
        
        # Add to cart
        price = record['price']
        total = price * quantity
        
        # Check if item already in cart
        for item in self.cart:
            if item['record_id'] == record['id']:
                item['quantity'] += quantity
                item['total'] = item['quantity'] * price
                break
        else:
            self.cart.append({
                'record_id': record['id'],
                'item': f"{album} - {artist}",
                'quantity': quantity,
                'price': price,
                'total': total
            })
        
        # Update cart display
        self.update_cart_display()
        messagebox.showinfo("Added to Cart", f"Added {quantity} x '{album}' to cart")
    
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
        if not self.cart:
            messagebox.showinfo("Empty Cart", "Your cart is empty!")
            return
        
        # Update stock
        for cart_item in self.cart:
            for record in self.records:
                if record['id'] == cart_item['record_id']:
                    record['stock'] -= cart_item['quantity']
                    break
        
        self.save_records()
        
        # Show success message
        messagebox.showinfo("Order Placed", 
                          f"Thank you for your order!\n\nTotal: ${self.cart_total:.2f}\n\nYour records will be shipped soon.")
        
        # Clear cart
        self.cart = []
        self.update_cart_display()
        self.refresh_records()
    
    def export_to_csv(self):
        """Export records to CSV"""
        if not self.records:
            messagebox.showinfo("No Data", "No records to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Records to CSV"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'artist', 'album', 'genre', 'year', 'price', 'stock', 'date_added']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in self.records:
                    writer.writerow(record)
            
            messagebox.showinfo("Export Successful", f"Exported {len(self.records)} records to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def import_from_csv(self):
        """Import records from CSV"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Records from CSV"
        )
        
        if not filename:
            return
        
        try:
            imported_records = []
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Validate required fields
                    required_fields = ['artist', 'album', 'genre', 'year', 'price', 'stock']
                    if not all(field in row and row[field].strip() for field in required_fields):
                        continue
                    
                    # Convert data types
                    try:
                        record = {
                            'id': len(self.records) + len(imported_records) + 1,
                            'artist': row['artist'].strip(),
                            'album': row['album'].strip(),
                            'genre': row['genre'].strip(),
                            'year': int(row['year']),
                            'price': float(row['price']),
                            'stock': int(row['stock']),
                            'date_added': row.get('date_added', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }
                        imported_records.append(record)
                    except (ValueError, KeyError):
                        continue
            
            if imported_records:
                self.records.extend(imported_records)
                self.save_records()
                self.refresh_records()
                messagebox.showinfo("Import Successful", f"Imported {len(imported_records)} records")
            else:
                messagebox.showwarning("No Data", "No valid records found in the file")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {str(e)}")
    
    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            if self.logout_callback:
                self.logout_callback()