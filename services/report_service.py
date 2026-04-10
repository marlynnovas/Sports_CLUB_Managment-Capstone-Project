from database.connection import get_connection

def get_monthly_revenue():
    """
    Obtiene ingresos totales agrupados por mes. 
    Utiliza la view monthly_revenue_view creada en el schema.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM monthly_revenue_view ORDER BY month DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching monthly revenue: {e}")
        return []
    finally:
        if conn: conn.close()


def get_membership_distribution():
    """
    Calcula cuántos miembros hay por cada estado (active, expired, etc).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM memberships 
            GROUP BY status
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching membership distribution: {e}")
        return []
    finally:
        if conn: conn.close()


def get_denied_access_stats():
    """
    Obtiene estadísticas de accesos denegados.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT message, COUNT(*) as count 
            FROM access_logs 
            WHERE result = 'denied'
            GROUP BY message
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching denied access stats: {e}")
        return []
    finally:
        if conn: conn.close()
