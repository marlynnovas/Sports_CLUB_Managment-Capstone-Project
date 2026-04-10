import sqlite3
import os

DB_NAME = os.getenv("DB_NAME", "sports_club.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db(schema_path):
    """Initializes the database with the provided SQL schema."""
    if not os.path.exists(schema_path):
        print(f"Schema file {schema_path} not found.")
        return

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()
