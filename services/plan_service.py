from database.connection import get_connection

class PlanService:
    @staticmethod
    def get_all_plans():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plans")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def create_plan(name, price, months, description=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO plans (name, price, duration_months, description) VALUES (?, ?, ?, ?)",
                (name, price, months, description)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def delete_plan(plan_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update_plan(plan_id, name, price, months, description):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE plans SET name=?, price=?, duration_months=?, description=? WHERE id=?",
                (name, price, months, description, plan_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def count_members_per_plan():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, COUNT(ms.id) as count
            FROM plans p
            LEFT JOIN memberships ms ON p.id = ms.plan_id
            GROUP BY p.name
        """)
        rows = cursor.fetchall()
        conn.close()
        return [(r["name"], r["count"]) for r in rows]
