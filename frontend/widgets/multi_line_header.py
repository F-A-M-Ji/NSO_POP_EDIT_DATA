from PyQt5.QtWidgets import (
    QHeaderView,
    QApplication,
    QStyleOptionHeader,
    QStyle,
    QTableWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFrame,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal, QPoint
from PyQt5.QtGui import (
    QPainter,
    QPen,
    QColor,
    QIcon,
    QFontMetrics,
    QFont,
    QPolygon,
    QBrush,
)


class FilterDropdown(QWidget):
    """Widget สำหรับแสดงตัวเลือกฟิลเตอร์"""

    filter_applied = pyqtSignal(int, str, bool)  # column, text, show_blank_only
    filter_cleared = pyqtSignal(int)  # column

    def __init__(self, column, parent=None):
        super().__init__(parent)
        self.column = column
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setup_ui()
        self.adjustSize()

    def setup_ui(self):
        self.setStyleSheet(
            """
            FilterDropdown { /* Changed QWidget to FilterDropdown for specific targeting */
                background-color: white;
                border: none; /* Removed the border */
                border-radius: 6px; /* Keep for rounded background */
                padding: 1px; /* Prevents content from touching edge if background is rounded */
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QCheckBox {
                font-size: 12px;
                color: #333;
                padding: 4px;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#clearBtn {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                color: #666;
            }
            QPushButton#clearBtn:hover {
                background-color: #e0e0e0;
            }
            QPushButton#applyBtn {
                background-color: #2196F3;
                border: none;
                color: white;
            }
            QPushButton#applyBtn:hover {
                background-color: #1976D2;
            }
            QLabel#filterLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333;
                border: none; /* Ensure label has no border if QWidget style was too general */
            }
        """
        )
        self.setObjectName(
            "FilterDropdown"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            12, 12, 12, 12
        )
        layout.setSpacing(10)

        # ช่องค้นหา
        search_label = QLabel("ค้นหาข้อมูล:")
        search_label.setObjectName("filterLabel")
        layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ป้อนข้อความที่ต้องการค้นหา...")
        layout.addWidget(self.search_input)

        # ตัวเลือก Blank
        self.blank_checkbox = QCheckBox("แสดงเฉพาะข้อมูลว่าง (Null/Empty)")
        layout.addWidget(self.blank_checkbox)

        # ปุ่ม
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("ล้าง")
        self.clear_button.setObjectName("clearBtn")
        self.clear_button.clicked.connect(self.clear_filter)
        self.clear_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.apply_button = QPushButton("ค้นหา")
        self.apply_button.setObjectName("applyBtn")
        self.apply_button.clicked.connect(self.apply_filter)
        self.apply_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)

        layout.addLayout(button_layout)

        # เชื่อมต่อ Enter key
        self.search_input.returnPressed.connect(self.apply_filter)

    def apply_filter(self):
        """ใช้ฟิลเตอร์"""
        search_text = self.search_input.text().strip()
        show_blank_only = self.blank_checkbox.isChecked()

        self.filter_applied.emit(self.column, search_text, show_blank_only)
        self.hide()

    def clear_filter(self):
        """ล้างฟิลเตอร์"""
        self.search_input.clear()
        self.blank_checkbox.setChecked(False)
        self.filter_cleared.emit(self.column)
        self.hide()

    def set_filter_values(self, search_text="", show_blank=False):
        """ตั้งค่าฟิลเตอร์"""
        self.search_input.setText(search_text)
        self.blank_checkbox.setChecked(show_blank)
        self.adjustSize()

    def showEvent(self, event):
        """ปรับขนาดเมื่อ widget แสดงผล"""
        super().showEvent(event)
        self.adjustSize()


