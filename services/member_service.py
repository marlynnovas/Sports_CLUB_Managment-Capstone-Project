from database.connection import get_connection

class MemberService:
    @staticmethod
    def create_member(first_name, last_name, email, phone):
        """
        Registra un nuevo miembro.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO members (first_name, last_name, email, phone)
                VALUES (?, ?, ?, ?)
            """, (first_name, last_name, email, phone))

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating member: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: conn.close()

    @staticmethod
    def get_all_members():
        """Recupera la lista completa de miembros con datos de membresía."""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Usamos JOINs similares a develop para dar más info a la UI
            cursor.execute("""
                SELECT m.*,
                       ms.status   AS membership_status,
                       ms.end_date AS end_date,
                       p.name      AS plan_name
                FROM members m
                LEFT JOIN memberships ms ON m.id = ms.member_id
                LEFT JOIN plans p        ON ms.plan_id = p.id
                ORDER BY m.first_name ASC, m.last_name ASC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching members: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def search_members(query):
        """Busca miembros por nombre o correo."""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT m.*,
                       ms.status   AS membership_status,
                       ms.end_date AS end_date,
                       p.name      AS plan_name
                FROM members m
                LEFT JOIN memberships ms ON m.id = ms.member_id
                LEFT JOIN plans p        ON ms.plan_id = p.id
                WHERE m.first_name LIKE ? OR m.last_name LIKE ? OR m.email LIKE ?
                ORDER BY m.first_name ASC, m.last_name ASC
            """, (search_pattern, search_pattern, search_pattern))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching members: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def count_members():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM members")
            count = cursor.fetchone()[0]
            return count
        except:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_by_status(status: str) -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM memberships WHERE status = ?", (status,)
            )
            count = cursor.fetchone()[0]
            return count
        except:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_no_plan() -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM members WHERE id NOT IN (SELECT member_id FROM memberships)"
            )
            count = cursor.fetchone()[0]
            return count
        except:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def count_renewals_this_month() -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM memberships WHERE strftime('%Y-%m', end_date) = strftime('%Y-%m', 'now')"
            )
            count = cursor.fetchone()[0]
            return count
        except:
            return 0
        finally:
            if conn: conn.close()

    @staticmethod
    def update_member(member_id, first_name, last_name, email, phone):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE members SET first_name=?, last_name=?, email=?, phone=? WHERE id=?",
                (first_name, last_name, email, phone, member_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating member: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete_member(member_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Also delete memberships of this member
            cursor.execute("DELETE FROM memberships WHERE member_id=?", (member_id,))
            cursor.execute("DELETE FROM members WHERE id=?", (member_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting member: {e}")
            return False
        finally:
            conn.close()
