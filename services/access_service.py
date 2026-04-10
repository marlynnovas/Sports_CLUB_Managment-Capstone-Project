from database.connection import get_connection
from services.membership_service import MembershipService

class AccessService:
    @staticmethod
    def validate_access(member_id):
        """
        Valida el acceso de un miembro y registra el intento.
        Versión unificada para la UI de develop y el motor robusto.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            membership = MembershipService.get_active_membership(member_id)

            if not membership:
                result = "denied"
                message = "Sin membresía registrada"
            else:
                status = MembershipService.refresh_membership_status(membership)
                if status == "active":
                    result = "granted"
                    message = "Acceso Permitido"
                else:
                    result = "denied"
                    message = f"Membresía {status}"

            # Registrar en access_logs (usando columnas del esquema: member_id, granted, message)
            cursor.execute("""
                INSERT INTO access_logs (member_id, granted, message)
                VALUES (?, ?, ?)
            """, (member_id, result == "granted", message))

            conn.commit()
            return {"result": result, "message": message}
        except Exception as e:
            print(f"Error in access validation: {e}")
            return {"result": "denied", "message": "Error de sistema"}
        finally:
            if conn: conn.close()

    @staticmethod
    def log_access(member_id, granted, message):
        """Manually log an access attempt."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO access_logs (member_id, granted, message)
                VALUES (?, ?, ?)
            """, (member_id, granted, message))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error logging access: {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def get_recent_logs(limit: int = 50):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT al.id,
                       al.access_time,
                       al.granted,
                       al.message,
                       m.first_name,
                       m.last_name
                FROM access_logs al
                JOIN members m ON al.member_id = m.id
                ORDER BY al.id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def count_today() -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM access_logs WHERE date(access_time) = date('now')")
            return cursor.fetchone()[0]
        except: return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_granted_today() -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM access_logs WHERE date(access_time) = date('now') AND granted = 1")
            return cursor.fetchone()[0]
        except: return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_denied_today() -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM access_logs WHERE date(access_time) = date('now') AND granted = 0")
            return cursor.fetchone()[0]
        except: return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_active_now() -> int:
        """Estimated active members (accessed in the last 3 hours)."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT member_id) FROM access_logs WHERE access_time > datetime('now', '-3 hours') AND granted = 1")
            return cursor.fetchone()[0]
        except: return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def peak_hour_today() -> str:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%H', access_time) as hr, COUNT(*) as cnt 
                FROM access_logs 
                WHERE date(access_time) = date('now')
                GROUP BY hr ORDER BY cnt DESC LIMIT 1
            """)
            res = cursor.fetchone()
            return f"{res[0]}:00" if res else "N/A"
        except: return "N/A"
        finally:
            if conn: conn.close()

    @staticmethod
    def hourly_traffic_today():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                WITH hours AS (
                    SELECT '08' as hr UNION SELECT '09' UNION SELECT '10' UNION SELECT '11' UNION 
                    SELECT '12' UNION SELECT '13' UNION SELECT '14' UNION SELECT '15' UNION 
                    SELECT '16' UNION SELECT '17' UNION SELECT '18' UNION SELECT '19' UNION 
                    SELECT '20' UNION SELECT '21'
                )
                SELECT h.hr, COUNT(al.id) 
                FROM hours h
                LEFT JOIN access_logs al ON strftime('%H', al.access_time) = h.hr AND date(al.access_time) = date('now')
                GROUP BY h.hr ORDER BY h.hr
            """)
            return cursor.fetchall()
        except: return []
        finally:
            if conn: conn.close()

    @staticmethod
    def week_outcome_counts():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN granted = 1 THEN 1 ELSE 0 END) as g,
                    SUM(CASE WHEN granted = 0 THEN 1 ELSE 0 END) as d,
                    COUNT(*) as t
                FROM access_logs 
                WHERE access_time > datetime('now', '-7 days')
            """)
            res = cursor.fetchone()
            if not res or res[2] == 0: return 0, 0, 1 # Avoid division by zero
            return res[0] or 0, res[1] or 0, res[2] or 1
        except: return 0, 0, 1
        finally:
            if conn: conn.close()
