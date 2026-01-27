import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

class VinylFlowPrototype:
    def __init__(self, root):
        self.root = root
        self.root.title("VinylFlow Prototype - Record Store")
        self.root.geometry("1000x600")
        
        # Data storage
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.records_file = os.path.join(self.base_dir, "records_inventory.json")
        self.records = self.load_records()
        
        # GUI Setup
        self.setup_styles()
        self.create_widgets()
        self.load_data()
        
    def setup_styles(self):
        """Basic styling for prototype"""
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_widgets(self):
        """Create main interface"""
        # Header
        header = tk.Frame(self.root, bg='#4a6fa5', height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        tk.Label(header, 
                text="💿 VinylFlow - Record Store Prototype", 
                font=('Segoe UI', 20, 'bold'),
                bg='#4a6fa5',
                fg='white').pack(pady=15)
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Add/Edit form
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Records list
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side='right', fill='both')
        right_panel.pack_propagate(False)
        
        self.create_record_form(left_panel)
        self.create_records_list(right_panel)
        
    def create_record_form(self, parent):
        """Create form for adding/editing records"""
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
            
            entry = ttk.Entry(frame, width=30)
            entry.pack(side='left', fill='x', expand=True)
            
            self.form_entries[name] = entry
        
        # Action buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame,
                  text="➕ Add Record",
                  command=self.add_record).pack(side='left', padx=(0, 5))
        
        ttk.Button(btn_frame,
                  text="✏️ Update",
                  command=self.update_record).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="🗑️ Delete",
                  command=self.delete_record).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                  text="🧹 Clear",
                  command=self.clear_form).pack(side='left', padx=5)
    
    def create_records_list(self, parent):
        """Create records list with search"""
        # Search bar
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self.search_records())
        
        # Treeview for records
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ("ID", "Artist", "Album", "Genre", "Year", "Price", "Stock")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
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
                  command=self.refresh_records).pack(side='left', padx=5)
        
        ttk.Button(action_frame,
                  text="📤 Export JSON",
                  command=self.export_json).pack(side='left', padx=5)
        
        ttk.Button(action_frame,
                  text="📥 Load JSON",
                  command=self.import_json).pack(side='left', padx=5)
    
    # Core functionality methods
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
            self.tree.insert('', 'end', values=(
                record['id'],
                record['artist'],
                record['album'],
                record['genre'],
                record['year'],
                f"${record['price']:.2f}",
                record['stock']
            ))
    
    def search_records(self):
        """Search records based on search term"""
        query = self.search_var.get()
        
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
                
                self.tree.insert('', 'end', values=(
                    record['id'],
                    record['artist'],
                    record['album'],
                    record['genre'],
                    record['year'],
                    f"${record['price']:.2f}",
                    record['stock']
                ))
    
    def on_record_select(self, event):
        """Handle record selection"""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0])['values']
            self.load_form_from_record(values)
    
    def load_form_from_record(self, values):
        """Load record data into form"""
        self.form_entries['artist_entry'].delete(0, 'end')
        self.form_entries['artist_entry'].insert(0, values[1])
        
        self.form_entries['album_entry'].delete(0, 'end')
        self.form_entries['album_entry'].insert(0, values[2])
        
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
        
        # Basic validation
        if not data['artist'] or not data['album']:
            messagebox.showwarning("Missing Info", "Artist and Album are required")
            return
        
        # Create record
        record = {
            'id': len(self.records) + 1,
            'artist': data['artist'],
            'album': data['album'],
            'genre': data['genre'],
            'year': int(data['year']) if data['year'].isdigit() else 2024,
            'price': float(data['price']) if data['price'].replace('.', '', 1).isdigit() else 10.0,
            'stock': int(data['stock']) if data['stock'].isdigit() else 1,
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
                record['artist'] = self.form_entries['artist_entry'].get().strip()
                record['album'] = self.form_entries['album_entry'].get().strip()
                record['genre'] = self.form_entries['genre_entry'].get().strip()
                
                try:
                    record['year'] = int(self.form_entries['year_entry'].get().strip())
                    record['price'] = float(self.form_entries['price_entry'].get().strip())
                    record['stock'] = int(self.form_entries['stock_entry'].get().strip())
                except ValueError:
                    pass
                
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
    
    def export_json(self):
        """Export records to JSON file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Records"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.records, f, indent=4)
                messagebox.showinfo("Success", f"Records exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def import_json(self):
        """Import records from JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Records"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported_records = json.load(f)
                
                # Assign new IDs to avoid conflicts
                for record in imported_records:
                    record['id'] = len(self.records) + 1
                    self.records.append(record)
                
                self.save_records()
                self.refresh_records()
                messagebox.showinfo("Success", f"Imported {len(imported_records)} records")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {str(e)}")

def main():
    root = tk.Tk()
    app = VinylFlowPrototype(root)
    root.mainloop()

if __name__ == "__main__":
    main()