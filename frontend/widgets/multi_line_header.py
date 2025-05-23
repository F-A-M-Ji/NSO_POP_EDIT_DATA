from PyQt5.QtWidgets import (
    QHeaderView,
    QApplication,
    QStyleOptionHeader,
    QStyle,
    QTableWidget,
)
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import (
    QPainter,
    QPen,
    QColor,
    QIcon,
    QFontMetrics,
    QFont,
)


class MultiLineHeaderView(QHeaderView):
    TEXT_LINES_ALLOWANCE = 3
    # ปรับระยะห่างระหว่างบรรทัดหลักและบรรทัดย่อยที่นี่
    VERTICAL_PADDING_PER_LINE = 0
    # ปรับระยะห่างรอบๆ บล็อกข้อความทั้งหมด (รวมถึงระยะห่างจากขอบบนถึงบรรทัดแรก)
    TEXT_BLOCK_PADDING = 6

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.mainTexts = {}
        self.subTexts = {}
        self.setDefaultAlignment(Qt.AlignCenter)
        self.setSectionsMovable(True)

        self.sectionResized.connect(self.on_section_resized)

    def on_section_resized(self, logicalIndex, oldSize, newSize):
        """When a section is resized, update its geometry and trigger header height update."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.updateGeometries()
        if self.parentWidget() and isinstance(self.parentWidget(), QTableWidget):
            self.parentWidget().updateGeometries()

    def setColumnText(self, column, mainText, subText=""):
        self.mainTexts[column] = mainText
        self.subTexts[column] = subText
        if self.model():
            self.model().headerDataChanged.emit(Qt.Horizontal, column, column)
        self.updateSection(column)
        self.on_section_resized(column, 0, self.sectionSize(column))

    def sizeHint(self):
        fm = self.font()
        font_metrics = QFontMetrics(fm)

        text_part_height = (
            (font_metrics.height() * self.TEXT_LINES_ALLOWANCE)
            + (
                (self.TEXT_LINES_ALLOWANCE - 1) * self.VERTICAL_PADDING_PER_LINE
                if self.TEXT_LINES_ALLOWANCE > 0
                else 0
            )
            + self.TEXT_BLOCK_PADDING
        )

        min_height = font_metrics.height() + self.TEXT_BLOCK_PADDING
        final_height = max(text_part_height, min_height)

        return QSize(super().sizeHint().width(), int(final_height))

    def paintSection(self, painter, rect, logicalIndex):
        if not rect.isValid():
            return

        option = QStyleOptionHeader()
        self.initStyleOption(option)
        option.rect = rect
        option.section = logicalIndex
        option.text = ""
        option.icon = QIcon()

        current_state = QStyle.State_None
        if self.isEnabled():
            current_state |= QStyle.State_Enabled
        if self.window() and self.window().isActiveWindow():
            current_state |= QStyle.State_Active
        
        if self.isSortIndicatorShown() and self.sortIndicatorSection() == logicalIndex:
            option.sortIndicator = self.sortIndicatorOrder()
        else:
            option.sortIndicator = QStyleOptionHeader.None_
        option.state = current_state

        self.style().drawControl(QStyle.CE_HeaderSection, option, painter, self)

        mainText = self.mainTexts.get(logicalIndex, "")
        subText = self.subTexts.get(logicalIndex, "")

        # Area for drawing text, adjusted for internal padding
        text_drawing_rect = QRect(rect).adjusted(
            self.TEXT_BLOCK_PADDING // 2,
            self.TEXT_BLOCK_PADDING // 2,
            -self.TEXT_BLOCK_PADDING // 2,
            -self.TEXT_BLOCK_PADDING // 2
        )
        
        painter.save()

        current_y = text_drawing_rect.y()
        available_width = text_drawing_rect.width()
        max_y = text_drawing_rect.bottom()

        # Draw Main Text
        if mainText:
            main_painter_font = QFont(self.font())
            main_painter_font.setBold(True)
            painter.setFont(main_painter_font)
            main_fm = QFontMetrics(painter.font())
            painter.setPen(Qt.black)

            max_h_for_main = max_y - current_y
            if subText:
                min_sub_h_needed = main_fm.height() + self.VERTICAL_PADDING_PER_LINE 
                max_h_for_main = max(main_fm.height(), max_y - current_y - min_sub_h_needed)


            main_text_bound_rect = main_fm.boundingRect(
                QRect(0, 0, available_width, int(max_h_for_main)),
                Qt.AlignCenter | Qt.TextWordWrap, 
                mainText
            )
            
            actual_main_h = main_text_bound_rect.height()
            
            if current_y + actual_main_h <= max_y + 1:
                draw_rect = QRect(text_drawing_rect.x(), current_y, available_width, actual_main_h)
                painter.drawText(draw_rect, Qt.AlignCenter | Qt.TextWordWrap, mainText)
                current_y += actual_main_h

        # Draw Sub Text
        if subText:
            if mainText and current_y < max_y:
                current_y += self.VERTICAL_PADDING_PER_LINE
            
            if current_y <= max_y:
                sub_painter_font = QFont(self.font())
                sub_painter_font.setPointSize(sub_painter_font.pointSize() - 1)
                painter.setFont(sub_painter_font)
                sub_fm = QFontMetrics(painter.font())
                painter.setPen(Qt.darkGray)

                remaining_height_for_sub = max_y - current_y + 1
                if remaining_height_for_sub > 0:                    
                    draw_rect = QRect(text_drawing_rect.x(), current_y, available_width, remaining_height_for_sub)
                    painter.drawText(draw_rect, Qt.AlignCenter | Qt.TextWordWrap, subText)
        
        painter.restore()

    def setModel(self, model):
        super().setModel(model)
        self.updateGeometries()

    def showEvent(self, event):
        super().showEvent(event)

    def hideEvent(self, event):
        super().hideEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.on_section_resized(-1, 0, 0)

    def updateGeometries(self):
        super().updateGeometries()
