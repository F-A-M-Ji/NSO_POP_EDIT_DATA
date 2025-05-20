from .user import User

class Auth:
    @staticmethod
    def login(username, password):
        """Login a user and return user data if authentication is successful."""
        return User.authenticate(username, password)
    
    @staticmethod
    def is_admin(username):
        """Check if the given username is an admin."""
        return username == 'admin'
