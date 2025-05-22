import bcrypt
from .db import get_connection


class User:
    @staticmethod
    def authenticate(username, password):
        """Authenticate a user with the given credentials."""
        conn = get_connection()
        if not conn:
            return None

        cursor = conn.cursor()

        # Special case for admin
        if username == "admin":
            query = (
                "SELECT username, password, fullname FROM edit_user WHERE username = ?"
            )
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            if user and user.password == password:
                return {"username": user.username, "fullname": user.fullname}
            return None

        # Regular users with hashed passwords
        query = "SELECT username, password, fullname FROM edit_user WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")
        ):
            return {"username": user.username, "fullname": user.fullname}

        return None

    @staticmethod
    def add_user(username, password, fullname):
        """Add a new user with the given credentials."""
        if len(username) > 8:
            return False, "Username must be 8 characters or less"

        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT 1 FROM edit_user WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already exists"

        # Hash password before storing
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        try:
            cursor.execute(
                "INSERT INTO edit_user (username, password, fullname) VALUES (?, ?, ?)",
                (username, hashed_password.decode("utf-8"), fullname),
            )
            conn.commit()
            return True, "User added successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)

        finally:
            conn.close()

    @staticmethod
    def update_password(username, new_password):
        """อัปเดตรหัสผ่านของผู้ใช้"""
        conn = get_connection()
        if not conn:
            return False, "ไม่สามารถเชื่อมต่อกับฐานข้อมูลได้"

        cursor = conn.cursor()

        try:
            # กรณีเป็นผู้ใช้ admin
            if username == "admin":
                cursor.execute(
                    "UPDATE edit_user SET password = ? WHERE username = ?",
                    (new_password, username),
                )
            else:
                # สำหรับผู้ใช้ปกติ ใช้การเข้ารหัสด้วย bcrypt
                hashed_password = bcrypt.hashpw(
                    new_password.encode("utf-8"), bcrypt.gensalt()
                )
                cursor.execute(
                    "UPDATE edit_user SET password = ? WHERE username = ?",
                    (hashed_password.decode("utf-8"), username),
                )

            conn.commit()
            return True, "เปลี่ยนรหัสผ่านสำเร็จ"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def reset_password_to_username(username):
        """รีเซ็ตรหัสผ่านของผู้ใช้ให้เป็นเหมือนกับ username"""
        if username == "admin":
            return False, "ไม่สามารถรีเซ็ตรหัสผ่าน admin ได้"

        conn = get_connection()
        if not conn:
            return False, "ไม่สามารถเชื่อมต่อกับฐานข้อมูลได้"

        cursor = conn.cursor()

        try:
            # ตรวจสอบว่ามีผู้ใช้นี้หรือไม่
            cursor.execute("SELECT 1 FROM edit_user WHERE username = ?", (username,))
            if not cursor.fetchone():
                return False, "ไม่พบผู้ใช้งานในระบบ"

            # เข้ารหัสชื่อผู้ใช้เพื่อใช้เป็นรหัสผ่านใหม่
            hashed_password = bcrypt.hashpw(username.encode("utf-8"), bcrypt.gensalt())

            # อัปเดตรหัสผ่านของผู้ใช้
            cursor.execute(
                "UPDATE edit_user SET password = ? WHERE username = ?",
                (hashed_password.decode("utf-8"), username),
            )

            conn.commit()
            return True, "รีเซ็ตรหัสผ่านสำเร็จ"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
