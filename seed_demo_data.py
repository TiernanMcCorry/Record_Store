"""
Seed script for Record_Store-main (VinylFlow) demo data.

Creates demo customers (matching quick-login credentials), artist profiles,
records, bookings, and a couple of sales. Safe to run multiple times; existing
usernames are skipped. Backs up the existing SQLite DB before modifying it.

Run:
    python seed_demo_data.py

"""
import os
import shutil
from datetime import datetime, timedelta
import random

from database import Database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vinylflow.db")


def backup_db():
    if os.path.exists(DB_PATH):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(BASE_DIR, f"vinylflow_backup_{ts}.db")
        shutil.copy2(DB_PATH, backup_path)
        print(f"Backed up existing DB to: {backup_path}")
    else:
        print("No existing DB found; a new database will be created.")


def seed():
    backup_db()

    db = Database(BASE_DIR)

    # Demo customers to ensure quick-login works as coded in auth_window.py
    demo_customers = [
        {
            'username': 'Tiernan123',
            'password': '123456',
            'email': 'tiernan@example.com',
            'full_name': 'Tiernan O',
            'address': '12 Vinyl Ave',
            'phone': '07123456789',
            'role': 'customer'
        },
        {
            'username': 'kokilumi',
            'password': 'Shea123',
            'email': 'koki@example.com',
            'full_name': 'Koki Lumi',
            'address': '34 Groove St',
            'phone': '07900111222',
            'role': 'artist'
        },
    ]

    extra_customers = []
    # generate a few more customers
    for i in range(1, 8):
        extra_customers.append({
            'username': f'user{i}',
            'password': f'pass{i}!',
            'email': f'user{i}@example.com',
            'full_name': f'Demo User {i}',
            'address': f'{i} Example Road',
            'phone': f'07000000{i:02d}',
            'role': 'customer'
        })

    all_customers = demo_customers + extra_customers

    created_customers = {}
    for c in all_customers:
        try:
            cid = db.register_customer(c)
            created_customers[c['username']] = cid
            print(f"Created customer: {c['username']} (id={cid})")
        except ValueError:
            # Already exists: fetch id
            existing = db.get_customer_by_username(c['username'])
            if existing:
                created_customers[c['username']] = existing['id']
                print(f"Skipped (exists): {c['username']} (id={existing['id']})")

    # Create artist profile for kokilumi (if role is artist)
    if 'kokilumi' in created_customers:
        koki_id = created_customers['kokilumi']
        artist = db.get_artist_by_customer_id(koki_id)
        if not artist:
            artist_data = {
                'stage_name': 'Koki Lumi',
                'bio': 'Experimental electronic artist from the demo dataset.',
                'genre': 'Electronic',
                'website': 'https://example.com/koki',
                'phone': '07900111222'
            }
            artist_id = db.register_artist(koki_id, artist_data)
            print(f"Created artist profile for kokilumi -> artist_id={artist_id}")
        else:
            print(f"Artist profile already exists for kokilumi (artist id={artist['id']})")

    # Add a mixture of records
    sample_records = [
        {'artist': 'Koki Lumi', 'album': 'Neon Nights', 'genre': 'Electronic', 'year': 2021, 'price': 24.99, 'stock': 12},
        {'artist': 'The Sundials', 'album': 'Morning Breeze', 'genre': 'Folk', 'year': 2018, 'price': 19.99, 'stock': 5},
        {'artist': 'Velvet Echo', 'album': 'Midnight Bloom', 'genre': 'Soul', 'year': 2019, 'price': 21.50, 'stock': 8},
        {'artist': 'Retro Kids', 'album': 'Arcade Love', 'genre': 'Pop', 'year': 2016, 'price': 17.00, 'stock': 2},
        {'artist': 'Blue Horizon', 'album': 'Oceanic Dreams', 'genre': 'Jazz', 'year': 2020, 'price': 26.00, 'stock': 4},
        {'artist': 'Old School', 'album': 'Golden Days', 'genre': 'Rock', 'year': 1975, 'price': 39.99, 'stock': 1},
        {'artist': 'Synth Alley', 'album': 'Pulse', 'genre': 'Electronic', 'year': 2022, 'price': 22.00, 'stock': 10},
        {'artist': 'Various Artists', 'album': 'Live at FirstPress', 'genre': 'Compilation', 'year': 2024, 'price': 15.00, 'stock': 20},
    ]

    record_ids = []
    for rec in sample_records:
        try:
            rid = db.add_record(rec)
            record_ids.append(rid)
            print(f"Added record: {rec['artist']} - {rec['album']} (id={rid})")
        except Exception as e:
            # If duplicate (unique artist+album), try to fetch existing
            try:
                rows = db.search_records(rec['album'])
                if rows:
                    existing = next((r for r in rows if r['artist'] == rec['artist'] and r['album'] == rec['album']), None)
                    if existing:
                        record_ids.append(existing['id'])
                        print(f"Record already exists: {rec['artist']} - {rec['album']} (id={existing['id']})")
                        continue
            except Exception:
                pass
            print(f"Failed to add record {rec['album']}: {e}")

    # Create some bookings for Koki Lumi if artist exists
    try:
        koki_artist = db.get_artist_by_customer_id(created_customers.get('kokilumi'))
        if koki_artist:
            base_date = datetime.now() + timedelta(days=7)
            for i in range(3):
                perf_date = (base_date + timedelta(days=i)).replace(hour=19, minute=0, second=0, microsecond=0)
                bid = db.create_booking(koki_artist['id'], perf_date, duration_minutes=60, notes='Demo booking', user_id=created_customers.get('kokilumi'))
                print(f"Created booking for Koki Lumi at {perf_date} (booking id={bid})")
    except Exception as e:
        print(f"Could not create bookings: {e}")

    # Create a couple of demo sales
    try:
        # pick a customer with an id
        custs = list(created_customers.items())
        if custs and record_ids:
            # make a sale for Tiernan123
            tiernan_id = created_customers.get('Tiernan123')
            sale_items = [
                {'record_id': record_ids[0], 'quantity': 1},
                {'record_id': record_ids[2], 'quantity': 2} if len(record_ids) > 2 else {}
            ]
            # remove empty entries
            sale_items = [it for it in sale_items if it]
            if sale_items:
                sale_id = db.create_sale(tiernan_id, sale_items, shipping_address='12 Vinyl Ave')
                print(f"Created sale (id={sale_id}) for Tiernan123")

            # make a sale for a random user
            rand_user = random.choice(list(created_customers.keys()))
            rand_id = created_customers[rand_user]
            sale_items2 = [{'record_id': random.choice(record_ids), 'quantity': 1}]
            sale2 = db.create_sale(rand_id, sale_items2, shipping_address='PO Box Demo')
            print(f"Created sale (id={sale2}) for {rand_user}")
    except Exception as e:
        print(f"Could not create demo sales: {e}")

    print('\nSeeding complete.')
    print(f"Customers created/seen: {len(created_customers)} | Records present: {len(db.get_all_records())}")


if __name__ == '__main__':
    seed()
