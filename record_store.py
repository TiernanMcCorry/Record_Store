import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog
import json
import os
from datetime import datetime, timedelta
import csv
from config import COLORS, FONTS, LIGHT_COLORS, DARK_COLORS
from database import Database

class RecordStoreApp:
    def __init__(self, root, is_owner=False, user=None, logout_callback=None):
        self.root = root
        self.is_owner = is_owner
        self.user = user or {}
        self.user_id = self.user.get('id', None)
        self.user_role = self.user.get('role', 'guest')
        self.logout_callback = logout_callback
        
        # Initialize database
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db = Database(self.base_dir)
        
        # Shopping cart
        self.cart = []
        self.cart_total = 0.0
        # UI helpers
        self.tag_configured = False
        # Sorting state for catalog/tree views
        self.catalog_sort_by = 'Album'
        self.catalog_sort_reverse = False

        # Theme
        self.dark_mode = False
        self.load_theme()
        
        # Setup GUI
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.load_data()
    
    def setup_window(self):
        self.root.configure(bg=COLORS['bg'])
    
    def load_theme(self):
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
        try:
            config_file = os.path.join(self.base_dir, 'theme_config.json')
            with open(config_file, 'w') as f:
                json.dump({'dark_mode': self.dark_mode}, f)
        except:
            pass
    
    def create_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('.', background=COLORS['bg'], foreground=COLORS['fg'])
        self.style.configure('TFrame', background=COLORS['bg'])
        self.style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['fg'], font=FONTS['label'])
        
        # Treeview - larger font, alternating rows
        self.style.configure('Treeview',
                           background=COLORS['tree_bg'],
                           foreground=COLORS['tree_fg'],
                           fieldbackground=COLORS['tree_bg'],
                           rowheight=30,
                           font=FONTS['body'])
        
        self.style.configure('Treeview.Heading',
                           background=COLORS['tree_heading_bg'],
                           foreground=COLORS['tree_heading_fg'],
                           font=FONTS['button'])
        
        self.style.map('Treeview',
                      background=[('selected', COLORS['tree_selected_bg'])],
                      foreground=[('selected', COLORS['tree_selected_fg'])])
        
        # Alternating row colors (not directly in ttk, so we'll do in code)
        self.style.configure('Custom.TEntry',
                           fieldbackground=COLORS['entry_bg'],
                           foreground=COLORS['fg'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('Primary.TButton', background=COLORS['primary'], foreground=COLORS['white'])
        self.style.configure('Secondary.TButton', background=COLORS['secondary'], foreground=COLORS['white'])
        self.style.configure('Success.TButton', background=COLORS['success'], foreground=COLORS['white'])
        self.style.configure('Danger.TButton', background=COLORS['danger'], foreground=COLORS['white'])
        self.style.configure('Warning.TButton', background=COLORS['warning'], foreground=COLORS['dark'])
        
        self.style.map('Primary.TButton',
                      background=[('active', COLORS['primary_dark']),
                                 ('!disabled', COLORS['primary'])])
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            COLORS.update(DARK_COLORS)
        else:
            COLORS.update(LIGHT_COLORS)
        self.save_theme()
        self.root.configure(bg=COLORS['bg'])
        self.create_styles()
        self.refresh_widget_styles()
    
    def refresh_widget_styles(self):
        # For simplicity, we'll just refresh the whole interface
        # (A more thorough approach would reconfigure existing widgets)
        pass
    
    def create_widgets(self):
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.create_header()
        
        main_container = ttk.Frame(self.root)
        main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        if self.is_owner:
            self.create_owner_interface(main_container)
        else:
            self.create_customer_interface(main_container)

    def load_data(self):
        """Populate UI with initial data from the database.

        This method is defensive: each refresh call is wrapped so that missing
        pieces of the UI or unexpected DB errors won't crash initialization.
        """
        # Records
        try:
            self.refresh_records()
        except Exception:
            pass

        # Artists and bookings (owner views)
        try:
            if hasattr(self, 'refresh_artists_list'):
                self.refresh_artists_list()
        except Exception:
            pass

        try:
            if hasattr(self, 'refresh_bookings_list'):
                self.refresh_bookings_list()
        except Exception:
            pass

        # Deleted records
        try:
            if hasattr(self, 'refresh_deleted_records'):
                self.refresh_deleted_records()
        except Exception:
            pass

        # Cart
        try:
            if hasattr(self, 'update_cart_display'):
                self.update_cart_display()
        except Exception:
            pass

        # Artist-specific slots/bookings
        try:
            if hasattr(self, 'refresh_available_slots'):
                self.refresh_available_slots()
        except Exception:
            pass
        try:
            if hasattr(self, 'refresh_artist_bookings'):
                self.refresh_artist_bookings()
        except Exception:
            pass
        try:
            if hasattr(self, 'refresh_events'):
                self.refresh_events()
        except Exception:
            pass
    
    def create_header(self):
        self.header = tk.Frame(self.root, bg=COLORS['primary'], height=70)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        
        self.header.grid_columnconfigure(0, weight=0)
        self.header.grid_columnconfigure(1, weight=1)
        self.header.grid_columnconfigure(2, weight=0)
        
        left_spacer = tk.Frame(self.header, bg=COLORS['primary'], width=20)
        left_spacer.grid(row=0, column=0, sticky="ns")
        
        title_frame = tk.Frame(self.header, bg=COLORS['primary'])
        title_frame.grid(row=0, column=1, sticky="nsew")
        title_frame.grid_columnconfigure(0, weight=1)
        title_frame.grid_rowconfigure(0, weight=1)
        
        title_content = tk.Frame(title_frame, bg=COLORS['primary'])
        title_content.grid(row=0, column=0)
        
        # Logo
        tk.Label(title_content,
                text="💿",  # Vinyl record emoji as placeholder
                font=('Segoe UI Emoji', 28),
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left', padx=5)
        
        tk.Label(title_content,
                text="FirstPress Vinyl",
                font=FONTS['title'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left')
        
        tk.Label(title_content,
                text=f"{' Manager' if self.is_owner else ''}",
                font=FONTS['subtitle'],
                bg=COLORS['primary'],
                fg=COLORS['white']).pack(side='left')
        
        user_frame = tk.Frame(self.header, bg=COLORS['primary'])
        user_frame.grid(row=0, column=2, sticky="e", padx=20)
        
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
        
        username = self.user.get('username', 'Guest')
        user_label = tk.Label(user_frame,
                            text=f"👤 {username}",
                            font=FONTS['label'],
                            bg=COLORS['primary'],
                            fg=COLORS['white'])
        user_label.pack(side='left', padx=10)
        
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
    
    def logout(self):
        """Logout the current user and return to the auth window.

        This clears the root window and invokes the provided logout_callback
        so the main application can show the authentication screen.
        """
        try:
            # Clear all widgets from the root to avoid stale references
            for widget in list(self.root.winfo_children()):
                try:
                    widget.destroy()
                except Exception:
                    pass

            if callable(self.logout_callback):
                # Call the callback to show the auth/login window
                self.logout_callback()
        except Exception as e:
            # Fallback: print to stderr so the developer can see issues
            import sys
            print(f"Error during logout: {e}", file=sys.stderr)
    
    # Owner interface (tabs)
    def create_owner_interface(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        inventory_tab = ttk.Frame(notebook)
        statistics_tab = ttk.Frame(notebook)
        artist_tab = ttk.Frame(notebook)          # New
        deleted_tab = ttk.Frame(notebook)         # New
        
        notebook.add(inventory_tab, text="📦 Inventory")
        notebook.add(statistics_tab, text="📊 Statistics")
        notebook.add(artist_tab, text="🎤 Artist Management")
        notebook.add(deleted_tab, text="🗑️ Deleted Records")
        
        inventory_tab.grid_rowconfigure(0, weight=1)
        inventory_tab.grid_columnconfigure(0, weight=1)
        statistics_tab.grid_rowconfigure(0, weight=1)
        statistics_tab.grid_columnconfigure(0, weight=1)
        artist_tab.grid_rowconfigure(0, weight=1)
        artist_tab.grid_columnconfigure(0, weight=1)
        deleted_tab.grid_rowconfigure(0, weight=1)
        deleted_tab.grid_columnconfigure(0, weight=1)
        
        self.create_inventory_section(inventory_tab)
        self.create_enhanced_statistics_section(statistics_tab)
        self.create_artist_management_tab(artist_tab)
        self.create_deleted_records_tab(deleted_tab)
    
    def create_inventory_section(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        left_panel = ttk.LabelFrame(parent, text=" Add/Edit Record ", padding=15)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        right_panel = ttk.LabelFrame(parent, text=" Records List ", padding=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        self.create_record_form(left_panel)
        self.create_records_list(right_panel, is_owner=True)
    
    def create_record_form(self, parent):
        form_container = tk.Frame(parent, bg=COLORS['bg'])
        form_container.grid(row=0, column=0, sticky="nsew")
        
        form_container.grid_rowconfigure(0, weight=0)
        form_container.grid_rowconfigure(1, weight=1)
        form_container.grid_rowconfigure(2, weight=0)
        form_container.grid_columnconfigure(0, weight=1)
        
        fields_frame = tk.Frame(form_container, bg=COLORS['bg'])
        fields_frame.grid(row=0, column=0, sticky="ew")
        
        fields = [
            ("Artist:", "artist_entry"),
            ("Album:", "album_entry"),
            ("Genre:", "genre_entry"),
            ("Year:", "year_entry"),
            ("Price (£):", "price_entry"),
            ("Stock:", "stock_entry"),
        ]
        
        self.form_entries = {}
        
        # Predefined genres for dropdown
        genres = ["Rock", "Pop", "Soul", "Hip Hop", "Jazz", "Classical", "Electronic", "Folk", "Blues", "Country", "Other"]
        
        for i, (label, name) in enumerate(fields):
            tk.Label(fields_frame,
                    text=label,
                    font=FONTS['label'],
                    bg=COLORS['bg'],
                    fg=COLORS['fg']).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))
            
            if name == "genre_entry":
                entry = ttk.Combobox(fields_frame,
                                    values=genres,
                                    font=FONTS['entry'],
                                    background=COLORS['entry_bg'],
                                    foreground=COLORS['fg'])
                entry.set("")
            else:
                entry = tk.Entry(fields_frame,
                               font=FONTS['entry'],
                               bg=COLORS['entry_bg'],
                               fg=COLORS['fg'],
                               relief='solid',
                               borderwidth=1)
            
            entry.grid(row=i, column=1, sticky="ew", pady=5, ipady=5)
            self.form_entries[name] = entry
        
        # Artist autocomplete: we'll set up later after loading existing artists
        self.setup_artist_autocomplete()
        
        fields_frame.grid_columnconfigure(1, weight=1)
        
        button_frame = tk.Frame(form_container, bg=COLORS['bg'])
        button_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        
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
    
    def setup_artist_autocomplete(self):
        """Fetch all distinct artists from the database and set up autocomplete"""
        records = self.db.get_all_records()
        artists = sorted(set(r['artist'] for r in records if r['artist']))
        self.artist_list = artists
        
        def on_keyrelease(event):
            entry = self.form_entries['artist_entry']
            typed = entry.get()
            if typed == '':
                entry['values'] = []
            else:
                matches = [a for a in artists if typed.lower() in a.lower()]
                entry['values'] = matches
        
        # Replace artist entry with a Combobox for autocomplete
        # But we already created it as Entry; we'll replace it
        old_entry = self.form_entries['artist_entry']
        row = old_entry.grid_info()['row']
        column = old_entry.grid_info()['column']
        parent = old_entry.master
        old_entry.destroy()
        
        new_entry = ttk.Combobox(parent,
                                 values=artists,
                                 font=FONTS['entry'])
        new_entry.grid(row=row, column=column, sticky="ew", pady=5, ipady=5)
        new_entry.bind('<KeyRelease>', on_keyrelease)
        self.form_entries['artist_entry'] = new_entry
    
    def create_records_list(self, parent, is_owner=False):
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(2, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        
        search_frame = tk.Frame(parent, bg=COLORS['bg'])
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)
        search_frame.grid_columnconfigure(2, weight=0)
        
        tk.Label(search_frame,
                text="🔍 Search:",
                font=FONTS['label'],
                bg=COLORS['bg'],
                fg=COLORS['fg']).grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                              textvariable=self.search_var,
                              font=FONTS['entry'],
                              bg=COLORS['entry_bg'],
                              fg=COLORS['fg'],
                              relief='solid',
                              borderwidth=1)
        search_entry.grid(row=0, column=1, sticky="ew", ipady=5, padx=(0, 5))
        search_entry.bind('<KeyRelease>', lambda e: self.search_records())
        
        search_btn = tk.Button(search_frame,
                             text="Search",
                             font=FONTS['button_small'],
                             bg=COLORS['primary'],
                             fg=COLORS['white'],
                             relief='flat',
                             command=self.search_records,
                             cursor='hand2',
                             padx=15,
                             pady=5)
        search_btn.grid(row=0, column=2)
        
        tree_frame = tk.Frame(parent, bg=COLORS['bg'])
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        columns = ("ID", "Album", "Artist", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            # Make headings clickable to sort by column
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            if col == "ID":
                self.tree.column(col, width=50, anchor="center")
            elif col in ["Album", "Artist"]:
                self.tree.column(col, width=180, anchor="w")
            elif col == "Genre":
                self.tree.column(col, width=100, anchor="w")
            elif col == "Year":
                self.tree.column(col, width=80, anchor="center")
            elif col == "Price":
                self.tree.column(col, width=100, anchor="e")
            elif col == "Stock":
                self.tree.column(col, width=80, anchor="center")
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew", columnspan=2)
        
        if is_owner:
            self.tree.bind('<<TreeviewSelect>>', self.on_record_select)
        
        # Alternating row colors (after items are inserted)
        self.tag_configured = False
        
        action_frame = tk.Frame(parent, bg=COLORS['bg'])
        action_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        action_frame.grid_columnconfigure(2, weight=1)
        
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
    
    def refresh_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = self.db.get_all_records()
        # Apply catalog sorting if set (defaults to Album alphabetical for customer view)
        sort_col = getattr(self, 'catalog_sort_by', None)
        sort_rev = getattr(self, 'catalog_sort_reverse', False)
        if sort_col:
            try:
                records = sorted(records, key=lambda r: self._record_sort_key(r, sort_col), reverse=sort_rev)
            except Exception:
                # fallback: no sort
                pass
        for idx, record in enumerate(records):
            item_id = self.tree.insert('', 'end', values=(
                record.get('id', ''),
                record.get('album', ''),
                record.get('artist', ''),
                record.get('genre', ''),
                record.get('year', ''),
                f"£{record.get('price', 0):.2f}",
                record.get('stock', 0)
            ))
            # Apply tag for alternating colors
            if not self.tag_configured:
                self.tree.tag_configure('odd', background=COLORS['tree_bg'])
                self.tree.tag_configure('even', background=COLORS['light_gray'])
                self.tag_configured = True
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.item(item_id, tags=(tag,))

    def _record_sort_key(self, record, col_name):
        """Return a sortable key for a record based on the column name."""
        col_map = {
            'ID': lambda r: int(r.get('id') or 0),
            'Album': lambda r: (r.get('album') or '').lower(),
            'Artist': lambda r: (r.get('artist') or '').lower(),
            'Genre': lambda r: (r.get('genre') or '').lower(),
            'Year': lambda r: int(r.get('year') or 0),
            'Price': lambda r: float(r.get('price') or 0.0),
            'Stock': lambda r: int(r.get('stock') or 0)
        }
        fn = col_map.get(col_name, lambda r: (r.get('album') or '').lower())
        return fn(record)

    def sort_by_column(self, col_name):
        """Toggle sorting by a column and refresh the view."""
        # Initialize default sort to Album ascending for guest/catalog
        if not hasattr(self, 'catalog_sort_by') or self.catalog_sort_by != col_name:
            self.catalog_sort_by = col_name
            # default ascending except for Price/Year/Stock perhaps ascending too
            self.catalog_sort_reverse = False
        else:
            # toggle
            self.catalog_sort_reverse = not getattr(self, 'catalog_sort_reverse', False)
        # Refresh the records shown
        try:
            self.refresh_records()
        except Exception:
            pass
    
    def search_records(self):
        if self.is_owner:
            query = self.search_var.get()
        else:
            query = self.customer_search_var.get()
            if query == "Search by artist, album, or genre...":
                query = ""
        
        if not query:
            self.refresh_records()
            return
        
        results = self.db.search_records(query)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, record in enumerate(results):
            item_id = self.tree.insert('', 'end', values=(
                record.get('id', ''),
                record.get('album', ''),
                record.get('artist', ''),
                record.get('genre', ''),
                record.get('year', ''),
                f"£{record.get('price', 0):.2f}",
                record.get('stock', 0)
            ))
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.item(item_id, tags=(tag,))
    
    def on_record_select(self, event):
        selection = self.tree.selection()
        if selection and self.is_owner:
            values = self.tree.item(selection[0])['values']
            if values and len(values) >= 7:
                self.load_form_from_record(values)
    
    def load_form_from_record(self, values):
        if not self.is_owner:
            return
        entries = ['artist_entry', 'album_entry', 'genre_entry', 'year_entry', 'price_entry', 'stock_entry']
        form_values = [values[2], values[1], values[3], values[4], str(values[5]).replace('£', ''), values[6]]
        for entry_name, value in zip(entries, form_values):
            if entry_name in self.form_entries:
                entry = self.form_entries[entry_name]
                entry.delete(0, tk.END)
                entry.insert(0, value)
    
    def add_record(self):
        if not self.is_owner:
            return
        
        data = {
            'artist': self.form_entries['artist_entry'].get().strip(),
            'album': self.form_entries['album_entry'].get().strip(),
            'genre': self.form_entries['genre_entry'].get().strip(),
            'year': self.form_entries['year_entry'].get().strip(),
            'price': self.form_entries['price_entry'].get().strip(),
            'stock': self.form_entries['stock_entry'].get().strip()
        }
        
        errors = []
        try:
            data['year'] = int(data['year']) if data['year'] else 0
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
            record_id = self.db.add_record(data, self.user_id)
            self.refresh_records()
            self.clear_form()
            messagebox.showinfo("Success", f"Record added successfully! (ID: {record_id})")
            self.setup_artist_autocomplete()  # Update artist list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add record: {str(e)}")
    
    def update_record(self):
        if not self.is_owner:
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to update")
            return
        record_id = self.tree.item(selection[0])['values'][0]
        
        updates = {
            'artist': self.form_entries['artist_entry'].get().strip(),
            'album': self.form_entries['album_entry'].get().strip(),
            'genre': self.form_entries['genre_entry'].get().strip(),
            'year': self.form_entries['year_entry'].get().strip(),
            'price': self.form_entries['price_entry'].get().strip(),
            'stock': self.form_entries['stock_entry'].get().strip()
        }
        
        try:
            updates['year'] = int(updates['year']) if updates['year'] else 0
            updates['price'] = float(updates['price'])
            updates['stock'] = int(updates['stock'])
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values")
            return
        
        if self.db.update_record(record_id, updates, self.user_id):
            self.refresh_records()
            self.setup_artist_autocomplete()
            messagebox.showinfo("Success", "Record updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update record")
    
    def delete_record(self):
        if not self.is_owner:
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to delete")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record? It will be moved to Deleted Records and can be restored."):
            return
        record_id = self.tree.item(selection[0])['values'][0]
        if self.db.delete_record(record_id, self.user_id):
            self.refresh_records()
            self.clear_form()
            messagebox.showinfo("Success", "Record deleted (soft delete). It can be restored from the Deleted Records tab.")
        else:
            messagebox.showerror("Error", "Failed to delete record")
    
    def clear_form(self):
        if not self.is_owner:
            return
        for entry in self.form_entries.values():
            entry.delete(0, 'end')
    
    def export_to_csv(self):
        if not self.is_owner:
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV files", "*.csv")],
                                               title="Export Records to CSV")
        if not filename:
            return
        try:
            self.db.export_to_csv(filename, 'records')
            messagebox.showinfo("Export Successful", f"Records exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def import_from_csv(self):
        if not self.is_owner:
            return
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Import Records from CSV")
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
    
    def create_enhanced_statistics_section(self, parent):
        """Create a detailed statistics dashboard."""
        # Main container with scrollbar for large content
        canvas = tk.Canvas(parent, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Fetch statistics
        stats = self.db.get_statistics()

        # Title
        tk.Label(scrollable_frame,
                text="📈 Store Statistics",
                font=FONTS['h3'],
                bg=COLORS['bg'],
                fg=COLORS['fg']).pack(pady=20)

        # Metrics frame
        metrics_frame = tk.Frame(scrollable_frame, bg=COLORS['bg'])
        metrics_frame.pack(fill='x', pady=10)

        # Define metric cards
        metrics = [
            ("Total Records", stats.get('total_records', 0)),
            ("Total Stock", stats.get('total_stock', 0)),
            ("Total Value", f"£{stats.get('total_value', 0):,.2f}"),
            ("Average Price", f"£{stats.get('avg_price', 0):,.2f}"),
            ("Total Sales", stats.get('total_sales_count', 0)),
            ("Sales Revenue", f"£{stats.get('total_sales_amount', 0):,.2f}"),
            ("Avg Sale Value", f"£{stats.get('avg_sale_value', 0):,.2f}")
        ]

        # Display metrics in a grid
        for i, (label, value) in enumerate(metrics):
            card = tk.Frame(metrics_frame, bg=COLORS['card_bg'], relief='solid', bd=1)
            card.grid(row=i//4, column=i%4, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            tk.Label(card,
                    text=label,
                    font=FONTS['caption'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['secondary']).pack(pady=(10, 0))
            tk.Label(card,
                    text=str(value),
                    font=FONTS['h4'],
                    bg=COLORS['card_bg'],
                    fg=COLORS['primary']).pack(pady=(5, 10))

        # Genre distribution
        genre_frame = ttk.LabelFrame(scrollable_frame, text=" Genre Distribution ", padding=10)
        genre_frame.pack(fill='x', pady=20)

        genres = stats.get('genre_distribution', {})
        if genres:
            # Create a simple bar chart using labels
            for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
                row = tk.Frame(genre_frame, bg=COLORS['bg'])
                row.pack(fill='x', pady=2)

                tk.Label(row, text=genre, width=15, anchor='w',
                        bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left')
                tk.Label(row, text=str(count), width=5, anchor='e',
                        bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left')
                # Simple bar
                bar_len = int(200 * count / max(genres.values())) if genres else 0
                bar = tk.Frame(row, bg=COLORS['primary'], height=20, width=bar_len)
                bar.pack(side='left', padx=5)
        else:
            tk.Label(genre_frame, text="No genre data available.",
                    bg=COLORS['bg'], fg=COLORS['secondary']).pack()

        # Low stock items
        low_stock = stats.get('low_stock', [])
        if low_stock:
            low_frame = ttk.LabelFrame(scrollable_frame, text=" ⚠️ Low Stock (≤5) ", padding=10)
            low_frame.pack(fill='x', pady=10)

            tree = ttk.Treeview(low_frame, columns=("ID", "Album", "Artist", "Stock"), show='headings', height=5)
            tree.heading("ID", text="ID")
            tree.heading("Album", text="Album")
            tree.heading("Artist", text="Artist")
            tree.heading("Stock", text="Stock")
            for rec in low_stock:
                tree.insert('', 'end', values=(rec['id'], rec['album'], rec['artist'], rec['stock']))
            tree.pack(fill='x')

        # Out of stock items
        out_of_stock = stats.get('out_of_stock', [])
        if out_of_stock:
            out_frame = ttk.LabelFrame(scrollable_frame, text=" ❌ Out of Stock ", padding=10)
            out_frame.pack(fill='x', pady=10)

            tree = ttk.Treeview(out_frame, columns=("ID", "Album", "Artist"), show='headings', height=5)
            tree.heading("ID", text="ID")
            tree.heading("Album", text="Album")
            tree.heading("Artist", text="Artist")
            for rec in out_of_stock:
                tree.insert('', 'end', values=(rec['id'], rec['album'], rec['artist']))
            tree.pack(fill='x')
        
    # New: Artist Management Tab (Owner only)
    def create_artist_management_tab(self, parent):
        # Configure grid
        parent.grid_rowconfigure(0, weight=0)   # header
        parent.grid_rowconfigure(1, weight=1)   # artist list
        parent.grid_rowconfigure(2, weight=0)   # bookings list
        parent.grid_columnconfigure(0, weight=1)
        
        # Header with Add Artist button
        header_frame = tk.Frame(parent, bg=COLORS['bg'])
        header_frame.grid(row=0, column=0, sticky="ew", pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        tk.Label(header_frame,
                text="🎤 Registered Artists",
                font=FONTS['h5'],
                bg=COLORS['bg'],
                fg=COLORS['fg']).grid(row=0, column=0, sticky="w")
        
        add_artist_btn = tk.Button(header_frame,
                                  text="➕ Add Artist",
                                  font=FONTS['button_small'],
                                  bg=COLORS['success'],
                                  fg=COLORS['white'],
                                  relief='flat',
                                  command=self.add_artist,
                                  cursor='hand2',
                                  padx=15,
                                  pady=5)
        add_artist_btn.grid(row=0, column=1)
        
        # Artist list frame
        artist_frame = ttk.LabelFrame(parent, text=" Artists ", padding=10)
        artist_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        artist_frame.grid_rowconfigure(0, weight=1)
        artist_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview for artists
        artist_columns = ("ID", "Stage Name", "Real Name", "Genre", "Status")
        self.artist_tree = ttk.Treeview(artist_frame, columns=artist_columns, show='headings', height=8)
        for col in artist_columns:
            self.artist_tree.heading(col, text=col)
            self.artist_tree.column(col, width=120 if col != "Stage Name" else 150)
        vscroll = ttk.Scrollbar(artist_frame, orient="vertical", command=self.artist_tree.yview)
        self.artist_tree.configure(yscrollcommand=vscroll.set)
        self.artist_tree.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        
        self.artist_tree.bind('<<TreeviewSelect>>', self.on_artist_select)
        
        # Bookings list frame
        bookings_frame = ttk.LabelFrame(parent, text=" Bookings ", padding=10)
        bookings_frame.grid(row=2, column=0, sticky="nsew")
        bookings_frame.grid_rowconfigure(0, weight=1)
        bookings_frame.grid_columnconfigure(0, weight=1)
        bookings_frame.grid_columnconfigure(1, weight=0)
        
        # Treeview for bookings
        booking_columns = ("ID", "Artist", "Date", "Duration", "Status", "Notes")
        self.booking_tree = ttk.Treeview(bookings_frame, columns=booking_columns, show='headings', height=6)
        for col in booking_columns:
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=100 if col != "Notes" else 150)
        vscroll2 = ttk.Scrollbar(bookings_frame, orient="vertical", command=self.booking_tree.yview)
        self.booking_tree.configure(yscrollcommand=vscroll2.set)
        self.booking_tree.grid(row=0, column=0, sticky="nsew")
        vscroll2.grid(row=0, column=1, sticky="ns")
        
        # Buttons for bookings
        booking_btn_frame = tk.Frame(bookings_frame, bg=COLORS['bg'])
        booking_btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        booking_btn_frame.grid_columnconfigure(0, weight=1)
        booking_btn_frame.grid_columnconfigure(1, weight=1)
        
        approve_btn = tk.Button(booking_btn_frame,
                               text="✓ Approve",
                               font=FONTS['button_small'],
                               bg=COLORS['success'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=lambda: self.update_booking_status('confirmed'),
                               cursor='hand2')
        approve_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        cancel_btn = tk.Button(booking_btn_frame,
                              text="✗ Cancel",
                              font=FONTS['button_small'],
                              bg=COLORS['danger'],
                              fg=COLORS['white'],
                              relief='flat',
                              command=lambda: self.update_booking_status('cancelled'),
                              cursor='hand2')
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        complete_btn = tk.Button(booking_btn_frame,
                                text="✔ Complete",
                                font=FONTS['button_small'],
                                bg=COLORS['info'],
                                fg=COLORS['white'],
                                relief='flat',
                                command=lambda: self.update_booking_status('completed'),
                                cursor='hand2')
        complete_btn.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Load data
        self.refresh_artists_list()
    
    def refresh_artists_list(self):
        for item in self.artist_tree.get_children():
            self.artist_tree.delete(item)
        artists = self.db.get_all_artists()
        for artist in artists:
            status = "Approved" if artist.get('is_approved') else "Pending"
            self.artist_tree.insert('', 'end', values=(
                artist['id'],
                artist.get('stage_name', ''),
                artist.get('full_name', ''),
                artist.get('genre', ''),
                status
            ))
    
    def add_artist(self):
        # Simple dialog to add an artist (could be more elaborate)
        stage_name = simpledialog.askstring("Add Artist", "Stage Name:")
        if not stage_name:
            return
        real_name = simpledialog.askstring("Add Artist", "Real Name (optional):")
        genre = simpledialog.askstring("Add Artist", "Genre:")
        # In a real system, you'd also collect customer_id, but for simplicity we'll create a dummy customer
        # This is a placeholder; normally you'd have a separate flow.
        messagebox.showinfo("Info", "Adding artist is a placeholder. In a real system, artists would be linked to customer accounts.")
        # For now, just refresh list
        self.refresh_artists_list()
    
    def delete_artist(self):
        selection = self.artist_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an artist to delete")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this artist? This will also remove their bookings."):
            artist_id = self.artist_tree.item(selection[0])['values'][0]
            self.db.delete_artist(artist_id)
            self.refresh_artists_list()
            self.refresh_bookings_list()
    
    def on_artist_select(self, event):
        selection = self.artist_tree.selection()
        if selection:
            self.refresh_bookings_list(artist_id=self.artist_tree.item(selection[0])['values'][0])
        else:
            self.refresh_bookings_list()
    
    def refresh_bookings_list(self, artist_id=None):
        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)
        if artist_id:
            bookings = self.db.get_artist_bookings(artist_id)
        else:
            bookings = self.db.get_all_bookings()
        for booking in bookings:
            self.booking_tree.insert('', 'end', values=(
                booking['id'],
                booking.get('stage_name', 'Unknown'),
                booking['performance_date'],
                f"{booking['duration_minutes']} min",
                booking['status'],
                booking.get('notes', '')
            ))
    
    def update_booking_status(self, new_status):
        selection = self.booking_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a booking")
            return
        booking_id = self.booking_tree.item(selection[0])['values'][0]
        self.db.update_booking_status(booking_id, new_status, self.user_id)
        self.refresh_bookings_list()
        if self.artist_tree.selection():
            artist_id = self.artist_tree.item(self.artist_tree.selection()[0])['values'][0]
            self.refresh_bookings_list(artist_id)
        else:
            self.refresh_bookings_list()
    
    # New: Deleted Records Tab
    def create_deleted_records_tab(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        tree_frame = ttk.LabelFrame(parent, text=" Soft-Deleted Records ", padding=10)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("ID", "Artist", "Album", "Genre", "Year", "Price", "Stock", "Deleted At")
        self.deleted_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.deleted_tree.heading(col, text=col)
            self.deleted_tree.column(col, width=100)
        vscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.deleted_tree.yview)
        self.deleted_tree.configure(yscrollcommand=vscroll.set)
        self.deleted_tree.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        
        btn_frame = tk.Frame(parent, bg=COLORS['bg'])
        btn_frame.grid(row=1, column=0, sticky="ew", pady=10)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        restore_btn = tk.Button(btn_frame,
                               text="Restore Selected",
                               font=FONTS['button_small'],
                               bg=COLORS['success'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=self.restore_record,
                               cursor='hand2')
        restore_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        refresh_btn = tk.Button(btn_frame,
                               text="Refresh",
                               font=FONTS['button_small'],
                               bg=COLORS['secondary'],
                               fg=COLORS['white'],
                               relief='flat',
                               command=self.refresh_deleted_records,
                               cursor='hand2')
        refresh_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.refresh_deleted_records()
    
    def refresh_deleted_records(self):
        for item in self.deleted_tree.get_children():
            self.deleted_tree.delete(item)
        records = self.db.get_deleted_records()
        for rec in records:
            self.deleted_tree.insert('', 'end', values=(
                rec['id'],
                rec['artist'],
                rec['album'],
                rec['genre'],
                rec['year'],
                f"£{rec['price']:.2f}",
                rec['stock'],
                rec['deleted_at']
            ))
    
    def restore_record(self):
        selection = self.deleted_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record to restore")
            return
        record_id = self.deleted_tree.item(selection[0])['values'][0]
        if self.db.restore_record(record_id, self.user_id):
            self.refresh_deleted_records()
            self.refresh_records()
            messagebox.showinfo("Success", "Record restored.")
        else:
            messagebox.showerror("Error", "Failed to restore record")
    
    # Customer interface
    def create_customer_interface(self, parent):
    # Use a notebook for catalog, cart, and artist portal (if artist)
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Catalog tab
        catalog_tab = ttk.Frame(notebook)
        notebook.add(catalog_tab, text="📀 Catalog")
        catalog_tab.grid_rowconfigure(0, weight=1)
        catalog_tab.grid_columnconfigure(0, weight=1)

        # Cart tab
        cart_tab = ttk.Frame(notebook)
        notebook.add(cart_tab, text="🛒 Cart")
        cart_tab.grid_rowconfigure(0, weight=1)
        cart_tab.grid_columnconfigure(0, weight=1)

        # Events tab (public facing list of upcoming artist bookings)
        events_tab = ttk.Frame(notebook)
        notebook.add(events_tab, text="📅 Events")
        events_tab.grid_rowconfigure(0, weight=1)
        events_tab.grid_columnconfigure(0, weight=1)

        # Build catalog section inside catalog_tab
        self.create_catalog_section(catalog_tab)
        # Build cart section inside cart_tab
        self.create_cart_section(cart_tab)

        # Build events section inside events_tab
        self.create_events_tab(events_tab)

        # If user is an artist, add artist portal tab
        if self.user_role == 'artist':
            artist_tab = ttk.Frame(notebook)
            notebook.add(artist_tab, text="🎤 Artist Portal")
            artist_tab.grid_rowconfigure(0, weight=1)
            artist_tab.grid_columnconfigure(0, weight=1)
            self.create_artist_portal_tab(artist_tab)
    
    def create_catalog_section(self, parent):
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(2, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        
        search_frame = tk.Frame(parent, bg=COLORS['bg'])
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)
        search_frame.grid_columnconfigure(2, weight=0)
        
        self.customer_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                              textvariable=self.customer_search_var,
                              font=FONTS['entry'],
                              bg=COLORS['entry_bg'],
                              fg=COLORS['fg'],
                              relief='solid',
                              borderwidth=1)
        search_entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 5))
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
        
        search_btn = tk.Button(search_frame,
                             text="🔍 Search",
                             font=FONTS['button_small'],
                             bg=COLORS['primary'],
                             fg=COLORS['white'],
                             relief='flat',
                             command=self.search_records,
                             cursor='hand2',
                             padx=15,
                             pady=5)
        search_btn.grid(row=0, column=1, padx=(0, 5))
        
        refresh_btn = tk.Button(search_frame,
                              text="🔄 Refresh",
                              font=FONTS['button_small'],
                              bg=COLORS['secondary'],
                              fg=COLORS['white'],
                              relief='flat',
                              command=self.refresh_records,
                              cursor='hand2',
                              padx=15,
                              pady=5)
        refresh_btn.grid(row=0, column=2)
        
        tree_frame = tk.Frame(parent, bg=COLORS['bg'])
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        columns = ("ID", "Album", "Artist", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        for col in columns:
            # clickable headings for sorting
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            if col == "ID":
                self.tree.column(col, width=0, stretch=False)
            elif col in ["Album", "Artist"]:
                self.tree.column(col, width=150)
            else:
                self.tree.column(col, width=80)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        # Allow double-click to add an item to cart for convenience
        try:
            self.tree.bind('<Double-1>', lambda e: self.add_to_cart())
        except Exception:
            pass
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        button_frame = tk.Frame(parent, bg=COLORS['bg'])
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        
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
        # Populate catalog immediately
        try:
            # Default sort for catalog: Album alphabetical
            if not hasattr(self, 'catalog_sort_by'):
                self.catalog_sort_by = 'Album'
                self.catalog_sort_reverse = False
            self.refresh_records()
        except Exception:
            pass
    
    def create_cart_section(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_rowconfigure(2, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        
        tree_frame = tk.Frame(parent, bg=COLORS['bg'])
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(1, weight=0)
        
        columns = ("Item", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.cart_tree.heading(col, text=col)
            width = 120 if col == "Item" else 60
            self.cart_tree.column(col, width=width, anchor="center" if col != "Item" else "w")
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=v_scrollbar.set)
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
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
                                    text="£0.00",
                                    font=FONTS['heading'],
                                    bg=COLORS['bg'],
                                    fg=COLORS['primary'])
        self.total_label.grid(row=0, column=1, sticky="e")
        
        btn_frame = tk.Frame(parent, bg=COLORS['bg'])
        btn_frame.grid(row=2, column=0, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
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
    
    def create_artist_portal_tab(self, parent):
   
    # Get artist ID from customer ID
        artist = self.db.get_artist_by_customer_id(self.user['id'])
        if not artist:
            # If no artist profile exists (shouldn't happen), show message
            tk.Label(parent, text="Artist profile not found. Please contact the store.",
                    font=FONTS['body'], bg=COLORS['bg'], fg=COLORS['danger']).pack(pady=50)
            return

        self.artist_id = artist['id']   # store for later use

        # Main frame
        main_frame = tk.Frame(parent, bg=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Left: Existing bookings
        left_frame = ttk.LabelFrame(main_frame, text=" Your Bookings ", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Treeview for bookings
        booking_columns = ("ID", "Date", "Duration", "Status", "Notes")
        self.artist_booking_tree = ttk.Treeview(left_frame, columns=booking_columns, show='headings', height=12)
        for col in booking_columns:
            self.artist_booking_tree.heading(col, text=col)
            self.artist_booking_tree.column(col, width=100)
        vscroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.artist_booking_tree.yview)
        self.artist_booking_tree.configure(yscrollcommand=vscroll.set)
        self.artist_booking_tree.pack(side='left', fill='both', expand=True)
        vscroll.pack(side='right', fill='y')

        # Right: Request new booking
        right_frame = ttk.LabelFrame(main_frame, text=" Request a Performance ", padding=10)
        right_frame.pack(side='right', fill='both', expand=True)

        # Available slots selection
        tk.Label(right_frame, text="Select Date & Time:", font=FONTS['caption'],
                bg=COLORS['bg'], fg=COLORS['fg']).pack(anchor='w', pady=(0, 5))
        self.slot_var = tk.StringVar()
        self.slot_combo = ttk.Combobox(right_frame, textvariable=self.slot_var, state='readonly', width=30)
        self.slot_combo.pack(fill='x', pady=(0, 15))

        # Refresh available slots
        self.refresh_available_slots()

        # Notes
        tk.Label(right_frame, text="Notes (optional):", font=FONTS['caption'],
                bg=COLORS['bg'], fg=COLORS['fg']).pack(anchor='w', pady=(0, 5))
        self.booking_notes = tk.Text(right_frame, height=4, width=30, bg=COLORS['entry_bg'], fg=COLORS['fg'],
                                    relief='solid', bd=1)
        self.booking_notes.pack(fill='x', pady=(0, 15))

        # Request button
        request_btn = tk.Button(right_frame, text="Request Booking",
                                font=FONTS['button'], bg=COLORS['success'], fg=COLORS['white'],
                                relief='flat', command=self.request_booking, cursor='hand2')
        request_btn.pack(pady=10)

        # Refresh button
        refresh_btn = tk.Button(right_frame, text="Refresh Available Slots",
                                font=FONTS['button_small'], bg=COLORS['secondary'], fg=COLORS['white'],
                                relief='flat', command=self.refresh_available_slots, cursor='hand2')
        refresh_btn.pack()

        # Load initial bookings
        self.refresh_artist_bookings()

    # Public Events tab for customers/guests
    def create_events_tab(self, parent):
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        header = tk.Frame(parent, bg=COLORS['bg'])
        header.grid(row=0, column=0, sticky='ew', pady=8, padx=8)
        header.grid_columnconfigure(0, weight=1)

        tk.Label(header, text="Upcoming Events", font=FONTS['h4'], bg=COLORS['bg'], fg=COLORS['fg']).grid(row=0, column=0, sticky='w')

        btn_frame = tk.Frame(header, bg=COLORS['bg'])
        btn_frame.grid(row=0, column=1, sticky='e')
        refresh_btn = tk.Button(btn_frame, text="Refresh", font=FONTS['button_small'], bg=COLORS['secondary'], fg=COLORS['white'], relief='flat', command=self.refresh_events, cursor='hand2')
        refresh_btn.pack(side='right')

        # Treeview
        tree_frame = tk.Frame(parent, bg=COLORS['bg'])
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=8, pady=8)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        cols = ("ID", "Date", "Artist", "Stage Name", "Duration", "Status", "Notes")
        self.events_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
        for c in cols:
            self.events_tree.heading(c, text=c)
            if c == 'Notes':
                self.events_tree.column(c, width=220)
            elif c in ('Artist', 'Stage Name'):
                self.events_tree.column(c, width=150)
            else:
                self.events_tree.column(c, width=100)

        v = ttk.Scrollbar(tree_frame, orient='vertical', command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=v.set)
        self.events_tree.grid(row=0, column=0, sticky='nsew')
        v.grid(row=0, column=1, sticky='ns')

        # initial populate
        try:
            self.refresh_events()
        except Exception:
            pass

    def refresh_events(self):
        """Populate the events tree with upcoming bookings (next 90 days)."""
        try:
            for item in getattr(self, 'events_tree', {}).get_children() if hasattr(self, 'events_tree') else []:
                try:
                    self.events_tree.delete(item)
                except Exception:
                    pass

            # Get bookings from DB
            bookings = self.db.get_all_bookings()
            # Filter upcoming only
            upcoming = []
            now = datetime.now()
            for b in bookings:
                try:
                    pd = datetime.fromisoformat(b['performance_date']) if isinstance(b['performance_date'], str) else b['performance_date']
                except Exception:
                    continue
                if pd >= now:
                    upcoming.append((pd, b))

            upcoming.sort(key=lambda x: x[0])

            for pd, b in upcoming:
                notes = b.get('notes') or ''
                artist_name = b.get('username') or ''
                stage = b.get('stage_name') or ''
                duration = f"{b.get('duration_minutes', 60)} min"
                status = b.get('status', '')
                self.events_tree.insert('', 'end', values=(b.get('id'), pd.strftime('%Y-%m-%d %I:%M %p'), artist_name, stage, duration, status, notes))
        except Exception as e:
            # don't crash the UI
            try:
                print(f"Error refreshing events: {e}")
            except Exception:
                pass

    def refresh_available_slots(self):
        """Populate the slot combobox with available performance slots."""
        slots = self.db.get_available_slots()
        if slots:
            self.slot_combo['values'] = [slot['formatted'] for slot in slots]
            self.slot_combo.set("")  # clear selection
        else:
            self.slot_combo['values'] = []
            self.slot_combo.set("No available slots")

    def request_booking(self):
        """Create a new booking request for the artist."""
        selected = self.slot_var.get()
        if not selected:
            messagebox.showwarning("No Slot", "Please select a date and time.")
            return

        # Find the corresponding datetime object
        slots = self.db.get_available_slots()
        selected_slot = None
        for slot in slots:
            if slot['formatted'] == selected:
                selected_slot = slot['datetime']
                break
        if not selected_slot:
            messagebox.showerror("Error", "Selected slot no longer available. Please refresh.")
            return

        notes = self.booking_notes.get("1.0", tk.END).strip()
        try:
            booking_id = self.db.create_booking(self.artist_id, selected_slot, 60, notes, self.user_id)
            messagebox.showinfo("Booking Requested", f"Your booking request (ID: {booking_id}) has been submitted. It will be reviewed by the store.")
            self.refresh_artist_bookings()
            self.refresh_available_slots()
            self.booking_notes.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to request booking: {str(e)}")

    def refresh_artist_bookings(self):
        """Refresh the list of bookings for this artist."""
        if not hasattr(self, 'artist_id'):
            return
        for item in self.artist_booking_tree.get_children():
            self.artist_booking_tree.delete(item)

        bookings = self.db.get_artist_bookings(self.artist_id)
        for booking in bookings:
            self.artist_booking_tree.insert('', 'end', values=(
                booking['id'],
                booking['performance_date'],
                f"{booking['duration_minutes']} min",
                booking['status'],
                booking.get('notes', '')
            ))
    
    def add_to_cart(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to add to cart")
            return
        
        values = self.tree.item(selection[0])['values']
        record_id = values[0]
        record = self.db.get_record(record_id)
        if not record:
            messagebox.showerror("Error", "Record not found")
            return
        
        if record['stock'] <= 0:
            messagebox.showwarning("Out of Stock", "This item is out of stock")
            return
        
        quantity = simpledialog.askinteger("Quantity",
                                         f"How many '{record['album']}' would you like?\nAvailable: {record['stock']}",
                                         minvalue=1,
                                         maxvalue=record['stock'])
        if not quantity:
            return
        
        price = record['price']
        total = price * quantity
        
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
        
        self.update_cart_display()
        messagebox.showinfo("Added to Cart", f"Added {quantity} x '{record['album']}' to cart")
    
    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        self.cart_total = 0
        for item in self.cart:
            self.cart_tree.insert('', 'end', values=(
                item['item'],
                item['quantity'],
                f"£{item['price']:.2f}",
                f"£{item['total']:.2f}"
            ))
            self.cart_total += item['total']
        
        self.total_label.config(text=f"${self.cart_total:.2f}")
    
    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Clear Cart", "Are you sure you want to clear your cart?"):
            self.cart = []
            self.update_cart_display()
    
    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Empty Cart", "Your cart is empty!")
            return

        if self.user.get('username') == 'guest':
            shipping_address = simpledialog.askstring("Shipping Address", "Please enter your shipping address:")
            if not shipping_address:
                return
        else:
            shipping_address = self.user.get('address', '')

        try:
            items = [{'record_id': item['record_id'], 'quantity': item['quantity']} for item in self.cart]
            sale_id = self.db.create_sale(
                customer_id=self.user.get('id'),
                items=items,
                shipping_address=shipping_address
            )
            messagebox.showinfo("Order Placed",
                            f"Thank you for your order!\n\nOrder ID: {sale_id}\nTotal: £{self.cart_total:.2f}\n\nYour records will be shipped soon.")
            self.cart = []
            self.update_cart_display()
            self.refresh_records()
        except Exception as e:
            messagebox.showerror("Checkout Error", f"Failed to process order: {str(e)}")
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            if self.logout_callback:
                self.logout_callback()