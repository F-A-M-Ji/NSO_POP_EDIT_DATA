import os
import datetime

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QApplication,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QColor, QBrush, QFont, QFontMetrics

from backend.column_mapper import ColumnMapper
from backend.alldata_operations import (
    fetch_all_r_alldata_fields,
    search_r_alldata,
    save_edited_r_alldata_rows,
    get_distinct_values,
    get_area_name_mapping,
)
from frontend.widgets.multi_line_header import MultiLineHeaderView
from frontend.widgets.multi_line_header import FilterableMultiLineHeaderView
from frontend.utils.error_message import show_error_message, show_info_message
from frontend.utils.shadow_effect import add_shadow_effect
from frontend.utils.resource_path import resource_path
from frontend.data_rules.edit_data_rules import (
    LOGICAL_PK_FIELDS_CONFIG,
    NON_EDITABLE_FIELDS_CONFIG,
    FIELD_VALIDATION_RULES_CONFIG,
    update_rules_from_excel_data,
)
from frontend.data_rules.edit_data_validation import (
    validate_field_value,
    _validate_excel_padded_number,
    _validate_text,
    _validate_options,
    _validate_range,
    _validate_custom,
    _validate_int_range,
    _validate_padded_number,
    validate_edited_data,
    show_validation_errors,
    load_validation_data_from_excel,
)
from frontend.widgets.filters import (
    apply_table_filter,
    clear_table_filter,
    filter_table_data,
    display_filtered_results,
)


