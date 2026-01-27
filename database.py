import json
import os
from datetime import datetime
import csv
import sqlite3
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.records_file = os.path.join(base_dir, "records_inventory.json")
        self.customers_file = os.path.join(base_dir, "customers.json")
        self.orders_file = os.path.join(base_dir, "orders.json")
        self.records = self._load_records()
        self.customers = self._load_customers()
        self.orders = self._load_orders()
        
        # SQLite setup (optional, for better performance)
        self.db_path = os.path.join(base_dir, "vinylflow.db")
        self.init_sqlite()
    
    def init_sqlite(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist TEXT NOT NULL,
                album TEXT NOT NULL,
                genre TEXT,
                year INTEGER,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(artist, album)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                address TEXT,
                phone TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL,
                status TEXT DEFAULT 'pending',
                shipping_address TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                record_id INTEGER,
                quantity INTEGER,
                price_at_time REAL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (record_id) REFERENCES records(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_records(self) -> List[Dict]:
        """Load records from JSON file"""
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_customers(self) -> List[Dict]:
        """Load customers from JSON file"""
        if os.path.exists(self.customers_file):
            try:
                with open(self.customers_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_orders(self) -> List[Dict]:
        """Load orders from JSON file"""
        if os.path.exists(self.orders_file):
            try:
                with open(self.orders_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_records(self):
        """Save records to JSON file"""
        with open(self.records_file, 'w') as f:
            json.dump(self.records, f, indent=4)
    
    def save_customers(self):
        """Save customers to JSON file"""
        with open(self.customers_file, 'w') as f:
            json.dump(self.customers, f, indent=4)
    
    def save_orders(self):
        """Save orders to JSON file"""
        with open(self.orders_file, 'w') as f:
            json.dump(self.orders, f, indent=4)
    
    def add_record(self, record: Dict) -> Dict:
        """Add a new record with validation"""
        # Generate ID if not present
        if 'id' not in record:
            record['id'] = len(self.records) + 1
        
        record['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.records.append(record)
        self.save_records()
        
        # Also add to SQLite
        self._add_record_to_sqlite(record)
        
        return record
    
    def _add_record_to_sqlite(self, record: Dict):
        """Add record to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO records 
            (id, artist, album, genre, year, price, stock, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.get('id'),
            record['artist'],
            record['album'],
            record.get('genre', ''),
            record.get('year', 0),
            record['price'],
            record['stock'],
            record.get('date_added', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ))
        
        conn.commit()
        conn.close()
    
    def update_record(self, record_id: int, updates: Dict) -> bool:
        """Update an existing record"""
        for record in self.records:
            if record['id'] == record_id:
                record.update(updates)
                self.save_records()
                self._update_record_sqlite(record_id, updates)
                return True
        return False
    
    def _update_record_sqlite(self, record_id: int, updates: Dict):
        """Update record in SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values())
        values.append(record_id)
        
        cursor.execute(f'''
            UPDATE records SET {set_clause} WHERE id=?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def delete_record(self, record_id: int) -> bool:
        """Delete a record"""
        for i, record in enumerate(self.records):
            if record['id'] == record_id:
                del self.records[i]
                self.save_records()
                self._delete_record_sqlite(record_id)
                return True
        return False
    
    def _delete_record_sqlite(self, record_id: int):
        """Delete record from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM records WHERE id=?', (record_id,))
        conn.commit()
        conn.close()
    
    def search_records(self, query: str) -> List[Dict]:
        """Search records by artist, album, or genre"""
        query = query.lower()
        results = []
        
        for record in self.records:
            if (query in record['artist'].lower() or
                query in record['album'].lower() or
                query in record['genre'].lower()):
                results.append(record)
        
        return results
    
    def register_customer(self, customer_data: Dict) -> Dict:
        """Register a new customer"""
        # Check if username exists
        for customer in self.customers:
            if customer['username'] == customer_data['username']:
                raise ValueError("Username already exists")
        
        customer_data['id'] = len(self.customers) + 1
        customer_data['registration_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        customer_data['is_active'] = True
        
        self.customers.append(customer_data)
        self.save_customers()
        
        # Add to SQLite
        self._add_customer_to_sqlite(customer_data)
        
        return customer_data
    
    def _add_customer_to_sqlite(self, customer: Dict):
        """Add customer to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers 
            (username, password_hash, email, full_name, address, phone, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer['username'],
            customer['password'],  # In production, use hashed password
            customer.get('email', ''),
            customer.get('full_name', ''),
            customer.get('address', ''),
            customer.get('phone', ''),
            customer.get('registration_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ))
        
        conn.commit()
        conn.close()
    
    def authenticate_customer(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate customer login"""
        for customer in self.customers:
            if (customer['username'] == username and 
                customer['password'] == password and
                customer.get('is_active', True)):
                return customer
        return None
    
    def create_order(self, customer_id: int, items: List[Dict], shipping_address: str = "") -> Dict:
        """Create a new order"""
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in items)
        
        order = {
            'id': len(self.orders) + 1,
            'customer_id': customer_id,
            'order_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_amount': total,
            'status': 'pending',
            'shipping_address': shipping_address,
            'items': items
        }
        
        self.orders.append(order)
        self.save_orders()
        
        # Update stock
        for item in items:
            self.decrease_stock(item['record_id'], item['quantity'])
        
        return order
    
    def decrease_stock(self, record_id: int, quantity: int) -> bool:
        """Decrease stock quantity"""
        for record in self.records:
            if record['id'] == record_id:
                if record['stock'] >= quantity:
                    record['stock'] -= quantity
                    self.save_records()
                    return True
                else:
                    raise ValueError(f"Insufficient stock for record {record_id}")
        return False
    
    def export_to_csv(self, filename: str, data_type: str = 'records'):
        """Export data to CSV file"""
        if data_type == 'records':
            data = self.records
            fieldnames = ['id', 'artist', 'album', 'genre', 'year', 'price', 'stock', 'date_added']
        elif data_type == 'customers':
            data = self.customers
            fieldnames = ['id', 'username', 'email', 'full_name', 'address', 'phone', 'registration_date']
        elif data_type == 'orders':
            data = self.orders
            fieldnames = ['id', 'customer_id', 'order_date', 'total_amount', 'status', 'shipping_address']
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                # Filter only the fields we want
                filtered_item = {k: item.get(k, '') for k in fieldnames}
                writer.writerow(filtered_item)
    
    def import_from_csv(self, filename: str, data_type: str = 'records'):
        """Import data from CSV file"""
        imported_count = 0
        
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                if data_type == 'records':
                    # Convert data types
                    record = {
                        'artist': row['artist'].strip(),
                        'album': row['album'].strip(),
                        'genre': row['genre'].strip(),
                        'year': int(row['year']),
                        'price': float(row['price']),
                        'stock': int(row['stock'])
                    }
                    self.add_record(record)
                    imported_count += 1
                
                elif data_type == 'customers':
                    customer = {
                        'username': row['username'].strip(),
                        'password': row.get('password', ''),
                        'email': row.get('email', ''),
                        'full_name': row.get('full_name', ''),
                        'address': row.get('address', ''),
                        'phone': row.get('phone', '')
                    }
                    try:
                        self.register_customer(customer)
                        imported_count += 1
                    except ValueError:
                        continue
        
        return imported_count
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        if not self.records:
            return {}
        
        stats = {
            'total_records': len(self.records),
            'total_stock': sum(r['stock'] for r in self.records),
            'total_value': sum(r['price'] * r['stock'] for r in self.records),
            'avg_price': sum(r['price'] for r in self.records) / len(self.records),
            'genre_distribution': {},
            'year_distribution': {},
            'low_stock': [],
            'out_of_stock': []
        }
        
        # Genre distribution
        for record in self.records:
            genre = record['genre']
            stats['genre_distribution'][genre] = stats['genre_distribution'].get(genre, 0) + 1
            
            # Year distribution
            year = record['year']
            stats['year_distribution'][year] = stats['year_distribution'].get(year, 0) + 1
            
            # Stock alerts
            if record['stock'] == 0:
                stats['out_of_stock'].append(record)
            elif record['stock'] <= 5:
                stats['low_stock'].append(record)
        
        # Most expensive
        if self.records:
            stats['most_expensive'] = max(self.records, key=lambda x: x['price'])
            stats['least_expensive'] = min(self.records, key=lambda x: x['price'])
        
        return stats