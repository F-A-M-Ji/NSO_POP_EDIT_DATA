from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt5.QtCore import Qt
from frontend.utils.shadow_effect import add_shadow_effect


class AdminMenuScreen(QWidget):
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

        # header_title_label = QLabel("Admin Menu")
        # header_title_label.setAlignment(Qt.AlignCenter)
        # header_title_label.setObjectName("headerLabel")
        # header_layout.addWidget(header_title_label)

        header_layout.addStretch(1)

        logout_button = QPushButton("back")
        logout_button.setObjectName("secondaryButton")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.clicked.connect(self.back)
        header_layout.addWidget(logout_button)

        center_column.addLayout(header_layout)

        # สร้างกรอบเมนู
        menu_frame = QFrame()
        menu_frame.setObjectName("contentFrame")

        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setSpacing(20)

        add_shadow_effect(menu_frame)

        # ปุ่มเพิ่มผู้ใช้งาน
        add_user_button = QPushButton("Add User")
        add_user_button.setObjectName("primaryButton")
        add_user_button.setCursor(Qt.PointingHandCursor)
        add_user_button.clicked.connect(self.navigate_to_add_user)
        add_user_button.setFixedWidth(200)
        add_user_button.setFixedHeight(40)
        menu_layout.addWidget(add_user_button, alignment=Qt.AlignCenter)

        # ปุ่มรีเซ็ตรหัสผ่าน
        reset_password_button = QPushButton("Reset Password")
        reset_password_button.setObjectName("primaryButton")
        reset_password_button.setCursor(Qt.PointingHandCursor)
        reset_password_button.clicked.connect(self.navigate_to_reset_password)
        reset_password_button.setFixedWidth(200)
        reset_password_button.setFixedHeight(40)
        menu_layout.addWidget(reset_password_button, alignment=Qt.AlignCenter)

        center_column.addWidget(menu_frame)
        center_column.addStretch(1)

        container_layout.addLayout(center_column)
        container_layout.addStretch(1)

        main_layout.addLayout(container_layout)
        self.setLayout(main_layout)

    def navigate_to_add_user(self):
        self.parent_app.navigate_to("add_user")

    def navigate_to_reset_password(self):
        self.parent_app.navigate_to("reset_password")

    def back(self):
        self.parent_app.navigate_to("login")
