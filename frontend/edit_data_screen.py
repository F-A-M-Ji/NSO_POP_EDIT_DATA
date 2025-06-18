import os
import datetime
import math

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
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QBrush, QFont, QFontMetrics, QIcon

from backend.column_mapper import ColumnMapper
from backend.alldata_operations import (
    fetch_all_r_alldata_fields,
    search_r_alldata,
    save_edited_r_alldata_rows,
    get_distinct_values,
    get_area_name_mapping,
    get_regions_from_db,
    get_provinces_from_db,
    get_districts_from_db,
    get_subdistricts_from_db,
    RECORDS_PER_PAGE,
    count_search_r_alldata,
)
from frontend.widgets.multi_line_header import FilterableMultiLineHeaderView
from frontend.utils.error_message import show_error_message, show_info_message
from frontend.utils.shadow_effect import add_shadow_effect
from frontend.data_rules.edit_data_rules import (
    LOGICAL_PK_FIELDS_CONFIG,
    NON_EDITABLE_FIELDS_CONFIG,
    FIELD_VALIDATION_RULES_CONFIG,
    update_rules_from_excel_data,
)
from frontend.data_rules.edit_data_validation import (
    validate_edited_data,
    show_validation_errors,
    load_validation_data_from_excel,
)
from frontend.widgets.filters import (
    apply_table_filter,
    clear_table_filter,
    filter_table_data,
)
from frontend.widgets.column_selector import ColumnSelectorPopup