class FilterableMultiLineHeaderView(QHeaderView):
    """MultiLineHeaderView ที่มีฟิลเตอร์"""

    filter_requested = pyqtSignal(int, str, bool)  # column, text, show_blank_only
    filter_cleared = pyqtSignal(int)  # column

    TEXT_LINES_ALLOWANCE = 3
    VERTICAL_PADDING_PER_LINE = 0
    TEXT_BLOCK_PADDING = 6

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.mainTexts = {}
        self.subTexts = {}
        self.filter_buttons = {}  # เก็บตำแหน่งปุ่มฟิลเตอร์
        self.active_filters = {}  # เก็บฟิลเตอร์ที่ใช้งานอยู่
        self.filter_dropdown = None

        self.setDefaultAlignment(Qt.AlignCenter)
        self.setSectionsMovable(True)
        self.sectionResized.connect(self.on_section_resized)
        self.sectionClicked.connect(self.handle_section_clicked)

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

        # Area for drawing text, adjusted for filter button
        filter_button_width = 20 if logicalIndex > 0 else 0
        text_drawing_rect = QRect(rect).adjusted(
            self.TEXT_BLOCK_PADDING // 2,
            self.TEXT_BLOCK_PADDING // 2,
            -(self.TEXT_BLOCK_PADDING // 2 + filter_button_width),
            -self.TEXT_BLOCK_PADDING // 2,
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
                max_h_for_main = max(
                    main_fm.height(), max_y - current_y - min_sub_h_needed
                )

            main_text_bound_rect = main_fm.boundingRect(
                QRect(0, 0, available_width, int(max_h_for_main)),
                Qt.AlignCenter | Qt.TextWordWrap,
                mainText,
            )

            actual_main_h = main_text_bound_rect.height()

            if current_y + actual_main_h <= max_y + 1:
                draw_rect = QRect(
                    text_drawing_rect.x(), current_y, available_width, actual_main_h
                )
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
                    draw_rect = QRect(
                        text_drawing_rect.x(),
                        current_y,
                        available_width,
                        remaining_height_for_sub,
                    )
                    painter.drawText(
                        draw_rect, Qt.AlignCenter | Qt.TextWordWrap, subText
                    )

        painter.restore()

        # Draw filter button (ข้ามคอลัมน์ลำดับ)
        if logicalIndex > 0:
            self.draw_filter_button(painter, rect, logicalIndex)

    def draw_filter_button(self, painter, rect, logicalIndex):
        """วาดปุ่มฟิลเตอร์"""
        button_size = 16
        padding = 4

        # คำนวณตำแหน่งปุ่ม (มุมขวาบน)
        button_x = rect.right() - button_size - padding
        button_y = rect.top() + padding
        button_rect = QRect(button_x, button_y, button_size, button_size)

        # เก็บตำแหน่งปุ่ม
        self.filter_buttons[logicalIndex] = button_rect

        painter.save()

        # ตรวจสอบว่ามีฟิลเตอร์ใช้งานอยู่หรือไม่
        has_active_filter = logicalIndex in self.active_filters

        # สีพื้นหลังปุ่ม
        if has_active_filter:
            painter.setBrush(QBrush(QColor("#2196F3")))
            painter.setPen(QPen(QColor("#1976D2"), 1))
        else:
            painter.setBrush(QBrush(QColor("#f0f0f0")))
            painter.setPen(QPen(QColor("#bdbdbd"), 1))

        # วาดกรอบปุ่ม
        painter.drawRoundedRect(button_rect, 2, 2)

        # วาดไอคอนฟิลเตอร์ (สามเหลี่ยม)
        icon_color = QColor("white") if has_active_filter else QColor("#666666")
        painter.setPen(QPen(icon_color, 1))
        painter.setBrush(QBrush(icon_color))

        # สร้างรูปสามเหลี่ยม (ไอคอนฟิลเตอร์)
        center_x = button_rect.center().x()
        center_y = button_rect.center().y()
        triangle_size = 6

        triangle = QPolygon(
            [
                QPoint(center_x - triangle_size // 2, center_y - triangle_size // 4),
                QPoint(center_x + triangle_size // 2, center_y - triangle_size // 4),
                QPoint(center_x, center_y + triangle_size // 4),
            ]
        )

        painter.drawPolygon(triangle)
        painter.restore()

    def mousePressEvent(self, event):
        """จัดการการคลิกเมาส์"""
        if event.button() == Qt.LeftButton:
            logical_index = self.logicalIndexAt(event.pos())

            if logical_index >= 0 and logical_index in self.filter_buttons:
                button_rect = self.filter_buttons[logical_index]
                if button_rect.contains(event.pos()):
                    self.show_filter_dropdown(logical_index, event.globalPos())
                    return

        # ถ้าไม่ใช่การคลิกปุ่มฟิลเตอร์ ให้ทำงานปกติ
        super().mousePressEvent(event)

    def handle_section_clicked(self, logical_index):
        """จัดการการคลิกที่ส่วนหัว (ไม่ใช่ปุ่มฟิลเตอร์)"""
        pass

    def show_filter_dropdown(self, column, global_pos):
        """แสดง dropdown ฟิลเตอร์"""
        if self.filter_dropdown:
            self.filter_dropdown.close()

        self.filter_dropdown = FilterDropdown(column, self)
        self.filter_dropdown.filter_applied.connect(self.apply_filter)
        self.filter_dropdown.filter_cleared.connect(self.clear_filter)

        # ตั้งค่าฟิลเตอร์ปัจจุบัน (ถ้ามี)
        if column in self.active_filters:
            filter_info = self.active_filters[column]
            self.filter_dropdown.set_filter_values(
                filter_info.get("text", ""), filter_info.get("show_blank", False)
            )

        # แสดง dropdown ใต้ปุ่มฟิลเตอร์
        dropdown_x = global_pos.x() - 250  # ขยับไปทางซ้าย
        dropdown_y = global_pos.y() + 10

        self.filter_dropdown.move(dropdown_x, dropdown_y)
        self.filter_dropdown.show()
        self.filter_dropdown.search_input.setFocus()

    def apply_filter(self, column, text, show_blank_only):
        """ใช้ฟิลเตอร์"""
        if text or show_blank_only:
            self.active_filters[column] = {"text": text, "show_blank": show_blank_only}
        else:
            if column in self.active_filters:
                del self.active_filters[column]

        self.filter_requested.emit(column, text, show_blank_only)
        self.update()

    def clear_filter(self, column):
        """ล้างฟิลเตอร์"""
        if column in self.active_filters:
            del self.active_filters[column]

        self.filter_cleared.emit(column)
        self.update()

    def clear_all_filters(self):
        """ล้างฟิลเตอร์ทั้งหมด"""
        self.active_filters.clear()
        self.update()

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


# เพิ่ม alias เพื่อความเข้ากันได้
MultiLineHeaderView = FilterableMultiLineHeaderView
