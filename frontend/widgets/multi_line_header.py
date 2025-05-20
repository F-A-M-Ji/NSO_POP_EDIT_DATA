# from PyQt5.QtWidgets import QHeaderView
# from PyQt5.QtCore import Qt, QRect, QSize
# from PyQt5.QtGui import QPainter


# class MultiLineHeaderView(QHeaderView):
#     def __init__(self, orientation, parent=None):
#         super().__init__(orientation, parent)
#         self.mainTexts = {}
#         self.subTexts = {}
#         self.setDefaultAlignment(Qt.AlignCenter)

#         # ตั้งค่าให้สามารถปรับขนาดคอลัมน์ได้
#         self.setSectionsMovable(True)
#         self.setSectionsClickable(True)

#     def setColumnText(self, column, mainText, subText=""):
#         self.mainTexts[column] = mainText
#         self.subTexts[column] = subText
#         self.model().headerDataChanged.emit(Qt.Horizontal, column, column)

#     def sizeHint(self):
#         # คำนวณความสูงที่เหมาะสมสำหรับหัวคอลัมน์ 2 บรรทัด
#         fm = self.fontMetrics()
#         height = fm.height() * 2 + 12  # สูง 2 บรรทัด + padding
#         size = super().sizeHint()
#         return QSize(size.width(), height)

#     def paintSection(self, painter, rect, logicalIndex):
#         painter.save()

#         # วาดพื้นหลังและกรอบ
#         option = self.viewOptions()
#         self.style().drawControl(self.style().CE_Header, option, painter, self)

#         # ดึงข้อความสำหรับแสดง
#         mainText = self.mainTexts.get(logicalIndex, "")
#         subText = self.subTexts.get(logicalIndex, "")

#         # คำนวณตำแหน่งสำหรับแสดงข้อความ
#         fm = painter.fontMetrics()
#         padding = 3
#         mainRect = QRect(
#             rect.x() + padding,
#             rect.y() + padding,
#             rect.width() - 2 * padding,
#             fm.height(),
#         )
#         subRect = QRect(
#             rect.x() + padding,
#             rect.y() + padding + fm.height(),
#             rect.width() - 2 * padding,
#             fm.height(),
#         )

#         # วาดข้อความหลัก
#         painter.drawText(mainRect, Qt.AlignCenter, mainText)

#         # วาดข้อความรอง (ข้อความในวงเล็บ)
#         if subText:
#             font = painter.font()
#             font.setPointSize(font.pointSize() - 1)
#             painter.setFont(font)
#             painter.drawText(subRect, Qt.AlignCenter, subText)

#         painter.restore()


from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QPen, QColor


class MultiLineHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.mainTexts = {}
        self.subTexts = {}
        self.setDefaultAlignment(Qt.AlignCenter)

        # เปิดให้คอลัมน์ปรับขนาดได้
        self.setSectionsMovable(True)
        self.setSectionsClickable(True)

        # เพิ่ม stylesheet สำหรับเส้นขอบ
        # self.setStyleSheet(
        #     """
        #     QHeaderView::section {
        #         background-color: #e3f2fd;
        #         border: 1px solid #bbdefb;
        #         border-top: 1px solid #bbdefb;
        #         border-left: 1px solid #bbdefb;
        #         border-right: 1px solid #bbdefb;
        #         border-bottom: 1px solid #bbdefb;
        #         padding: 4px;
        #     }
        #     QHeaderView::section:selected {
        #         background-color: #bbdefb;
        #     }
        # """
        # )

    def setColumnText(self, column, mainText, subText=""):
        self.mainTexts[column] = mainText
        self.subTexts[column] = subText
        self.model().headerDataChanged.emit(Qt.Horizontal, column, column)

    def sizeHint(self):
        # คำนวณความสูงที่เหมาะสมสำหรับหัวคอลัมน์ 2 บรรทัด
        fm = self.fontMetrics()
        height = fm.height() * 2 + 10  # สูง 2 บรรทัด + padding
        size = super().sizeHint()
        return QSize(size.width(), height)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()

        # วาดพื้นหลังและกรอบ
        option = self.viewOptions()
        self.style().drawControl(self.style().CE_Header, option, painter, self)

        # ดึงข้อความสำหรับแสดง
        mainText = self.mainTexts.get(logicalIndex, "")
        subText = self.subTexts.get(logicalIndex, "")

        # คำนวณตำแหน่งสำหรับแสดงข้อความ
        fm = painter.fontMetrics()
        padding = 4
        mainRect = QRect(
            rect.x() + padding,
            rect.y() + padding,
            rect.width() - 2 * padding,
            fm.height(),
        )
        subRect = QRect(
            rect.x() + padding,
            rect.y() + padding + fm.height(),
            rect.width() - 2 * padding,
            fm.height(),
        )

        # วาดข้อความหลัก
        painter.setPen(Qt.black)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(mainRect, Qt.AlignCenter, mainText)

        # วาดข้อความรอง (ข้อความในวงเล็บ)
        if subText:
            font = painter.font()
            font.setBold(False)
            font.setPointSize(font.pointSize() - 1)
            painter.setPen(Qt.darkGray)
            painter.setFont(font)
            painter.drawText(subRect, Qt.AlignCenter, subText)

        # วาดเส้นขอบของหัวคอลัมน์
        painter.setPen(QPen(QColor("#bdbdbd"), 1))  # สีและความหนาของเส้น
        painter.drawLine(rect.topRight(), rect.bottomRight())  # เส้นขวา
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())  # เส้นล่าง

        painter.restore()
