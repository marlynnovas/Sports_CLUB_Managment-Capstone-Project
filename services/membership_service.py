from datetime import datetime, date, timedelta
from database.connection import get_connection

class MembershipService:
    @staticmethod
    def get_all_memberships():
        """Obtiene todas las membresías con información de miembro y plan (vía JOINs)."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ms.*,
                       m.first_name,
                       m.last_name,
                       p.name AS plan_name,
                       p.price
                FROM memberships ms
                JOIN members m ON ms.member_id = m.id
                JOIN plans p   ON ms.plan_id   = p.id
                ORDER BY ms.id DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching memberships: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_membership(member_id, plan_id, duration_days):
        """Crea una membresía calculando automáticamente la fecha de fin."""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            start_date = date.today()
            end_date = start_date + timedelta(days=duration_days)

            cursor.execute(
                """INSERT INTO memberships (member_id, plan_id, start_date, end_date, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (member_id, plan_id, start_date, end_date, "active"),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating membership: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()

    @staticmethod
    def update_membership_status(membership_id, status):
        """Actualiza el estado de una membresía en la DB."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE memberships SET status = ? WHERE id = ?
            """, (status, membership_id))
            conn.commit()
        except:
            if conn: conn.rollback()
        finally:
            if conn: conn.close()

    @staticmethod
    def refresh_membership_status(membership):
        """Lógica proactiva de expiración."""
        if not membership: return None
        try:
            if isinstance(membership["end_date"], str):
                end_date = datetime.strptime(membership["end_date"], "%Y-%m-%d").date()
            else:
                end_date = membership["end_date"]

            if end_date < date.today() and membership["status"] == "active":
                MembershipService.update_membership_status(membership["id"], "expired")
                return "expired"
            return membership["status"]
        except:
            return membership.get("status")

    @staticmethod
    def auto_expire_memberships():
        """Proceso por lotes para expirar membresías pasadas."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE memberships
                SET status = 'expired'
                WHERE status = 'active' AND end_date < ?
            """, (date.today(),))
            changed = cursor.rowcount
            conn.commit()
            return changed
        except:
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()
