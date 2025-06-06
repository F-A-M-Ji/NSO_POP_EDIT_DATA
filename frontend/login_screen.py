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

from backend.auth import Auth
from frontend.utils.shadow_effect import add_shadow_effect


class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)

        container_layout = QHBoxLayout()
        container_layout.addStretch(1)

        center_column = QVBoxLayout()
        center_column.addStretch(1)

        header_label = QLabel("Welcome to Application")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setObjectName("headerLabel")
        center_column.addWidget(header_label)

        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")

        add_shadow_effect(login_frame)

        login_layout = QVBoxLayout(login_frame)
        login_layout.setSpacing(20)

        form_title = QLabel("Login")
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setObjectName("formTitle")
        login_layout.addWidget(form_title)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMaxLength(8)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)

        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        toggle_password = QAction(self.password_input)
        toggle_password.setIcon(QIcon("assets/eye-open.svg"))
        toggle_password.setCheckable(True)
        self.password_input.addAction(toggle_password, QLineEdit.TrailingPosition)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)

        def toggle_password_visibility(checked):
            if checked:
                toggle_password.setIcon(QIcon("assets/eye-closed.svg"))
                self.password_input.setEchoMode(QLineEdit.Normal)
            else:
                toggle_password.setIcon(QIcon("assets/eye-open.svg"))
                self.password_input.setEchoMode(QLineEdit.Password)

        toggle_password.toggled.connect(toggle_password_visibility)

        login_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("primaryButton")
        self.login_button.setFixedWidth(150)
        self.login_button.setFixedHeight(30)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.login_button)

        button_layout.addStretch()
        login_layout.addLayout(button_layout)

        center_column.addWidget(login_frame)
        center_column.addStretch(1)

        container_layout.addLayout(center_column)
        container_layout.addStretch(1)

        main_layout.addLayout(container_layout)

        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Username และ Password ไม่ถูกต้อง",
            )
            return

        if username == password:
            user_data = Auth.login(username, password)
            if user_data:
                self.username_input.clear()
                self.password_input.clear()
                self.parent_app.navigate_to_change_password(user_data)
                return
            else:
                QMessageBox.warning(
                    self,
                    "Login Failed",
                    "Username หรือ Password ไม่ถูกต้อง",
                )
                return

        user_data = Auth.login(username, password)
        if user_data:
            self.username_input.clear()
            self.password_input.clear()
            self.parent_app.login_successful(user_data)
        else:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Username หรือ Password ไม่ถูกต้อง",
            )
