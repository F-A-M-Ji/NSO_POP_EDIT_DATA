from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os

from .login_screen import LoginScreen
from .add_user_screen import AddUserScreen
from .edit_data_screen import EditDataScreen
from .change_password_screen import ChangePasswordScreen
from .admin_menu_screen import AdminMenuScreen
from .reset_password_screen import ResetPasswordScreen


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None  # เพิ่มตัวแปรเก็บข้อมูลผู้ใช้ปัจจุบัน
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("การแก้ไขข้อมูล สปค. 68")
        self.setGeometry(100, 100, 800, 600)

        self.load_stylesheet()

        self.stacked_widget = QStackedWidget()

        self.login_screen = LoginScreen(self)
        self.admin_menu_screen = AdminMenuScreen(self)
        self.add_user_screen = AddUserScreen(self)
        self.reset_password_screen = ResetPasswordScreen(self)
        self.edit_data_screen = EditDataScreen(self)
        self.change_password_screen = ChangePasswordScreen(self)
    
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.admin_menu_screen)
        self.stacked_widget.addWidget(self.add_user_screen)
        self.stacked_widget.addWidget(self.reset_password_screen)
        self.stacked_widget.addWidget(self.edit_data_screen)
        self.stacked_widget.addWidget(self.change_password_screen)

        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.setCentralWidget(self.stacked_widget)

        self.set_application_font()

    def set_application_font(self):
        font = QFont("Segoe UI", 10)
        self.setFont(font)

    def load_stylesheet(self):
        stylesheet_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "styles.qss",
        )
        try:
            with open(stylesheet_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found. Using default style.")

    def navigate_to(self, screen_name):
        """Navigate to a specific screen."""
        if screen_name == "login":
            if hasattr(self, "edit_data_screen") and self.edit_data_screen:
                self.edit_data_screen.reset_screen_state()
            if hasattr(self, "add_user_screen") and self.add_user_screen:
                pass
            self.current_user = None
            self.stacked_widget.setCurrentWidget(self.login_screen)

            if hasattr(self.login_screen, "clear_inputs"):
                self.login_screen.clear_inputs()

        elif screen_name == "add_user":
            self.stacked_widget.setCurrentWidget(self.add_user_screen)
        elif screen_name == "edit_data":
            self.stacked_widget.setCurrentWidget(self.edit_data_screen)
        elif screen_name == "change_password":
            self.stacked_widget.setCurrentWidget(self.change_password_screen)
        elif screen_name == "admin_menu":
            self.stacked_widget.setCurrentWidget(self.admin_menu_screen)
        elif screen_name == "reset_password":
            self.stacked_widget.setCurrentWidget(self.reset_password_screen)

    def login_successful(self, user_data):
        """Handle successful login."""
        self.current_user = user_data

        if hasattr(self.edit_data_screen, "update_user_fullname"):
            self.edit_data_screen.update_user_fullname(user_data.get("fullname", "N/A"))

        from backend.auth import (
            Auth,
        )

        if Auth.is_admin(user_data["username"]):
            self.navigate_to("admin_menu")
        else:
            self.navigate_to("edit_data")

    def perform_logout(self):
        """Handles the full logout process including screen resets."""
        self.navigate_to("login")

    def navigate_to_change_password(self, user_data):
        """นำทางไปยังหน้าเปลี่ยนรหัสผ่านพร้อมส่งข้อมูลผู้ใช้"""
        self.current_user = user_data
        self.change_password_screen.set_user_data(user_data)
        self.stacked_widget.setCurrentWidget(self.change_password_screen)
