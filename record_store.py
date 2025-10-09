import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
from tkinter import filedialog
import json
import os
from datetime import datetime
from tkinter import PhotoImage
import webbrowser
import csv

# Color schemes
LIGHT_COLORS = {
    'primary': '#4a6fa5',
    'primary_light': '#6c8bc7',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'light_gray': '#f5f5f5',
    'dark': '#343a40',
    'dark_gray': '#666666',
    'white': '#ffffff',
    'gray': '#e9ecef',
    'bg': '#f8f9fa',
    'fg': '#212529',
    'entry_bg': '#ffffff',
    'tree_bg': '#ffffff',
    'tree_fg': '#212529',
    'tree_heading_bg': '#e9ecef',
    'tree_heading_fg': '#212529',
    'tree_selected_bg': '#e2e6ea',
    'tree_selected_fg': '#212529'
}

DARK_COLORS = {
    'primary': '#5a7bb5',
    'primary_light': '#7d9bd7',
    'secondary': '#858e96',
    'success': '#38b753',
    'danger': '#f14e63',
    'warning': '#ffd23f',
    'info': '#3db4c8',
    'light': '#2d2d2d',
    'light_gray': '#3d3d3d',
    'dark': '#e1e1e1',
    'dark_gray': '#a0a0a0',
    'white': '#2d2d2d',
    'gray': '#4d4d4d',
    'bg': '#1e1e1e',
    'fg': '#e1e1e1',
    'entry_bg': '#2d2d2d',
    'tree_bg': '#2d2d2d',
    'tree_fg': '#e1e1e1',
    'tree_heading_bg': '#3d3d3d',
    'tree_heading_fg': '#ffffff',
    'tree_selected_bg': '#4d4d4d',
    'tree_selected_fg': '#ffffff'
}

# Default to light mode
COLORS = LIGHT_COLORS.copy()

# Modern font styles
FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'subtitle': ('Segoe UI', 12),
    'button': ('Segoe UI', 10, 'bold'),
    'label': ('Segoe UI', 10, 'bold'),
    'entry': ('Segoe UI', 10),
    'status': ('Segoe UI', 9)
}

class ModernButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.style = ttk.Style()
        self.style.configure('Modern.TButton', 
                           font=FONTS['button'],
                           padding=6)
        self.configure(style='Modern.TButton')

class ModernEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **{'font': FONTS['entry'], **kwargs})

class ModernLabel(ttk.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **{'font': FONTS['label'], **kwargs})

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.window = tk.Toplevel(root)
        self.window.title("Login to VinylFlow")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Center the window
        window_width = 400
        window_height = 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Owner credentials (in a real app, these would be hashed and stored securely)
        self.owner_username = "FP"
        self.owner_password = "1539"
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="VinylFlow Login", font=FONTS['title']).pack(pady=(0, 30))
        
        # Username
        ttk.Label(main_frame, text="Username:", font=FONTS['label']).pack(anchor='w')
        self.username_entry = ttk.Entry(main_frame, font=FONTS['entry'], width=30)
        self.username_entry.pack(pady=(0, 15))
        
        # Password
        ttk.Label(main_frame, text="Password:", font=FONTS['label']).pack(anchor='w')
        self.password_entry = ttk.Entry(main_frame, font=FONTS['entry'], width=30, show="*")
        self.password_entry.pack(pady=(0, 30))
        
        # Login button
        ttk.Button(main_frame, 
                  text="Login as Owner", 
                  command=self.owner_login,
                  style='primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(main_frame,
                  text="Continue as Customer",
                  command=self.customer_login,
                  style='secondary.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Error message
        self.error_label = ttk.Label(main_frame, text="", foreground=COLORS['danger'])
        self.error_label.pack(pady=(20, 0))
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.owner_login())
        
        # Focus on username field
        self.username_entry.focus()
    
    def owner_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username == self.owner_username and password == self.owner_password:
            self.window.destroy()
            self.on_login_success(is_owner=True)
        else:
            self.error_label.config(text="Invalid username or password")
    
    def customer_login(self):
        self.window.destroy()
        self.on_login_success(is_owner=False)


