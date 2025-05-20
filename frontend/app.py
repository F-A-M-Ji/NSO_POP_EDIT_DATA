from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os

from .login_screen import LoginScreen
from .add_user_screen import AddUserScreen
from .edit_data_screen import EditDataScreen

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("FAM")
        self.setGeometry(100, 100, 800, 600)
        
        # Load stylesheet
        self.load_stylesheet()
        
        # Create stacked widget for multiple screens
        self.stacked_widget = QStackedWidget()
        
        # Initialize screens
        self.login_screen = LoginScreen(self)
        self.add_user_screen = AddUserScreen(self)
        self.edit_data_screen = EditDataScreen(self)
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.add_user_screen)
        self.stacked_widget.addWidget(self.edit_data_screen)
        
        # Set initial screen
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.setCentralWidget(self.stacked_widget)
        
        # Set application font
        self.set_application_font()
    
    def set_application_font(self):
        font = QFont("Segoe UI", 10)
        self.setFont(font)
    
    def load_stylesheet(self):
        stylesheet_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "styles.qss"
        )
        try:
            with open(stylesheet_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found. Using default style.")
    
    def navigate_to(self, screen_name):
        """Navigate to a specific screen."""
        if screen_name == "login":
            self.stacked_widget.setCurrentWidget(self.login_screen)
        elif screen_name == "add_user":
            self.stacked_widget.setCurrentWidget(self.add_user_screen)
        elif screen_name == "edit_data":
            self.stacked_widget.setCurrentWidget(self.edit_data_screen)
    
    def login_successful(self, user_data):
        """Handle successful login."""
        from backend.auth import Auth
        
        # Determine where to navigate based on user role
        if Auth.is_admin(user_data['username']):
            self.navigate_to("add_user")
        else:
            self.navigate_to("edit_data")
