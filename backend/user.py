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
        if username == 'admin':
            query = "SELECT username, password, fullname FROM edit_user WHERE username = ?"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if user and user.password == password:
                return {'username': user.username, 'fullname': user.fullname}
            return None
        
        # Regular users with hashed passwords
        query = "SELECT username, password, fullname FROM edit_user WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return {'username': user.username, 'fullname': user.fullname}
        
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
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute(
                "INSERT INTO Users (username, password, fullname) VALUES (?, ?, ?)",
                (username, hashed_password.decode('utf-8'), fullname)
            )
            conn.commit()
            return True, "User added successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