class EditDataScreen(QWidget):
    LOGICAL_PK_FIELDS = LOGICAL_PK_FIELDS_CONFIG
    NON_EDITABLE_FIELDS = NON_EDITABLE_FIELDS_CONFIG
    FIELD_VALIDATION_RULES = FIELD_VALIDATION_RULES_CONFIG

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.location_data = None
        self.column_mapper = ColumnMapper.get_instance()

        self.db_column_names = []
        self.original_data_cache = []
        self.filtered_data_cache = []
        self.edited_items = {}
        self.active_filters = {}

        self._all_db_fields_r_alldata = []

        # โหลดข้อมูลการตรวจสอบจากไฟล์ Excel
        self.validation_data_from_excel = load_validation_data_from_excel(self)

        # อัปเดตกฎการตรวจสอบ
        update_rules_from_excel_data(self)

        self.setup_ui()
        self.load_location_data()
        self._all_db_fields_r_alldata = fetch_all_r_alldata_fields()

    def update_user_fullname(self, fullname):
        if hasattr(self, "user_fullname_label"):
            self.user_fullname_label.setText(fullname)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        header_layout = QHBoxLayout()
        header_label = QLabel("ระบบแก้ไขข้อมูล สปค. 68")
        header_label.setObjectName("headerLabel")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        self.user_fullname_label = QLabel("User: N/A")
        self.user_fullname_label.setObjectName("userFullnameLabel")
        header_layout.addWidget(self.user_fullname_label)
        spacer = QLabel("|")
        header_layout.addWidget(spacer)
        logout_button = QPushButton("ออกจากระบบ")
        logout_button.setObjectName("secondaryButton")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)
        main_layout.addLayout(header_layout)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(self.content_frame)
        add_shadow_effect(self.content_frame)

        search_section = QFrame()
        search_section.setObjectName("searchSection")
        search_layout = QVBoxLayout(search_section)
        search_title = QLabel("ค้นหาข้อมูล")
        search_title.setObjectName("sectionTitle")
        search_layout.addWidget(search_title)

        search_row1_layout = QHBoxLayout()

        region_layout = QVBoxLayout()
        region_label = QLabel("ภาค:")
        self.region_combo = QComboBox()
        self.region_combo.setObjectName("searchComboBox")
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_combo)
        search_row1_layout.addLayout(region_layout)

        province_layout = QVBoxLayout()
        province_label = QLabel("จังหวัด:")
        self.province_combo = QComboBox()
        self.province_combo.setObjectName("searchComboBox")
        self.province_combo.currentIndexChanged.connect(self.on_province_changed)
        province_layout.addWidget(province_label)
        province_layout.addWidget(self.province_combo)
        search_row1_layout.addLayout(province_layout)

        district_layout = QVBoxLayout()
        district_label = QLabel("อำเภอ/เขต:")
        self.district_combo = QComboBox()
        self.district_combo.setObjectName("searchComboBox")
        self.district_combo.currentIndexChanged.connect(self.on_district_changed)
        district_layout.addWidget(district_label)
        district_layout.addWidget(self.district_combo)
        search_row1_layout.addLayout(district_layout)

        subdistrict_layout = QVBoxLayout()
        subdistrict_label = QLabel("ตำบล/แขวง:")
        self.subdistrict_combo = QComboBox()
        self.subdistrict_combo.setObjectName("searchComboBox")
        self.subdistrict_combo.currentIndexChanged.connect(self.on_subdistrict_changed)
        subdistrict_layout.addWidget(subdistrict_label)
        subdistrict_layout.addWidget(self.subdistrict_combo)
        search_row1_layout.addLayout(subdistrict_layout)

        # เพิ่ม dropdown สำหรับ AreaCode
        area_code_layout = QVBoxLayout()
        area_code_label = QLabel("เขตการปกครอง:")
        self.area_code_combo = QComboBox()
        self.area_code_combo.setObjectName("searchComboBox")
        self.area_code_combo.currentIndexChanged.connect(self.on_area_code_changed)
        area_code_layout.addWidget(area_code_label)
        area_code_layout.addWidget(self.area_code_combo)
        search_row1_layout.addLayout(area_code_layout)

        # เพิ่ม dropdown สำหรับ EA_NO
        ea_no_layout = QVBoxLayout()
        ea_no_label = QLabel("เขตแจงนับ:")
        self.ea_no_combo = QComboBox()
        self.ea_no_combo.setObjectName("searchComboBox")
        self.ea_no_combo.currentIndexChanged.connect(self.on_ea_no_changed)
        ea_no_layout.addWidget(ea_no_label)
        ea_no_layout.addWidget(self.ea_no_combo)
        search_row1_layout.addLayout(ea_no_layout)

        search_layout.addLayout(search_row1_layout)

        # ชั้นที่ 2
        search_row2_layout = QHBoxLayout()

        # เพิ่ม dropdown สำหรับ VilCode
        vil_code_layout = QVBoxLayout()
        vil_code_label = QLabel("หมู่ที่:")
        self.vil_code_combo = QComboBox()
        self.vil_code_combo.setObjectName("searchComboBox")
        self.vil_code_combo.currentIndexChanged.connect(self.on_vil_code_changed)
        vil_code_layout.addWidget(vil_code_label)
        vil_code_layout.addWidget(self.vil_code_combo)
        search_row2_layout.addLayout(vil_code_layout)

        # เพิ่ม dropdown สำหรับ VilName
        vil_name_layout = QVBoxLayout()
        vil_name_label = QLabel("ชื่อหมู่บ้าน:")
        self.vil_name_combo = QComboBox()
        self.vil_name_combo.setObjectName("searchComboBox")
        self.vil_name_combo.currentIndexChanged.connect(self.on_vil_name_changed)
        vil_name_layout.addWidget(vil_name_label)
        vil_name_layout.addWidget(self.vil_name_combo)
        search_row2_layout.addLayout(vil_name_layout)

        # เพิ่ม dropdown สำหรับ BuildingNumber
        building_number_layout = QVBoxLayout()
        building_number_label = QLabel("ลำดับที่สิ่งปลูกสร้าง:")
        self.building_number_combo = QComboBox()
        self.building_number_combo.setObjectName("searchComboBox")
        self.building_number_combo.currentIndexChanged.connect(
            self.on_building_number_changed
        )
        building_number_layout.addWidget(building_number_label)
        building_number_layout.addWidget(self.building_number_combo)
        search_row2_layout.addLayout(building_number_layout)

        # เพิ่ม dropdown สำหรับ HouseholdNumber
        household_number_layout = QVBoxLayout()
        household_number_label = QLabel("ลำดับที่ครัวเรือน:")
        self.household_number_combo = QComboBox()
        self.household_number_combo.setObjectName("searchComboBox")
        self.household_number_combo.currentIndexChanged.connect(
            self.on_household_number_changed
        )
        household_number_layout.addWidget(household_number_label)
        household_number_layout.addWidget(self.household_number_combo)
        search_row2_layout.addLayout(household_number_layout)

        # เพิ่ม dropdown สำหรับ HouseholdMemberNumber
        household_member_number_layout = QVBoxLayout()
        household_member_number_label = QLabel("ลำดับที่สมาชิกในครัวเรือน:")
        self.household_member_number_combo = QComboBox()
        self.household_member_number_combo.setObjectName("searchComboBox")
        self.household_member_number_combo.currentIndexChanged.connect(
            self.on_household_member_number_changed
        )
        household_member_number_layout.addWidget(household_member_number_label)
        household_member_number_layout.addWidget(self.household_member_number_combo)
        search_row2_layout.addLayout(household_member_number_layout)

        buttons_layout = QVBoxLayout()
        buttons_label = QLabel("")  # เว้นพื้นที่สำหรับ label เหมือน dropdown อื่นๆ
        buttons_layout.addWidget(buttons_label)

        buttons_container = QHBoxLayout()
        self.search_button = QPushButton("ค้นหา")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.clicked.connect(self.search_data)
        self.search_button.setFixedWidth(120)
        self.search_button.setFixedHeight(20)  # ให้สูงเท่า dropdown
        buttons_container.addWidget(self.search_button)

        self.clear_button = QPushButton("ล้าง")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.setFixedWidth(120)
        self.clear_button.setFixedHeight(20)  # ให้สูงเท่า dropdown
        buttons_container.addWidget(self.clear_button)

        # สร้าง widget container เพื่อให้ปุ่มอยู่ในตำแหน่งล่าง
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_container)
        buttons_layout.addWidget(buttons_widget)

        search_row2_layout.addLayout(buttons_layout)

        # กำหนด minimum width ให้ dropdown ทั้งหมด
        min_width = 150

        # บรรทัดแรก
        self.region_combo.setMinimumWidth(min_width)
        self.province_combo.setMinimumWidth(min_width)
        self.district_combo.setMinimumWidth(min_width)
        self.subdistrict_combo.setMinimumWidth(min_width)
        self.area_code_combo.setMinimumWidth(min_width)
        self.ea_no_combo.setMinimumWidth(min_width)

        # บรรทัดที่สอง
        self.vil_code_combo.setMinimumWidth(min_width)
        self.vil_name_combo.setMinimumWidth(min_width)
        self.building_number_combo.setMinimumWidth(min_width)
        self.household_number_combo.setMinimumWidth(min_width)
        self.household_member_number_combo.setMinimumWidth(min_width)

        content_layout.addWidget(search_section)

        search_layout.addLayout(search_row2_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(line)

        results_section = QFrame()
        results_section.setObjectName("resultsSection")
        results_layout = QVBoxLayout(results_section)
        results_title = QLabel("ผลการค้นหา (ดับเบิ้ลคลิกเพื่อแก้ไข)")
        results_title.setObjectName("sectionTitle")
        results_layout.addWidget(results_title)

        # เพิ่มพื้นที่แสดงสถานะการแก้ไข
        status_layout = QHBoxLayout()

        self.edit_status_label = QLabel("ไม่มีการแก้ไข")
        # self.edit_status_label.setStyleSheet("color: #666666; font-style: italic;")
        status_layout.addWidget(self.edit_status_label)

        status_layout.addStretch()

        self.results_table = QTableWidget()
        self.setup_results_table()
        results_layout.addWidget(self.results_table)

        self.reset_edits_button = QPushButton("ยกเลิกการแก้ไข")
        self.reset_edits_button.setObjectName("secondaryButton")
        self.reset_edits_button.setCursor(Qt.PointingHandCursor)
        self.reset_edits_button.clicked.connect(self.reset_all_edits)
        self.reset_edits_button.setVisible(False)  # ซ่อนไว้ก่อน
        # status_layout.addWidget(self.reset_edits_button)

        results_layout.addLayout(status_layout)

        self.save_edits_button = QPushButton("บันทึกการแก้ไข")
        self.save_edits_button.setObjectName("primaryButton")
        self.save_edits_button.setCursor(Qt.PointingHandCursor)
        self.save_edits_button.clicked.connect(self.prompt_save_edits)
        # self.save_edits_button.setFixedWidth(130)
        self.save_edits_button.setEnabled(False)

        buttons_under_table_layout = QHBoxLayout()
        buttons_under_table_layout.addStretch()
        buttons_under_table_layout.addWidget(self.reset_edits_button)
        buttons_under_table_layout.addWidget(self.save_edits_button)
        results_layout.addLayout(buttons_under_table_layout)

        content_layout.addWidget(results_section, 1)
        main_layout.addWidget(self.content_frame, 1)
        self.setLayout(main_layout)

        self.setup_table_headers_text_and_widths()

    def setup_results_table(self):
        self.results_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.results_table.itemChanged.connect(self.handle_item_changed)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_table.setShowGrid(True)
        self.results_table.setGridStyle(Qt.SolidLine)
        self.results_table.verticalHeader().setVisible(False)

        # === เพิ่มบรรทัดนี้เพื่อตรึงคอลัมน์แรก ===
        # self.results_table.setFixedColumnCount(1)
        # self.results_table.setColumnFrozen(0, True)
        # =======================================

        from frontend.widgets.multi_line_header import (
            FilterableMultiLineHeaderView,
        )  # ย้าย import มาไว้ใกล้จุดใช้งาน หรือไว้ด้านบนตามปกติ

        self.header = FilterableMultiLineHeaderView(Qt.Horizontal, self.results_table)

        # Import ฟังก์ชันกรอง
        from frontend.widgets.filters import apply_table_filter, clear_table_filter

        self.header.filter_requested.connect(
            lambda column, text, show_blank_only: apply_table_filter(
                self, column, text, show_blank_only
            )
        )
        self.header.filter_cleared.connect(
            lambda column: clear_table_filter(self, column)
        )

        self.results_table.setHorizontalHeader(self.header)

    def setup_table_headers_text_and_widths(self):
        displayed_fields = self.column_mapper.get_fields_to_show()
        if not displayed_fields:
            self.results_table.setColumnCount(1)
            self.header.setColumnText(0, "ลำดับ", "")
            self.results_table.setColumnWidth(0, 60)
            return

        self.results_table.setColumnCount(len(displayed_fields) + 1)

        header_base_font = self.header.font()

        self.header.setColumnText(0, "ลำดับ", "")
        self.results_table.setColumnWidth(0, 60)

        for i, field_name in enumerate(displayed_fields):
            visual_col_idx = i + 1
            column_name_display = self.column_mapper.get_column_name(field_name)
            main_text, sub_text = self.column_mapper.format_column_header(
                column_name_display
            )
            self.header.setColumnText(visual_col_idx, main_text, sub_text)

            main_text_painter_font = QFont(header_base_font)
            main_text_painter_font.setBold(True)
            main_fm = QFontMetrics(main_text_painter_font)

            sub_text_painter_font = QFont(header_base_font)
            sub_text_painter_font.setPointSize(header_base_font.pointSize() - 1)
            sub_fm = QFontMetrics(sub_text_painter_font)

            main_w = main_fm.horizontalAdvance(main_text) if main_text else 0
            sub_w = sub_fm.horizontalAdvance(sub_text) if sub_text else 0

            required_unwrapped_text_width = max(main_w, sub_w)
            calculated_width = (
                required_unwrapped_text_width + self.header.TEXT_BLOCK_PADDING
            )
            calculated_width += 20

            min_col_width = 100
            final_column_width = max(calculated_width, min_col_width)

            self.results_table.setColumnWidth(visual_col_idx, int(final_column_width))

        self.header.setSectionResizeMode(QHeaderView.Interactive)

        self.header.style().unpolish(self.header)
        self.header.style().polish(self.header)
        self.header.updateGeometries()
        self.results_table.updateGeometries()

    def reset_all_edits(self):
        """ยกเลิกการแก้ไขทั้งหมดและคืนค่าเดิม"""
        if not self.edited_items:
            return

        reply = QMessageBox.question(
            self,
            "ยกเลิกการแก้ไข",
            f"คุณต้องการยกเลิกการแก้ไขทั้งหมด {len(self.edited_items)} รายการหรือไม่?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # คืนค่าเดิมให้กับทุก cell ที่ถูกแก้ไข
            displayed_db_fields = self.column_mapper.get_fields_to_show()

            for row, visual_col in list(self.edited_items.keys()):
                item = self.results_table.item(row, visual_col)
                if item and row < len(self.original_data_cache):
                    db_field_col_idx = visual_col - 1
                    if 0 <= db_field_col_idx < len(displayed_db_fields):
                        db_field_name = displayed_db_fields[db_field_col_idx]
                        original_value = self.original_data_cache[row].get(
                            db_field_name
                        )
                        original_text = (
                            str(original_value) if original_value is not None else ""
                        )
                        item.setText(original_text)
                        item.setBackground(QBrush())  # คืนสีพื้นหลัง

            # ล้างการแก้ไขทั้งหมด
            self.edited_items.clear()
            self.update_save_button_state()

    def update_save_button_state(self):
        """อัปเดตสถานะปุ่มบันทึก และแสดงข้อมูลการแก้ไขปัจจุบัน"""
        has_edits = bool(self.edited_items)
        edit_count = len(self.edited_items)

        # อัปเดตสถานะปุ่มบันทึก
        self.save_edits_button.setEnabled(has_edits)

        # อัปเดตข้อความบนปุ่ม
        if has_edits:
            self.save_edits_button.setText(f"บันทึกการแก้ไข ({edit_count})")
        else:
            self.save_edits_button.setText("บันทึกการแก้ไข")

        # อัปเดตสถานะการแก้ไข
        if hasattr(self, "edit_status_label"):
            if has_edits:
                self.edit_status_label.setText(f"มีการแก้ไข {edit_count} รายการ")
                self.edit_status_label.setStyleSheet(
                    "color: #FF9800; font-style: italic; font-weight: bold;"
                )
            else:
                self.edit_status_label.setText("ไม่มีการแก้ไข")
                # self.edit_status_label.setStyleSheet(
                #     "color: #666666; font-style: italic;"
                # )
                self.edit_status_label.setStyleSheet("")

        # แสดง/ซ่อนปุ่มรีเซ็ต
        if hasattr(self, "reset_edits_button"):
            self.reset_edits_button.setVisible(has_edits)

        # Force style update
        # self.save_edits_button.style().unpolish(self.save_edits_button)
        # self.save_edits_button.style().polish(self.save_edits_button)
        # self.save_edits_button.update()

    def handle_item_changed(self, item: QTableWidgetItem):
        """ตรวจสอบและจัดการการเปลี่ยนแปลงข้อมูลในตารางแบบเรียลไทม์"""
        if not item or not self.original_data_cache:
            return

        row = item.row()
        visual_col = item.column()

        # ข้ามคอลัมน์ลำดับ
        if visual_col == 0:
            return

        db_field_col_idx = visual_col - 1

        # **สำคัญ: จัดการกรณีที่มีการกรองข้อมูล**
        if (
            hasattr(self, "filtered_data_cache")
            and self.filtered_data_cache
            and row < len(self.filtered_data_cache)
        ):
            # หา index ของข้อมูลนี้ใน original_data_cache
            filtered_row_data = self.filtered_data_cache[row]
            original_row_idx = -1

            # ค้นหาใน original_data_cache โดยใช้ Primary Key
            for i, original_row in enumerate(self.original_data_cache):
                # เปรียบเทียบ Primary Key
                is_same_row = True
                for pk_field in self.LOGICAL_PK_FIELDS:
                    if original_row.get(pk_field) != filtered_row_data.get(pk_field):
                        is_same_row = False
                        break

                if is_same_row:
                    original_row_idx = i
                    break

            if original_row_idx == -1:
                return

            # ใช้ original row index แทน filtered row index
            original_row_dict = self.original_data_cache[original_row_idx]
        else:
            if row >= len(self.original_data_cache):
                return
            original_row_dict = self.original_data_cache[row]
            original_row_idx = row

        displayed_db_fields = self.column_mapper.get_fields_to_show()

        if db_field_col_idx >= len(displayed_db_fields) or db_field_col_idx < 0:
            return

        db_field_name_for_column = displayed_db_fields[db_field_col_idx]

        # ป้องกันการแก้ไข Primary Key fields และฟิลด์ที่กำหนดว่าไม่สามารถแก้ไขได้
        if (
            db_field_name_for_column in self.LOGICAL_PK_FIELDS
            or db_field_name_for_column in self.NON_EDITABLE_FIELDS
        ):
            original_value = original_row_dict.get(db_field_name_for_column)
            item.setText(str(original_value) if original_value is not None else "")
            return

        # ดึงข้อมูลใหม่และเดิม
        new_text = item.text().strip()
        original_value = original_row_dict.get(db_field_name_for_column)

        # แปลงข้อมูลเดิมเป็น string เพื่อเปรียบเทียบ
        if original_value is None:
            original_value_str = ""
        elif isinstance(original_value, (int, float)):
            if float(original_value).is_integer():
                original_value_str = str(int(original_value))
            else:
                original_value_str = str(original_value)
        else:
            original_value_str = str(original_value).strip()

        # เปรียบเทียบข้อมูล
        is_changed = original_value_str != new_text

        # **สำคัญ: ใช้ original_row_idx สำหรับ edited_items key**
        edit_key = (original_row_idx, visual_col)

        if is_changed:
            # มีการเปลี่ยนแปลง - เพิ่มลงใน edited_items และเปลี่ยนสีพื้นหลัง
            self.edited_items[edit_key] = new_text
            item.setBackground(QColor("lightyellow"))
        else:
            # ไม่มีการเปลี่ยนแปลง หรือเปลี่ยนกลับเป็นค่าเดิม - ลบออกจาก edited_items
            if edit_key in self.edited_items:
                del self.edited_items[edit_key]
            item.setBackground(QBrush())

        # อัปเดตสถานะปุ่มทันทีหลังจากการเปลี่ยนแปลง
        self.update_save_button_state()

    def search_data(self):
        """ค้นหาข้อมูล พร้อมเตือนถ้ามีการแก้ไขที่ยังไม่ได้บันทึก"""
    
        # ตรวจสอบการแก้ไขที่ยังไม่ได้บันทึก (เหมือนเดิม)
        if self.edited_items:
            reply = QMessageBox.question(
                self,
                "การเปลี่ยนแปลงที่ยังไม่ได้บันทึก",
                f"คุณมีการแก้ไข {len(self.edited_items)} รายการที่ยังไม่ได้บันทึก "
                "ต้องการบันทึกก่อนค้นหาใหม่หรือไม่?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                self.execute_save_edits()
                if self.edited_items:
                    return
            elif reply == QMessageBox.Cancel:
                return

        if not self._all_db_fields_r_alldata:
            self._all_db_fields_r_alldata = fetch_all_r_alldata_fields()
            if not self._all_db_fields_r_alldata:
                show_error_message(
                    self, "Error", "โครงสร้างตาราง r_alldata_edit ไม่พร้อมใช้งาน ไม่สามารถค้นหาได้"
                )
                return

        # รวมเงื่อนไขการค้นหาทั้งหมด
        search_conditions = {}
    
        # เงื่อนไขจาก location (เดิม)
        location_codes = self.get_selected_codes()
        search_conditions.update(location_codes)
    
        # เงื่อนไขใหม่
        additional_conditions = {
            "AreaCode": self.get_selected_area_code(),
            "EA_NO": self.get_selected_ea_no(),
            "VilCode": self.get_selected_vil_code(),
            "VilName": self.get_selected_vil_name(),
            "BuildingNumber": self.get_selected_building_number(),
            "HouseholdNumber": self.get_selected_household_number(),
            "HouseholdMemberNumber": self.get_selected_household_member_number(),
        }
    
        # เพิ่มเงื่อนไขที่มีการเลือก
        for key, value in additional_conditions.items():
            if value is not None:
                search_conditions[key] = value  # รวมทั้งค่า blank ("")

        # ตรวจสอบว่ามีเงื่อนไขการค้นหาหรือไม่
        if all(value is None for value in search_conditions.values()):
            show_error_message(
                self, "Search Error", "กรุณาเลือกเงื่อนไขในการค้นหาอย่างน้อยหนึ่งรายการ"
            )
            return

        # ค้นหาข้อมูล
        results, db_cols, error_msg = search_r_alldata(
            search_conditions, self._all_db_fields_r_alldata, self.LOGICAL_PK_FIELDS
        )

        if error_msg:
            show_error_message(self, "Search Error", error_msg)
            self.results_table.setRowCount(0)
            self.original_data_cache.clear()
            return

        self.db_column_names = db_cols
        self.edited_items.clear()
        self.update_save_button_state()
        self.display_results(results)

    def display_results(self, results_tuples):
        self.setup_table_headers_text_and_widths()

        self.results_table.setUpdatesEnabled(False)
        try:
            self.results_table.itemChanged.disconnect(self.handle_item_changed)
        except TypeError:
            pass

        self.results_table.setRowCount(0)
        self.original_data_cache.clear()

        # **สำคัญ: ล้างข้อมูลที่เกี่ยวข้องกับฟิลเตอร์**
        if hasattr(self, "filtered_data_cache"):
            self.filtered_data_cache.clear()
        if hasattr(self, "active_filters"):
            self.active_filters.clear()

        # ล้างฟิลเตอร์ใน header ถ้ามี
        if hasattr(self, "header") and hasattr(self.header, "clear_all_filters"):
            self.header.clear_all_filters()

        self.edited_items.clear()
        self.update_save_button_state()

        if not results_tuples:
            if self.results_table.columnCount() > 0:
                from frontend.utils.error_message import show_info_message

                show_info_message(self, "ผลการค้นหา", "ไม่พบข้อมูลตามเงื่อนไขที่ระบุ")
        else:
            self.results_table.setRowCount(len(results_tuples))
            displayed_db_fields_in_table = self.column_mapper.get_fields_to_show()

            for row_idx, db_row_tuple in enumerate(results_tuples):
                sequence_text = str(row_idx + 1)
                sequence_item = QTableWidgetItem(sequence_text)
                sequence_item.setTextAlignment(Qt.AlignCenter)
                flags = sequence_item.flags()
                sequence_item.setFlags(flags & ~Qt.ItemIsEditable)
                sequence_item.setBackground(QColor("#f0f0f0"))
                self.results_table.setItem(row_idx, 0, sequence_item)

                current_row_full_data_dict = dict(
                    zip(self.db_column_names, db_row_tuple)
                )
                self.original_data_cache.append(current_row_full_data_dict)

                for db_field_idx, displayed_field_name in enumerate(
                    displayed_db_fields_in_table
                ):
                    visual_col_idx_table = db_field_idx + 1

                    cell_value = ""
                    if displayed_field_name in current_row_full_data_dict:
                        raw_value = current_row_full_data_dict[displayed_field_name]
                        cell_value = str(raw_value) if raw_value is not None else ""

                    item = QTableWidgetItem(cell_value)
                    # **แก้ไข: ปรับการจัดตำแหน่งตามชื่อฟิลด์**
                    if displayed_field_name in ["FirstName", "LastName"]:
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ชิดซ้าย
                    else:
                        item.setTextAlignment(Qt.AlignCenter)  # ตรงกลางเหมือนเดิม

                    if (
                        displayed_field_name in self.LOGICAL_PK_FIELDS
                        or displayed_field_name in self.NON_EDITABLE_FIELDS
                    ):
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        item.setBackground(QColor("#f0f0f0"))
                    else:
                        item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.results_table.setItem(row_idx, visual_col_idx_table, item)

        self.results_table.itemChanged.connect(self.handle_item_changed)
        self.results_table.setUpdatesEnabled(True)

    def prompt_save_edits(self):
        if self.results_table.state() == QAbstractItemView.EditingState:
            self.results_table.setCurrentItem(None)
            QApplication.processEvents()

        if not self.edited_items:
            show_info_message(self, "ไม่มีการเปลี่ยนแปลง", "ไม่มีข้อมูลที่แตกต่างจากเดิมให้บันทึก")
            self.update_save_button_state()
            return

        reply = QMessageBox.question(
            self,
            "ยืนยันการบันทึก",
            "คุณต้องการบันทึกข้อมูลที่แก้ไขหรือไม่?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.execute_save_edits()

    def execute_save_edits(self):
        if (
            self.parent_app.current_user is None
            or "fullname" not in self.parent_app.current_user
        ):
            show_error_message(self, "ข้อผิดพลาด", "ไม่พบข้อมูลผู้ใช้งานปัจจุบัน ไม่สามารถบันทึกได้")
            return

        if not self.edited_items:
            show_info_message(self, "ไม่มีการเปลี่ยนแปลง", "ไม่มีข้อมูลที่แตกต่างจากเดิมให้บันทึก")
            self.update_save_button_state()
            return

        # ตรวจสอบข้อมูลก่อนบันทึก
        validation_errors = validate_edited_data(self)
        if validation_errors:
            show_validation_errors(self, validation_errors)
            return

        editor_fullname = self.parent_app.current_user["fullname"]
        edit_timestamp = datetime.datetime.now()

        list_of_records_to_save = []
        displayed_db_fields_in_table = self.column_mapper.get_fields_to_show()

        edited_table_row_indices = sorted(
            list(set(row_col[0] for row_col in self.edited_items.keys()))
        )

        if not edited_table_row_indices:
            show_info_message(self, "ไม่มีการเปลี่ยนแปลง", "ไม่มีข้อมูลที่แตกต่างจากเดิมให้บันทึก")
            self.save_edits_button.setEnabled(False)
            return

        for table_row_idx in edited_table_row_indices:
            if table_row_idx >= len(self.original_data_cache):
                continue

            data_for_this_row_dict = self.original_data_cache[table_row_idx].copy()

            has_actual_edits_for_db = False
            for (r_edit, c_visual), new_text_val in self.edited_items.items():
                if r_edit == table_row_idx:
                    if c_visual > 0:
                        db_field_index = c_visual - 1
                        if db_field_index < len(displayed_db_fields_in_table):
                            db_field_name_for_edit = displayed_db_fields_in_table[
                                db_field_index
                            ]

                            # ป้องกันการบันทึกฟิลด์ที่ไม่สามารถแก้ไขได้
                            if (
                                db_field_name_for_edit in self.LOGICAL_PK_FIELDS
                                or db_field_name_for_edit in self.NON_EDITABLE_FIELDS
                            ):
                                continue

                            data_for_this_row_dict[db_field_name_for_edit] = (
                                new_text_val if new_text_val else None
                            )
                            has_actual_edits_for_db = True
                        else:
                            print(
                                f"Warning: Column visual index {c_visual} (DB index {db_field_index}) out of bounds for displayed DB fields in row {r_edit}."
                            )

            if has_actual_edits_for_db:
                data_for_this_row_dict["fullname"] = editor_fullname
                data_for_this_row_dict["time_edit"] = edit_timestamp
                list_of_records_to_save.append(data_for_this_row_dict)

        if not list_of_records_to_save:
            show_info_message(
                self,
                "ข้อมูลล่าสุด",
                "ไม่มีข้อมูลที่ถูกต้องสำหรับบันทึก (อาจเป็นเพราะการเปลี่ยนแปลงถูกละเว้น)",
            )
            for r_idx, c_idx in list(self.edited_items.keys()):
                item = self.results_table.item(r_idx, c_idx)
                if item:
                    item.setBackground(QBrush())
            self.edited_items.clear()
            self.save_edits_button.setEnabled(False)
            return

        saved_count, error_msg = save_edited_r_alldata_rows(
            list_of_records_to_save, self._all_db_fields_r_alldata
        )

        if error_msg:
            show_error_message(self, "Save Error", error_msg)
        else:
            if saved_count > 0:
                show_info_message(
                    self, "สำเร็จ", f"บันทึกข้อมูลที่แก้ไขจำนวน {saved_count} แถวเรียบร้อยแล้ว"
                )
                for r_idx, c_idx in list(self.edited_items.keys()):
                    item = self.results_table.item(r_idx, c_idx)
                    if item:
                        item.setBackground(QBrush())
                self.edited_items.clear()
                # self.save_edits_button.setEnabled(False)
                self.update_save_button_state()
                # print("Refreshing data after save...")
                self.search_data()
            else:
                show_info_message(
                    self,
                    "ข้อมูลล่าสุด",
                    "ไม่มีการเปลี่ยนแปลงที่จำเป็นต้องบันทึกเพิ่มเติม หรือ ไม่มีข้อมูลที่ถูกต้องสำหรับบันทึก",
                )
                if not list_of_records_to_save and self.edited_items:
                    for r_idx, c_idx in list(self.edited_items.keys()):
                        item = self.results_table.item(r_idx, c_idx)
                        if item:
                            item.setBackground(QBrush())
                    self.edited_items.clear()
                    self.save_edits_button.setEnabled(False)
                    self.search_data()
                else:
                    show_info_message(
                        self,
                        "ข้อมูลล่าสุด",
                        "ไม่มีการเปลี่ยนแปลงที่จำเป็นต้องบันทึกเพิ่มเติม หรือ ไม่มีข้อมูลที่ถูกต้องสำหรับบันทึก",
                    )

    def reset_screen_state(self):
        self.region_combo.setCurrentIndex(0)
        self.clear_area_code_and_below()  # เพิ่มบรรทัดนี้

        # ส่วนที่เหลือเหมือนเดิม
        try:
            self.results_table.itemChanged.disconnect(self.handle_item_changed)
        except TypeError:
            pass
        self.results_table.setRowCount(0)
        self.results_table.itemChanged.connect(self.handle_item_changed)

        self.original_data_cache.clear()
        self.filtered_data_cache.clear()
        self.db_column_names = []
        self.edited_items.clear()
        self.active_filters.clear()

        if hasattr(self, "header"):
            self.header.clear_all_filters()

        self.update_save_button_state()

        if hasattr(self, "user_fullname_label"):
            self.user_fullname_label.setText("User: N/A")

    def clear_search(self):
        # ล้าง dropdown เดิม
        self.region_combo.setCurrentIndex(0)

        # ล้าง dropdown ใหม่
        self.clear_area_code_and_below()

        # ส่วนที่เหลือเหมือนเดิม
        try:
            self.results_table.itemChanged.disconnect(self.handle_item_changed)
        except TypeError:
            pass
        self.results_table.setRowCount(0)
        self.results_table.itemChanged.connect(self.handle_item_changed)

        self.original_data_cache.clear()
        self.filtered_data_cache.clear()
        self.db_column_names = []
        self.edited_items.clear()
        self.active_filters.clear()

        if hasattr(self, "header"):
            self.header.clear_all_filters()

        self.update_save_button_state()

    def logout(self):
        if self.edited_items:
            reply = QMessageBox.question(
                self,
                "การเปลี่ยนแปลงที่ยังไม่ได้บันทึก",
                "คุณมีการแก้ไขที่ยังไม่ได้บันทึก ต้องการบันทึกก่อนออกจากระบบหรือไม่?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                self.execute_save_edits()
                if not self.edited_items:
                    self.parent_app.perform_logout()
            elif reply == QMessageBox.Discard:
                self.parent_app.perform_logout()
        else:
            self.parent_app.perform_logout()

    def load_location_data(self):
        try:
            excel_path = resource_path(
                os.path.join("assets", "reg_prov_dist_subdist.xlsx")
            )
            self.location_data = pd.read_excel(excel_path, sheet_name="Area_code")

            self.region_combo.blockSignals(True)
            self.region_combo.clear()
            self.region_combo.addItem("-- เลือกภาค --")
            regions = sorted(self.location_data["RegName"].unique())
            for region in regions:
                self.region_combo.addItem(region)
            self.region_combo.blockSignals(False)

            self.province_combo.clear()
            self.province_combo.addItem("-- เลือกจังหวัด --")
            self.district_combo.clear()
            self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
            self.subdistrict_combo.clear()
            self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        except Exception as e:
            show_error_message(self, "Error", f"Failed to load location data: {str(e)}")
            self.location_data = pd.DataFrame()

    def on_region_changed(self, index):
        self.province_combo.blockSignals(True)
        self.district_combo.blockSignals(True)
        self.subdistrict_combo.blockSignals(True)

        self.province_combo.clear()
        self.province_combo.addItem("-- เลือกจังหวัด --")
        self.district_combo.clear()
        self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
        self.subdistrict_combo.clear()
        self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        if (
            index > 0
            and self.location_data is not None
            and not self.location_data.empty
        ):
            selected_region = self.region_combo.currentText()
            provinces = sorted(
                self.location_data[self.location_data["RegName"] == selected_region][
                    "ProvName"
                ].unique()
            )
            for province in provinces:
                self.province_combo.addItem(province)

        self.province_combo.blockSignals(False)
        self.district_combo.blockSignals(False)
        self.subdistrict_combo.blockSignals(False)
        self.on_province_changed(0)

    def on_province_changed(self, index):
        self.district_combo.blockSignals(True)
        self.subdistrict_combo.blockSignals(True)
        self.district_combo.clear()
        self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
        self.subdistrict_combo.clear()
        self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        if (
            index > 0
            and self.region_combo.currentIndex() > 0
            and self.location_data is not None
            and not self.location_data.empty
        ):
            selected_region = self.region_combo.currentText()
            selected_province = self.province_combo.currentText()
            if selected_province != "-- เลือกจังหวัด --":
                filtered_data = self.location_data[
                    (self.location_data["RegName"] == selected_region)
                    & (self.location_data["ProvName"] == selected_province)
                ]
                districts = sorted(filtered_data["DistName"].unique())
                for district in districts:
                    self.district_combo.addItem(district)

        self.district_combo.blockSignals(False)
        self.subdistrict_combo.blockSignals(False)
        self.on_district_changed(0)

    def on_district_changed(self, index):
        self.subdistrict_combo.blockSignals(True)
        self.subdistrict_combo.clear()
        self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        if (
            index > 0
            and self.province_combo.currentIndex() > 0
            and self.region_combo.currentIndex() > 0
            and self.location_data is not None
            and not self.location_data.empty
        ):
            selected_region = self.region_combo.currentText()
            selected_province = self.province_combo.currentText()
            selected_district = self.district_combo.currentText()
            if selected_district != "-- เลือกอำเภอ/เขต --":
                filtered_data = self.location_data[
                    (self.location_data["RegName"] == selected_region)
                    & (self.location_data["ProvName"] == selected_province)
                    & (self.location_data["DistName"] == selected_district)
                ]
                subdistricts = sorted(filtered_data["SubDistName"].unique())
                for subdistrict in subdistricts:
                    self.subdistrict_combo.addItem(subdistrict)
        self.subdistrict_combo.blockSignals(False)

    def on_subdistrict_changed(self, index):
        """เมื่อเปลี่ยนตำบล ให้ populate area code เสมอ"""
        self.area_code_combo.blockSignals(True)
        self.clear_area_code_and_below()
    
        # Populate area code แม้ว่าจะไม่เลือกตำบล (index = 0) ก็ตาม
        self.populate_area_code()
    
        self.area_code_combo.blockSignals(False)

    def on_area_code_changed(self, index):
        """เมื่อเปลี่ยน area code ให้ populate EA_NO เสมอ"""
        self.ea_no_combo.blockSignals(True)
        self.clear_ea_no_and_below()
    
        # Populate EA_NO แม้ว่าจะไม่เลือก area code (index = 0) หรือเลือก blank ก็ตาม
        self.populate_ea_no()
    
        self.ea_no_combo.blockSignals(False)

    def on_ea_no_changed(self, index):
        """เมื่อเปลี่ยน EA_NO ให้ populate VilCode เสมอ"""
        self.vil_code_combo.blockSignals(True)
        self.clear_vil_code_and_below()
    
        self.populate_vil_code()
    
        self.vil_code_combo.blockSignals(False)

    def on_vil_code_changed(self, index):
        """เมื่อเปลี่ยน VilCode ให้ populate VilName เสมอ"""
        self.vil_name_combo.blockSignals(True)
        self.clear_vil_name_and_below()
    
        self.populate_vil_name()
    
        self.vil_name_combo.blockSignals(False)

    def on_vil_name_changed(self, index):
        """เมื่อเปลี่ยน VilName ให้ populate BuildingNumber เสมอ"""
        self.building_number_combo.blockSignals(True)
        self.clear_building_number_and_below()
    
        self.populate_building_number()
    
        self.building_number_combo.blockSignals(False)

    def on_building_number_changed(self, index):
        """เมื่อเปลี่ยน BuildingNumber ให้ populate HouseholdNumber เสมอ"""
        self.household_number_combo.blockSignals(True)
        self.clear_household_number_and_below()
    
        self.populate_household_number()
    
        self.household_number_combo.blockSignals(False)

    def on_household_number_changed(self, index):
        """เมื่อเปลี่ยน HouseholdNumber ให้ populate HouseholdMemberNumber เสมอ"""
        self.household_member_number_combo.blockSignals(True)
        self.clear_household_member_number_and_below()
    
        self.populate_household_member_number()
    
        self.household_member_number_combo.blockSignals(False)

    def on_household_member_number_changed(self, index):
        pass

    def get_selected_codes(self):
        codes = {
            "RegCode": None,
            "ProvCode": None,
            "DistCode": None,
            "SubDistCode": None,
        }
        if self.location_data is None or self.location_data.empty:
            return codes

        selected_region = self.region_combo.currentText()
        selected_province = self.province_combo.currentText()
        selected_district = self.district_combo.currentText()
        selected_subdistrict = self.subdistrict_combo.currentText()

        current_filter = pd.Series(
            [True] * len(self.location_data), index=self.location_data.index
        )

        if selected_region != "-- เลือกภาค --":
            current_filter &= self.location_data["RegName"] == selected_region
            df_filtered = self.location_data[current_filter]
            if not df_filtered.empty:
                codes["RegCode"] = df_filtered["RegCode"].iloc[0]
        else:
            return codes

        if selected_province != "-- เลือกจังหวัด --":
            current_filter &= self.location_data["ProvName"] == selected_province
            df_filtered = self.location_data[current_filter]
            if not df_filtered.empty:
                codes["ProvCode"] = df_filtered["ProvCode"].iloc[0]
        else:
            return codes

        if selected_district != "-- เลือกอำเภอ/เขต --":
            current_filter &= self.location_data["DistName"] == selected_district
            df_filtered = self.location_data[current_filter]
            if not df_filtered.empty:
                codes["DistCode"] = df_filtered["DistCode"].iloc[0]
        else:
            return codes

        if selected_subdistrict != "-- เลือกตำบล/แขวง --":
            current_filter &= self.location_data["SubDistName"] == selected_subdistrict
            df_filtered = self.location_data[current_filter]
            if not df_filtered.empty:
                codes["SubDistCode"] = df_filtered["SubDistCode"].iloc[0]

        return codes

    def populate_area_code(self):
        """เติมข้อมูล AreaCode dropdown"""
        where_conditions, where_params = self.build_where_conditions_up_to_subdistrict()
    
        # ดึงข้อมูลทั้งหมด แม้ไม่มี where_conditions
        area_codes = get_distinct_values("AreaCode", where_conditions, where_params)
        area_name_mapping = get_area_name_mapping()
    
        self.area_code_combo.clear()
        self.area_code_combo.addItem("-- เลือกเขตการปกครอง --")
    
        for code in area_codes:
            if code == "":
                display_text = "-- Blank --"
            else:
                display_name = area_name_mapping.get(code, code)
                display_text = f"{display_name}" if display_name else code
        
            self.area_code_combo.addItem(display_text)
            # เก็บค่า AreaCode ไว้ใน userData
            self.area_code_combo.setItemData(self.area_code_combo.count() - 1, code)

    def populate_ea_no(self):
        """เติมข้อมูล EA_NO dropdown"""
        where_conditions, where_params = self.build_where_conditions_up_to_area_code()
    
        ea_nos = get_distinct_values("EA_NO", where_conditions, where_params)
    
        self.ea_no_combo.clear()
        self.ea_no_combo.addItem("-- เลือกเขตแจงนับ --")
    
        for ea_no in ea_nos:
            display_text = "-- Blank --" if ea_no == "" else ea_no
            self.ea_no_combo.addItem(display_text)
            self.ea_no_combo.setItemData(self.ea_no_combo.count() - 1, ea_no)

    def populate_vil_code(self):
        """เติมข้อมูล VilCode dropdown"""
        where_conditions, where_params = self.build_where_conditions_up_to_ea_no()
    
        vil_codes = get_distinct_values("VilCode", where_conditions, where_params)
    
        self.vil_code_combo.clear()
        self.vil_code_combo.addItem("-- เลือกหมู่ที่ --")
    
        for vil_code in vil_codes:
            display_text = "-- Blank --" if vil_code == "" else vil_code
            self.vil_code_combo.addItem(display_text)
            self.vil_code_combo.setItemData(self.vil_code_combo.count() - 1, vil_code)

    def populate_vil_name(self):
        """เติมข้อมูล VilName dropdown"""
        where_conditions, where_params = self.build_where_conditions_up_to_vil_code()
    
        vil_names = get_distinct_values("VilName", where_conditions, where_params)
    
        self.vil_name_combo.clear()
        self.vil_name_combo.addItem("-- เลือกชื่อหมู่บ้าน --")
    
        for vil_name in vil_names:
            display_text = "-- Blank --" if vil_name == "" else vil_name
            self.vil_name_combo.addItem(display_text)
            self.vil_name_combo.setItemData(self.vil_name_combo.count() - 1, vil_name)

    def populate_building_number(self):
        """เติมข้อมูล BuildingNumber dropdown"""
        where_conditions, where_params = self.build_where_conditions_up_to_vil_name()
    
        building_numbers = get_distinct_values("BuildingNumber", where_conditions, where_params)
    
        self.building_number_combo.clear()
        self.building_number_combo.addItem("-- เลือกลำดับที่สิ่งปลูกสร้าง --")
    
        for building_number in building_numbers:
            display_text = "-- Blank --" if building_number == "" else building_number
            self.building_number_combo.addItem(display_text)
            self.building_number_combo.setItemData(self.building_number_combo.count() - 1, building_number)

    def populate_household_number(self):
        """เติมข้อมูล HouseholdNumber dropdown"""
        where_conditions, where_params = self.build_where_conditions_up_to_building_number()
    
        household_numbers = get_distinct_values("HouseholdNumber", where_conditions, where_params)
    
        self.household_number_combo.clear()
        self.household_number_combo.addItem("-- เลือกลำดับที่ครัวเรือน --")
    
        for household_number in household_numbers:
            display_text = "-- Blank --" if household_number == "" else household_number
            self.household_number_combo.addItem(display_text)
            self.household_number_combo.setItemData(self.household_number_combo.count() - 1, household_number)

    def populate_household_member_number(self):
        """เติมข้อมูล HouseholdMemberNumber dropdown"""
        where_conditions, where_params = self.build_where_conditions_up_to_household_number()
    
        member_numbers = get_distinct_values("HouseholdMemberNumber", where_conditions, where_params)
    
        self.household_member_number_combo.clear()
        self.household_member_number_combo.addItem("-- เลือกลำดับที่สมาชิกในครัวเรือน --")
    
        for member_number in member_numbers:
            display_text = "-- Blank --" if member_number == "" else member_number
            self.household_member_number_combo.addItem(display_text)
            self.household_member_number_combo.setItemData(self.household_member_number_combo.count() - 1, member_number)

    # ฟังก์ชัน clear
    def clear_area_code_and_below(self):
        """ล้าง AreaCode และ dropdown ข้างล่าง"""
        self.area_code_combo.clear()
        self.area_code_combo.addItem("-- เลือกเขตการปกครอง --")
        self.clear_ea_no_and_below()

    def clear_ea_no_and_below(self):
        """ล้าง EA_NO และ dropdown ข้างล่าง"""
        self.ea_no_combo.clear()
        self.ea_no_combo.addItem("-- เลือกเขตแจงนับ --")
        self.clear_vil_code_and_below()

    def clear_vil_code_and_below(self):
        """ล้าง VilCode และ dropdown ข้างล่าง"""
        self.vil_code_combo.clear()
        self.vil_code_combo.addItem("-- เลือกหมู่ที่ --")
        self.clear_vil_name_and_below()

    def clear_vil_name_and_below(self):
        """ล้าง VilName และ dropdown ข้างล่าง"""
        self.vil_name_combo.clear()
        self.vil_name_combo.addItem("-- เลือกชื่อหมู่บ้าน --")
        self.clear_building_number_and_below()

    def clear_building_number_and_below(self):
        """ล้าง BuildingNumber และ dropdown ข้างล่าง"""
        self.building_number_combo.clear()
        self.building_number_combo.addItem("-- เลือกลำดับที่สิ่งปลูกสร้าง --")
        self.clear_household_number_and_below()

    def clear_household_number_and_below(self):
        """ล้าง HouseholdNumber และ dropdown ข้างล่าง"""
        self.household_number_combo.clear()
        self.household_number_combo.addItem("-- เลือกลำดับที่ครัวเรือน --")
        self.clear_household_member_number_and_below()

    def clear_household_member_number_and_below(self):
        """ล้าง HouseholdMemberNumber dropdown"""
        self.household_member_number_combo.clear()
        self.household_member_number_combo.addItem("-- เลือกลำดับที่สมาชิกในครัวเรือน --")

    # ฟังก์ชันสร้าง WHERE conditions
    def build_where_conditions_up_to_subdistrict(self):
        """สร้าง WHERE conditions จนถึงระดับตำบล"""
        conditions = []
        params = []
    
        # รวมเงื่อนไขจาก location codes เดิม
        codes = self.get_selected_codes()
        for key, value in codes.items():
            if value is not None:
                conditions.append(f"[{key}] = ?")
                params.append(value)
    
        return " AND ".join(conditions) if conditions else None, params

    def build_where_conditions_up_to_area_code(self):
        """สร้าง WHERE conditions จนถึง AreaCode"""
        base_conditions, base_params = self.build_where_conditions_up_to_subdistrict()
    
        # เพิ่มเงื่อนไข AreaCode
        area_code_value = self.get_selected_area_code()
        if area_code_value is not None:
            if area_code_value == "":
                # จัดการกรณีเลือก blank - ให้ค้นหาค่า null หรือ empty
                area_condition = "([AreaCode] IS NULL OR [AreaCode] = '' OR LTRIM(RTRIM([AreaCode])) = '')"
            else:
                area_condition = "[AreaCode] = ?"
            
            if base_conditions:
                conditions = f"{base_conditions} AND {area_condition}"
            else:
                conditions = area_condition
        
            params = base_params.copy()
            if area_code_value != "":
                params.append(area_code_value)
        else:
            conditions = base_conditions
            params = base_params
    
        return conditions, params

    def build_where_conditions_up_to_ea_no(self):
        """สร้าง WHERE conditions จนถึง EA_NO"""
        base_conditions, base_params = self.build_where_conditions_up_to_area_code()
    
        ea_no_value = self.get_selected_ea_no()
        if ea_no_value is not None:
            if ea_no_value == "":
                ea_condition = "([EA_NO] IS NULL OR [EA_NO] = '' OR LTRIM(RTRIM([EA_NO])) = '')"
            else:
                ea_condition = "[EA_NO] = ?"
            
            if base_conditions:
                conditions = f"{base_conditions} AND {ea_condition}"
            else:
                conditions = ea_condition
        
            params = base_params.copy()
            if ea_no_value != "":
                params.append(ea_no_value)
        else:
            conditions = base_conditions
            params = base_params
    
        return conditions, params

    def build_where_conditions_up_to_vil_code(self):
        """สร้าง WHERE conditions จนถึง VilCode"""
        base_conditions, base_params = self.build_where_conditions_up_to_ea_no()
    
        vil_code_value = self.get_selected_vil_code()
        if vil_code_value is not None:
            if vil_code_value == "":
                vil_condition = "([VilCode] IS NULL OR [VilCode] = '' OR LTRIM(RTRIM([VilCode])) = '')"
            else:
                vil_condition = "[VilCode] = ?"
            
            if base_conditions:
                conditions = f"{base_conditions} AND {vil_condition}"
            else:
                conditions = vil_condition
        
            params = base_params.copy()
            if vil_code_value != "":
                params.append(vil_code_value)
        else:
            conditions = base_conditions
            params = base_params
    
        return conditions, params

    def build_where_conditions_up_to_vil_name(self):
        """สร้าง WHERE conditions จนถึง VilName"""
        base_conditions, base_params = self.build_where_conditions_up_to_vil_code()
    
        vil_name_value = self.get_selected_vil_name()
        if vil_name_value is not None:
            if vil_name_value == "":
                vil_name_condition = "([VilName] IS NULL OR [VilName] = '' OR LTRIM(RTRIM([VilName])) = '')"
            else:
                vil_name_condition = "[VilName] = ?"
            
            if base_conditions:
                conditions = f"{base_conditions} AND {vil_name_condition}"
            else:
                conditions = vil_name_condition
        
            params = base_params.copy()
            if vil_name_value != "":
                params.append(vil_name_value)
        else:
            conditions = base_conditions
            params = base_params
    
        return conditions, params

    def build_where_conditions_up_to_building_number(self):
        """สร้าง WHERE conditions จนถึง BuildingNumber"""
        base_conditions, base_params = self.build_where_conditions_up_to_vil_name()
    
        building_number_value = self.get_selected_building_number()
        if building_number_value is not None:
            if building_number_value == "":
                building_condition = "([BuildingNumber] IS NULL OR [BuildingNumber] = '' OR LTRIM(RTRIM([BuildingNumber])) = '')"
            else:
                building_condition = "[BuildingNumber] = ?"
            
            if base_conditions:
                conditions = f"{base_conditions} AND {building_condition}"
            else:
                conditions = building_condition
        
            params = base_params.copy()
            if building_number_value != "":
                params.append(building_number_value)
        else:
            conditions = base_conditions
            params = base_params
    
        return conditions, params

    def build_where_conditions_up_to_household_number(self):
        """สร้าง WHERE conditions จนถึง HouseholdNumber"""
        base_conditions, base_params = self.build_where_conditions_up_to_building_number()
    
        household_number_value = self.get_selected_household_number()
        if household_number_value is not None:
            if household_number_value == "":
                household_condition = "([HouseholdNumber] IS NULL OR [HouseholdNumber] = '' OR LTRIM(RTRIM([HouseholdNumber])) = '')"
            else:
                household_condition = "[HouseholdNumber] = ?"
            
            if base_conditions:
                conditions = f"{base_conditions} AND {household_condition}"
            else:
                conditions = household_condition
        
            params = base_params.copy()
            if household_number_value != "":
                params.append(household_number_value)
        else:
            conditions = base_conditions
            params = base_params
    
        return conditions, params

    def get_selected_area_code(self):
        """ดึงค่า AreaCode ที่เลือก"""
        if self.area_code_combo.currentIndex() > 0:
            return self.area_code_combo.itemData(self.area_code_combo.currentIndex())
        return None

    def get_selected_ea_no(self):
        """ดึงค่า EA_NO ที่เลือก"""
        if self.ea_no_combo.currentIndex() > 0:
            return self.ea_no_combo.itemData(self.ea_no_combo.currentIndex())
        return None

    def get_selected_vil_code(self):
        """ดึงค่า VilCode ที่เลือก"""
        if self.vil_code_combo.currentIndex() > 0:
            return self.vil_code_combo.itemData(self.vil_code_combo.currentIndex())
        return None

    def get_selected_vil_name(self):
        """ดึงค่า VilName ที่เลือก"""
        if self.vil_name_combo.currentIndex() > 0:
            return self.vil_name_combo.itemData(self.vil_name_combo.currentIndex())
        return None

    def get_selected_building_number(self):
        """ดึงค่า BuildingNumber ที่เลือก"""
        if self.building_number_combo.currentIndex() > 0:
            return self.building_number_combo.itemData(
                self.building_number_combo.currentIndex()
            )
        return None

    def get_selected_household_number(self):
        """ดึงค่า HouseholdNumber ที่เลือก"""
        if self.household_number_combo.currentIndex() > 0:
            return self.household_number_combo.itemData(
                self.household_number_combo.currentIndex()
            )
        return None

    def get_selected_household_member_number(self):
        """ดึงค่า HouseholdMemberNumber ที่เลือก"""
        if self.household_member_number_combo.currentIndex() > 0:
            return self.household_member_number_combo.itemData(
                self.household_member_number_combo.currentIndex()
            )
        return None
