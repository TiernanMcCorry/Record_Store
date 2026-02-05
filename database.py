import os
from datetime import datetime
import csv
import sqlite3
from typing import List, Dict, Any, Optional
import hashlib  # For password hashing

class Database:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, "vinylflow.db")
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create records table
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
        
        # Create customers table with proper password hashing
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
        
        # Create sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL,
                status TEXT DEFAULT 'pending',
                shipping_address TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # Create sale items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                record_id INTEGER,
                quantity INTEGER,
                price_at_time REAL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (record_id) REFERENCES records(id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_artist ON records(artist)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_genre ON records(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def add_record(self, record: Dict) -> int:
        """Add a new record to the database"""
        required_fields = ['artist', 'album', 'price']
        for field in required_fields:
            if field not in record:
                raise ValueError(f"Missing required field: {field}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO records (artist, album, genre, year, price, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            record['artist'],
            record['album'],
            record.get('genre', ''),
            record.get('year', 0),
            record['price'],
            record.get('stock', 0)
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def update_record(self, record_id: int, updates: Dict) -> bool:
        """Update an existing record"""
        if not updates:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values())
        values.append(record_id)
        
        cursor.execute(f'''
            UPDATE records SET {set_clause} WHERE id=?
        ''', values)
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def delete_record(self, record_id: int) -> bool:
        """Delete a record from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM records WHERE id=?', (record_id,))
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def get_record(self, record_id: int) -> Optional[Dict]:
        """Get a single record by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM records WHERE id=?', (record_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_records(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """Get all records with optional pagination"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM records ORDER BY artist, album'
        if limit:
            query += f' LIMIT {limit} OFFSET {offset}'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_records(self, query: str, limit: int = 50) -> List[Dict]:
        """Search records by artist, album, or genre using SQL LIKE"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT * FROM records 
            WHERE artist LIKE ? OR album LIKE ? OR genre LIKE ?
            ORDER BY artist, album
            LIMIT ?
        ''', (search_pattern, search_pattern, search_pattern, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def register_customer(self, customer_data: Dict) -> int:
        """Register a new customer with hashed password"""
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in customer_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if username exists
        if self.get_customer_by_username(customer_data['username']):
            raise ValueError("Username already exists")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers 
            (username, password_hash, email, full_name, address, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            customer_data['username'],
            self._hash_password(customer_data['password']),
            customer_data.get('email', ''),
            customer_data.get('full_name', ''),
            customer_data.get('address', ''),
            customer_data.get('phone', '')
        ))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return customer_id
    
    def get_customer_by_username(self, username: str) -> Optional[Dict]:
        """Get customer by username"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers WHERE username=?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def authenticate_customer(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate customer login"""
        customer = self.get_customer_by_username(username)
        if not customer:
            return None
        
        # Verify password hash
        if customer['password_hash'] == self._hash_password(password):
            # Remove password hash from returned dict for security
            customer.pop('password_hash', None)
            return customer
        
        return None
    
    def create_sale(self, customer_id: int, items: List[Dict], 
                     shipping_address: str = "") -> int:
        """Create a new sale with transaction support"""
        if not items:
            raise ValueError("Sale must contain at least one item")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Begin transaction
            cursor.execute('BEGIN TRANSACTION')
            
            # Calculate total and verify stock
            total_amount = 0
            for item in items:
                record_id = item['record_id']
                quantity = item['quantity']
                
                # Get current price and stock
                cursor.execute('SELECT price, stock FROM records WHERE id=?', (record_id,))
                record = cursor.fetchone()
                
                if not record:
                    raise ValueError(f"Record {record_id} not found")
                
                price, stock = record
                
                if stock < quantity:
                    raise ValueError(f"Insufficient stock for record {record_id}")
                
                total_amount += price * quantity
            
            # Create sale
            cursor.execute('''
                INSERT INTO sales (customer_id, total_amount, shipping_address)
                VALUES (?, ?, ?)
            ''', (customer_id, total_amount, shipping_address))
            
            sale_id = cursor.lastrowid
            
            # Add sale items and update stock
            for item in items:
                record_id = item['record_id']
                quantity = item['quantity']
                
                # Get current price
                cursor.execute('SELECT price FROM records WHERE id=?', (record_id,))
                price = cursor.fetchone()[0]
                
                # Add sale item
                cursor.execute('''
                    INSERT INTO sale_items (sale_id, record_id, quantity, price_at_time)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, record_id, quantity, price))
                
                # Update stock
                cursor.execute('''
                    UPDATE records SET stock = stock - ? WHERE id=?
                ''', (quantity, record_id))
            
            # Commit transaction
            conn.commit()
            return sale_id
            
        except Exception as e:
            # Rollback on error
            conn.rollback()
            raise e
            
        finally:
            conn.close()
    
    def get_customer_sales(self, customer_id: int) -> List[Dict]:
        """Get all sales for a specific customer"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, 
                   COUNT(si.id) as item_count,
                   GROUP_CONCAT(si.record_id) as record_ids
            FROM sales s
            LEFT JOIN sale_items si ON s.id = si.sale_id
            WHERE s.customer_id = ?
            GROUP BY s.id
            ORDER BY s.sale_date DESC
        ''', (customer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_sale_details(self, sale_id: int) -> Dict:
        """Get sale details with items"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get sale info
        cursor.execute('SELECT * FROM sales WHERE id=?', (sale_id,))
        sale = cursor.fetchone()
        
        if not sale:
            conn.close()
            return {}
        
        # Get sale items with record details
        cursor.execute('''
            SELECT si.*, r.artist, r.album, r.genre
            FROM sale_items si
            JOIN records r ON si.record_id = r.id
            WHERE si.sale_id = ?
        ''', (sale_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        result = dict(sale)
        result['items'] = [dict(item) for item in items]
        
        return result
    
    def export_to_csv(self, filename: str, data_type: str = 'records'):
        """Export data to CSV file"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if data_type == 'records':
            cursor.execute('SELECT * FROM records ORDER BY artist, album')
            fieldnames = ['id', 'artist', 'album', 'genre', 'year', 'price', 'stock', 'date_added']
        elif data_type == 'customers':
            cursor.execute('''
                SELECT id, username, email, full_name, address, phone, registration_date, is_active
                FROM customers ORDER BY registration_date
            ''')
            fieldnames = ['id', 'username', 'email', 'full_name', 'address', 'phone', 
                         'registration_date', 'is_active']
        elif data_type == 'sales':
            cursor.execute('''
                SELECT s.*, c.username, c.email
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                ORDER BY s.sale_date DESC
            ''')
            fieldnames = ['id', 'customer_id', 'sale_date', 'total_amount', 'status', 
                         'shipping_address', 'username', 'email']
        else:
            conn.close()
            raise ValueError(f"Unknown data type: {data_type}")
        
        rows = cursor.fetchall()
        conn.close()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))
    
    def import_from_csv(self, filename: str, data_type: str = 'records') -> int:
        """Import data from CSV file"""
        imported_count = 0
        
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    if data_type == 'records':
                        record = {
                            'artist': row['artist'].strip(),
                            'album': row['album'].strip(),
                            'genre': row['genre'].strip() if 'genre' in row else '',
                            'year': int(row['year']) if 'year' in row and row['year'] else 0,
                            'price': float(row['price']),
                            'stock': int(row['stock']) if 'stock' in row else 0
                        }
                        self.add_record(record)
                        imported_count += 1
                    
                    elif data_type == 'customers':
                        customer = {
                            'username': row['username'].strip(),
                            'password': row.get('password', 'default123'),  # Default password
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
                
                except (ValueError, KeyError) as e:
                    print(f"Error importing row: {e}")
                    continue
        
        return imported_count
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics using SQL queries"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        stats = {}
        
        # Basic counts
        cursor.execute('SELECT COUNT(*) as count, SUM(stock) as total_stock FROM records')
        record_stats = cursor.fetchone()
        stats['total_records'] = record_stats['count']
        stats['total_stock'] = record_stats['total_stock'] or 0
        
        # Total inventory value
        cursor.execute('SELECT SUM(price * stock) as total_value FROM records')
        stats['total_value'] = cursor.fetchone()['total_value'] or 0
        
        # Average price
        cursor.execute('SELECT AVG(price) as avg_price FROM records')
        stats['avg_price'] = cursor.fetchone()['avg_price'] or 0
        
        # Genre distribution
        cursor.execute('''
            SELECT genre, COUNT(*) as count 
            FROM records 
            WHERE genre IS NOT NULL AND genre != ''
            GROUP BY genre 
            ORDER BY count DESC
        ''')
        stats['genre_distribution'] = {row['genre']: row['count'] for row in cursor.fetchall()}
        
        # Year distribution
        cursor.execute('''
            SELECT year, COUNT(*) as count 
            FROM records 
            WHERE year > 0
            GROUP BY year 
            ORDER BY year DESC
        ''')
        stats['year_distribution'] = {row['year']: row['count'] for row in cursor.fetchall()}
        
        # Stock alerts
        cursor.execute('SELECT * FROM records WHERE stock = 0')
        stats['out_of_stock'] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM records WHERE stock > 0 AND stock <= 5')
        stats['low_stock'] = [dict(row) for row in cursor.fetchall()]
        
        # Most/Least expensive
        cursor.execute('SELECT * FROM records ORDER BY price DESC LIMIT 1')
        most_expensive = cursor.fetchone()
        stats['most_expensive'] = dict(most_expensive) if most_expensive else None
        
        cursor.execute('SELECT * FROM records ORDER BY price ASC LIMIT 1')
        least_expensive = cursor.fetchone()
        stats['least_expensive'] = dict(least_expensive) if least_expensive else None
        
        # Sales statistics - FIXED: Correct column aliases
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sales_count,
                SUM(total_amount) as total_sales_amount,
                AVG(total_amount) as avg_sale_value
            FROM sales 
            WHERE status != 'cancelled'
        ''')
        sales_stats = cursor.fetchone()
        stats['total_sales_count'] = sales_stats['total_sales_count'] or 0
        stats['total_sales_amount'] = sales_stats['total_sales_amount'] or 0
        stats['avg_sale_value'] = sales_stats['avg_sale_value'] or 0
        
        conn.close()
        return stats
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.base_dir, f"backup_{timestamp}.db")
        
        # Simple backup by copying the database file
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def execute_query(self, query: str, parameters: tuple = None) -> List[Dict]:
        """Execute a custom SQL query (for advanced users)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            
            conn.commit()
            return result
            
        except sqlite3.Error as e:
            raise e
        finally:
            conn.close()