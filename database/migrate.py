import sqlite3
import os

DB_NAME = "sports_club.db"

def migrate():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Add description to plans
    try:
        cursor.execute("ALTER TABLE plans ADD COLUMN description TEXT;")
        print("Added description to plans")
    except sqlite3.OperationalError as e:
        print(f"Plans migration skipped: {e}")

    # 2. Add duration_days to plans
    try:
        cursor.execute("ALTER TABLE plans ADD COLUMN duration_days INTEGER;")
        print("Added duration_days to plans")
    except sqlite3.OperationalError as e:
        print(f"Plans migration skipped (duration_days): {e}")

    # 3. Add join_date to members
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN join_date DATE;")
        print("Added join_date to members")
    except sqlite3.OperationalError as e:
        print(f"Members migration skipped: {e}")

    # 4. Correct payment schema if needed
    try:
        cursor.execute("ALTER TABLE payments ADD COLUMN due_date DATE;")
        print("Added due_date to payments")
    except sqlite3.OperationalError as e:
        print(f"Payments migration skipped: {e}")

    conn.commit()
    conn.close()
    print("Migration finished!")

if __name__ == "__main__":
    migrate()
