from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QAction,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from backend.user import User
from frontend.utils.shadow_effect import add_shadow_effect


class AddUserScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Create container for centering content
        container_layout = QHBoxLayout()
        container_layout.addStretch(1)  # Flexible space on the left side

        # Create the main column layout for header and content
        center_column = QVBoxLayout()
        center_column.addStretch(1)  # Flexible space on the top

        # Header with logout option
        header_layout = QHBoxLayout()

        header_title_label = QLabel("Add New User")
        header_title_label.setAlignment(Qt.AlignCenter)
        header_title_label.setObjectName("headerLabel")
        header_layout.addWidget(header_title_label)

        header_layout.addStretch(1)  # Space between label and logout button

        logout_button = QPushButton("Logout")
        logout_button.setObjectName("secondaryButton")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)

        center_column.addLayout(header_layout)

        # Create user form inside a frame
        user_frame = QFrame()
        user_frame.setObjectName("contentFrame")

        user_layout = QVBoxLayout(user_frame)
        user_layout.setSpacing(15)

        add_shadow_effect(user_frame)

        # Fullname input
        fullname_layout = QVBoxLayout()
        fullname_label = QLabel("Full Name:")
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Enter full name")
        self.fullname_input.setFixedWidth(300)
        fullname_layout.addWidget(fullname_label)
        fullname_layout.addWidget(self.fullname_input)
        user_layout.addLayout(fullname_layout)

        # Username input
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username (max 8 characters)")
        self.username_input.setMaxLength(8)
        self.username_input.setFixedWidth(300)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        user_layout.addLayout(username_layout)

        # Password input
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        toggle_password = QAction(self.password_input)
        toggle_password.setIcon(QIcon("assets/eye-open.svg"))  # ใช้ไอคอนตาเปิด
        toggle_password.setCheckable(True)
        self.password_input.addAction(toggle_password, QLineEdit.TrailingPosition)
        self.password_input.setFixedWidth(300)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        user_layout.addLayout(password_layout)

        # สลับไอคอนเมื่อกด toggle
        def toggle_password_visibility(checked):
            if checked:
                toggle_password.setIcon(
                    QIcon("assets/eye-closed.svg")
                )  # เปลี่ยนเป็นไอคอนตาปิด
                self.password_input.setEchoMode(QLineEdit.Normal)
            else:
                toggle_password.setIcon(
                    QIcon("assets/eye-open.svg")
                )  # เปลี่ยนกลับเป็นไอคอนตาเปิด
                self.password_input.setEchoMode(QLineEdit.Password)

        toggle_password.toggled.connect(toggle_password_visibility)

        # Add button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.add_button = QPushButton("Add User")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.handle_add_user)
        self.add_button.setFixedWidth(150)
        self.add_button.setFixedHeight(30)
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        user_layout.addLayout(button_layout)

        center_column.addWidget(user_frame)
        center_column.addStretch(1)

        container_layout.addLayout(center_column)
        container_layout.addStretch(1)

        main_layout.addLayout(container_layout)
        self.setLayout(main_layout)

    def handle_add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        fullname = self.fullname_input.text().strip()

        if not username or not password or not fullname:
            QMessageBox.warning(self, "Validation Error", "กรุณากรอกข้อมูลให้ถูกต้อง")
            return

        success, message = User.add_user(username, password, fullname)

        if success:
            QMessageBox.information(self, "Success", message)
            self.clear_input_fields()  # Use helper method
        else:
            QMessageBox.warning(self, "Error", message)

    def clear_input_fields(self):
        """Clears all input fields on this screen."""
        self.fullname_input.clear()
        self.username_input.clear()
        self.password_input.clear()

    def logout(self):
        """Clears input fields and navigates to the login screen."""
        self.clear_input_fields()

        if self.parent_app and hasattr(self.parent_app, "perform_logout"):
            self.parent_app.perform_logout()
        else:
            self.parent_app.navigate_to("login")

    def update_user_fullname(self, fullname):
        """Updates the display name of the logged-in admin user."""
        pass

    def reset_screen_state(self):
        """Resets this screen to its initial state."""
        self.clear_input_fields()