class RecordStoreApp:
    def __init__(self, root, is_owner=False):
        self.root = root
        self.is_owner = is_owner
        self.root.title("VinylFlow - Record Store" + (" Manager" if is_owner else ""))
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Initialize theme
        self.dark_mode = False
        self.load_theme_preference()
        
        # Apply theme
        self.apply_theme()

        # Data storage
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.records_file = os.path.join(self.base_dir, "records_inventory.json")
        self.records = self.load_records()
        
        # Shopping cart for customers
        self.cart = []
        self.cart_total = 0.0

        # Create GUI
        self.create_gui()

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

    def export_to_csv(self):
        """Export inventory to CSV file"""
        if not self.records:
            messagebox.showinfo("No Data", "No records to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Inventory to CSV"
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

            messagebox.showinfo("Export Successful",
                              f"Exported {len(self.records)} records to {filename}")
            self.status_var.set(f"Exported {len(self.records)} records to CSV")

        except Exception as e:
            self.log_error(f"Error exporting to CSV: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def import_from_csv(self):
        """Import records from CSV file"""
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
                        messagebox.showwarning("Invalid Data",
                                             f"Skipping row with missing required fields: {row}")
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
                    except (ValueError, KeyError) as e:
                        messagebox.showwarning("Invalid Data",
                                             f"Skipping invalid row: {row}. Error: {str(e)}")
                        continue

            if imported_records:
                # Add imported records to existing records
                self.records.extend(imported_records)
                self.save_records()
                self.show_all_records()

                messagebox.showinfo("Import Successful",
                                  f"Imported {len(imported_records)} records from {filename}")
                self.status_var.set(f"Imported {len(imported_records)} records from CSV")
        except Exception as e:
            self.log_error(f"Error importing from CSV: {str(e)}")
            messagebox.showerror("Import Error", f"Failed to import data: {str(e)}")

    def show_statistics(self):
        """Display comprehensive statistics dashboard"""
        if not self.records:
            messagebox.showinfo("No Data", "No records available for statistics")
            return

        # Create statistics window
        stats_win = tk.Toplevel(self.root)
        stats_win.title("VinylFlow - Statistics Dashboard")
        stats_win.geometry("600x500")
        stats_win.resizable(False, False)
        stats_win.transient(self.root)
        stats_win.grab_set()

        # Center the window
        self.center_window(stats_win)

        # Main frame
        main_frame = ttk.Frame(stats_win, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame,
                              text="📊 Inventory Statistics",
                              font=('Segoe UI', 16, 'bold'),
                              foreground=COLORS['primary'])
        title_label.pack(pady=(0, 20))

        # Calculate statistics
        total_records = len(self.records)
        total_value = sum(record['price'] * record['stock'] for record in self.records)
        total_stock = sum(record['stock'] for record in self.records)
        avg_price = total_value / total_records if total_records > 0 else 0

        # Low stock items (stock <= 5)
        low_stock = [r for r in self.records if r['stock'] <= 5]
        out_of_stock = [r for r in self.records if r['stock'] == 0]

        # Genre distribution
        genres = {}
        for record in self.records:
            genre = record['genre']
            genres[genre] = genres.get(genre, 0) + 1

        # Most expensive item
        most_expensive = max(self.records, key=lambda x: x['price']) if self.records else None
        least_expensive = min(self.records, key=lambda x: x['price']) if self.records else None

        # Create statistics cards
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True)

        # Top row - Key metrics
        top_row = ttk.Frame(stats_frame)
        top_row.pack(fill=tk.X, pady=(0, 15))

        # Total Records
        self.create_stat_card(top_row, "📀 Total Records", str(total_records), COLORS['primary'])

        # Total Value
        self.create_stat_card(top_row, "💰 Total Value", f"${total_value:.2f}", COLORS['success'])

        # Total Stock
        self.create_stat_card(top_row, "📦 Total Stock", str(total_stock), COLORS['info'])

        # Average Price
        self.create_stat_card(top_row, "💵 Avg Price", f"${avg_price:.2f}", COLORS['warning'])

        # Second row - Alerts
        alerts_frame = ttk.LabelFrame(stats_frame, text="⚠️ Alerts", padding=10)
        alerts_frame.pack(fill=tk.X, pady=(0, 15))

        alerts_text = f"Low Stock Items: {len(low_stock)}\n"
        alerts_text += f"Out of Stock: {len(out_of_stock)}\n"

        alerts_label = ttk.Label(alerts_frame, text=alerts_text, justify=tk.LEFT)
        alerts_label.pack(anchor='w')

        # Third row - Genre distribution
        genre_frame = ttk.LabelFrame(stats_frame, text="🎵 Genre Distribution", padding=10)
        genre_frame.pack(fill=tk.BOTH, expand=True)

        # Create a text widget for genre stats
        genre_text = tk.Text(genre_frame, height=8, width=50, font=('Segoe UI', 9))
        genre_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(genre_frame, command=genre_text.yview)
        genre_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insert genre statistics
        genre_text.insert(tk.END, "Genre Distribution:\n\n")
        for genre, count in sorted(genres.items()):
            percentage = (count / total_records) * 100
            genre_text.insert(tk.END, f"{genre}: {count} ({percentage:.1f}%)\n")

        genre_text.insert(tk.END, f"\nMost Popular Genre: {max(genres, key=genres.get)} ({genres[max(genres, key=genres.get)]} records)")
        genre_text.config(state=tk.DISABLED)

        # Bottom row - Price range info
        price_frame = ttk.LabelFrame(stats_frame, text="💰 Price Analysis", padding=10)
        price_frame.pack(fill=tk.X, pady=(15, 0))

        if most_expensive and least_expensive:
            price_text = f"Most Expensive: ${most_expensive['price']:.2f} - {most_expensive['artist']} - {most_expensive['album']}\n"
            price_text += f"Least Expensive: ${least_expensive['price']:.2f} - {least_expensive['artist']} - {least_expensive['album']}\n"
            price_text += f"Price Range: ${least_expensive['price']:.2f} - ${most_expensive['price']:.2f}"

            price_label = ttk.Label(price_frame, text=price_text, justify=tk.LEFT)
            price_label.pack(anchor='w')

        # Close button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame,
                  text="Close",
                  command=stats_win.destroy,
                  style='primary.TButton').pack(side=tk.RIGHT)

    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card widget"""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding=10)
        card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        title_label = ttk.Label(card_frame, text=title, font=('Segoe UI', 10, 'bold'))
        title_label.pack(anchor='center')

        value_label = ttk.Label(card_frame,
                              text=value,
                              font=('Segoe UI', 14, 'bold'),
                              foreground=color)
        value_label.pack(anchor='center', pady=(5, 0))

        return card_frame

    def create_gui(self):
        """Create the main GUI with different views for owners and customers"""
        # Create a main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header with user info
        self.create_header()
        
        # Create the appropriate view based on user type
        if self.is_owner:
            self.create_owner_view()
        else:
            self.create_customer_view()
    
    def load_theme_preference(self):
        """Load theme preference from config file"""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vinylflow_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.dark_mode = config.get('dark_mode', False)
            except:
                self.dark_mode = False
        else:
            self.dark_mode = False

    def save_theme_preference(self):
        """Save theme preference to config file"""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vinylflow_config.json')
        try:
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            
            config['dark_mode'] = self.dark_mode
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving theme preference: {e}")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        self.save_theme_preference()
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to the application"""
        global COLORS
        
        # Update global COLORS
        COLORS.update(DARK_COLORS if self.dark_mode else LIGHT_COLORS)
        
        # Configure root window
        self.root.configure(bg=COLORS['bg'])
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Base styles
        self.style.configure('.', background=COLORS['bg'], foreground=COLORS['fg'])
        
        # Frame
        self.style.configure('TFrame', background=COLORS['bg'])
        
        # Labels
        self.style.configure('TLabel', 
                           background=COLORS['bg'], 
                           foreground=COLORS['fg'],
                           font=FONTS['label'])
        
        # Buttons
        self.style.configure('TButton',
                           font=FONTS['button'],
                           background=COLORS['secondary'],
                           foreground=COLORS['white'] if self.dark_mode else COLORS['dark'],
                           borderwidth=0)
        
        # Treeview
        self.style.configure('Treeview',
                           background=COLORS['tree_bg'],
                           foreground=COLORS['tree_fg'],
                           fieldbackground=COLORS['tree_bg'],
                           rowheight=25,
                           font=FONTS['entry'])
        
        self.style.configure('Treeview.Heading',
                           background=COLORS['tree_heading_bg'],
                           foreground=COLORS['tree_heading_fg'],
                           font=FONTS['label'])
        
        self.style.map('Treeview',
                      background=[('selected', COLORS['tree_selected_bg'])],
                      foreground=[('selected', COLORS['tree_selected_fg'])])
        
        # Entry
        self.style.configure('TEntry',
                           fieldbackground=COLORS['entry_bg'],
                           foreground=COLORS['fg'],
                           insertcolor=COLORS['fg'],
                           borderwidth=1)
        
        # Custom button styles
        for color in ['primary', 'success', 'danger', 'warning', 'info', 'secondary']:
            self.style.configure(f'{color}.TButton',
                               foreground=COLORS['white'],
                               background=COLORS[color],
                               borderwidth=0,
                               focuscolor=COLORS['light'])
            
            self.style.map(f'{color}.TButton',
                         foreground=[('active', COLORS['white']), ('!disabled', COLORS['white'])],
                         background=[('active', COLORS[color]), ('!disabled', COLORS[color])])
        
        # Update any existing widgets
        if hasattr(self, 'main_container'):
            self.main_container.configure(style='TFrame')
        if hasattr(self, 'header'):
            self.header.configure(bg=COLORS['primary'])
        if hasattr(self, 'content_frame'):
            self.content_frame.configure(style='TFrame')

    def create_header(self):
        """Create the header with gradient background and user info"""
        # Header with gradient background
        self.header = tk.Canvas(self.main_container, height=80, highlightthickness=0, bg=COLORS['primary'])
        self.header.pack(fill=tk.X)
        
        # Create gradient from dark to light blue
        for i in range(80):
            r = int(42 + (i/80) * 20)
            g = int(111 + (i/80) * 50)
            b = int(165 + (i/80) * 30)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.header.create_line(0, i, 2000, i, fill=color, width=1)
        
        # Title with vinyl icons
        title_frame = ttk.Frame(self.header, style='TFrame')
        title_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Create a frame for the title row
        title_row = ttk.Frame(title_frame)
        title_row.pack()
        
        # Left vinyl icon
        ttk.Label(title_row, 
                 text="💿", 
                 font=('Segoe UI Emoji', 28),
                 background=COLORS['primary']).pack(side=tk.LEFT, padx=(0, 10))
        
        # Main title
        self.title_label = ttk.Label(title_row, 
                                  text="VinylFlow" + (" Manager" if self.is_owner else ""),
                                  font=FONTS['title'],
                                  foreground=COLORS['white'],
                                  background=COLORS['primary'])
        self.title_label.pack(side=tk.LEFT)
        
        # Right vinyl icon
        ttk.Label(title_row, 
                 text="💿", 
                 font=('Segoe UI Emoji', 28),
                 background=COLORS['primary']).pack(side=tk.LEFT, padx=(10, 0))
        
        # User info frame
        user_frame = ttk.Frame(self.header, style='TFrame')
        user_frame.place(relx=0.95, rely=0.5, anchor='e')
        
        # Theme toggle button
        self.theme_btn = ttk.Button(user_frame,
                                  text="🌙" if not self.dark_mode else "☀️",
                                  command=self.toggle_theme,
                                  style='info.TButton',
                                  width=3)
        self.theme_btn.pack(side=tk.RIGHT, padx=5)
        
        # Display user type
        user_type = "Owner" if self.is_owner else "Customer"
        self.user_label = ttk.Label(user_frame, 
                                 text=f"Logged in as: {user_type}",
                                 foreground=COLORS['white'],
                                 background=COLORS['primary'],
                                 font=FONTS['label'])
        self.user_label.pack(anchor='e')
        
        # Logout button
        ttk.Button(user_frame,
                  text="Logout",
                  command=self.logout,
                  style='danger.TButton').pack(anchor='e', pady=(5, 0))
    
    def create_owner_view(self):
        """Create the owner's view with full management capabilities"""
        # Content frame
        content_frame = ttk.Frame(self.main_container, padding="20 15")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Add new record
        left_frame = ttk.LabelFrame(content_frame, 
                                  text="  Add New Record  ", 
                                  padding="20 15",
                                  style='Card.TLabelframe')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Form fields
        form_elements = [
            ("Artist:", "artist_entry"),
            ("Album:", "album_entry"),
            ("Genre:", "genre_entry"),
            ("Year:", "year_entry"),
            ("Price ($):", "price_entry"),
            ("Stock:", "stock_entry")
        ]
        
        for label_text, entry_name in form_elements:
            row_frame = ttk.Frame(left_frame)
            row_frame.pack(fill=tk.X, pady=4)
            
            ttk.Label(row_frame, text=label_text, width=10, anchor='e').pack(side=tk.LEFT, padx=(0, 10))
            entry = ttk.Entry(row_frame, font=FONTS['entry'], width=30)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            setattr(self, entry_name, entry)
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, 
                  text="➕ Add Record", 
                  command=self.add_record,
                  style='success.TButton').pack(side=tk.LEFT, expand=True, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="Clear Form",
                  command=self.clear_form,
                  style='warning.TButton').pack(side=tk.LEFT, expand=True)
        
        # Right panel - Records list
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Search bar
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=FONTS['entry'])
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(search_frame,
                  text="🔍 Search",
                  command=self.search_records,
                  style='info.TButton').pack(side=tk.LEFT)
        
        # Records treeview
        columns = ("ID", "Album", "Artist", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings', selectmode='browse')
        
        # Configure columns
        self.tree.column("ID", width=40, anchor='center')
        self.tree.column("Album", width=150)
        self.tree.column("Artist", width=120)
        self.tree.column("Genre", width=80)
        self.tree.column("Year", width=60, anchor='center')
        self.tree.column("Price", width=80, anchor='e')
        self.tree.column("Stock", width=60, anchor='center')
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to view details
        self.tree.bind('<Double-1>', self.view_details)
        
        # Action buttons frame
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame,
                  text="🔄 Refresh",
                  command=self.show_all_records,
                  style='info.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(action_frame,
                  text="📊 Statistics",
                  command=self.show_statistics,
                  style='info.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame,
                  text="📤 Export CSV",
                  command=self.export_to_csv,
                  style='success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame,
                  text="📥 Import CSV",
                  command=self.import_from_csv,
                  style='warning.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame,
                  text="✏️ Update Stock",
                  command=self.update_stock,
                  style='primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame,
                  text="🗑️ Delete",
                  command=self.delete_record,
                  style='danger.TButton').pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(right_frame, 
                             textvariable=self.status_var,
                             relief=tk.SUNKEN, 
                             anchor=tk.W,
                             style='TLabel')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Show all records initially
        self.show_all_records()
    
    def create_customer_view(self):
        """Create the customer view with shopping functionality"""
        # Main content frame
        content_frame = ttk.Frame(self.main_container, padding="20 15")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Records list
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Search bar with modern styling
        search_container = ttk.Frame(left_frame)
        search_container.pack(fill=tk.X, pady=(0, 15))
        
        # Search frame with rounded corners
        search_frame = ttk.Frame(search_container, style='Card.TFrame')
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search icon
        search_icon = ttk.Label(search_frame, text="🔍", font=('Segoe UI Emoji', 12))
        search_icon.pack(side=tk.LEFT, padx=(10, 5))
        
        # Search entry with placeholder
        self.search_entry = ttk.Entry(
            search_frame, 
            font=FONTS['entry'],
            style='Search.TEntry'
        )
        self.search_entry.insert(0, "Search by artist, album, or genre...")
        self.search_entry.bind('<FocusIn>', 
            lambda e: self.search_entry.delete('0', 'end') 
            if self.search_entry.get() == "Search by artist, album, or genre..." 
            else None
        )
        self.search_entry.bind('<FocusOut>', 
            lambda e: self.search_entry.insert(0, "Search by artist, album, or genre...") 
            if not self.search_entry.get() 
            else None
        )
        self.search_entry.bind('<Return>', lambda e: self.search_records())
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Search button with modern styling
        search_btn = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_records,
            style='primary.TButton',
            width=10
        )
        search_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Records treeview with proper column configuration
        self.tree = ttk.Treeview(left_frame, 
                               columns=("album", "artist", "genre", "year", "price", "stock"),
                               show='headings', 
                               selectmode='browse')
        
        # Define column properties
        columns_config = {
            'album': {'text': 'Album', 'width': 200, 'anchor': 'w'},
            'artist': {'text': 'Artist', 'width': 150, 'anchor': 'w'},
            'genre': {'text': 'Genre', 'width': 100, 'anchor': 'center'},
            'year': {'text': 'Year', 'width': 80, 'anchor': 'center'},
            'price': {'text': 'Price', 'width': 100, 'anchor': 'center'},
            'stock': {'text': 'In Stock', 'width': 80, 'anchor': 'center'}
        }
        
        # Configure columns
        for col, config in columns_config.items():
            self.tree.heading(col, text=config['text'], 
                            command=lambda c=col: self.sort_by_column(c),
                            anchor=config['anchor'])
            self.tree.column(col, width=config['width'], 
                           anchor=config['anchor'],
                           stretch=tk.YES if col in ['album', 'artist'] else tk.NO)
        
        # Configure styles for treeview
        style = ttk.Style()
        style.configure('Treeview', 
                       rowheight=25,  # Slightly taller rows for better readability
                       font=('Segoe UI', 9))
        
        style.configure('Treeview.Heading', 
                      font=('Segoe UI', 9, 'bold'),
                      background=COLORS['primary'],
                      foreground='white',
                      padding=(5, 3, 5, 3))
        
        # Style for alternating row colors
        style.map('Treeview',
                 background=[('selected', COLORS['primary_light'])],
                 foreground=[('selected', 'black')])
            
        # Configure tags for alternating row colors
        self.tree.tag_configure('evenrow', background='#f5f5f5')
        self.tree.tag_configure('oddrow', background='#ffffff')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to view details
        self.tree.bind('<Double-1>', self.view_details)
        
        # Right panel - Shopping cart
        right_frame = ttk.LabelFrame(content_frame, 
                                   text="  Shopping Cart  ", 
                                   padding="15 10",
                                   style='Card.TLabelframe',
                                   width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        
        # Cart items frame with scrollbar
        cart_items_frame = ttk.Frame(right_frame)
        cart_items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.cart_tree = ttk.Treeview(cart_items_frame, 
                                    columns=("Item", "Qty", "Price"), 
                                    show='headings',
                                    height=8)
        self.cart_tree.heading("Item", text="Item")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Price", text="Price")
        self.cart_tree.column("Item", width=150)
        self.cart_tree.column("Qty", width=50, anchor='center')
        self.cart_tree.column("Price", width=80, anchor='e')
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Cart total
        total_frame = ttk.Frame(right_frame)
        total_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(total_frame, 
                 text="Total:", 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        self.total_label = ttk.Label(total_frame, 
                                   text="$0.00", 
                                   font=('Segoe UI', 10, 'bold'),
                                   foreground=COLORS['primary'])
        self.total_label.pack(side=tk.RIGHT)
        
        # Action buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Add to Cart button
        add_to_cart_btn = ttk.Button(
            button_frame,
            text="🛒 Add to Cart",
            command=self.add_to_cart,
            style='success.TButton'
        )
        add_to_cart_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Clear Cart button
        clear_cart_btn = ttk.Button(
            button_frame,
            text="❌ Clear Cart",
            command=self.clear_cart,
            style='danger.TButton'
        )
        clear_cart_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Checkout button
        checkout_btn = ttk.Button(
            button_frame,
            text="💳 Checkout",
            command=self.checkout,
            style='primary.TButton'
        )
        checkout_btn.pack(fill=tk.X)
        
        # Status bar with better styling
        status_frame = ttk.Frame(left_frame, style='Card.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Status label with better styling
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.FLAT,
            anchor=tk.W,
            padding=(10, 5, 10, 5),
            style='Status.TLabel'
        )
        status_bar.pack(fill=tk.X, expand=True)
        
        # Configure status bar style
        style = ttk.Style()
        style.configure('Status.TLabel',
                      background=COLORS['light_gray'],
                      foreground=COLORS['dark_gray'],
                      font=('Segoe UI', 9),
                      padding=5)
        
        # Show all records initially
        self.show_all_records()
    
    def log_error(self, message):
        """
        Log errors to a file for debugging and support purposes.
{{ ... }}
        
        Args:
            message (str): The error message to log
        """
        try:
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"Failed to write to error log: {e}")
    
    def add_to_cart(self):
        """
        Add a selected item to the shopping cart with comprehensive validation.
        
        This method handles the entire process of adding an item to the shopping cart,
        including user input validation, stock checking, and cart updates. It follows
        a strict validation process to ensure data integrity and provides detailed
        feedback to the user at each step.
        
        Process:
        1. Validates that an item is selected in the treeview
        2. Extracts and validates the item data
        3. Checks stock availability
        4. Prompts for quantity with proper validation
        5. Updates the cart with the selected item(s)
        
        Error Handling:
        - No selection made
        - Invalid item data
        - Out of stock items
        - Invalid quantity input
        - Database inconsistencies
        
        Returns:
            None
        """
        try:
            # Validate that an item is selected
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning(
                    "Selection Required",
                    "Please select an item from the catalog to add to your cart.",
                    icon='warning'
                )
                return
                
            # Safely extract item data with validation
            try:
                item = self.tree.item(selected[0], 'values')
                if not item or len(item) < 7:  # Expected: id, artist, album, genre, year, price, stock
                    raise ValueError("Incomplete item data")
                    
                # Unpack and validate all fields
                item_id = str(item[0]).strip()
                artist = str(item[1]).strip()
                album = str(item[2]).strip()
                genre = str(item[3]).strip()
                year = str(item[4]).strip()
                price_str = str(item[5]).replace('£', '').replace('$', '').strip()
                stock_str = str(item[6]).strip()
                
                # Validate required fields
                if not all([item_id, artist, album, price_str, stock_str]):
                    raise ValueError("Required fields are missing")
                    
                # Convert and validate numeric fields
                try:
                    price = float(price_str)
                    stock = int(stock_str)
                    if price < 0 or stock < 0:
                        raise ValueError("Negative values not allowed")
                except (ValueError, TypeError) as e:
                    raise ValueError("Invalid numeric format in item data") from e
                    
            except (IndexError, ValueError) as e:
                self.log_error(f"Invalid item data: {str(e)}")
                messagebox.showerror(
                    "Data Error",
                    "The selected item contains invalid data. Please try another item or contact support.",
                    icon='error'
                )
                return
            
            # Check stock availability
            if stock <= 0:
                messagebox.showinfo(
                    "Out of Stock",
                    f"Sorry, '{album}' by {artist} is currently out of stock.\n"
                    "Please check back later or browse our other items.",
                    icon='info'
                )
                return
                
            # Get quantity from user with validation
            try:
                quantity = simpledialog.askinteger(
                    "Quantity Selection",
                    f"How many '{album}' would you like to add to cart?\n"
                    f"(Available: {stock} in stock)",
                    parent=self.root,
                    minvalue=1,
                    maxvalue=stock
                )
                
                if not quantity:  # User cancelled
                    return
                    
                if quantity > stock:
                    raise ValueError("Requested quantity exceeds available stock")
                    
            except ValueError as e:
                self.log_error(f"Invalid quantity input: {str(e)}")
                messagebox.showerror(
                    "Invalid Quantity",
                    f"Please enter a valid quantity between 1 and {stock}",
                    icon='error'
                )
                return
                
            # Add item to cart
            self._add_item_to_cart(item_id, artist, album, price, quantity)
            
            # Update stock display
            self.show_all_records()
            
        except Exception as e:
            self.log_error(f"Unexpected error in add_to_cart: {str(e)}")
            messagebox.showerror(
                "System Error",
                "An unexpected error occurred. Please try again or contact support.",
                icon='error'
            )
    
    def _add_item_to_cart(self, item_id, artist, album, price, quantity):
        """
        Helper method to add an item to the cart with the specified quantity.
        
        Args:
            item_id (str): Unique identifier for the item
            artist (str): Artist name
            album (str): Album title

        # Dark/Light mode setting
        self.dark_mode = tk.BooleanVar(value=False)
        self.dark_mode.set(self.get_config('dark_mode', False))
            price (float): Item price
            quantity (int): Quantity to add
        """
        try:
            total_price = price * quantity
            
            # Check if item already exists in cart
            item_found = False
            for child in self.cart_tree.get_children():
                values = self.cart_tree.item(child, 'values')
                if values and values[0] == f"{album} - {artist}":
                    # Update existing item
                    current_qty = int(values[1])
                    current_total = float(values[2].replace('$', '').replace(',', ''))
                    self.cart_tree.item(child, values=(
                        f"{album} - {artist}",
                        current_qty + quantity,
                        f"${(current_total + total_price):.2f}"
                    ))
                    item_found = True
                    break
                    
            if not item_found:
                # Add new item
                self.cart_tree.insert('', 'end', values=(
                    f"{album} - {artist}",
                    quantity,
                    f"${total_price:.2f}"
                ))
            
            # Update cart total and show success message
            self.update_cart_total()
            messagebox.showinfo(
                "Item Added",
                f"Added {quantity} x '{album}' to your cart.",
                icon='info'
            )
            
        except Exception as e:
            self.log_error(f"Error adding item to cart: {str(e)}")
            raise
            
        # Ask for quantity
        quantity = simpledialog.askinteger("Quantity", 
                                         f"How many '{album}' would you like to add to cart?\n(Max: {stock})",
                                         parent=self.root,
                                         minvalue=1,
                                         maxvalue=int(stock))
        
        if quantity:
            # Add to cart
            item_price = float(price.replace('$', ''))
            total_price = item_price * quantity
            
            # Check if item already in cart
            for child in self.cart_tree.get_children():
                cart_item = self.cart_tree.item(child, 'values')
                if cart_item and cart_item[0].startswith(album):
                    # Update existing item
                    current_qty = int(cart_item[1])
                    current_total = float(cart_item[2].replace('$', ''))
                    self.cart_tree.item(child, values=(
                        f"{album} - {artist}",
                        current_qty + quantity,
                        f"${current_total + total_price:.2f}"
                    ))
                    break
            else:
                # Add new item
                self.cart_tree.insert('', 'end', values=(
                    f"{album} - {artist}",
                    quantity,
                    f"${total_price:.2f}"
                ))
            
            # Update cart total
            self.update_cart_total()
            messagebox.showinfo("Success", f"Added {quantity} x {album} to cart")
            
    def update_cart_total(self):
        """Update the cart total amount"""
        total = 0.0
        for child in self.cart_tree.get_children():
            price = float(self.cart_tree.item(child, 'values')[2].replace('$', ''))
            total += price
        
        self.cart_total = total
        self.total_label.config(text=f"${total:.2f}")
        
    def clear_cart(self):
        """Clear all items from the shopping cart"""
        if messagebox.askyesno("Clear Cart", "Are you sure you want to clear your cart?"):
            for item in self.cart_tree.get_children():
                self.cart_tree.delete(item)
            self.update_cart_total()
    
    def checkout(self):
        """Process the checkout"""
        if not self.cart_tree.get_children():
            messagebox.showinfo("Cart Empty", "Your cart is empty!")
            return
            
        # In a real app, this would process payment
        # For now, just show a success message
        messagebox.showinfo("Order Placed!", 
                          f"Thank you for your order!\n\nTotal: ${self.cart_total:.2f}\n\nYour records will be shipped soon.")
        
        # Update stock and clear cart
        self.update_stock_from_cart()
        self.clear_cart()
        self.show_all_records()
    
    def update_stock_from_cart(self):
        """Update stock levels after checkout"""
        # This is a simplified version - in a real app, you'd want to handle this more carefully
        # to prevent race conditions if multiple users are shopping at the same time
        
        # Load current records
        records = self.load_records()
        
        # For each item in cart, update the stock
        for item in self.cart_tree.get_children():
            values = self.cart_tree.item(item, 'values')
            item_name = values[0].split(' - ')[0]  # Get album name
            qty = int(values[1])
            
            # Find and update the record
            for record in records:
                if record['album'] == item_name:
                    record['stock'] = str(int(record['stock']) - qty)
                    break
        
        # Save updated records
        with open(self.records_file, 'w') as f:
            json.dump(records, f, indent=4)
    
    def logout(self):
        """Log out the current user and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            main()  # Restart the application
        title_label.pack(side=tk.LEFT)
        
        # Right vinyl icon
        ttk.Label(title_row, 
                 text="💿", 
                 font=('Segoe UI Emoji', 28),
                 background=COLORS['primary']).pack(side=tk.LEFT, padx=(10, 0))
        
        # Subtitle
        subtitle_label = ttk.Label(title_frame,
                                 text="Record Store Management System",
                                 font=FONTS['subtitle'],
                                 foreground=COLORS['light'],
                                 background=COLORS['primary'])
        subtitle_label.pack()
        
        # Main content area with padding
        content_frame = ttk.Frame(main_container, padding="20 15")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Add new record with card-like appearance
        left_frame = ttk.LabelFrame(content_frame, 
                                  text="  Add New Record  ", 
                                  padding="20 15",
                                  style='Card.TLabelframe')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Form fields with modern styling
        form_elements = [
            ("Artist:", "artist_entry"),
            ("Album:", "album_entry"),
            ("Genre:", "genre_entry"),
            ("Year:", "year_entry"),
            ("Price ($):", "price_entry"),
            ("Stock:", "stock_entry")
        ]
        
        for i, (label_text, entry_name) in enumerate(form_elements):
            # Create a frame for each form row
            row_frame = ttk.Frame(left_frame)
            row_frame.pack(fill=tk.X, pady=4)
            
            # Label with consistent width
            label = ttk.Label(row_frame, text=label_text, width=10, anchor='e')
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Modern entry field with placeholder text
            entry = ttk.Entry(row_frame, font=FONTS['entry'], width=30)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            setattr(self, entry_name, entry)

        # Buttons with modern styling
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Primary action button
        add_btn = ttk.Button(button_frame, 
                           text="➕ Add Record", 
                           command=self.add_record,
                           style='success.TButton')
        add_btn.pack(side=tk.LEFT, expand=True, padx=(0, 5))
        
        # Secondary action button
        clear_btn = ttk.Button(button_frame, 
                             text="🗑️ Clear Form", 
                             command=self.clear_form,
                             style='secondary.TButton')
        clear_btn.pack(side=tk.LEFT, expand=True, padx=(5, 0))

        # Right panel - Search and view with card-like appearance
        right_frame = ttk.LabelFrame(content_frame, 
                                   text="  Search & View Records  ", 
                                   padding="20 15",
                                   style='Card.TLabelframe')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Modern search bar with icon
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search icon and entry with rounded corners
        search_container = ttk.Frame(search_frame)
        search_container.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Search icon
        search_icon = ttk.Label(search_container, text="🔍", width=3)
        search_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # Search entry with placeholder
        self.search_entry = ttk.Entry(search_container, font=FONTS['entry'])
        self.search_entry.insert(0, "Search by artist, album, or genre...")
        self.search_entry.bind('<FocusIn>', lambda e: self.search_entry.delete('0', 'end') if self.search_entry.get() == "Search by artist, album, or genre..." else None)
        self.search_entry.bind('<FocusOut>', lambda e: self.search_entry.insert(0, "Search by artist, album, or genre...") if not self.search_entry.get() else None)
        self.search_entry.bind('<Return>', lambda e: self.search_records())
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Search and show all buttons
        search_btn = ttk.Button(search_frame, 
                              text="Search", 
                              command=self.search_records,
                              style='info.TButton')
        search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        show_all_btn = ttk.Button(search_frame, 
                                text="Show All", 
                                command=self.show_all_records,
                                style='secondary.TButton')
        show_all_btn.pack(side=tk.LEFT)

        # Modern treeview with better styling
        columns = ("ID", "Artist", "Album", "Genre", "Year", "Price", "Stock")
        
        # Create a frame for the treeview and scrollbar
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview",
                      background=COLORS['white'],
                      foreground=COLORS['dark'],
                      rowheight=30,
                      fieldbackground=COLORS['white'],
                      borderwidth=0)
        style.map('Treeview', background=[('selected', COLORS['primary'])], 
                                     foreground=[('selected', COLORS['white'])])
        
        # Create the treeview
        self.tree = ttk.Treeview(tree_frame, 
                                columns=columns, 
                                show="headings",
                                selectmode='browse',
                                style='Custom.Treeview')
        
        # Configure treeview columns and headings
        for col in columns:
            self.tree.heading(col, text=col, 
                            command=lambda c=col: self.sort_by_column(c),
                            anchor='center')
            self.tree.column(col, width=100, anchor='center')
        
        # Adjust specific column widths
        self.tree.column("ID", width=40)
        self.tree.column("Artist", width=150)
        self.tree.column("Album", width=150)
        self.tree.column("Genre", width=100)
        self.tree.column("Year", width=60)
        self.tree.column("Price", width=80)
        self.tree.column("Stock", width=60)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add hover effect
        self.tree.bind('<Motion>', self.on_tree_hover)
        
        # Add double-click to view details
        self.tree.bind('<Double-1>', lambda e: self.view_details())

        # Modern action buttons with icons
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Action buttons with icons and consistent styling
        actions = [
            ("📦 Update Stock", self.update_stock, 'primary'),
            ("👁️ View Details", self.view_details, 'info'),
            ("🗑️ Delete Record", self.delete_record, 'danger')
        ]
        
        for text, command, style in actions:
            btn = ttk.Button(action_frame, 
                           text=text, 
                           command=command,
                           style=f'{style}.TButton')
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Modern status bar
        status_bar = ttk.Frame(self.root, style='Status.TFrame')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Status message with icon
        self.status_var = tk.StringVar()
        self.status_var.set("🟢 Ready")
        
        status_label = ttk.Label(status_bar, 
                               textvariable=self.status_var,
                               font=FONTS['status'],
                               background=COLORS['dark'],
                               foreground=COLORS['light'],
                               padding=(10, 5))
        status_label.pack(fill=tk.X)
        
        # Add custom styles for status bar
        self.style.configure('Status.TFrame', background=COLORS['dark'])
        
        # Add a subtle shadow effect to the status bar
        shadow = ttk.Frame(self.root, style='Shadow.TFrame')
        shadow.place(relx=0, rely=1, relwidth=1, height=2, anchor='sw')
        self.style.configure('Shadow.TFrame', background=COLORS['secondary'])
        
        # Add a subtle shadow to the header
        header_shadow = ttk.Frame(main_container, style='HeaderShadow.TFrame')
        header_shadow.place(relx=0, rely=80, relwidth=1, height=3, anchor='nw')
        self.style.configure('HeaderShadow.TFrame', background=COLORS['secondary'])
        
        # Add a subtle animation for status updates
        self.after_id = None

        # Load initial data
        self.show_all_records()

    def on_tree_hover(self, event):
        """Change cursor to hand when hovering over treeview items"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            self.tree.config(cursor="hand2")
        else:
            self.tree.config(cursor="")
    
    def add_record(self):
        """Add a new record to inventory with validation"""
        # Get values from form
        fields = {
            'artist': self.artist_entry.get().strip(),
            'album': self.album_entry.get().strip(),
            'genre': self.genre_entry.get().strip(),
            'year': self.year_entry.get().strip(),
            'price': self.price_entry.get().strip(),
            'stock': self.stock_entry.get().strip()
        }
        
        # Validate required fields
        for field, value in fields.items():
            if not value:
                self.highlight_field(field)
                self.update_status(f"Please fill in the {field} field", 'error')
                return
        
        # Validate numeric fields
        try:
            price = float(fields['price'])
            stock = int(fields['stock'])
            year = int(fields['year'])
            
            if year < 1900 or year > datetime.now().year + 1:
                raise ValueError("Invalid year")
                
            if price <= 0 or stock < 0:
                raise ValueError("Price and stock must be positive numbers")
                
        except ValueError as e:
            self.update_stock("Invalid input: " + str(e), 'error')
            return

        # Create new record
        record = {
            "id": len(self.records) + 1,
            "artist": fields['artist'],
            "album": fields['album'],
            "genre": fields['genre'],
            "year": year,
            "price": price,
            "stock": stock,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Add to records and update UI
        self.records.append(record)
        self.save_records()
        self.clear_form()
        self.show_all_records()
        self.update_status(f"Successfully added: {fields['artist']} - {fields['album']}", 'success')
        
        # Auto-scroll to the new record
        self.tree.see(self.tree.get_children()[-1])

    def clear_form(self):
        """Clear the input form"""
        self.artist_entry.delete(0, tk.END)
        self.album_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)

    def show_all_records(self):
        """
        Display all records in the treeview with proper formatting and alignment.
        
        This method populates the treeview with all records from the inventory,
        applying proper formatting for different data types and ensuring correct
        alignment in the treeview columns.
        """
        try:
            print(f"Loading {len(self.records)} records...")  # Debug print
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if not self.records:
                print("No records to display")  # Debug print
                if hasattr(self, 'status_var'):
                    self.status_var.set("No records found")
                return
            
            # Add records with proper formatting
            for idx, record in enumerate(self.records):
                try:
                    # Format values appropriately
                    values = (
                        str(record.get("album", "")),      # Album name
                        str(record.get("artist", "")),     # Artist
                        str(record.get("genre", "")),      # Genre
                        str(record.get("year", "")),       # Year
                        f"${float(record.get('price', 0)):.2f}",  # Price with 2 decimal places
                        str(record.get("stock", 0))         # Stock quantity
                    )
                    
                    # Insert the record with alternating row colors
                    tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                    self.tree.insert("", tk.END, values=values, tags=(tag,))
                    
                except Exception as e:
                    print(f"Error displaying record {record.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Update status bar
            if hasattr(self, 'status_var'):
                self.status_var.set(f"Displaying {len(self.records)} records")
            
            print("Records loaded successfully")  # Debug print
            
        except Exception as e:
            error_msg = f"Error displaying records: {str(e)}"
            print(error_msg)  # Debug print
            self.log_error(error_msg)
            if hasattr(self, 'status_var'):
                self.status_var.set("Error loading records")
            else:
                print("Status bar not available")  # Debug print
                messagebox.showerror(
                    "Display Error",
                    "An error occurred while loading records.\nPlease check the error log for details.",
                    icon='error'
                )

    def search_records(self):
        """Search records based on search term"""
        search_term = self.search_entry.get().strip().lower()

        if not search_term or search_term == "search by artist, album, or genre...":
            self.show_all_records()
            return

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Search and add matching records
        for record in self.records:
            if (search_term in record["artist"].lower() or
                search_term in record["album"].lower() or
                search_term in record["genre"].lower()):
                self.tree.insert("", tk.END, values=(
                    record["id"],
                    record["artist"],
                    record["album"],
                    record["genre"],
                    record["year"],
                    f"${record['price']:.2f}",
                    record["stock"]
                ))

        self.status_var.set(f"Found {len(self.tree.get_children())} matching records")

    def sort_by_column(self, col):
        """
        Sort the treeview by the specified column with visual feedback.
        
        This method handles sorting of different data types including:
        - Text (artist, album, genre)
        - Numeric (price, year, stock)
        - Currency (formatted numbers with $)
        
        Args:
            col (str): The column identifier to sort by
            
        The method toggles between ascending and descending order on subsequent clicks.
        Visual indicators (↑/↓) are shown in the column header to indicate sort direction.
        """
        try:
            # Get all items from the treeview
            items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
            
            # Determine if we need to sort in reverse (toggle on subsequent clicks)
            current_sort = getattr(self, f'_current_sort_{col}', None)
            reverse_sort = not current_sort if current_sort is not None else False
            
            # Store the current sort direction for this column
            setattr(self, f'_current_sort_{col}', reverse_sort)
            
            # Clear previous sort indicators
            for c in self.tree['columns']:
                heading = self.tree.heading(c)
                heading_text = heading['text']
                if c != col:  # Remove indicator from other columns
                    heading['text'] = heading_text.rstrip(' ↑↓')
            
            # Get the current heading text without sort indicators
            heading = self.tree.heading(col)
            heading_text = heading['text'].rstrip(' ↑↓')
            
            # Set the new sort indicator
            sort_indicator = ' ↓' if reverse_sort else ' ↑'
            heading['text'] = f"{heading_text}{sort_indicator}"
            
            # Define a key function for sorting based on column type
            def get_sort_key(item):
                value = item[0]  # The value to sort by
                
                # Handle empty or None values
                if not value:
                    return (0,)  # Sort empty values first
                
                # Special handling for price (remove $ and convert to float)
                if col == 'Price':
                    try:
                        return (float(value.replace('$', '').replace(',', '')),)
                    except (ValueError, AttributeError):
                        return (0,)
                # Numeric columns
                elif col in ['Year', 'Stock']:
                    try:
                        return (int(value),)
                    except (ValueError, TypeError):
                        return (0,)
                # Text columns (artist, album, genre)
                else:
                    return (str(value).lower(),)
            
            # Sort the items
            items.sort(key=get_sort_key, reverse=reverse_sort)
            
            # Reorder the items in the treeview
            for index, (_, item) in enumerate(items):
                self.tree.move(item, '', index)
                
            # Update the status bar
            sort_direction = "descending" if reverse_sort else "ascending"
            self.status_var.set(f"Sorted by {col} in {sort_direction} order")
            
        except Exception as e:
            self.log_error(f"Error sorting by {col}: {str(e)}")
            messagebox.showerror(
                "Sort Error",
                f"An error occurred while sorting by {col}.\n{str(e)}",
                icon='error'
            )

    def update_stock(self):
        """Update stock for selected record"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to update")
            return

        item = self.tree.item(selection[0])
        record_id = item["values"][0]

        # Find the record
        record = next((r for r in self.records if r["id"] == record_id), None)
        if not record:
            messagebox.showerror("Error", "Record not found")
            return

        # Get new stock value
        new_stock = simpledialog.askinteger("Update Stock",
                                          f"Current stock for '{record['artist']} - {record['album']}': {record['stock']}\nEnter new stock quantity:",
                                          initialvalue=record["stock"])

        if new_stock is not None:
            record["stock"] = new_stock
            self.save_records()
            self.show_all_records()
            self.status_var.set(f"Updated stock for: {record['artist']} - {record['album']}")
            messagebox.showinfo("Success", "Stock updated successfully!")

    def delete_record(self):
        """Delete selected record"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return

        item = self.tree.item(selection[0])
        record_id = item["values"][0]

        # Find the record
        record = next((r for r in self.records if r["id"] == record_id), None)
        if not record:
            messagebox.showerror("Error", "Record not found")
            return

        # Confirm deletion
        if messagebox.askyesno("Confirm Delete",
                              f"Are you sure you want to delete '{record['artist']} - {record['album']}'?"):
            self.records.remove(record)
            self.save_records()
            self.show_all_records()
            self.status_var.set(f"Deleted: {record['artist']} - {record['album']}" if record else "")

    def view_details(self, event=None):
        """Display detailed information about the selected record in a modern dialog"""
        selection = self.tree.selection()
        if not selection:
            self.update_status("Please select a record to view details", 'warning')
            return

        item = self.tree.item(selection[0])
        record_id = item["values"][0]

        # Find the record
        record = next((r for r in self.records if r["id"] == record_id), None)
        if not record:
            self.update_status("Record not found", 'error')
            return

        # Create a custom dialog
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Record Details - {record['artist']} - {record['album']}")
        detail_win.geometry("400x350")
        detail_win.resizable(False, False)
        detail_win.transient(self.root)
        detail_win.grab_set()
        
        # Center the dialog
        self.center_window(detail_win)
        
        # Custom style for the dialog
        detail_win.configure(bg=COLORS['light'])
        
        # Header with album art placeholder and title
        header_frame = ttk.Frame(detail_win, style='Card.TFrame')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Album art placeholder (you could add actual album art loading here)
        album_art = ttk.Label(header_frame, 
                             text="🎵", 
                             font=('Arial', 40),
                             background=COLORS['white'],
                             width=8,
                             anchor='center')
        album_art.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Album info
        info_frame = ttk.Frame(header_frame, style='Card.TFrame')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        ttk.Label(info_frame, 
                 text=record['artist'], 
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, 
                 text=record['album'], 
                 font=('Segoe UI', 10)).pack(anchor='w')
        ttk.Label(info_frame, 
                 text=f"{record['genre']} • {record['year']}", 
                 font=('Segoe UI', 9),
                 foreground=COLORS['secondary']).pack(anchor='w', pady=(5, 0))
        
        # Details section
        details_frame = ttk.Frame(detail_win, style='Card.TFrame')
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create detail rows
        details = [
            ("💿 Album", record['album']),
            ("🎤 Artist", record['artist']),
            ("🎵 Genre", record['genre']),
            ("📅 Year", record['year']),
            ("💰 Price", f"${record['price']:.2f}"),
            ("📦 Stock", f"{record['stock']} in stock"),
            ("📅 Added", record['date_added'])
        ]
        
        for i, (label, value) in enumerate(details):
            row = ttk.Frame(details_frame)
            row.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(row, 
                     text=label, 
                     width=10, 
                     anchor='w',
                     font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
            ttk.Label(row, 
                     text=value,
                     anchor='w').pack(side=tk.LEFT, padx=10)
        
        # Close button
        btn_frame = ttk.Frame(detail_win)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Button(btn_frame, 
                  text="Close", 
                  command=detail_win.destroy,
                  style='primary.TButton').pack(side=tk.RIGHT)
    
    def center_window(self, window):
        """Center a window on the screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially
    
    # Set application icon and title
    try:
        root.iconbitmap(default='record_icon.ico')  # Add an icon file if available
    except:
        pass  # Use default icon if custom icon not found
    
    # Set application-wide font
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)
    
    # Set application style
    style = ttk.Style()
    style.theme_use('clam')
    
    def start_app(is_owner):
        # Create a new window for the application
        app_window = tk.Toplevel(root)
        app = RecordStoreApp(app_window, is_owner=is_owner)
        
        # Center the window on screen
        window_width = 1000
        window_height = 700
        screen_width = app_window.winfo_screenwidth()
        screen_height = app_window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        app_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Handle window close
        app_window.protocol("WM_DELETE_WINDOW", lambda: on_close(app_window))
    
    def on_close(window):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.destroy()
            root.destroy()
    
    # Show login window
    login = LoginWindow(root, start_app)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
