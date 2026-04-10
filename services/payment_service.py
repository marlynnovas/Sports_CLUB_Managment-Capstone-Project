from database.connection import get_connection
from services.membership_service import MembershipService

class PaymentService:
    @staticmethod
    def get_all_payments(limit: int = 100):
        """Recupera todos los pagos con información relacionada."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT py.id,
                       py.amount,
                       py.payment_date,
                       py.status,
                       m.first_name,
                       m.last_name,
                       p.name AS plan_name
                FROM payments py
                JOIN memberships ms ON py.membership_id = ms.id
                JOIN members m      ON ms.member_id = m.id
                JOIN plans p        ON ms.plan_id   = p.id
                ORDER BY py.payment_date DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching payments: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def revenue_mtd() -> float:
        """Ingresos del mes actual (Month To Date)"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM payments
                WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
                  AND status = 'completed'
            """)
            val = cursor.fetchone()[0]
            return float(val)
        except:
            return 0.0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_by_status(status: str) -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM payments WHERE status = ?", (status,))
            count = cursor.fetchone()[0]
            return count
        except:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def average_amount() -> float:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(AVG(amount), 0) FROM payments")
            val = cursor.fetchone()[0]
            return float(val)
        except:
            return 0.0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_this_month() -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM payments WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')")
            return cursor.fetchone()[0]
        except: return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def create_payment(membership_id, amount, status='completed'):
        """
        Registra un pago y activa la membresía asociada.
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Obtener member_id de la membresía
            cursor.execute("SELECT member_id FROM memberships WHERE id = ?", (membership_id,))
            res = cursor.fetchone()
            if not res: return False
            member_id = res[0]

            cursor.execute("""
                INSERT INTO payments (member_id, membership_id, amount, status)
                VALUES (?, ?, ?, ?)
            """, (member_id, membership_id, amount, status))

            # Activar membresía si el pago fue completado
            if status == 'completed':
                MembershipService.update_membership_status(membership_id, "active")

            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating payment: {e}")
            if conn: conn.rollback()
            return False
        finally:
            if conn: conn.close()
            
    @staticmethod
    def get_payments_by_member(member_id):
        """Historial de pagos de un miembro."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM payments 
                WHERE member_id = ? 
                ORDER BY payment_date DESC
            """, (member_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching payments: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def delete_payment(payment_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting payment: {e}")
            return False
        finally:
            conn.close()
