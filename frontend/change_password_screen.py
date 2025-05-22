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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from backend.user import User
from frontend.utils.shadow_effect import add_shadow_effect


class ChangePasswordScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.user_data = None
        self.setup_ui()

    def set_user_data(self, user_data):
        """รับข้อมูลผู้ใช้จากหน้าล็อกอิน"""
        self.user_data = user_data
        if hasattr(self, "username_display"):
            self.username_display.setText(f"Username: {user_data['username']}")

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)

        container_layout = QHBoxLayout()
        container_layout.addStretch(1)

        center_column = QVBoxLayout()
        center_column.addStretch(1)

        # ส่วนหัว - ให้เหมือนกับหน้าอื่น
        header_layout = QHBoxLayout()

        header_title_label = QLabel("เปลี่ยนรหัสผ่าน")
        header_title_label.setAlignment(Qt.AlignCenter)
        header_title_label.setObjectName("headerLabel")
        header_layout.addWidget(header_title_label)

        header_layout.addStretch(1)

        logout_button = QPushButton("back")  # ให้เหมือนกับหน้าอื่น ใช้ "back"
        logout_button.setObjectName("secondaryButton")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.clicked.connect(self.go_back_to_login)
        header_layout.addWidget(logout_button)

        center_column.addLayout(header_layout)

        # สร้างเฟรมสำหรับฟอร์มเปลี่ยนรหัสผ่าน (เปลี่ยนเป็น contentFrame เหมือนหน้าอื่น)
        password_frame = QFrame()
        password_frame.setObjectName(
            "contentFrame"
        )  # เปลี่ยนจาก loginFrame เป็น contentFrame
        add_shadow_effect(password_frame)

        password_layout = QVBoxLayout(password_frame)
        password_layout.setSpacing(15)  # เปลี่ยนให้เหมือนกับหน้าอื่น

        # หัวข้อฟอร์ม
        form_title = QLabel("กรุณาตั้งรหัสผ่านใหม่")
        form_title.setAlignment(Qt.AlignCenter)
        form_title.setObjectName("formTitle")
        password_layout.addWidget(form_title)

        # แสดงชื่อผู้ใช้ที่กำลังเปลี่ยนรหัสผ่าน
        self.username_display = QLabel("")
        self.username_display.setAlignment(Qt.AlignCenter)
        password_layout.addWidget(self.username_display)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # ช่องป้อนรหัสผ่านใหม่
        new_password_layout = QVBoxLayout()
        new_password_label = QLabel("รหัสผ่านใหม่:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("ป้อนรหัสผ่านใหม่")
        self.new_password_input.setEchoMode(QLineEdit.Password)

        toggle_new_password = QAction(self.new_password_input)
        toggle_new_password.setIcon(QIcon("assets/eye-open.svg"))
        toggle_new_password.setCheckable(True)
        self.new_password_input.addAction(
            toggle_new_password, QLineEdit.TrailingPosition
        )

        toggle_new_password.toggled.connect(
            lambda checked: self.new_password_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )

        new_password_layout.addWidget(new_password_label)
        new_password_layout.addWidget(self.new_password_input)
        form_layout.addLayout(new_password_layout)

        # ช่องยืนยันรหัสผ่านใหม่
        confirm_password_layout = QVBoxLayout()
        confirm_password_label = QLabel("ยืนยันรหัสผ่านใหม่:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("ป้อนรหัสผ่านใหม่อีกครั้ง")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        toggle_confirm_password = QAction(self.confirm_password_input)
        toggle_confirm_password.setIcon(QIcon("assets/eye-open.svg"))
        toggle_confirm_password.setCheckable(True)
        self.confirm_password_input.addAction(
            toggle_confirm_password, QLineEdit.TrailingPosition
        )

        toggle_confirm_password.toggled.connect(
            lambda checked: self.confirm_password_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )

        confirm_password_layout.addWidget(confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_password_input)
        form_layout.addLayout(confirm_password_layout)

        password_layout.addLayout(form_layout)

        # ปุ่มยืนยันการเปลี่ยนรหัสผ่าน
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.submit_button = QPushButton("เปลี่ยนรหัสผ่าน")
        self.submit_button.setObjectName("primaryButton")
        self.submit_button.setFixedWidth(150)
        self.submit_button.setFixedHeight(30)
        self.submit_button.clicked.connect(self.handle_change_password)
        self.submit_button.setCursor(Qt.PointingHandCursor)

        button_layout.addWidget(self.submit_button)
        button_layout.addStretch()
        password_layout.addLayout(button_layout)

        # ตัดปุ่มกลับที่อยู่ด้านล่างออก เพราะมี back button ด้านบนแล้ว

        center_column.addWidget(password_frame)
        center_column.addStretch(1)

        container_layout.addLayout(center_column)
        container_layout.addStretch(1)

        main_layout.addLayout(container_layout)
        self.setLayout(main_layout)

    def handle_change_password(self):
        """จัดการการส่งข้อมูลรหัสผ่านใหม่"""
        if not self.user_data:
            QMessageBox.warning(
                self,
                "Error",
                "ไม่พบข้อมูลผู้ใช้งาน",
            )
            return

        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        if not new_password:
            QMessageBox.warning(
                self,
                "ข้อผิดพลาด",
                "โปรดระบุรหัสผ่านใหม่",
            )
            return

        if new_password != confirm_password:
            QMessageBox.warning(
                self,
                "ข้อผิดพลาด",
                "รหัสผ่านใหม่ไม่ตรงกัน",
            )
            return

        if new_password == self.user_data["username"]:
            QMessageBox.warning(
                self,
                "ข้อผิดพลาด",
                "รหัสผ่านใหม่ต้องไม่ตรงกับชื่อผู้ใช้",
            )
            return

        # เรียกใช้ backend เพื่ออัปเดตรหัสผ่าน
        success, message = User.update_password(
            self.user_data["username"], new_password
        )

        if success:
            QMessageBox.information(
                self,
                "สำเร็จ",
                "เปลี่ยนรหัสผ่านสำเร็จ กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่",
            )
            self.clear_inputs()
            self.parent_app.navigate_to("login")
        else:
            QMessageBox.warning(
                self,
                "ข้อผิดพลาด",
                f"เปลี่ยนรหัสผ่านไม่สำเร็จ: {message}",
            )

    def clear_inputs(self):
        """ล้างข้อมูลในฟอร์ม"""
        self.new_password_input.clear()
        self.confirm_password_input.clear()

    def go_back_to_login(self):
        """กลับไปที่หน้าล็อกอิน"""
        self.clear_inputs()
        self.parent_app.navigate_to("login")
