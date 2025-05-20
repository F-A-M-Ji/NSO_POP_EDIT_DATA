from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt

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

        # สร้าง container สำหรับจัดกลางหน้าจอ
        container_layout = QHBoxLayout()
        container_layout.addStretch(1)  # พื้นที่ยืดหยุ่นด้านซ้าย
        
        # สร้าง column หลักตรงกลาง
        center_column = QVBoxLayout()
        center_column.addStretch(1)  # พื้นที่ยืดหยุ่นด้านบน
        
        # Header
        header_label = QLabel("Welcome to Application")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setObjectName("headerLabel")
        center_column.addWidget(header_label)
        
        # Create a frame for login form
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        # login_frame.setMinimumWidth(350)  # ความกว้างขั้นต่ำ
        # login_frame.setMaximumWidth(500)  # ความกว้างสูงสุด

        add_shadow_effect(login_frame)

        # สร้าง layout ภายใน frame
        login_layout = QVBoxLayout(login_frame)
        login_layout.setSpacing(20)
        
        # Login form title
        form_title = QLabel("Login")
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setObjectName("formTitle")
        login_layout.addWidget(form_title)

        # สร้าง form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Username
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMaxLength(8)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)
        
        # Password
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)

        login_layout.addLayout(form_layout)
        
        # Login button
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
        
        # เพิ่ม login frame เข้าไปใน column หลัก
        center_column.addWidget(login_frame)
        center_column.addStretch(1)  # พื้นที่ยืดหยุ่นด้านล่าง
        
        # เพิ่ม column หลักเข้าไปใน container
        container_layout.addLayout(center_column)
        container_layout.addStretch(1)  # พื้นที่ยืดหยุ่นด้านขวา
        
        # เพิ่ม container เข้าไปใน main layout
        main_layout.addLayout(container_layout)
        
        self.setLayout(main_layout)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(
                self, "Login Failed", 
                # "Username and password are required."
                "Username และ Password ไม่ถูกต้อง"
            )
            return
        
        user_data = Auth.login(username, password)
        
        if user_data:
            self.username_input.clear()
            self.password_input.clear()
            self.parent_app.login_successful(user_data)
        else:
            QMessageBox.warning(
                self, "Login Failed", 
                # "Invalid username or password."
                "Username หรือ Password ไม่ถูกต้อง"
            )
