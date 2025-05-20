from PyQt5.QtWidgets import (QMessageBox, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QColor


def show_error_message(parent, title, message):
    """Show an error message box."""
    QMessageBox.critical(parent, title, message)


def show_info_message(parent, title, message):
    """Show an information message box."""
    QMessageBox.information(parent, title, message)


def add_shadow_effect(
    widget, blur_radius=10, offset_x=0, offset_y=2, color=(0, 0, 0, 40)
):
    """เพิ่มเงาให้กับ widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(QColor(*color))
    shadow.setOffset(offset_x, offset_y)
    widget.setGraphicsEffect(shadow)
