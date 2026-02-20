import sqlite3

DB_FILE = 'data.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    #user table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL ,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    
    #product table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    #cart table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            username TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            PRIMARY KEY (username, product_id)
        )
    ''')
    #order table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            total_price REAL NOT NULL,
            discount_code TEXT NOT NULL,
            discount_amount REAL DEFAULT 0.0,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    #order_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discount_codes (
            code TEXT PRIMARY KEY,
            percent REAL NOT NULL,
            active INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()