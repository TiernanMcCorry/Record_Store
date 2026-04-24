import os
from datetime import datetime
import csv
import sqlite3
from typing import List, Dict, Any, Optional
import hashlib
import shutil

class Database:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, "vinylflow.db")
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enable foreign keys
        cursor.execute('PRAGMA foreign_keys = ON')

        # Records table with soft delete support
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
                deleted_at TIMESTAMP,
                deleted_by INTEGER,
                UNIQUE(artist, album)
            )
        ''')

        # Check if deleted_at column exists; if not, add it (for existing databases)
        cursor.execute("PRAGMA table_info(records)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'deleted_at' not in columns:
            cursor.execute("ALTER TABLE records ADD COLUMN deleted_at TIMESTAMP")
        if 'deleted_by' not in columns:
            cursor.execute("ALTER TABLE records ADD COLUMN deleted_by INTEGER")

        # Customers table with role
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
                is_active BOOLEAN DEFAULT 1,
                role TEXT DEFAULT 'customer'
            )
        ''')

        # Ensure older databases get new columns added if they are missing
        cursor.execute("PRAGMA table_info(customers)")
        existing_cols = [col[1] for col in cursor.fetchall()]
        # Define columns we expect and their SQL definitions (safe defaults)
        expected_customer_cols = {
            'password_hash': 'TEXT',
            'email': 'TEXT',
            'full_name': 'TEXT',
            'address': 'TEXT',
            'phone': 'TEXT',
            'registration_date': "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            'is_active': "BOOLEAN DEFAULT 1",
            'role': "TEXT DEFAULT 'customer'"
        }
        for col_name, col_def in expected_customer_cols.items():
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_def}")
                except Exception:
                    # If adding a column fails for any reason, continue; it's non-fatal for seeding
                    pass

        # Artists table (extends customers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                stage_name TEXT,
                bio TEXT,
                genre TEXT,
                website TEXT,
                phone TEXT,
                is_approved BOOLEAN DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')

        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER NOT NULL,
                performance_date TIMESTAMP NOT NULL,
                duration_minutes INTEGER DEFAULT 60,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (artist_id) REFERENCES artists(id)
            )
        ''')

        # Sales tables
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

        # Audit log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                table_name TEXT,
                record_id INTEGER,
                old_data TEXT,
                new_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Indexes (now safe because deleted_at exists)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_artist ON records(artist)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_genre ON records(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_deleted ON records(deleted_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(performance_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)')

        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def log_audit(self, user_id: int, action: str, table_name: str, record_id: int = None,
                  old_data: dict = None, new_data: dict = None):
        """Log an action in the audit log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_log (user_id, action, table_name, record_id, old_data, new_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, action, table_name, record_id,
              str(old_data) if old_data else None,
              str(new_data) if new_data else None))
        conn.commit()
        conn.close()
    
    # ---------- Record methods (with soft delete) ----------
    def add_record(self, record: Dict, user_id: int = None) -> int:
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
        
        if user_id:
            self.log_audit(user_id, 'INSERT', 'records', record_id, None, record)
        return record_id
    
    def update_record(self, record_id: int, updates: Dict, user_id: int = None) -> bool:
        """Update an existing record"""
        if not updates:
            return False
        
        # Get old data for audit
        old_data = self.get_record(record_id)
        if not old_data:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values())
        values.append(record_id)
        
        cursor.execute(f'UPDATE records SET {set_clause} WHERE id=?', values)
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if rows_affected > 0 and user_id:
            self.log_audit(user_id, 'UPDATE', 'records', record_id, old_data, updates)
        return rows_affected > 0
    
    def delete_record(self, record_id: int, user_id: int = None) -> bool:
        """Soft delete a record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get old data for audit
        old_data = self.get_record(record_id)
        if not old_data:
            conn.close()
            return False
        
        cursor.execute('''
            UPDATE records SET deleted_at = CURRENT_TIMESTAMP, deleted_by = ?
            WHERE id = ?
        ''', (user_id, record_id))
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if rows_affected > 0 and user_id:
            self.log_audit(user_id, 'SOFT_DELETE', 'records', record_id, old_data, None)
        return rows_affected > 0
    
    def restore_record(self, record_id: int, user_id: int = None) -> bool:
        """Restore a soft‑deleted record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE records SET deleted_at = NULL, deleted_by = NULL
            WHERE id = ?
        ''', (record_id,))
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if rows_affected > 0 and user_id:
            self.log_audit(user_id, 'RESTORE', 'records', record_id, None, None)
        return rows_affected > 0
    
    def get_record(self, record_id: int) -> Optional[Dict]:
        """Get a single record by ID (excluding deleted)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM records WHERE id=? AND deleted_at IS NULL', (record_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_records(self, limit: int = None, offset: int = 0, include_deleted: bool = False) -> List[Dict]:
        """Get all records, optionally including deleted ones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM records'
        if not include_deleted:
            query += ' WHERE deleted_at IS NULL'
        query += ' ORDER BY artist, album'
        if limit:
            query += f' LIMIT {limit} OFFSET {offset}'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_deleted_records(self) -> List[Dict]:
        """Get all soft‑deleted records"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM records WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_records(self, query: str, limit: int = 50) -> List[Dict]:
        """Search records by artist, album, or genre (excluding deleted)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT * FROM records 
            WHERE (artist LIKE ? OR album LIKE ? OR genre LIKE ?)
            AND deleted_at IS NULL
            ORDER BY artist, album
            LIMIT ?
        ''', (search_pattern, search_pattern, search_pattern, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ---------- Artist methods ----------
    def register_artist(self, customer_id: int, artist_data: Dict) -> int:
        """Create an artist profile for an existing customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO artists (customer_id, stage_name, bio, genre, website, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            customer_id,
            artist_data.get('stage_name', ''),
            artist_data.get('bio', ''),
            artist_data.get('genre', ''),
            artist_data.get('website', ''),
            artist_data.get('phone', '')
        ))
        
        artist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return artist_id
    
    def get_artist_by_customer_id(self, customer_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM artists WHERE customer_id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_artist_by_id(self, artist_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM artists WHERE id = ?', (artist_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_artists(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, c.username, c.email, c.full_name
            FROM artists a
            JOIN customers c ON a.customer_id = c.id
            ORDER BY a.stage_name
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_artist(self, artist_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM artists WHERE id = ?', (artist_id,))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0
    
    # ---------- Booking methods ----------
    def get_available_slots(self, from_date: datetime = None, to_date: datetime = None) -> List[Dict]:
        """Return available time slots (every 60 minutes, 10am-8pm, next 30 days)"""
        if from_date is None:
            from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if to_date is None:
            to_date = from_date.replace(day=from_date.day + 30)
        
        # Generate all slots in the range (simple: every day, 10am-8pm in 1h slots)
        slots = []
        current = from_date
        while current <= to_date:
            for hour in range(10, 20):  # 10am to 7pm (8pm start is 20)
                slot_time = current.replace(hour=hour, minute=0, second=0, microsecond=0)
                if slot_time > datetime.now():
                    slots.append({
                        'datetime': slot_time,
                        'formatted': slot_time.strftime('%Y-%m-%d %I:%M %p')
                    })
            current = current.replace(day=current.day + 1)
        
        # Remove already booked slots (pending or confirmed)
        booked = self.get_booked_slots(from_date, to_date)
        available = [s for s in slots if s['datetime'] not in booked]
        return available
    
    def get_booked_slots(self, from_date: datetime, to_date: datetime) -> List[datetime]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT performance_date FROM bookings
            WHERE status IN ('pending', 'confirmed')
            AND performance_date BETWEEN ? AND ?
        ''', (from_date, to_date))
        rows = cursor.fetchall()
        conn.close()
        return [datetime.fromisoformat(row[0]) for row in rows]
    
    def create_booking(self, artist_id: int, performance_date: datetime, duration_minutes: int = 60,
                       notes: str = "", user_id: int = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookings (artist_id, performance_date, duration_minutes, notes, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (artist_id, performance_date, duration_minutes, notes))
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if user_id:
            self.log_audit(user_id, 'INSERT', 'bookings', booking_id, None, {
                'artist_id': artist_id,
                'performance_date': str(performance_date)
            })
        return booking_id
    
    def get_artist_bookings(self, artist_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bookings
            WHERE artist_id = ?
            ORDER BY performance_date DESC
        ''', (artist_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_all_bookings(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, a.stage_name, c.username
            FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN customers c ON a.customer_id = c.id
            ORDER BY b.performance_date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_booking_status(self, booking_id: int, status: str, user_id: int = None) -> bool:
        allowed = ['pending', 'confirmed', 'completed', 'cancelled']
        if status not in allowed:
            raise ValueError(f"Invalid status. Choose from {allowed}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE bookings SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, booking_id))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows > 0 and user_id:
            self.log_audit(user_id, 'UPDATE', 'bookings', booking_id,
                           {'old_status': '?'}, {'new_status': status})
        return rows > 0
    
    # ---------- Customer methods ----------
    def register_customer(self, customer_data: Dict) -> int:
        """Register a new customer with hashed password"""
        if self.get_customer_by_username(customer_data['username']):
            raise ValueError("Username already exists")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers (username, password_hash, email, full_name, address, phone, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_data['username'],
            self._hash_password(customer_data['password']),
            customer_data.get('email', ''),
            customer_data.get('full_name', ''),
            customer_data.get('address', ''),
            customer_data.get('phone', ''),
            customer_data.get('role', 'customer')
        ))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id
    
    def get_customer_by_username(self, username: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def authenticate_customer(self, username: str, password: str) -> Optional[Dict]:
        customer = self.get_customer_by_username(username)
        if not customer:
            return None
        if customer['password_hash'] == self._hash_password(password):
            customer.pop('password_hash', None)
            return customer
        return None
    
    # ---------- Sales methods (unchanged) ----------
    def create_sale(self, customer_id: int, items: List[Dict], shipping_address: str = "") -> int:
        # (same as before)
        if not items:
            raise ValueError("Sale must contain at least one item")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('BEGIN TRANSACTION')
            total_amount = 0
            for item in items:
                record_id = item['record_id']
                quantity = item['quantity']
                cursor.execute('SELECT price, stock FROM records WHERE id=?', (record_id,))
                record = cursor.fetchone()
                if not record:
                    raise ValueError(f"Record {record_id} not found")
                price, stock = record
                if stock < quantity:
                    raise ValueError(f"Insufficient stock for record {record_id}")
                total_amount += price * quantity
            
            cursor.execute('''
                INSERT INTO sales (customer_id, total_amount, shipping_address)
                VALUES (?, ?, ?)
            ''', (customer_id, total_amount, shipping_address))
            sale_id = cursor.lastrowid
            
            for item in items:
                record_id = item['record_id']
                quantity = item['quantity']
                cursor.execute('SELECT price FROM records WHERE id=?', (record_id,))
                price = cursor.fetchone()[0]
                cursor.execute('''
                    INSERT INTO sale_items (sale_id, record_id, quantity, price_at_time)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, record_id, quantity, price))
                cursor.execute('UPDATE records SET stock = stock - ? WHERE id=?', (quantity, record_id))
            
            conn.commit()
            return sale_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_customer_sales(self, customer_id: int) -> List[Dict]:
        # (same as before)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, COUNT(si.id) as item_count
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
        # (same as before)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sales WHERE id=?', (sale_id,))
        sale = cursor.fetchone()
        if not sale:
            conn.close()
            return {}
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
    
    # ---------- Statistics (unchanged) ----------
    def get_statistics(self) -> Dict:
        # (same as before, but now ignoring deleted records)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        stats = {}
        cursor.execute('SELECT COUNT(*) as count, SUM(stock) as total_stock FROM records WHERE deleted_at IS NULL')
        record_stats = cursor.fetchone()
        stats['total_records'] = record_stats['count'] or 0
        stats['total_stock'] = record_stats['total_stock'] or 0
        
        cursor.execute('SELECT SUM(price * stock) as total_value FROM records WHERE deleted_at IS NULL')
        stats['total_value'] = cursor.fetchone()['total_value'] or 0
        
        cursor.execute('SELECT AVG(price) as avg_price FROM records WHERE deleted_at IS NULL')
        stats['avg_price'] = cursor.fetchone()['avg_price'] or 0
        
        # Genre distribution
        cursor.execute('''
            SELECT genre, COUNT(*) as count FROM records
            WHERE genre IS NOT NULL AND genre != '' AND deleted_at IS NULL
            GROUP BY genre ORDER BY count DESC
        ''')
        stats['genre_distribution'] = {row['genre']: row['count'] for row in cursor.fetchall()}
        
        # Low stock (stock <=5 and >0)
        cursor.execute('SELECT * FROM records WHERE stock > 0 AND stock <= 5 AND deleted_at IS NULL')
        stats['low_stock'] = [dict(row) for row in cursor.fetchall()]
        cursor.execute('SELECT * FROM records WHERE stock = 0 AND deleted_at IS NULL')
        stats['out_of_stock'] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM records WHERE deleted_at IS NULL ORDER BY price DESC LIMIT 1')
        most = cursor.fetchone()
        stats['most_expensive'] = dict(most) if most else None
        cursor.execute('SELECT * FROM records WHERE deleted_at IS NULL ORDER BY price ASC LIMIT 1')
        least = cursor.fetchone()
        stats['least_expensive'] = dict(least) if least else None
        
        # Sales statistics (ignore deleted records? sales unaffected)
        cursor.execute('''
            SELECT COUNT(*) as total_sales_count, SUM(total_amount) as total_sales_amount,
                   AVG(total_amount) as avg_sale_value
            FROM sales WHERE status != 'cancelled'
        ''')
        sales_stats = cursor.fetchone()
        stats['total_sales_count'] = sales_stats['total_sales_count'] or 0
        stats['total_sales_amount'] = sales_stats['total_sales_amount'] or 0
        stats['avg_sale_value'] = sales_stats['avg_sale_value'] or 0
        
        conn.close()
        return stats
    
    # ---------- Export / Import / Backup ----------
    def export_to_csv(self, filename: str, data_type: str = 'records'):
        # (unchanged but works with current tables)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if data_type == 'records':
            cursor.execute('SELECT id, artist, album, genre, year, price, stock, date_added FROM records WHERE deleted_at IS NULL ORDER BY artist, album')
            fieldnames = ['id', 'artist', 'album', 'genre', 'year', 'price', 'stock', 'date_added']
        elif data_type == 'customers':
            cursor.execute('SELECT id, username, email, full_name, address, phone, registration_date, is_active, role FROM customers')
            fieldnames = ['id', 'username', 'email', 'full_name', 'address', 'phone', 'registration_date', 'is_active', 'role']
        elif data_type == 'sales':
            cursor.execute('''
                SELECT s.*, c.username, c.email
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                ORDER BY s.sale_date DESC
            ''')
            fieldnames = ['id', 'customer_id', 'sale_date', 'total_amount', 'status', 'shipping_address', 'username', 'email']
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
        # (unchanged)
        imported_count = 0
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    if data_type == 'records':
                        record = {
                            'artist': row['artist'].strip(),
                            'album': row['album'].strip(),
                            'genre': row.get('genre', '').strip(),
                            'year': int(row.get('year', 0)),
                            'price': float(row['price']),
                            'stock': int(row.get('stock', 0))
                        }
                        self.add_record(record)
                        imported_count += 1
                    elif data_type == 'customers':
                        customer = {
                            'username': row['username'].strip(),
                            'password': row.get('password', 'default123'),
                            'email': row.get('email', ''),
                            'full_name': row.get('full_name', ''),
                            'address': row.get('address', ''),
                            'phone': row.get('phone', ''),
                            'role': row.get('role', 'customer')
                        }
                        try:
                            self.register_customer(customer)
                            imported_count += 1
                        except ValueError:
                            continue
                except (ValueError, KeyError):
                    continue
        return imported_count
    
    def backup_database(self, backup_path: str = None) -> str:
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.base_dir, f"vinylflow_backup_{timestamp}.db")
        shutil.copy2(self.db_path, backup_path)
        return backup_path