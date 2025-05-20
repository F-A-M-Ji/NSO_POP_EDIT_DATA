from PyQt5.QtWidgets import (QGraphicsDropShadowEffect)
from PyQt5.QtGui import QColor

def add_shadow_effect(
    widget, blur_radius=10, offset_x=0, offset_y=2, color=(0, 0, 0, 40)
):
    """เพิ่มเงาให้กับ widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(QColor(*color))
    shadow.setOffset(offset_x, offset_y)
    widget.setGraphicsEffect(shadow)