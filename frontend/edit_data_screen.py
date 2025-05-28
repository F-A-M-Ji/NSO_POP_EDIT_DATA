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
)
from frontend.widgets.multi_line_header import MultiLineHeaderView
from frontend.utils.error_message import show_error_message, show_info_message
from frontend.utils.shadow_effect import add_shadow_effect
from frontend.utils.resource_path import resource_path


class EditDataScreen(QWidget):
    LOGICAL_PK_FIELDS = ["EA_Code_15", "Building_No", "Household_No", "Population_No"]

    NON_EDITABLE_FIELDS = ["FirstName", "LastName"]

    # กำหนดกฎการตรวจสอบสำหรับแต่ละฟิลด์
    FIELD_VALIDATION_RULES = {
        "BuildingType": {
            "type": "range",
            "allowed_values": [f"{i:02d}" for i in range(1, 20)],  # 01-19
            "allow_blank": False,
            "description": "ต้องเป็น 01-19",
        },
        "BuildingTypeOther": {
            "type": "text",
            "max_length": 50,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
        },
        "Residing": {
            "type": "options",
            "allowed_values": ["1", "2"],
            "allow_blank": False,
            "description": "ต้องเป็น 1 หรือ 2",
        },
        "HouseholdEnumeration": {
            "type": "custom",
            "allowed_values": ["11", "12", "13", "20", "21", "22", "23"],
            "allow_blank": True,
            "description": "ต้องเป็น 11-13 หรือ 20-23",
        },
        "HouseholdEnumerationOther": {
            "type": "text",
            "max_length": 255,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 255 ตัวอักษร",
        },
        "HouseholdType": {
            "type": "range",
            "allowed_values": ["1", "2", "3"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-3",
        },
        "NumberOfHousehold": {
            "type": "int_range",
            "min_value": 1,
            "max_value": 99,
            "allow_blank": True,
            "description": "ต้องเป็นตัวเลข 1-99",
        },
        "TotalRoom": {
            "type": "padded_number",
            "length": 4,
            "min_value": 1,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็น 0001-9999",
        },
        "RoomVacant": {
            "type": "padded_number",
            "length": 4,
            "min_value": 1,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็น 0001-9999",
        },
        "RoomResidence": {
            "type": "padded_number",
            "length": 4,
            "min_value": 1,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็น 0001-9999",
        },
        "Language": {
            "type": "custom",
            "allowed_values": ["1", "2", "3", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-3 หรือ 9",
        },
        # "LanguageOther": {
        #     "type": "custom",
        #     "allowed_values": [f"{i:02d}" for i in range(2, 81)] + ["99"],
        #     "allow_blank": True,
        #     "description": "ต้องเป็น 02-80 หรือ 99",
        # },
        "HouseholdNumber": {
            "type": "padded_number",
            "length": 4,
            "min_value": 1,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็น 0001-9999",
        },
        "ConstructionMaterial": {
            "type": "range",
            "allowed_values": ["1", "2", "3", "4", "5", "6"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-6",
        },
        "ConstructionMaterialOther": {
            "type": "text",
            "max_length": 50,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
        },
        "TenureResidence": {
            "type": "range",
            "allowed_values": ["1", "2", "3", "4", "5", "6", "7"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-7",
        },
        "TenureResidenceOther": {
            "type": "text",
            "max_length": 30,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 30 ตัวอักษร",
        },
        "TenureLand": {
            "type": "range",
            "allowed_values": ["1", "2", "3", "4", "5"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-5",
        },
        "TenureLandOther": {
            "type": "text",
            "max_length": 255,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 255 ตัวอักษร",
        },
        "NumberOfHousueholdMember": {
            "type": "int_range",
            "min_value": 1,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็นตัวเลข 1-9999",
        },
        "HouseholdMemberNumber": {
            "type": "padded_number",
            "length": 5,
            "min_value": 1,
            "max_value": 99998,
            "allow_blank": True,
            "description": "ต้องเป็น 00001-99998",
        },
        "Title": {
            "type": "custom",
            "allowed_values": ["01", "02", "03", "04", "05", "09"],
            "allow_blank": True,
            "description": "ต้องเป็น 01-05 หรือ 09",
        },
        "TitleOther": {
            "type": "text",
            "max_length": 50,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
        },
        "Relationship": {
            "type": "range",
            "allowed_values": [f"{i:02d}" for i in range(0, 17)],  # 00-16
            "allow_blank": True,
            "description": "ต้องเป็น 00-16",
        },
        "Sex": {
            "type": "options",
            "allowed_values": ["1", "2"],
            "allow_blank": True,
            "description": "ต้องเป็น 1 หรือ 2",
        },
        "MonthOfBirth": {
            "type": "custom",
            "allowed_values": [f"{i:02d}" for i in range(1, 13)] + ["99"],
            "allow_blank": True,
            "description": "ต้องเป็น 01-12 หรือ 99",
        },
        "YearOfBirth": {
            "type": "custom",
            "allowed_values": [str(i) for i in range(2419, 2569)] + ["9999"],
            "allow_blank": True,
            "description": "ต้องเป็น 2419-2568 หรือ 9999",
        },
        "Age_01": {
            "type": "padded_number",
            "length": 3,
            "min_value": 0,
            "max_value": 150,
            "allow_blank": True,
            "description": "ต้องเป็น 000-150",
        },
        "Religion": {
            "type": "range",
            "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-9",
        },
        "ReligionOther": {
            "type": "text",
            "max_length": 50,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
        },
        # "NationalityNumeric": {
        #     "type": "custom",
        #     "allowed_values": [f"{i:03d}" for i in range(4, 910)]
        #     + ["997", "998", "999"],
        #     "allow_blank": True,
        #     "description": "ต้องเป็น 004-909 หรือ 997-999",
        # },
        "MaritalStatus": {
            "type": "custom",
            "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-7 หรือ 9",
        },
        "EducationalAttainment": {
            "type": "custom",
            "allowed_values": [f"{i:02d}" for i in range(1, 13)] + ["98", "99"],
            "allow_blank": True,
            "description": "ต้องเป็น 01-12 หรือ 98-99",
        },
        "EmploymentStatus": {
            "type": "range",
            "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-9",
        },
        "NameInHouseholdRegister": {
            "type": "custom",
            "allowed_values": ["1", "2", "3", "4", "5", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-5 หรือ 9",
        },
        "NameInHouseholdRegisterOther": {
            "type": "text",
            "max_length": 2,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 2 ตัวอักษร",
        },
        "DurationOfResidence": {
            "type": "custom",
            "allowed_values": ["0", "1", "2", "3", "4", "5", "6", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 0-6 หรือ 9",
        },
        "MigrationCharecteristics": {
            "type": "custom",
            "allowed_values": ["1", "2", "3", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-3 หรือ 9",
        },
        "MovedFromProvince": {
            "type": "custom",
            "allowed_values": (
                ["10"]
                + [str(i) for i in range(11, 20)]
                + [str(i) for i in range(70, 78)]
                + [str(i) for i in range(80, 87)]
                + [str(i) for i in range(90, 97)]
                + [str(i) for i in range(20, 28)]
                + [str(i) for i in range(30, 50)]
                + [str(i) for i in range(50, 59)]
                + [str(i) for i in range(60, 68)]
                + ["99"]
            ),
            "allow_blank": True,
            "description": "ต้องเป็นรหัสจังหวัดที่กำหนด",
        },
        # "MovedFromAbroad": {
        #     "type": "padded_number",
        #     "length": 3,
        #     "min_value": 0,
        #     "max_value": 999,
        #     "allow_blank": True,
        #     "description": "ต้องเป็น 000-999",
        # },
        "MigrationReason": {
            "type": "custom",
            "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-8 หรือ 9",
        },
        "MigrationReasonOther": {
            "type": "text",
            "max_length": 255,
            "allow_blank": True,
            "description": "ข้อความได้สูงสุด 255 ตัวอักษร",
        },
        "Gender": {
            "type": "range",
            "allowed_values": ["1", "2", "3", "4", "5"],
            "allow_blank": True,
            "description": "ต้องเป็น 1-5",
        },
        "TotalPopulation": {
            "type": "padded_number",
            "length": 4,
            "min_value": 1,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็น 0001-9999",
        },
        "TotalMale": {
            "type": "padded_number",
            "length": 4,
            "min_value": 0,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็น 0000-9999",
        },
        "TotalFemale": {
            "type": "padded_number",
            "length": 4,
            "min_value": 0,
            "max_value": 9999,
            "allow_blank": True,
            "description": "ต้องเป็น 0000-9999",
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.location_data = None
        self.column_mapper = ColumnMapper.get_instance()

        self.db_column_names = []
        self.original_data_cache = []
        self.filtered_data_cache = []  # เพิ่มสำหรับเก็บข้อมูลที่ถูกฟิลเตอร์
        self.edited_items = {}
        self.active_filters = {}  # เพิ่มสำหรับเก็บฟิลเตอร์

        self._all_db_fields_r_alldata = []

        # โหลดข้อมูลการตรวจสอบจากไฟล์ Excel
        self.validation_data_from_excel = self.load_validation_data_from_excel()

        # อัปเดตกฎการตรวจสอบ
        self.update_validation_rules()

        self.setup_ui()
        self.load_location_data()
        self._all_db_fields_r_alldata = fetch_all_r_alldata_fields()

    def update_validation_rules(self):
        """อัปเดตกฎการตรวจสอบด้วยข้อมูลจากไฟล์ Excel"""

        # อัปเดต LanguageOther
        if "LanguageOther" in self.validation_data_from_excel:
            self.FIELD_VALIDATION_RULES["LanguageOther"] = {
                "type": "custom",
                "allowed_values": self.validation_data_from_excel["LanguageOther"],
                "allow_blank": True,
                "description": "ต้องเป็นรหัสภาษาอื่นที่กำหนด",
            }

        # อัปเดต NationalityNumeric
        if "NationalityNumeric" in self.validation_data_from_excel:
            self.FIELD_VALIDATION_RULES["NationalityNumeric"] = {
                "type": "custom",
                "allowed_values": self.validation_data_from_excel["NationalityNumeric"],
                "allow_blank": True,
                "description": "ต้องเป็นรหัสสัญชาติที่กำหนด",
            }

        # อัปเดต MovedFromAbroad
        if "MovedFromAbroad" in self.validation_data_from_excel:
            # สำหรับ MovedFromAbroad ยังคงใช้ padded_number แต่เพิ่มการตรวจสอบค่าที่อนุญาต
            self.FIELD_VALIDATION_RULES["MovedFromAbroad"] = {
                "type": "excel_padded_number",  # ประเภทใหม่
                "length": 3,
                "allowed_values": self.validation_data_from_excel["MovedFromAbroad"],
                "allow_blank": True,
                "description": "ต้องเป็นรหัสประเทศที่กำหนด",
            }

    def update_user_fullname(self, fullname):
        if hasattr(self, "user_fullname_label"):
            self.user_fullname_label.setText(fullname)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        header_label = QLabel("การแก้ไขข้อมูล สปค. 68")
        header_label.setObjectName("headerLabel")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        self.user_fullname_label = QLabel("User: N/A")
        self.user_fullname_label.setObjectName("userFullnameLabel")
        # self.user_fullname_label.setStyleSheet(
        #     "font-weight: bold; color: #2196F3; margin-right: 5px;"
        # )
        header_layout.addWidget(self.user_fullname_label)
        spacer = QLabel("|")
        # spacer.setStyleSheet("color: #bdbdbd; margin-left: 5px; margin-right: 5px;")
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
        search_title = QLabel("ค้นหาข้อมูลตามพื้นที่")
        search_title.setObjectName("sectionTitle")
        search_layout.addWidget(search_title)
        dropdown_layout = QHBoxLayout()

        region_layout = QVBoxLayout()
        region_label = QLabel("ภาค:")
        self.region_combo = QComboBox()
        self.region_combo.setObjectName("searchComboBox")
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_combo)
        dropdown_layout.addLayout(region_layout)

        province_layout = QVBoxLayout()
        province_label = QLabel("จังหวัด:")
        self.province_combo = QComboBox()
        self.province_combo.setObjectName("searchComboBox")
        self.province_combo.currentIndexChanged.connect(self.on_province_changed)
        province_layout.addWidget(province_label)
        province_layout.addWidget(self.province_combo)
        dropdown_layout.addLayout(province_layout)

        district_layout = QVBoxLayout()
        district_label = QLabel("อำเภอ/เขต:")
        self.district_combo = QComboBox()
        self.district_combo.setObjectName("searchComboBox")
        self.district_combo.currentIndexChanged.connect(self.on_district_changed)
        district_layout.addWidget(district_label)
        district_layout.addWidget(self.district_combo)
        dropdown_layout.addLayout(district_layout)

        subdistrict_layout = QVBoxLayout()
        subdistrict_label = QLabel("ตำบล/แขวง:")
        self.subdistrict_combo = QComboBox()
        self.subdistrict_combo.setObjectName("searchComboBox")
        self.subdistrict_combo.currentIndexChanged.connect(self.on_subdistrict_changed)
        subdistrict_layout.addWidget(subdistrict_label)
        subdistrict_layout.addWidget(self.subdistrict_combo)
        dropdown_layout.addLayout(subdistrict_layout)
        search_layout.addLayout(dropdown_layout)

        search_buttons_layout = QHBoxLayout()
        search_buttons_layout.addStretch()
        self.search_button = QPushButton("ค้นหา")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.clicked.connect(self.search_data)
        self.search_button.setFixedWidth(120)
        search_buttons_layout.addWidget(self.search_button)
        self.clear_button = QPushButton("ล้าง")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.setFixedWidth(120)
        search_buttons_layout.addWidget(self.clear_button)
        search_layout.addLayout(search_buttons_layout)
        content_layout.addWidget(search_section)

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
    
        # ใช้ FilterableMultiLineHeaderView แทน MultiLineHeaderView
        from frontend.widgets.multi_line_header import FilterableMultiLineHeaderView
        self.header = FilterableMultiLineHeaderView(Qt.Horizontal, self.results_table)
        self.header.filter_requested.connect(self.apply_table_filter)
        self.header.filter_cleared.connect(self.clear_table_filter)
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
        if hasattr(self, 'filtered_data_cache') and self.filtered_data_cache and row < len(self.filtered_data_cache):
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

        # ตรวจสอบว่ามีการแก้ไขที่ยังไม่ได้บันทึกหรือไม่
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
                # บันทึกก่อนค้นหา
                self.execute_save_edits()
                if self.edited_items:  # ถ้ายังมีการแก้ไขอยู่ แสดงว่าบันทึกไม่สำเร็จ
                    return
            elif reply == QMessageBox.Cancel:
                # ยกเลิกการค้นหา
                return
            # ถ้าเลือก Discard จะดำเนินการค้นหาต่อไป

        if not self._all_db_fields_r_alldata:
            self._all_db_fields_r_alldata = fetch_all_r_alldata_fields()
            if not self._all_db_fields_r_alldata:
                show_error_message(
                    self, "Error", "โครงสร้างตาราง r_alldata ไม่พร้อมใช้งาน ไม่สามารถค้นหาได้"
                )
                return

        codes = self.get_selected_codes()
        processed_codes = codes.copy()
        if processed_codes["RegCode"] is not None:
            processed_codes["RegCode"] = int(processed_codes["RegCode"])
        if processed_codes["ProvCode"] is not None:
            processed_codes["ProvCode"] = int(processed_codes["ProvCode"])
        if processed_codes["DistCode"] is not None:
            processed_codes["DistCode"] = int(processed_codes["DistCode"])
        if processed_codes["SubDistCode"] is not None:
            processed_codes["SubDistCode"] = int(processed_codes["SubDistCode"])

        if all(value is None for value in processed_codes.values()):
            show_error_message(
                self, "Search Error", "กรุณาเลือกเงื่อนไขในการค้นหาอย่างน้อยหนึ่งรายการ"
            )
            return

        results, db_cols, error_msg = search_r_alldata(
            processed_codes, self._all_db_fields_r_alldata, self.LOGICAL_PK_FIELDS
        )

        if error_msg:
            show_error_message(self, "Search Error", error_msg)
            self.results_table.setRowCount(0)
            self.original_data_cache.clear()
            return

        self.db_column_names = db_cols

        self.edited_items.clear()
        # self.save_edits_button.setEnabled(False)
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
        if hasattr(self, 'filtered_data_cache'):
            self.filtered_data_cache.clear()
        if hasattr(self, 'active_filters'):
            self.active_filters.clear()
    
        # ล้างฟิลเตอร์ใน header ถ้ามี
        if hasattr(self, 'header') and hasattr(self.header, 'clear_all_filters'):
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
                    item.setTextAlignment(Qt.AlignCenter)

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
        validation_errors = self.validate_edited_data()
        if validation_errors:
            self.show_validation_errors(validation_errors)
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
        self.active_filters.clear()  # ล้างฟิลเตอร์
    
        # ล้างฟิลเตอร์ใน header
        if hasattr(self, 'header'):
            self.header.clear_all_filters()
        
        self.update_save_button_state()

        if hasattr(self, "user_fullname_label"):
            self.user_fullname_label.setText("User: N/A")

    def clear_search(self):
        self.region_combo.setCurrentIndex(0)

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
        self.active_filters.clear()  # ล้างฟิลเตอร์
    
        # ล้างฟิลเตอร์ใน header
        if hasattr(self, 'header'):
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

    def validate_field_value(self, field_name, value, row_number):
        """ตรวจสอบค่าของฟิลด์เดียว"""
        # ถ้าไม่มีกฎสำหรับฟิลด์นี้ ให้ผ่าน
        if field_name not in self.FIELD_VALIDATION_RULES:
            return None

        rule = self.FIELD_VALIDATION_RULES[field_name]
        field_display_name = self.column_mapper.get_column_name(field_name)

        # ถ้าค่าว่างและอนุญาตให้ว่างได้
        if not value or value.strip() == "":
            return (
                None
                if rule.get("allow_blank", True)
                else f"แถว {row_number}, คอลัมน์ '{field_display_name}': ไม่สามารถเป็นค่าว่างได้"
            )

        value = value.strip()

        # ตรวจสอบตามประเภท
        validation_type = rule.get("type", "text")

        if validation_type == "text":
            return self._validate_text(
                field_name, value, rule, field_display_name, row_number
            )
        elif validation_type == "options":
            return self._validate_options(
                field_name, value, rule, field_display_name, row_number
            )
        elif validation_type == "range":
            return self._validate_range(
                field_name, value, rule, field_display_name, row_number
            )
        elif validation_type == "custom":
            return self._validate_custom(
                field_name, value, rule, field_display_name, row_number
            )
        elif validation_type == "int_range":
            return self._validate_int_range(
                field_name, value, rule, field_display_name, row_number
            )
        elif validation_type == "padded_number":
            return self._validate_padded_number(
                field_name, value, rule, field_display_name, row_number
            )
        elif validation_type == "excel_padded_number":  # เพิ่มประเภทใหม่
            return self._validate_excel_padded_number(
                field_name, value, rule, field_display_name, row_number
            )

        return None

    def _validate_excel_padded_number(
        self, field_name, value, rule, field_display_name, row_number
    ):
        """ตรวจสอบฟิลด์ที่เป็นตัวเลขแบบเติม 0 ข้างหน้า และตรวจสอบกับรายการจาก Excel"""
        length = rule.get("length", 3)
        allowed_values = rule.get("allowed_values", [])

        # ตรวจสอบความยาว
        if len(value) != length:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องมีความยาว {length} หลัก"

        # ตรวจสอบว่าเป็นตัวเลขทั้งหมด
        if not value.isdigit():
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลขเท่านั้น"

        # ตรวจสอบกับรายการที่อนุญาต
        if value not in allowed_values:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"

        return None

    def _validate_text(self, field_name, value, rule, field_display_name, row_number):
        """ตรวจสอบฟิลด์ข้อความ"""
        max_length = rule.get("max_length")
        if max_length and len(value) > max_length:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ความยาวเกิน {max_length} ตัวอักษร (ปัจจุบัน: {len(value)})"
        return None

    def _validate_options(
        self, field_name, value, rule, field_display_name, row_number
    ):
        """ตรวจสอบฟิลด์ที่มีตัวเลือกจำกัด"""
        allowed_values = rule.get("allowed_values", [])
        if value not in allowed_values:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
        return None

    def _validate_range(self, field_name, value, rule, field_display_name, row_number):
        """ตรวจสอบฟิลด์ที่เป็นช่วงค่า"""
        allowed_values = rule.get("allowed_values", [])
        if value not in allowed_values:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
        return None

    def _validate_custom(self, field_name, value, rule, field_display_name, row_number):
        """ตรวจสอบฟิลด์ที่มีกฎพิเศษ"""
        allowed_values = rule.get("allowed_values", [])
        if value not in allowed_values:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
        return None

    def _validate_int_range(
        self, field_name, value, rule, field_display_name, row_number
    ):
        """ตรวจสอบฟิลด์ที่เป็นตัวเลขในช่วงที่กำหนด"""
        try:
            int_value = int(value)
            min_value = rule.get("min_value", 0)
            max_value = rule.get("max_value", float("inf"))

            if not (min_value <= int_value <= max_value):
                return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
        except ValueError:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลข"

        return None

    def _validate_padded_number(
        self, field_name, value, rule, field_display_name, row_number
    ):
        """ตรวจสอบฟิลด์ที่เป็นตัวเลขแบบเติม 0 ข้างหน้า"""
        length = rule.get("length", 4)
        min_value = rule.get("min_value", 0)
        max_value = rule.get("max_value", 9999)

        # ตรวจสอบความยาว
        if len(value) != length:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องมีความยาว {length} หลัก"

        # ตรวจสอบว่าเป็นตัวเลขทั้งหมด
        if not value.isdigit():
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลขเท่านั้น"

        # ตรวจสอบช่วงค่า
        try:
            int_value = int(value)
            if not (min_value <= int_value <= max_value):
                return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
        except ValueError:
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลข"

        return None

    def validate_edited_data(self):
        """ตรวจสอบข้อมูลที่แก้ไขทั้งหมดก่อนบันทึก"""
        validation_errors = []
        displayed_db_fields_in_table = self.column_mapper.get_fields_to_show()

        for (row, visual_col), new_value in self.edited_items.items():
            if visual_col > 0:  # ข้าม column ลำดับ
                db_field_index = visual_col - 1
                if db_field_index < len(displayed_db_fields_in_table):
                    field_name = displayed_db_fields_in_table[db_field_index]

                    # ข้ามฟิลด์ที่ไม่สามารถแก้ไขได้
                    if (
                        field_name in self.LOGICAL_PK_FIELDS
                        or field_name in self.NON_EDITABLE_FIELDS
                    ):
                        continue

                    # ตรวจสอบข้อมูลตามกฎที่กำหนด
                    error = self.validate_field_value(field_name, new_value, row + 1)
                    if error:
                        validation_errors.append(error)

        return validation_errors

    def show_validation_errors(self, errors):
        """แสดงข้อผิดพลาดในการตรวจสอบข้อมูล"""
        if not errors:
            return

        # จำกัดการแสดงผลไม่เกิน 20 ข้อผิดพลาด
        max_errors_to_show = 20
        errors_to_show = errors[:max_errors_to_show]

        error_message = "พบข้อผิดพลาดในข้อมูลที่แก้ไข:\n\n"
        for i, error in enumerate(errors_to_show, 1):
            error_message += f"{i}. {error}\n"

        if len(errors) > max_errors_to_show:
            error_message += (
                f"\n... และอีก {len(errors) - max_errors_to_show} ข้อผิดพลาด\n"
            )

        error_message += "\nกรุณาแก้ไขข้อมูลให้ถูกต้องก่อนบันทึก"

        # ใช้ QMessageBox แบบ scrollable สำหรับข้อความยาว
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("ข้อมูลไม่ถูกต้อง")
        msg.setText("พบข้อผิดพลาดในข้อมูลที่แก้ไข")
        msg.setDetailedText(error_message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def load_validation_data_from_excel(self):
        """โหลดข้อมูลการตรวจสอบจากไฟล์ Excel"""
        validation_data = {}

        # กำหนดค่าเริ่มต้นในกรณีที่โหลดไฟล์ไม่ได้
        default_values = {
            "LanguageOther": [f"{i:02d}" for i in range(2, 81)] + ["99"],  # ค่าเดิม
            "NationalityNumeric": [f"{i:03d}" for i in range(4, 910)]
            + ["000", "910", "920", "930", "940", "990", "997", "998", "999"],
            "MovedFromAbroad": [f"{i:03d}" for i in range(0, 1000)],  # 000-999
        }

        try:
            # โหลดข้อมูล LanguageOther
            language_other_path = resource_path("assets/language_other.xlsx")
            if os.path.exists(language_other_path):
                language_df = pd.read_excel(language_other_path)
                if "LanguageOther_Code" in language_df.columns:
                    language_codes = (
                        language_df["LanguageOther_Code"].dropna().astype(str).tolist()
                    )
                    language_codes = [
                        code.strip() for code in language_codes if code.strip()
                    ]
                    if language_codes:  # ถ้ามีข้อมูล
                        validation_data["LanguageOther"] = language_codes
                    else:
                        validation_data["LanguageOther"] = default_values[
                            "LanguageOther"
                        ]
                else:
                    validation_data["LanguageOther"] = default_values["LanguageOther"]
            else:
                validation_data["LanguageOther"] = default_values["LanguageOther"]
        except Exception as e:
            validation_data["LanguageOther"] = default_values["LanguageOther"]

        try:
            # โหลดข้อมูล NationalityNumeric
            nationality_path = resource_path("assets/nationality.xlsx")
            if os.path.exists(nationality_path):
                nationality_df = pd.read_excel(nationality_path)
                if "Nationality_Code_Numeric-3" in nationality_df.columns:
                    nationality_codes = (
                        nationality_df["Nationality_Code_Numeric-3"]
                        .dropna()
                        .astype(str)
                        .tolist()
                    )
                    nationality_codes = [
                        code.strip() for code in nationality_codes if code.strip()
                    ]
                    # เพิ่มรหัสพิเศษ
                    additional_codes = [
                        "000",
                        "910",
                        "920",
                        "930",
                        "940",
                        "990",
                        "997",
                        "998",
                        "999",
                    ]
                    nationality_codes.extend(additional_codes)
                    nationality_codes = list(set(nationality_codes))  # ลบค่าซ้ำ
                    if nationality_codes:
                        validation_data["NationalityNumeric"] = nationality_codes
                    else:
                        validation_data["NationalityNumeric"] = default_values[
                            "NationalityNumeric"
                        ]
                else:
                    validation_data["NationalityNumeric"] = default_values[
                        "NationalityNumeric"
                    ]
            else:
                validation_data["NationalityNumeric"] = default_values[
                    "NationalityNumeric"
                ]
        except Exception as e:
            validation_data["NationalityNumeric"] = default_values["NationalityNumeric"]

        try:
            # โหลดข้อมูล MovedFromAbroad
            country_path = resource_path("assets/country.xlsx")
            if os.path.exists(country_path):
                country_df = pd.read_excel(country_path)
                if "Countries_Code_Num-3" in country_df.columns:
                    country_codes = (
                        country_df["Countries_Code_Num-3"].dropna().astype(str).tolist()
                    )
                    country_codes = [
                        code.strip() for code in country_codes if code.strip()
                    ]
                    if country_codes:
                        validation_data["MovedFromAbroad"] = country_codes
                    else:
                        validation_data["MovedFromAbroad"] = default_values[
                            "MovedFromAbroad"
                        ]
                else:
                    validation_data["MovedFromAbroad"] = default_values[
                        "MovedFromAbroad"
                    ]
            else:
                validation_data["MovedFromAbroad"] = default_values["MovedFromAbroad"]
        except Exception as e:
            validation_data["MovedFromAbroad"] = default_values["MovedFromAbroad"]

        return validation_data
    
    # เพิ่ม methods สำหรับจัดการฟิลเตอร์
    def apply_table_filter(self, column, text, show_blank_only):
        """ใช้ฟิลเตอร์กับตาราง"""
        if not self.original_data_cache:
            return
    
        # บันทึกฟิลเตอร์
        if text or show_blank_only:
            self.active_filters[column] = {
                'text': text.lower(),
                'show_blank': show_blank_only
            }
        else:
            if column in self.active_filters:
                del self.active_filters[column]
    
        # กรองข้อมูล
        self.filter_table_data()

    def clear_table_filter(self, column):
        """ล้างฟิลเตอร์ของคอลัมน์"""
        if column in self.active_filters:
            del self.active_filters[column]
    
        # กรองข้อมูลใหม่
        self.filter_table_data()

    def filter_table_data(self):
        """กรองข้อมูลในตารางตามฟิลเตอร์ที่ใช้งานอยู่"""
        if not self.original_data_cache:
            return
    
        displayed_fields = self.column_mapper.get_fields_to_show()
        filtered_data = []
    
        for row_data in self.original_data_cache:
            should_include = True
        
            # ตรวจสอบทุกฟิลเตอร์
            for column, filter_info in self.active_filters.items():
                if column == 0:  # ข้ามคอลัมน์ลำดับ
                    continue
            
                # คำนวณ field index (ลบ 1 เพราะคอลัมน์ 0 คือลำดับ)
                field_index = column - 1
                if field_index >= len(displayed_fields):
                    continue
            
                field_name = displayed_fields[field_index]
                field_value = row_data.get(field_name)
            
                # แปลงค่าเป็น string สำหรับการเปรียบเทียบ
                if field_value is None:
                    value_str = ""
                else:
                    value_str = str(field_value).strip()
            
                # ตรวจสอบเงื่อนไข show_blank
                if filter_info.get('show_blank', False):
                    if value_str != "":  # ถ้าไม่ใช่ค่าว่าง ให้ข้าม
                        should_include = False
                        break
            
                # ตรวจสอบเงื่อนไขข้อความ
                filter_text = filter_info.get('text', '').strip()
                if filter_text:
                    if filter_text.lower() not in value_str.lower():
                        should_include = False
                        break
        
            if should_include:
                filtered_data.append(row_data)
    
        # อัปเดตตาราง
        self.display_filtered_results(filtered_data)

    def display_filtered_results(self, filtered_data):
        """แสดงผลข้อมูลที่ถูกฟิลเตอร์"""
        # **สำคัญ: ปิด itemChanged signal ก่อนอัปเดตตาราง**
        self.results_table.setUpdatesEnabled(False)
        try:
            self.results_table.itemChanged.disconnect(self.handle_item_changed)
        except TypeError:
            pass  # ถ้าไม่มี connection อยู่แล้ว

        # เก็บ edited_items ที่มีอยู่ไว้ก่อน
        existing_edits = self.edited_items.copy()
    
        # ตั้งค่าหัวตาราง
        self.setup_table_headers_text_and_widths()

        # ล้างตารางเก่า
        self.results_table.setRowCount(0)
    
        # เก็บข้อมูลที่กรองแล้ว
        self.filtered_data_cache = filtered_data
    
        if not filtered_data:
            from frontend.utils.error_message import show_info_message
            show_info_message(self, "ผลการกรอง", "ไม่พบข้อมูลที่ตรงกับเงื่อนไขการกรอง")
        else:
            self.results_table.setRowCount(len(filtered_data))
            displayed_db_fields_in_table = self.column_mapper.get_fields_to_show()

            for row_idx, row_data in enumerate(filtered_data):
                # สร้าง item ลำดับ
                sequence_text = str(row_idx + 1)
                sequence_item = QTableWidgetItem(sequence_text)
                sequence_item.setTextAlignment(Qt.AlignCenter)
                flags = sequence_item.flags()
                sequence_item.setFlags(flags & ~Qt.ItemIsEditable)
                sequence_item.setBackground(QColor("#f0f0f0"))
                self.results_table.setItem(row_idx, 0, sequence_item)

                # หา index ของข้อมูลนี้ใน original_data_cache
                original_row_index = -1
                for orig_idx, orig_data in enumerate(self.original_data_cache):
                    # เปรียบเทียบ Primary Key เพื่อหา original index
                    is_same_row = True
                    for pk_field in self.LOGICAL_PK_FIELDS:
                        if orig_data.get(pk_field) != row_data.get(pk_field):
                            is_same_row = False
                            break
                
                    if is_same_row:
                        original_row_index = orig_idx
                        break

                # สร้าง items สำหรับแต่ละคอลัมน์
                for db_field_idx, displayed_field_name in enumerate(displayed_db_fields_in_table):
                    visual_col_idx_table = db_field_idx + 1

                    cell_value = ""
                    if displayed_field_name in row_data:
                        raw_value = row_data[displayed_field_name]
                        cell_value = str(raw_value) if raw_value is not None else ""

                    item = QTableWidgetItem(cell_value)
                    item.setTextAlignment(Qt.AlignCenter)

                    # ตั้งค่าการแก้ไขได้หรือไม่
                    if (displayed_field_name in self.LOGICAL_PK_FIELDS or 
                        displayed_field_name in self.NON_EDITABLE_FIELDS):
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        item.setBackground(QColor("#f0f0f0"))
                    else:
                        item.setFlags(item.flags() | Qt.ItemIsEditable)
                
                    # **สำคัญ: ตรวจสอบว่ามีการแก้ไขในตำแหน่งนี้หรือไม่**
                    if original_row_index != -1:
                        edit_key = (original_row_index, visual_col_idx_table)
                        if edit_key in existing_edits:
                            # ถ้ามีการแก้ไขอยู่ ให้ใช้ข้อมูลที่แก้ไขแล้ว
                            item.setText(existing_edits[edit_key])
                            item.setBackground(QColor("lightyellow"))
                        
                            # อัปเดต edited_items ด้วย index ใหม่
                            new_edit_key = (row_idx, visual_col_idx_table)
                            self.edited_items[new_edit_key] = existing_edits[edit_key]
                
                    self.results_table.setItem(row_idx, visual_col_idx_table, item)

        # **สำคัญ: เปิด itemChanged signal กลับมาหลังจากอัปเดตเสร็จ**
        self.results_table.itemChanged.connect(self.handle_item_changed)
        self.results_table.setUpdatesEnabled(True)
