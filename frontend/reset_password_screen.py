from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
)
from PyQt5.QtCore import Qt

from backend.user import User
from frontend.utils.shadow_effect import add_shadow_effect


class ResetPasswordScreen(QWidget):
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

        # ส่วนหัว
        header_layout = QHBoxLayout()

        header_title_label = QLabel("Reset Password")
        header_title_label.setAlignment(Qt.AlignCenter)
        header_title_label.setObjectName("headerLabel")
        header_layout.addWidget(header_title_label)

        header_layout.addStretch(1)

        logout_button = QPushButton("back")
        logout_button.setObjectName("secondaryButton")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.clicked.connect(self.back)
        header_layout.addWidget(logout_button)

        center_column.addLayout(header_layout)

        # สร้างกรอบฟอร์ม
        reset_frame = QFrame()
        reset_frame.setObjectName("contentFrame")

        reset_layout = QVBoxLayout(reset_frame)
        reset_layout.setSpacing(20)

        add_shadow_effect(reset_frame)

        # ช่องป้อน username
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(
            "Enter username to reset password."
        )
        self.username_input.setFixedWidth(230)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        reset_layout.addLayout(username_layout)

        # ปุ่มรีเซ็ต
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.reset_button = QPushButton("reset password")
        self.reset_button.setObjectName("primaryButton")
        self.reset_button.setFixedWidth(150)
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self.handle_reset_password)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.reset_button)

        button_layout.addStretch()
        reset_layout.addLayout(button_layout)

        center_column.addWidget(reset_frame)
        center_column.addStretch(1)

        container_layout.addLayout(center_column)
        container_layout.addStretch(1)

        main_layout.addLayout(container_layout)
        self.setLayout(main_layout)

    def handle_reset_password(self):
        """รีเซ็ตรหัสผ่านให้เป็นเหมือนกับ username"""
        username = self.username_input.text().strip()

        if not username:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาป้อน Username")
            return

        # เรียกใช้เมธอด reset_password_to_username จาก User class
        success, message = User.reset_password_to_username(username)

        if success:
            QMessageBox.information(
                self,
                "สำเร็จ",
                f"รีเซ็ตรหัสผ่านสำเร็จ ผู้ใช้ {username} สามารถเข้าสู่ระบบด้วย username และ password เดียวกัน",
            )
            self.username_input.clear()
        else:
            QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถรีเซ็ตรหัสผ่านได้: {message}")

    def back(self):
        self.username_input.clear()
        self.parent_app.navigate_to("admin_menu")