class EditDataScreen(QWidget):
    LOGICAL_PK_FIELDS = LOGICAL_PK_FIELDS_CONFIG
    NON_EDITABLE_FIELDS = NON_EDITABLE_FIELDS_CONFIG
    FIELD_VALIDATION_RULES = FIELD_VALIDATION_RULES_CONFIG

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.column_mapper = ColumnMapper.get_instance()
        self.all_possible_fields = self.column_mapper.get_fields_to_show().copy()
        self.visible_fields = self.all_possible_fields.copy()
        self.column_selector_popup = None
        self.db_column_names = []
        self.original_data_cache = []
        self.filtered_data_cache = []
        self.edited_items = {}
        self.active_filters = {}
        self._all_db_fields_r_alldata = []
        self.current_page = 1
        self.total_records = 0
        self.total_pages = 0
        self.last_search_conditions = {}
        self.validation_data_from_excel = load_validation_data_from_excel(self)
        update_rules_from_excel_data(self)
        self.search_section_is_visible = True  # State for search visibility
        self.setup_ui()
        self.load_initial_data()

    def update_user_fullname(self, fullname):
        if hasattr(self, "user_fullname_label"):
            self.user_fullname_label.setText(fullname)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 0, 5, 5)

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
        content_layout.setSpacing(1)
        content_layout.setContentsMargins(5, 0, 5, 5)
        add_shadow_effect(self.content_frame)

        # --- UI MODIFICATION: Collapsible Search Section ---
        self.search_section_frame = QFrame()
        self.search_section_frame.setObjectName("searchSection")
        search_layout = QVBoxLayout(self.search_section_frame)
        search_layout.setContentsMargins(10, 5, 10, 0)
        search_layout.setSpacing(5)
        
        # Header with Title and Toggle Button
        search_header_layout = QHBoxLayout()
        search_header_layout.setContentsMargins(0, 0, 0, 0)
        search_title = QLabel("ค้นหาข้อมูล")
        search_title.setObjectName("sectionTitle")
        search_header_layout.addWidget(search_title)
        search_header_layout.addStretch()

        self.toggle_search_button = QPushButton("▲ ซ่อนตัวกรอง")
        self.toggle_search_button.setObjectName("toggleSearchButton")
        self.toggle_search_button.setCursor(Qt.PointingHandCursor)
        self.toggle_search_button.clicked.connect(self.toggle_search_visibility)
        search_header_layout.addWidget(self.toggle_search_button)

        search_layout.addLayout(search_header_layout)

        # Collapsible container for search inputs
        self.search_inputs_container = QWidget()
        search_inputs_layout = QVBoxLayout(self.search_inputs_container)
        search_inputs_layout.setContentsMargins(0, 0, 0, 0)
        search_inputs_layout.setSpacing(5)

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
        area_code_layout = QVBoxLayout()
        area_code_label = QLabel("เขตการปกครอง:")
        self.area_code_combo = QComboBox()
        self.area_code_combo.setObjectName("searchComboBox")
        self.area_code_combo.currentIndexChanged.connect(self.on_area_code_changed)
        area_code_layout.addWidget(area_code_label)
        area_code_layout.addWidget(self.area_code_combo)
        search_row1_layout.addLayout(area_code_layout)
        ea_no_layout = QVBoxLayout()
        ea_no_label = QLabel("เขตแจงนับ:")
        self.ea_no_combo = QComboBox()
        self.ea_no_combo.setObjectName("searchComboBox")
        self.ea_no_combo.currentIndexChanged.connect(self.on_ea_no_changed)
        ea_no_layout.addWidget(ea_no_label)
        ea_no_layout.addWidget(self.ea_no_combo)
        search_row1_layout.addLayout(ea_no_layout)
        search_inputs_layout.addLayout(search_row1_layout)

        search_row2_layout = QHBoxLayout()
        vil_code_layout = QVBoxLayout()
        vil_code_label = QLabel("หมู่ที่:")
        self.vil_code_combo = QComboBox()
        self.vil_code_combo.setObjectName("searchComboBox")
        self.vil_code_combo.currentIndexChanged.connect(self.on_vil_code_changed)
        vil_code_layout.addWidget(vil_code_label)
        vil_code_layout.addWidget(self.vil_code_combo)
        search_row2_layout.addLayout(vil_code_layout)
        vil_name_layout = QVBoxLayout()
        vil_name_label = QLabel("ชื่อหมู่บ้าน:")
        self.vil_name_combo = QComboBox()
        self.vil_name_combo.setObjectName("searchComboBox")
        self.vil_name_combo.currentIndexChanged.connect(self.on_vil_name_changed)
        vil_name_layout.addWidget(vil_name_label)
        vil_name_layout.addWidget(self.vil_name_combo)
        search_row2_layout.addLayout(vil_name_layout)
        building_number_layout = QVBoxLayout()
        building_number_label = QLabel("ลำดับที่สิ่งปลูกสร้าง:")
        self.building_number_combo = QComboBox()
        self.building_number_combo.setObjectName("searchComboBox")
        self.building_number_combo.currentIndexChanged.connect(self.on_building_number_changed)
        building_number_layout.addWidget(building_number_label)
        building_number_layout.addWidget(self.building_number_combo)
        search_row2_layout.addLayout(building_number_layout)
        household_number_layout = QVBoxLayout()
        household_number_label = QLabel("ลำดับที่ครัวเรือน:")
        self.household_number_combo = QComboBox()
        self.household_number_combo.setObjectName("searchComboBox")
        self.household_number_combo.currentIndexChanged.connect(self.on_household_number_changed)
        household_number_layout.addWidget(household_number_label)
        household_number_layout.addWidget(self.household_number_combo)
        search_row2_layout.addLayout(household_number_layout)
        household_member_number_layout = QVBoxLayout()
        household_member_number_label = QLabel("ลำดับที่สมาชิกในครัวเรือน:")
        self.household_member_number_combo = QComboBox()
        self.household_member_number_combo.setObjectName("searchComboBox")
        self.household_member_number_combo.currentIndexChanged.connect(self.on_household_member_number_changed)
        household_member_number_layout.addWidget(household_member_number_label)
        household_member_number_layout.addWidget(self.household_member_number_combo)
        search_row2_layout.addLayout(household_member_number_layout)
        buttons_layout = QVBoxLayout()
        buttons_label = QLabel("")
        buttons_layout.addWidget(buttons_label)
        buttons_container = QHBoxLayout()
        self.search_button = QPushButton("ค้นหา")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.clicked.connect(self.search_data)
        self.search_button.setFixedWidth(120)
        self.search_button.setFixedHeight(20)
        buttons_container.addWidget(self.search_button)
        self.clear_button = QPushButton("ล้าง")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.setFixedWidth(120)
        self.clear_button.setFixedHeight(20)
        buttons_container.addWidget(self.clear_button)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_container)
        buttons_layout.addWidget(buttons_widget)
        search_row2_layout.addLayout(buttons_layout)
        search_inputs_layout.addLayout(search_row2_layout)

        search_layout.addWidget(self.search_inputs_container)

        min_width = 150
        self.region_combo.setMinimumWidth(min_width)
        self.province_combo.setMinimumWidth(min_width)
        self.district_combo.setMinimumWidth(min_width)
        self.subdistrict_combo.setMinimumWidth(min_width)
        self.area_code_combo.setMinimumWidth(min_width)
        self.ea_no_combo.setMinimumWidth(min_width)
        self.vil_code_combo.setMinimumWidth(min_width)
        self.vil_name_combo.setMinimumWidth(min_width)
        self.building_number_combo.setMinimumWidth(min_width)
        self.household_number_combo.setMinimumWidth(min_width)
        self.household_member_number_combo.setMinimumWidth(min_width)
        
        content_layout.addWidget(self.search_section_frame)
        # --- End of UI MODIFICATION ---

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(line)

        results_section = QFrame()
        results_section.setObjectName("resultsSection")
        results_layout = QVBoxLayout(results_section)
        results_layout.setContentsMargins(10, 0, 10, 5)

        results_header_layout = QHBoxLayout()
        results_title = QLabel("ผลการค้นหา (ดับเบิ้ลคลิกเพื่อแก้ไข)")
        results_title.setObjectName("sectionTitle")
        results_header_layout.addWidget(results_title)

        self.column_selector_button = QPushButton("เลือกคอลัมน์")
        self.column_selector_button.setObjectName("secondaryButton")
        self.column_selector_button.setIcon(QIcon(os.path.join("assets", "columns.svg")))
        self.column_selector_button.clicked.connect(self.show_column_selector)
        results_header_layout.addWidget(self.column_selector_button)

        results_header_layout.addStretch()

        self.edit_status_label = QLabel("ไม่มีการแก้ไข")
        self.edit_status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        results_header_layout.addWidget(self.edit_status_label)

        results_layout.addLayout(results_header_layout)

        self.results_table = QTableWidget()
        self.setup_results_table()
        results_layout.addWidget(self.results_table)

        bottom_controls_layout = QHBoxLayout()
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("< ก่อนหน้า")
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.clicked.connect(self.go_to_prev_page)
        self.next_button = QPushButton("ถัดไป >")
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.next_button.clicked.connect(self.go_to_next_page)
        self.page_info_label = QLabel("")
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()
        bottom_controls_layout.addLayout(pagination_layout)

        self.reset_edits_button = QPushButton("ยกเลิกการแก้ไข")
        self.reset_edits_button.setObjectName("secondaryButton")
        self.reset_edits_button.setCursor(Qt.PointingHandCursor)
        self.reset_edits_button.clicked.connect(self.reset_all_edits)

        self.save_edits_button = QPushButton("บันทึกการแก้ไข")
        self.save_edits_button.setObjectName("primaryButton")
        self.save_edits_button.setCursor(Qt.PointingHandCursor)
        self.save_edits_button.clicked.connect(self.prompt_save_edits)

        bottom_controls_layout.addWidget(self.reset_edits_button)
        bottom_controls_layout.addWidget(self.save_edits_button)
        results_layout.addLayout(bottom_controls_layout)

        content_layout.addWidget(results_section, 1)
        main_layout.addWidget(self.content_frame, 1)
        self.setLayout(main_layout)

        self.update_pagination_controls()
        self.update_save_button_state()
        self.setup_table_headers_text_and_widths()

        # Setup animation for the collapsible search section
        self.animation = QPropertyAnimation(self.search_inputs_container, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.search_inputs_container.sizeHint().height())
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def toggle_search_visibility(self):
        """
        Toggles the visibility of the search input fields with a sliding animation.
        """
        if self.animation.state() == QPropertyAnimation.Running:
            return  # Ignore clicks during animation

        if self.search_section_is_visible:
            # Collapse
            self.animation.setDirection(QPropertyAnimation.Backward)
            self.toggle_search_button.setText("▼ แสดงตัวกรอง")
        else:
            # Expand
            self.animation.setDirection(QPropertyAnimation.Forward)
            self.toggle_search_button.setText("▲ ซ่อนตัวกรอง")
        
        self.animation.start()
        self.search_section_is_visible = not self.search_section_is_visible

    def show_column_selector(self):
        all_mappable_fields = self.column_mapper.get_all_mappable_fields()
        if self.column_selector_popup:
            self.column_selector_popup.close()
        self.column_selector_popup = ColumnSelectorPopup(
            all_columns=all_mappable_fields,
            visible_columns=self.visible_fields,
            parent=self,
        )
        self.column_selector_popup.visibility_changed.connect(self.update_column_visibility)
        self.column_selector_popup.exec_()

    def update_column_visibility(self, new_visible_fields):
        self.visible_fields = new_visible_fields
        self.apply_column_visibility()

    def apply_column_visibility(self):
        all_displayable_fields = self.column_mapper.get_fields_to_show()
        for i, field_name in enumerate(all_displayable_fields):
            visual_col_index = i + 1
            is_hidden = field_name not in self.visible_fields
            self.results_table.setColumnHidden(visual_col_index, is_hidden)

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
        self.header = FilterableMultiLineHeaderView(Qt.Horizontal, self.results_table)
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
            main_text, sub_text = self.column_mapper.format_column_header(column_name_display)
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
            calculated_width = required_unwrapped_text_width + self.header.TEXT_BLOCK_PADDING + 20
            min_col_width = 100
            final_column_width = max(calculated_width, min_col_width)
            self.results_table.setColumnWidth(visual_col_idx, int(final_column_width))

        self.header.setSectionResizeMode(QHeaderView.Interactive)
        self.header.style().unpolish(self)
        self.header.style().polish(self.header)
        self.header.updateGeometries()
        self.results_table.updateGeometries()

    def reset_all_edits(self):
        if not self.edited_items: return
        reply = QMessageBox.question(
            self, "ยกเลิกการแก้ไข",
            f"คุณต้องการยกเลิกการแก้ไขทั้งหมด {len(self.edited_items)} รายการหรือไม่?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.edited_items.clear()
            self.update_save_button_state()
            # Refresh the current view to remove highlights
            filter_table_data(self)

    def update_save_button_state(self):
        has_edits = bool(self.edited_items)
        edit_count = len(self.edited_items)
        self.save_edits_button.setEnabled(has_edits)
        self.reset_edits_button.setVisible(has_edits)
        if has_edits:
            self.save_edits_button.setText(f"บันทึกการแก้ไข ({edit_count})")
            self.edit_status_label.setText(f"มีการแก้ไข {edit_count} รายการ")
            self.edit_status_label.setStyleSheet(
                "color: #FF9800; font-style: italic; font-weight: bold;"
            )
        else:
            self.save_edits_button.setText("บันทึกการแก้ไข")
            self.edit_status_label.setText("ไม่มีการแก้ไข")
            self.edit_status_label.setStyleSheet("")

    def handle_item_changed(self, item: QTableWidgetItem):
        if not item or not self.original_data_cache: return
        visual_row, visual_col = item.row(), item.column()
        if visual_col == 0: return

        is_filtered = bool(self.active_filters)
        current_data_source = self.filtered_data_cache if is_filtered else self.original_data_cache
        if visual_row >= len(current_data_source): return

        row_data_for_pk = current_data_source[visual_row]
        pk_tuple = tuple(row_data_for_pk.get(pk) for pk in self.LOGICAL_PK_FIELDS)

        original_row_dict = next((org_row for org_row in self.original_data_cache
                                  if tuple(org_row.get(pk) for pk in self.LOGICAL_PK_FIELDS) == pk_tuple), None)
        if original_row_dict is None: return

        displayed_db_fields = self.column_mapper.get_fields_to_show()
        db_field_col_idx = visual_col - 1
        if db_field_col_idx >= len(displayed_db_fields): return
        db_field_name = displayed_db_fields[db_field_col_idx]

        if db_field_name in self.LOGICAL_PK_FIELDS or db_field_name in self.NON_EDITABLE_FIELDS:
            original_value = original_row_dict.get(db_field_name)
            item.setText(str(original_value) if original_value is not None else "")
            return

        new_text = item.text().strip()
        original_value = original_row_dict.get(db_field_name)
        original_value_str = ""
        if original_value is not None:
            if isinstance(original_value, float) and original_value.is_integer():
                original_value_str = str(int(original_value))
            else:
                original_value_str = str(original_value).strip()
        is_changed = original_value_str != new_text

        if is_changed:
            if pk_tuple not in self.edited_items:
                self.edited_items[pk_tuple] = {'edits': {}, 'original_row': original_row_dict}
            self.edited_items[pk_tuple]['edits'][db_field_name] = new_text
            item.setBackground(QColor("lightyellow"))
        else:
            if pk_tuple in self.edited_items:
                if db_field_name in self.edited_items[pk_tuple]['edits']:
                    del self.edited_items[pk_tuple]['edits'][db_field_name]
                if not self.edited_items[pk_tuple]['edits']:
                    del self.edited_items[pk_tuple]
            item.setBackground(QBrush())
        self.update_save_button_state()

    def search_data(self):
        if self.edited_items:
            reply = QMessageBox.question(
                self, "การเปลี่ยนแปลงที่ยังไม่ได้บันทึก",
                f"คุณมีการแก้ไข {len(self.edited_items)} รายการที่ยังไม่ได้บันทึก "
                "ต้องการบันทึกก่อนค้นหาใหม่หรือไม่?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                self.execute_save_edits()
                if self.edited_items: return
            elif reply == QMessageBox.Cancel: return
            else: # Discard
                self.edited_items.clear()
                self.update_save_button_state()

        self.current_page = 1
        self.last_search_conditions = self.get_current_search_conditions()
        active_conditions = {k: v for k, v in self.last_search_conditions.items() if v is not None}
        if not active_conditions:
            show_error_message(self, "Search Error", "กรุณาเลือกเงื่อนไขในการค้นหาอย่างน้อยหนึ่งรายการ")
            return

        total, err = count_search_r_alldata(self.last_search_conditions)
        if err:
            show_error_message(self, "Search Error", err)
            self.total_records = 0
        else:
            self.total_records = total
        self.total_pages = math.ceil(self.total_records / RECORDS_PER_PAGE) if RECORDS_PER_PAGE > 0 else 0
        self.fetch_page_data()

    def fetch_page_data(self):
        if not self.last_search_conditions: return
        if not self._all_db_fields_r_alldata:
            self._all_db_fields_r_alldata = fetch_all_r_alldata_fields()
        results, db_cols, error_msg = search_r_alldata(
            self.last_search_conditions, self._all_db_fields_r_alldata,
            self.LOGICAL_PK_FIELDS, self.current_page
        )
        if error_msg:
            show_error_message(self, "Search Error", error_msg)
            self.results_table.setRowCount(0)
            self.original_data_cache.clear()
            return
        self.db_column_names = db_cols
        self.display_results(results)

    def display_results(self, results_tuples):
        self.setup_table_headers_text_and_widths()
        self.results_table.setUpdatesEnabled(False)
        try:
            self.results_table.itemChanged.disconnect(self.handle_item_changed)
        except TypeError: pass

        self.results_table.setRowCount(0)
        self.original_data_cache.clear()
        if hasattr(self, "filtered_data_cache"): self.filtered_data_cache.clear()
        if hasattr(self, "active_filters"): self.active_filters.clear()
        if hasattr(self, "header"): self.header.clear_all_filters()
        
        # DO NOT clear self.edited_items here

        if not self.total_records > 0:
            show_info_message(self, "ผลการค้นหา", "ไม่พบข้อมูลตามเงื่อนไขที่ระบุ")
        else:
            self.results_table.setRowCount(len(results_tuples))
            displayed_db_fields = self.column_mapper.get_fields_to_show()
            for row_idx, db_row_tuple in enumerate(results_tuples):
                sequence_text = str((self.current_page - 1) * RECORDS_PER_PAGE + row_idx + 1)
                sequence_item = QTableWidgetItem(sequence_text)
                sequence_item.setTextAlignment(Qt.AlignCenter)
                sequence_item.setFlags(sequence_item.flags() & ~Qt.ItemIsEditable)
                sequence_item.setBackground(QColor("#f0f0f0"))
                self.results_table.setItem(row_idx, 0, sequence_item)

                current_row_data = dict(zip(self.db_column_names, db_row_tuple))
                self.original_data_cache.append(current_row_data)
                pk_tuple = tuple(current_row_data.get(pk) for pk in self.LOGICAL_PK_FIELDS)
                
                row_edits = self.edited_items.get(pk_tuple, {}).get('edits', {})

                for db_field_idx, field_name in enumerate(displayed_db_fields):
                    visual_col_idx = db_field_idx + 1
                    cell_value = str(row_edits.get(field_name, current_row_data.get(field_name, "")))
                    item = QTableWidgetItem(cell_value)
                    item.setTextAlignment(
                        Qt.AlignLeft | Qt.AlignVCenter if field_name in ["FirstName", "LastName"] else Qt.AlignCenter
                    )
                    is_non_editable = (field_name in self.LOGICAL_PK_FIELDS or field_name in self.NON_EDITABLE_FIELDS)
                    if not is_non_editable:
                        item.setFlags(item.flags() | Qt.ItemIsEditable)
                        if field_name in row_edits:
                            item.setBackground(QColor("lightyellow"))
                    else:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        item.setBackground(QColor("#f0f0f0"))
                    self.results_table.setItem(row_idx, visual_col_idx, item)

        self.results_table.itemChanged.connect(self.handle_item_changed)
        self.results_table.setUpdatesEnabled(True)
        self.update_pagination_controls()
        self.apply_column_visibility()

    def go_to_page_action(self, page_action_func):
        """Wrapper to check for edits before changing page."""
        if self.edited_items:
            reply = QMessageBox.question(
                self, "การเปลี่ยนแปลงที่ยังไม่ได้บันทึก",
                "คุณมีการแก้ไขที่ยังไม่ได้บันทึก ต้องการบันทึกก่อนเปลี่ยนหน้าหรือไม่?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                self.execute_save_edits()
                if not self.edited_items:  # Succeeded
                    page_action_func()
            elif reply == QMessageBox.Discard:
                self.edited_items.clear()
                self.update_save_button_state()
                page_action_func()
        else:
            page_action_func()

    def go_to_prev_page(self):
        def action():
            if self.current_page > 1:
                self.current_page -= 1
                self.fetch_page_data()
        self.go_to_page_action(action)

    def go_to_next_page(self):
        def action():
            if self.current_page < self.total_pages:
                self.current_page += 1
                self.fetch_page_data()
        self.go_to_page_action(action)

    def update_pagination_controls(self):
        if self.total_records > 0:
            self.page_info_label.setText(
                f"หน้า {self.current_page} / {self.total_pages} (ทั้งหมด {self.total_records} รายการ)"
            )
            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < self.total_pages)
        else:
            self.page_info_label.setText("")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

    def get_current_search_conditions(self):
        conditions = {}
        location_codes = self.get_selected_codes()
        conditions.update(location_codes)
        additional_conditions = {
            "AreaCode": self.get_selected_area_code(),
            "EA_NO": self.get_selected_ea_no(),
            "VilCode": self.get_selected_vil_code(),
            "VilName": self.get_selected_vil_name(),
            "BuildingNumber": self.get_selected_building_number(),
            "HouseholdNumber": self.get_selected_household_number(),
            "HouseholdMemberNumber": self.get_selected_household_member_number(),
        }
        for key, value in additional_conditions.items():
            if value is not None:
                conditions[key] = value
        return conditions

    def prompt_save_edits(self):
        if self.results_table.state() == QAbstractItemView.EditingState:
            self.results_table.setCurrentItem(None)
            QApplication.processEvents()
        if not self.edited_items:
            show_info_message(self, "ไม่มีการเปลี่ยนแปลง", "ไม่มีข้อมูลที่แตกต่างจากเดิมให้บันทึก")
            return
        reply = QMessageBox.question(
            self, "ยืนยันการบันทึก", "คุณต้องการบันทึกข้อมูลที่แก้ไขหรือไม่?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.execute_save_edits()

    def execute_save_edits(self):
        if self.parent_app.current_user is None or "fullname" not in self.parent_app.current_user:
            show_error_message(self, "ข้อผิดพลาด", "ไม่พบข้อมูลผู้ใช้งานปัจจุบัน ไม่สามารถบันทึกได้")
            return
        if not self.edited_items:
            show_info_message(self, "ไม่มีการเปลี่ยนแปลง", "ไม่มีข้อมูลที่แตกต่างจากเดิมให้บันทึก")
            return

        validation_errors = validate_edited_data(self)
        if validation_errors:
            show_validation_errors(self, validation_errors)
            return

        editor_fullname = self.parent_app.current_user["fullname"]
        edit_timestamp = datetime.datetime.now()
        list_of_records_to_save = []
        for pk_tuple, edit_info in self.edited_items.items():
            record_to_save = edit_info['original_row'].copy()
            record_to_save.update(edit_info['edits'])
            record_to_save["fullname"] = editor_fullname
            record_to_save["time_edit"] = edit_timestamp
            list_of_records_to_save.append(record_to_save)

        if not list_of_records_to_save:
            show_info_message(self, "ข้อมูลล่าสุด", "ไม่มีข้อมูลที่ถูกต้องสำหรับบันทึก")
            return

        saved_count, error_msg = save_edited_r_alldata_rows(
            list_of_records_to_save, self._all_db_fields_r_alldata
        )
        if error_msg:
            show_error_message(self, "Save Error", error_msg)
            return

        if saved_count > 0:
            show_info_message(self, "สำเร็จ", f"บันทึกข้อมูลที่แก้ไขจำนวน {saved_count} แถวเรียบร้อยแล้ว")
            self.edited_items.clear()
            self.update_save_button_state()
            filter_table_data(self)
        else:
            show_info_message(self, "ข้อมูลล่าสุด", "ไม่มีการเปลี่ยนแปลงที่จำเป็นต้องบันทึกเพิ่มเติม")
            self.edited_items.clear()
            self.update_save_button_state()

    def clear_user_info(self):
        """ล้างข้อมูลผู้ใช้ที่แสดงบนหน้าจอ"""
        if hasattr(self, "user_fullname_label"):
            self.user_fullname_label.setText("User: N/A")

    def reset_search_visibility_state(self):
        """
        รีเซ็ตส่วนการค้นหาให้กลับเป็นสถานะเริ่มต้น (แสดงผล)
        """
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.Running:
            self.animation.stop()

        self.search_section_is_visible = True
        
        if hasattr(self, 'toggle_search_button'):
            self.toggle_search_button.setText("▲ ซ่อนตัวกรอง")
            
        if hasattr(self, 'search_inputs_container'):
            # ตั้งค่าความสูงสูงสุดเป็นค่าที่เหมาะสมเพื่อให้แสดงผลเต็มที่ทันที
            self.search_inputs_container.setMaximumHeight(self.search_inputs_container.sizeHint().height())
            self.search_inputs_container.show()

    def reset_screen_state(self):
        """รีเซ็ตสถานะหน้าจอ (ฟอร์มค้นหาและตารางผลลัพธ์)"""
        self.region_combo.setCurrentIndex(0)
        self.setup_initial_dropdown_state()
        try:
            self.results_table.itemChanged.disconnect(self.handle_item_changed)
        except TypeError: pass
        self.results_table.setRowCount(0)
        self.results_table.itemChanged.connect(self.handle_item_changed)

        self.original_data_cache.clear()
        self.filtered_data_cache.clear()
        self.db_column_names = []
        self.edited_items.clear()
        self.active_filters.clear()
        self.last_search_conditions = {}
        self.current_page = 1
        self.total_records = 0
        self.total_pages = 0
        self.visible_fields = self.all_possible_fields.copy()
        self.apply_column_visibility()
        if hasattr(self, "header"):
            self.header.clear_all_filters()
        self.update_pagination_controls()
        self.update_save_button_state()
        
        # --- ADDED THIS LINE TO RESET FILTER VISIBILITY ---
        self.reset_search_visibility_state()
        
        # หมายเหตุ: บรรทัดที่ตั้งค่า user_fullname_label ถูกย้ายไปที่ clear_user_info()

    def clear_search(self):
        self.reset_screen_state()

    def logout(self):
        if self.edited_items:
            reply = QMessageBox.question(
                self, "การเปลี่ยนแปลงที่ยังไม่ได้บันทึก",
                "คุณมีการแก้ไขที่ยังไม่ได้บันทึก ต้องการบันทึกก่อนออกจากระบบหรือไม่?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.execute_save_edits()
                if not self.edited_items: self.parent_app.perform_logout()
            elif reply == QMessageBox.Discard:
                self.parent_app.perform_logout()
        else:
            self.parent_app.perform_logout()

    def load_initial_data(self):
        try:
            self._all_db_fields_r_alldata = fetch_all_r_alldata_fields()
            self.load_regions()
            self.setup_initial_dropdown_state()
        except Exception as e:
            show_error_message(self, "Error", f"ไม่สามารถโหลดข้อมูลเริ่มต้นได้: {str(e)}")

    def setup_initial_dropdown_state(self):
        self.province_combo.clear()
        self.district_combo.clear()
        self.subdistrict_combo.clear()
        self.area_code_combo.clear()
        self.ea_no_combo.clear()
        self.vil_code_combo.clear()
        self.vil_name_combo.clear()
        self.building_number_combo.clear()
        self.household_number_combo.clear()
        self.household_member_number_combo.clear()

    def load_regions(self):
        try:
            self.region_combo.blockSignals(True)
            self.region_combo.clear()
            self.region_combo.addItem("-- เลือกภาค --")
            for region in get_regions_from_db():
                self.region_combo.addItem(region["display"], region["code"])
            self.region_combo.blockSignals(False)
        except Exception as e:
            print(f"Error loading regions: {e}")

    def load_provinces_with_placeholder(self, reg_code=None):
        try:
            self.province_combo.clear()
            self.province_combo.addItem("-- เลือกจังหวัด --")
            for province in get_provinces_from_db(reg_code):
                self.province_combo.addItem(province["display"], province["code"])
        except Exception as e:
            print(f"Error loading provinces: {e}")

    def load_districts_with_placeholder(self, prov_code=None):
        try:
            self.district_combo.clear()
            self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
            for district in get_districts_from_db(prov_code):
                self.district_combo.addItem(district["display"], district["code"])
        except Exception as e:
            print(f"Error loading districts: {e}")

    def load_subdistricts_with_placeholder(self, dist_code=None, prov_code=None):
        try:
            self.subdistrict_combo.clear()
            self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")
            for subdistrict in get_subdistricts_from_db(dist_code, prov_code):
                self.subdistrict_combo.addItem(subdistrict["display"], subdistrict["code"])
        except Exception as e:
            print(f"Error loading subdistricts: {e}")

    def on_region_changed(self, index):
        self.clear_province_and_below_without_placeholder()
        if index > 0:
            reg_code = self.region_combo.itemData(index)
            if reg_code: self.load_provinces_with_placeholder(reg_code)

    def on_province_changed(self, index):
        self.clear_district_and_below_without_placeholder()
        if index > 0:
            prov_code = self.province_combo.itemData(index)
            if prov_code: self.load_districts_with_placeholder(prov_code)

    def on_district_changed(self, index):
        self.clear_subdistrict_and_below_without_placeholder()
        if index > 0:
            dist_code = self.district_combo.itemData(index)
            prov_code = self.get_selected_province_code()
            if dist_code: self.load_subdistricts_with_placeholder(dist_code, prov_code)

    def get_selected_province_code(self):
        return self.province_combo.itemData(self.province_combo.currentIndex()) if self.province_combo.currentIndex() > 0 else None

    def on_subdistrict_changed(self, index):
        self.clear_area_code_and_below_without_placeholder()
        if index > 0: self.populate_area_code()

    def on_area_code_changed(self, index):
        self.clear_ea_no_and_below_without_placeholder()
        if index > 0: self.populate_ea_no()

    def on_ea_no_changed(self, index):
        self.clear_vil_code_and_below_without_placeholder()
        if index > 0: self.populate_vil_code()

    def on_vil_code_changed(self, index):
        self.clear_vil_name_and_below_without_placeholder()
        if index > 0: self.populate_vil_name()

    def on_vil_name_changed(self, index):
        self.clear_building_number_and_below_without_placeholder()
        if index > 0: self.populate_building_number()

    def on_building_number_changed(self, index):
        self.clear_household_number_and_below_without_placeholder()
        if index > 0: self.populate_household_number()

    def on_household_number_changed(self, index):
        self.clear_household_member_number_and_below_without_placeholder()
        if index > 0: self.populate_household_member_number()

    def on_household_member_number_changed(self, index):    
        pass

    def get_selected_codes(self):
        codes = {}
        if self.region_combo.currentIndex() > 0: codes["RegCode"] = self.region_combo.itemData(self.region_combo.currentIndex())
        if self.province_combo.currentIndex() > 0: codes["ProvCode"] = self.province_combo.itemData(self.province_combo.currentIndex())
        if self.district_combo.currentIndex() > 0: codes["DistCode"] = self.district_combo.itemData(self.district_combo.currentIndex())
        if self.subdistrict_combo.currentIndex() > 0: codes["SubDistCode"] = self.subdistrict_combo.itemData(self.subdistrict_combo.currentIndex())
        return codes

    def populate_area_code(self):
        where_conditions, where_params = self.build_where_conditions_up_to_subdistrict()
        area_codes = get_distinct_values("AreaCode", where_conditions, tuple(where_params))
        area_name_mapping = get_area_name_mapping()
        self.area_code_combo.clear()
        self.area_code_combo.addItem("-- เลือกเขตการปกครอง --")
        for code in area_codes:
            display_text = f"{area_name_mapping.get(code, code)}" if code else "-- Blank --"
            self.area_code_combo.addItem(display_text, code)

    def populate_ea_no(self):
        where_conditions, where_params = self.build_where_conditions_up_to_area_code()
        ea_nos = get_distinct_values("EA_NO", where_conditions, tuple(where_params))
        self.ea_no_combo.clear()
        self.ea_no_combo.addItem("-- เลือกเขตแจงนับ --")
        for ea_no in ea_nos:
            self.ea_no_combo.addItem(ea_no if ea_no else "-- Blank --", ea_no)

    def populate_vil_code(self):
        where_conditions, where_params = self.build_where_conditions_up_to_ea_no()
        vil_codes = get_distinct_values("VilCode", where_conditions, tuple(where_params))
        self.vil_code_combo.clear()
        self.vil_code_combo.addItem("-- เลือกหมู่ที่ --")
        for vil_code in vil_codes:
            self.vil_code_combo.addItem(vil_code if vil_code else "-- Blank --", vil_code)

    def populate_vil_name(self):
        where_conditions, where_params = self.build_where_conditions_up_to_vil_code()
        vil_names = get_distinct_values("VilName", where_conditions, tuple(where_params))
        self.vil_name_combo.clear()
        self.vil_name_combo.addItem("-- เลือกชื่อหมู่บ้าน --")
        for vil_name in vil_names:
            self.vil_name_combo.addItem(vil_name if vil_name else "-- Blank --", vil_name)

    def populate_building_number(self):
        where_conditions, where_params = self.build_where_conditions_up_to_vil_name()
        building_numbers = get_distinct_values("BuildingNumber", where_conditions, tuple(where_params))
        self.building_number_combo.clear()
        self.building_number_combo.addItem("-- เลือกลำดับที่สิ่งปลูกสร้าง --")
        for num in building_numbers:
            self.building_number_combo.addItem(num if num else "-- Blank --", num)

    def populate_household_number(self):
        where_conditions, where_params = self.build_where_conditions_up_to_building_number()
        household_numbers = get_distinct_values("HouseholdNumber", where_conditions, tuple(where_params))
        self.household_number_combo.clear()
        self.household_number_combo.addItem("-- เลือกลำดับที่ครัวเรือน --")
        for num in household_numbers:
            self.household_number_combo.addItem(num if num else "-- Blank --", num)

    def populate_household_member_number(self):
        where_conditions, where_params = self.build_where_conditions_up_to_household_number()
        member_numbers = get_distinct_values("HouseholdMemberNumber", where_conditions, tuple(where_params))
        self.household_member_number_combo.clear()
        self.household_member_number_combo.addItem("-- เลือกลำดับที่สมาชิกในครัวเรือน --")
        for num in member_numbers:
            self.household_member_number_combo.addItem(num if num else "-- Blank --", num)

    def build_where_conditions_up_to_subdistrict(self):
        conditions, params = [], []
        codes = self.get_selected_codes()
        for key, value in codes.items():
            if value is not None:
                conditions.append(f"[{key}] = ?")
                params.append(value)
        return " AND ".join(conditions) if conditions else None, params

    def build_where_conditions_up_to_area_code(self):
        base_conditions, base_params = self.build_where_conditions_up_to_subdistrict()
        area_code_value = self.get_selected_area_code()
        if area_code_value is not None:
            area_condition = "([AreaCode] IS NULL OR [AreaCode] = '' OR LTRIM(RTRIM([AreaCode])) = '')" if area_code_value == "" else "[AreaCode] = ?"
            conditions = f"{base_conditions} AND {area_condition}" if base_conditions else area_condition
            params = base_params.copy()
            if area_code_value != "": params.append(area_code_value)
            return conditions, params
        return base_conditions, base_params

    def build_where_conditions_up_to_ea_no(self):
        base_conditions, base_params = self.build_where_conditions_up_to_area_code()
        ea_no_value = self.get_selected_ea_no()
        if ea_no_value is not None:
            ea_condition = "([EA_NO] IS NULL OR [EA_NO] = '' OR LTRIM(RTRIM([EA_NO])) = '')" if ea_no_value == "" else "[EA_NO] = ?"
            conditions = f"{base_conditions} AND {ea_condition}" if base_conditions else ea_condition
            params = base_params.copy()
            if ea_no_value != "": params.append(ea_no_value)
            return conditions, params
        return base_conditions, base_params

    def build_where_conditions_up_to_vil_code(self):
        base_conditions, base_params = self.build_where_conditions_up_to_ea_no()
        vil_code_value = self.get_selected_vil_code()
        if vil_code_value is not None:
            vil_condition = "([VilCode] IS NULL OR [VilCode] = '' OR LTRIM(RTRIM([VilCode])) = '')" if vil_code_value == "" else "[VilCode] = ?"
            conditions = f"{base_conditions} AND {vil_condition}" if base_conditions else vil_condition
            params = base_params.copy()
            if vil_code_value != "": params.append(vil_code_value)
            return conditions, params
        return base_conditions, base_params

    def build_where_conditions_up_to_vil_name(self):
        base_conditions, base_params = self.build_where_conditions_up_to_vil_code()
        vil_name_value = self.get_selected_vil_name()
        if vil_name_value is not None:
            vil_name_condition = "([VilName] IS NULL OR [VilName] = '' OR LTRIM(RTRIM([VilName])) = '')" if vil_name_value == "" else "[VilName] = ?"
            conditions = f"{base_conditions} AND {vil_name_condition}" if base_conditions else vil_name_condition
            params = base_params.copy()
            if vil_name_value != "": params.append(vil_name_value)
            return conditions, params
        return base_conditions, base_params

    def build_where_conditions_up_to_building_number(self):
        base_conditions, base_params = self.build_where_conditions_up_to_vil_name()
        building_number_value = self.get_selected_building_number()
        if building_number_value is not None:
            building_condition = "([BuildingNumber] IS NULL OR [BuildingNumber] = '' OR LTRIM(RTRIM([BuildingNumber])) = '')" if building_number_value == "" else "[BuildingNumber] = ?"
            conditions = f"{base_conditions} AND {building_condition}" if base_conditions else building_condition
            params = base_params.copy()
            if building_number_value != "": params.append(building_number_value)
            return conditions, params
        return base_conditions, base_params

    def build_where_conditions_up_to_household_number(self):
        base_conditions, base_params = self.build_where_conditions_up_to_building_number()
        household_number_value = self.get_selected_household_number()
        if household_number_value is not None:
            household_condition = "([HouseholdNumber] IS NULL OR [HouseholdNumber] = '' OR LTRIM(RTRIM([HouseholdNumber])) = '')" if household_number_value == "" else "[HouseholdNumber] = ?"
            conditions = f"{base_conditions} AND {household_condition}" if base_conditions else household_condition
            params = base_params.copy()
            if household_number_value != "": params.append(household_number_value)
            return conditions, params
        return base_conditions, base_params

    def get_selected_area_code(self):
        return self.area_code_combo.itemData(self.area_code_combo.currentIndex()) if self.area_code_combo.currentIndex() > 0 else None

    def get_selected_ea_no(self):
        return self.ea_no_combo.itemData(self.ea_no_combo.currentIndex()) if self.ea_no_combo.currentIndex() > 0 else None

    def get_selected_vil_code(self):
        return self.vil_code_combo.itemData(self.vil_code_combo.currentIndex()) if self.vil_code_combo.currentIndex() > 0 else None

    def get_selected_vil_name(self):
        return self.vil_name_combo.itemData(self.vil_name_combo.currentIndex()) if self.vil_name_combo.currentIndex() > 0 else None

    def get_selected_building_number(self):
        return self.building_number_combo.itemData(self.building_number_combo.currentIndex()) if self.building_number_combo.currentIndex() > 0 else None

    def get_selected_household_number(self):
        return self.household_number_combo.itemData(self.household_number_combo.currentIndex()) if self.household_number_combo.currentIndex() > 0 else None

    def get_selected_household_member_number(self):
        return self.household_member_number_combo.itemData(self.household_member_number_combo.currentIndex()) if self.household_member_number_combo.currentIndex() > 0 else None

    def clear_province_and_below_without_placeholder(self):
        self.province_combo.clear()
        self.clear_district_and_below_without_placeholder()

    def clear_district_and_below_without_placeholder(self):
        self.district_combo.clear()
        self.clear_subdistrict_and_below_without_placeholder()

    def clear_subdistrict_and_below_without_placeholder(self):
        self.subdistrict_combo.clear()
        self.clear_area_code_and_below_without_placeholder()

    def clear_area_code_and_below_without_placeholder(self):
        self.area_code_combo.clear()
        self.clear_ea_no_and_below_without_placeholder()

    def clear_ea_no_and_below_without_placeholder(self):
        self.ea_no_combo.clear()
        self.clear_vil_code_and_below_without_placeholder()

    def clear_vil_code_and_below_without_placeholder(self):
        self.vil_code_combo.clear()
        self.clear_vil_name_and_below_without_placeholder()

    def clear_vil_name_and_below_without_placeholder(self):
        self.vil_name_combo.clear()
        self.clear_building_number_and_below_without_placeholder()

    def clear_building_number_and_below_without_placeholder(self):
        self.building_number_combo.clear()
        self.clear_household_number_and_below_without_placeholder()

    def clear_household_number_and_below_without_placeholder(self):
        self.household_number_combo.clear()
        self.clear_household_member_number_and_below_without_placeholder()

    def clear_household_member_number_and_below_without_placeholder(self):
        self.household_member_number_combo.clear()
