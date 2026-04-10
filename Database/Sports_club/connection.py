import sqlite3
import os

DB_NAME = "sports_club.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
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


# 🔹 NEW: CRUD-style helper functions (clean, reusable)

def create_member(first_name, last_name, email):
    conn = get_connection()
    try:
        query = "INSERT INTO members (first_name, last_name, email) VALUES (?, ?, ?)"
        conn.execute(query, (first_name, last_name, email))
        conn.commit()
        print("Member created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating member: {e}")
    finally:
        conn.close()


def get_all_members():
    conn = get_connection()
    try:
        query = "SELECT * FROM members"
        results = conn.execute(query).fetchall()
        return results
    finally:
        conn.close()


def update_member(member_id, first_name, last_name, email):
    conn = get_connection()
    try:
        query = """
        UPDATE members
        SET first_name = ?, last_name = ?, email = ?
        WHERE id = ?
        """
        conn.execute(query, (first_name, last_name, email, member_id))
        conn.commit()
        print("Member updated successfully.")
    except sqlite3.Error as e:
        print(f"Error updating member: {e}")
    finally:
        conn.close()


def delete_member(member_id):
    conn = get_connection()
    try:
        query = "DELETE FROM members WHERE id = ?"
        conn.execute(query, (member_id,))
        conn.commit()
        print("Member deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting member: {e}")
    finally:
        conn.close()