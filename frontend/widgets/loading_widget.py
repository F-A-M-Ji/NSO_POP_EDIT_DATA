from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class LoadingOverlay(QDialog):
    """
    A modal, semi-transparent overlay to indicate that the application is busy.
    It shows a customizable message and prevents interaction with the parent window.
    """
    def __init__(self, parent=None, message="กำลังประมวลผล กรุณารอสักครู่..."):
        """
        Initializes the loading overlay.
        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            message (str, optional): The message to display.
        """
        super().__init__(parent)
        # ตั้งค่าให้หน้าต่างไม่มีกรอบ, เป็น Dialog, และโปร่งแสง
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        # Layout หลัก
        layout = QVBoxLayout(self)
        self.label = QLabel(message)
        
        # กำหนดสไตล์ให้ Label มีพื้นหลังสีเข้มและตัวอักษรสีขาว
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16pt;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 160);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

    def showEvent(self, event):
        """
        Overrides the show event to center the overlay on its parent widget.
        """
        if self.parent():
            parent_rect = self.parent().geometry()
            # ย้ายตำแหน่งของ overlay ไปยังจุดกึ่งกลางของ parent
            self.move(parent_rect.center() - self.rect().center())
        super().showEvent(event)

