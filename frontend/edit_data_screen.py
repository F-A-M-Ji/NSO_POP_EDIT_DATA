# from PyQt5.QtWidgets import (
#     QWidget,
#     QVBoxLayout,
#     QHBoxLayout,
#     QLabel,
#     QPushButton,
#     QFrame,
#     QComboBox,
#     QTableWidget,
#     QTableWidgetItem,
#     QHeaderView,
#     QAbstractItemView,
#     QDialog,
#     QVBoxLayout,
#     QTextBrowser,
# )
# from PyQt5.QtCore import Qt
# import pandas as pd
# import os
# import pyodbc

# from backend.db import get_connection
# from backend.column_mapper import ColumnMapper
# from frontend.widgets.multi_line_header import MultiLineHeaderView
# from frontend.utils.error_message import show_error_message
# from frontend.utils.shadow_effect import add_shadow_effect


# class EditDataScreen(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.parent_app = parent
#         self.location_data = None
#         self.cursor = None
#         self.column_mapper = ColumnMapper.get_instance()
#         self.setup_ui()
#         self.load_location_data()

#     def update_user_fullname(self, fullname):
#         """อัพเดทชื่อผู้ใช้ที่แสดง"""
#         if hasattr(self, "user_fullname_label"):
#             self.user_fullname_label.setText(fullname)

#     def setup_ui(self):
#         main_layout = QVBoxLayout()
#         main_layout.setContentsMargins(50, 50, 50, 50)

#         # Header with logout option
#         header_layout = QHBoxLayout()

#         header_label = QLabel("Edit Data")
#         header_label.setObjectName("headerLabel")
#         header_layout.addWidget(header_label)

#         header_layout.addStretch()

#         # เพิ่ม Label สำหรับแสดงชื่อผู้ใช้งาน
#         self.user_fullname_label = QLabel("")
#         self.user_fullname_label.setObjectName("userFullnameLabel")
#         self.user_fullname_label.setStyleSheet("font-weight: bold; color: #2196F3;")
#         header_layout.addWidget(self.user_fullname_label)

#         # เพิ่มระยะห่างระหว่างชื่อผู้ใช้กับปุ่ม Logout
#         spacer = QLabel("  |  ")
#         spacer.setStyleSheet("color: #bdbdbd;")
#         header_layout.addWidget(spacer)

#         logout_button = QPushButton("Logout")
#         logout_button.setObjectName("secondaryButton")
#         logout_button.setCursor(Qt.PointingHandCursor)
#         logout_button.clicked.connect(self.logout)
#         header_layout.addWidget(logout_button)

#         main_layout.addLayout(header_layout)

#         # Content frame
#         self.content_frame = QFrame()
#         self.content_frame.setObjectName("contentFrame")
#         content_layout = QVBoxLayout(self.content_frame)

#         add_shadow_effect(self.content_frame)

#         # Search section
#         search_section = QFrame()
#         search_section.setObjectName("searchSection")
#         search_layout = QVBoxLayout(search_section)

#         search_title = QLabel("ค้นหา")
#         search_title.setObjectName("sectionTitle")
#         search_layout.addWidget(search_title)

#         # Create dropdown row
#         dropdown_layout = QHBoxLayout()

#         # Region dropdown
#         region_layout = QVBoxLayout()
#         region_label = QLabel("ภาค:")
#         self.region_combo = QComboBox()
#         self.region_combo.setObjectName("searchComboBox")
#         self.region_combo.currentIndexChanged.connect(self.on_region_changed)
#         region_layout.addWidget(region_label)
#         region_layout.addWidget(self.region_combo)
#         dropdown_layout.addLayout(region_layout)

#         # Province dropdown
#         province_layout = QVBoxLayout()
#         province_label = QLabel("จังหวัด:")
#         self.province_combo = QComboBox()
#         self.province_combo.setObjectName("searchComboBox")
#         self.province_combo.currentIndexChanged.connect(self.on_province_changed)
#         province_layout.addWidget(province_label)
#         province_layout.addWidget(self.province_combo)
#         dropdown_layout.addLayout(province_layout)

#         # District dropdown
#         district_layout = QVBoxLayout()
#         district_label = QLabel("อำเภอ/เขต:")
#         self.district_combo = QComboBox()
#         self.district_combo.setObjectName("searchComboBox")
#         self.district_combo.currentIndexChanged.connect(self.on_district_changed)
#         district_layout.addWidget(district_label)
#         district_layout.addWidget(self.district_combo)
#         dropdown_layout.addLayout(district_layout)

#         # Subdistrict dropdown
#         subdistrict_layout = QVBoxLayout()
#         subdistrict_label = QLabel("ตำบล/แขวง:")
#         self.subdistrict_combo = QComboBox()
#         self.subdistrict_combo.setObjectName("searchComboBox")
#         self.subdistrict_combo.currentIndexChanged.connect(self.on_subdistrict_changed)
#         subdistrict_layout.addWidget(subdistrict_label)
#         subdistrict_layout.addWidget(self.subdistrict_combo)
#         dropdown_layout.addLayout(subdistrict_layout)

#         search_layout.addLayout(dropdown_layout)

#         # Search button
#         button_layout = QHBoxLayout()
#         button_layout.addStretch()

#         self.search_button = QPushButton("ค้นหา")
#         self.search_button.setObjectName("primaryButton")
#         self.search_button.setCursor(Qt.PointingHandCursor)
#         self.search_button.clicked.connect(self.search_data)
#         self.search_button.setFixedWidth(120)
#         button_layout.addWidget(self.search_button)

#         self.clear_button = QPushButton("ล้าง")
#         self.clear_button.setObjectName("secondaryButton")
#         self.clear_button.setCursor(Qt.PointingHandCursor)
#         self.clear_button.clicked.connect(self.clear_search)
#         self.clear_button.setFixedWidth(120)
#         button_layout.addWidget(self.clear_button)

#         search_layout.addLayout(button_layout)
#         content_layout.addWidget(search_section)

#         # Horizontal line separator
#         line = QFrame()
#         line.setFrameShape(QFrame.HLine)
#         line.setFrameShadow(QFrame.Sunken)
#         content_layout.addWidget(line)

#         # Results section
#         results_section = QFrame()
#         results_section.setObjectName("resultsSection")
#         results_layout = QVBoxLayout(results_section)

#         results_title = QLabel("ผลการค้นหา")
#         results_title.setObjectName("sectionTitle")
#         results_layout.addWidget(results_title)

#         # Create table for results
#         self.results_table = QTableWidget()
#         self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
#         self.results_table.doubleClicked.connect(self.show_row_details)
#         self.setup_results_table()

#         results_layout.addWidget(self.results_table)
#         content_layout.addWidget(results_section, 1)  # 1 = stretch factor

#         main_layout.addWidget(self.content_frame, 1)

#         self.setLayout(main_layout)

#     def setup_results_table(self):
#         # ใช้ MultiLineHeaderView แทน QHeaderView มาตรฐาน
#         self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
#         self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
#         self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)

#         # สร้างและกำหนด header view แบบ multi-line
#         self.header = MultiLineHeaderView(Qt.Horizontal, self.results_table)
#         self.results_table.setHorizontalHeader(self.header)

#     def load_location_data(self):
#         try:
#             # Get the path to the Excel file
#             excel_path = os.path.join(
#                 os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
#                 "assets",
#                 "reg_prov_dist_subdist.xlsx",
#             )

#             # Load the Excel file
#             self.location_data = pd.read_excel(excel_path, sheet_name="รหัสเขตการปกครอง")

#             # Populate the region dropdown
#             regions = sorted(self.location_data["RegName"].unique())
#             self.region_combo.addItem("-- เลือกภาค --")
#             for region in regions:
#                 self.region_combo.addItem(region)

#             # Initialize other dropdowns
#             self.province_combo.addItem("-- เลือกจังหวัด --")
#             self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
#             self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

#         except Exception as e:
#             show_error_message(self, "Error", f"Failed to load location data: {str(e)}")

#     def on_region_changed(self, index):
#         # Clear subsequent dropdowns
#         self.province_combo.clear()
#         self.district_combo.clear()
#         self.subdistrict_combo.clear()

#         # Add default items
#         self.province_combo.addItem("-- เลือกจังหวัด --")
#         self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
#         self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

#         # If the default item is selected, don't filter
#         if index == 0:
#             return

#         # Get the selected region
#         selected_region = self.region_combo.currentText()

#         # Filter provinces by the selected region
#         provinces = sorted(
#             self.location_data[self.location_data["RegName"] == selected_region][
#                 "ProvName"
#             ].unique()
#         )
#         for province in provinces:
#             self.province_combo.addItem(province)

#     def on_province_changed(self, index):
#         # Clear subsequent dropdowns
#         self.district_combo.clear()
#         self.subdistrict_combo.clear()

#         # Add default items
#         self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
#         self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

#         # If the default item is selected, don't filter
#         if index == 0:
#             return

#         # Get the selected region and province
#         selected_region = self.region_combo.currentText()
#         selected_province = self.province_combo.currentText()

#         # Filter districts by the selected region and province
#         filtered_data = self.location_data[
#             (self.location_data["RegName"] == selected_region)
#             & (self.location_data["ProvName"] == selected_province)
#         ]
#         districts = sorted(filtered_data["DistName"].unique())
#         for district in districts:
#             self.district_combo.addItem(district)

#     def on_district_changed(self, index):
#         # Clear subdistrict dropdown
#         self.subdistrict_combo.clear()

#         # Add default item
#         self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

#         # If the default item is selected, don't filter
#         if index == 0:
#             return

#         # Get the selected region, province, and district
#         selected_region = self.region_combo.currentText()
#         selected_province = self.province_combo.currentText()
#         selected_district = self.district_combo.currentText()

#         # Filter subdistricts by the selected region, province, and district
#         filtered_data = self.location_data[
#             (self.location_data["RegName"] == selected_region)
#             & (self.location_data["ProvName"] == selected_province)
#             & (self.location_data["DistName"] == selected_district)
#         ]
#         subdistricts = sorted(filtered_data["SubDistName"].unique())
#         for subdistrict in subdistricts:
#             self.subdistrict_combo.addItem(subdistrict)

#     def on_subdistrict_changed(self, index):
#         # This method can be used if you need to perform any action when a subdistrict is selected
#         pass

#     def get_selected_codes(self):
#         # Get codes from the Excel file based on selected names
#         selected_region = self.region_combo.currentText()
#         selected_province = self.province_combo.currentText()
#         selected_district = self.district_combo.currentText()
#         selected_subdistrict = self.subdistrict_combo.currentText()

#         codes = {
#             "RegCode": None,
#             "ProvCode": None,
#             "DistCode": None,
#             "SubDistCode": None,
#         }

#         # Find the matching codes
#         if selected_region != "-- เลือกภาค --":
#             filtered_data = self.location_data[
#                 self.location_data["RegName"] == selected_region
#             ]
#             if not filtered_data.empty:
#                 codes["RegCode"] = filtered_data["RegCode"].iloc[0]

#             if selected_province != "-- เลือกจังหวัด --":
#                 filtered_data = filtered_data[
#                     filtered_data["ProvName"] == selected_province
#                 ]
#                 if not filtered_data.empty:
#                     codes["ProvCode"] = filtered_data["ProvCode"].iloc[0]

#                 if selected_district != "-- เลือกอำเภอ/เขต --":
#                     filtered_data = filtered_data[
#                         filtered_data["DistName"] == selected_district
#                     ]
#                     if not filtered_data.empty:
#                         codes["DistCode"] = filtered_data["DistCode"].iloc[0]

#                     if selected_subdistrict != "-- เลือกตำบล/แขวง --":
#                         filtered_data = filtered_data[
#                             filtered_data["SubDistName"] == selected_subdistrict
#                         ]
#                         if not filtered_data.empty:
#                             codes["SubDistCode"] = filtered_data["SubDistCode"].iloc[0]

#         return codes

#     def search_data(self):
#         # Get selected codes
#         codes = self.get_selected_codes()

#         # แปลงค่า numpy.int64 เป็น int ปกติ
#         if codes["RegCode"] is not None:
#             codes["RegCode"] = int(codes["RegCode"])
#         if codes["ProvCode"] is not None:
#             codes["ProvCode"] = int(codes["ProvCode"])
#         if codes["DistCode"] is not None:
#             codes["DistCode"] = int(codes["DistCode"])
#         if codes["SubDistCode"] is not None:
#             codes["SubDistCode"] = int(codes["SubDistCode"])

#         # Build SQL query based on selected criteria
#         sql_conditions = []
#         params = []

#         if codes["RegCode"] is not None:
#             sql_conditions.append("RegCode = ?")
#             params.append(codes["RegCode"])

#         if codes["ProvCode"] is not None:
#             sql_conditions.append("ProvCode = ?")
#             params.append(codes["ProvCode"])

#         if codes["DistCode"] is not None:
#             sql_conditions.append("DistCode = ?")
#             params.append(codes["DistCode"])

#         if codes["SubDistCode"] is not None:
#             sql_conditions.append("SubDistCode = ?")
#             params.append(codes["SubDistCode"])

#         # If no conditions are selected, show a message and return
#         if not sql_conditions:
#             show_error_message(
#                 self, "Search Error", "กรุณาเลือกเงื่อนไขในการค้นหาอย่างน้อยหนึ่งรายการ"
#             )
#             return

#         # เปลี่ยนเป็นเลือกทุกฟิลด์ (SELECT * FROM)
#         query = "SELECT * FROM r_alldata"

#         # Add WHERE clause if conditions exist
#         if sql_conditions:
#             query += " WHERE " + " AND ".join(sql_conditions)

#         # Add order by clause
#         query += " ORDER BY RegName, ProvName, DistName, SubDistName"

#         try:
#             # Execute the query
#             conn = get_connection()
#             if not conn:
#                 show_error_message(self, "Database Error", "ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
#                 return

#             self.cursor = conn.cursor()
#             self.cursor.execute(query, params)
#             results = self.cursor.fetchall()

#             # Update the results table
#             self.display_results(results)

#         except Exception as e:
#             show_error_message(
#                 self, "Search Error", f"เกิดข้อผิดพลาดระหว่างการค้นหา: {str(e)}"
#             )

#     def display_results(self, results):
#         # Clear existing results
#         self.results_table.setRowCount(0)
#         self.results_table.setColumnCount(0)

#         # Check if any results were found
#         if not results:
#             show_error_message(self, "ผลการค้นหา", "ไม่พบข้อมูลตามเงื่อนไขที่ระบุ")
#             return

#         # Get column names from cursor description
#         columns = [column[0] for column in self.cursor.description]

#         # Set up columns in the table
#         self.results_table.setColumnCount(len(columns))

#         # Set column headers with multi-line text
#         for i, field_name in enumerate(columns):
#             # ดึงชื่อคอลัมน์จาก mapping
#             column_name = self.column_mapper.get_column_name(field_name)
#             # แยกข้อความในวงเล็บและนอกวงเล็บ
#             main_text, sub_text = self.column_mapper.format_column_header(column_name)
#             # กำหนดข้อความให้กับหัวคอลัมน์
#             self.header.setColumnText(i, main_text, sub_text)

#             # กำหนดความกว้างคอลัมน์ตามประเภทข้อมูล
#             if "Name" in field_name or "Other" in field_name:
#                 self.results_table.setColumnWidth(i, 180)
#             elif (
#                 "Code" in field_name
#                 or field_name.startswith("Vil")
#                 or field_name.startswith("Reg")
#             ):
#                 self.results_table.setColumnWidth(i, 100)
#             else:
#                 self.results_table.setColumnWidth(i, 120)

#         # Add results to the table
#         for row_index, row_data in enumerate(results):
#             self.results_table.insertRow(row_index)
#             for col_index, cell_data in enumerate(row_data):
#                 # Convert None to empty string
#                 if cell_data is None:
#                     cell_data = ""
#                 self.results_table.setItem(
#                     row_index, col_index, QTableWidgetItem(str(cell_data))
#                 )

#     def show_row_details(self, index):
#         # Get all data for the selected row
#         row = index.row()

#         # Create a dialog to show details
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Record Details")
#         dialog.setMinimumSize(600, 400)

#         # Create layout
#         layout = QVBoxLayout(dialog)

#         # Create a text browser to display details
#         details = QTextBrowser()

#         # Collect all data from the selected row
#         row_data = {}
#         for col in range(self.results_table.columnCount()):
#             header = self.results_table.horizontalHeaderItem(col).text()
#             item = self.results_table.item(row, col)
#             value = item.text() if item else ""
#             row_data[header] = value

#         # Format the details
#         html = "<h2>Record Details</h2>"
#         html += "<table style='width:100%; border-collapse: collapse;'>"
#         for key, value in row_data.items():
#             html += f"<tr><td style='padding:8px; border-bottom:1px solid #ddd; font-weight:bold;'>{key}</td>"
#             html += f"<td style='padding:8px; border-bottom:1px solid #ddd;'>{value}</td></tr>"
#         html += "</table>"

#         details.setHtml(html)
#         layout.addWidget(details)

#         # Add close button
#         close_button = QPushButton("Close")
#         close_button.clicked.connect(dialog.accept)
#         layout.addWidget(close_button)

#         # Show the dialog
#         dialog.exec_()

#     def clear_search(self):
#         # Reset all dropdowns
#         self.region_combo.setCurrentIndex(0)
#         self.province_combo.clear()
#         self.district_combo.clear()
#         self.subdistrict_combo.clear()

#         self.province_combo.addItem("-- เลือกจังหวัด --")
#         self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
#         self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

#         # Clear results table
#         self.results_table.setRowCount(0)

#     def logout(self):
#         self.parent_app.navigate_to("login")


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
    QDialog,
    QTextBrowser,
)
from PyQt5.QtCore import Qt
import pandas as pd
import os
import pyodbc

from backend.db import get_connection
from backend.column_mapper import ColumnMapper
from frontend.widgets.multi_line_header import MultiLineHeaderView
from frontend.utils.error_message import show_error_message
from frontend.utils.shadow_effect import add_shadow_effect
from frontend.utils.resource_path import resource_path

class EditDataScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.location_data = None
        self.cursor = None
        self.column_mapper = ColumnMapper.get_instance()
        self.setup_ui()
        self.load_location_data()
        self.setup_table_headers()  # เพิ่มบรรทัดนี้

    def update_user_fullname(self, fullname):
        """อัพเดทชื่อผู้ใช้ที่แสดง"""
        if hasattr(self, "user_fullname_label"):
            self.user_fullname_label.setText(fullname)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Header with logout option
        header_layout = QHBoxLayout()

        header_label = QLabel("Edit Data")
        header_label.setObjectName("headerLabel")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # เพิ่ม Label สำหรับแสดงชื่อผู้ใช้งาน
        self.user_fullname_label = QLabel("")
        self.user_fullname_label.setObjectName("userFullnameLabel")
        self.user_fullname_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        header_layout.addWidget(self.user_fullname_label)

        # เพิ่มระยะห่างระหว่างชื่อผู้ใช้กับปุ่ม Logout
        spacer = QLabel("  |  ")
        spacer.setStyleSheet("color: #bdbdbd;")
        header_layout.addWidget(spacer)

        logout_button = QPushButton("Logout")
        logout_button.setObjectName("secondaryButton")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)

        main_layout.addLayout(header_layout)

        # Content frame
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(self.content_frame)

        add_shadow_effect(self.content_frame)

        # Search section
        search_section = QFrame()
        search_section.setObjectName("searchSection")
        search_layout = QVBoxLayout(search_section)

        search_title = QLabel("ค้นหา")
        search_title.setObjectName("sectionTitle")
        search_layout.addWidget(search_title)

        # Create dropdown row
        dropdown_layout = QHBoxLayout()

        # Region dropdown
        region_layout = QVBoxLayout()
        region_label = QLabel("ภาค:")
        self.region_combo = QComboBox()
        self.region_combo.setObjectName("searchComboBox")
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_combo)
        dropdown_layout.addLayout(region_layout)

        # Province dropdown
        province_layout = QVBoxLayout()
        province_label = QLabel("จังหวัด:")
        self.province_combo = QComboBox()
        self.province_combo.setObjectName("searchComboBox")
        self.province_combo.currentIndexChanged.connect(self.on_province_changed)
        province_layout.addWidget(province_label)
        province_layout.addWidget(self.province_combo)
        dropdown_layout.addLayout(province_layout)

        # District dropdown
        district_layout = QVBoxLayout()
        district_label = QLabel("อำเภอ/เขต:")
        self.district_combo = QComboBox()
        self.district_combo.setObjectName("searchComboBox")
        self.district_combo.currentIndexChanged.connect(self.on_district_changed)
        district_layout.addWidget(district_label)
        district_layout.addWidget(self.district_combo)
        dropdown_layout.addLayout(district_layout)

        # Subdistrict dropdown
        subdistrict_layout = QVBoxLayout()
        subdistrict_label = QLabel("ตำบล/แขวง:")
        self.subdistrict_combo = QComboBox()
        self.subdistrict_combo.setObjectName("searchComboBox")
        self.subdistrict_combo.currentIndexChanged.connect(self.on_subdistrict_changed)
        subdistrict_layout.addWidget(subdistrict_label)
        subdistrict_layout.addWidget(self.subdistrict_combo)
        dropdown_layout.addLayout(subdistrict_layout)

        search_layout.addLayout(dropdown_layout)

        # Search button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.search_button = QPushButton("ค้นหา")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.clicked.connect(self.search_data)
        self.search_button.setFixedWidth(120)
        button_layout.addWidget(self.search_button)

        self.clear_button = QPushButton("ล้าง")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.setFixedWidth(120)
        button_layout.addWidget(self.clear_button)

        search_layout.addLayout(button_layout)
        content_layout.addWidget(search_section)

        # Horizontal line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(line)

        # Results section
        results_section = QFrame()
        results_section.setObjectName("resultsSection")
        results_layout = QVBoxLayout(results_section)

        results_title = QLabel("ผลการค้นหา")
        results_title.setObjectName("sectionTitle")
        results_layout.addWidget(results_title)

        # Create table for results
        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.results_table.doubleClicked.connect(self.show_row_details)
        self.setup_results_table()

        results_layout.addWidget(self.results_table)
        content_layout.addWidget(results_section, 1)  # 1 = stretch factor

        main_layout.addWidget(self.content_frame, 1)

        self.setLayout(main_layout)

    def setup_table_headers(self):
        """ตั้งค่าหัวตารางล่วงหน้า"""
        fields = self.column_mapper.get_fields_to_show()

        # ตั้งค่าจำนวนคอลัมน์
        self.results_table.setColumnCount(len(fields))

        # ตั้งค่าชื่อคอลัมน์
        for i, field_name in enumerate(fields):
            column_name = self.column_mapper.get_column_name(field_name)
            main_text, sub_text = self.column_mapper.format_column_header(column_name)
            self.header.setColumnText(i, main_text, sub_text)

            # คำนวณความกว้างตามข้อความในหัวตาราง
            font_metrics = self.fontMetrics()
            main_width = font_metrics.width(main_text)
            sub_width = font_metrics.width(sub_text) if sub_text else 0
            width = max(main_width, sub_width) + 50  # เพิ่ม padding
            self.results_table.setColumnWidth(i, width)

        # อนุญาตให้ผู้ใช้สามารถปรับขนาดคอลัมน์ได้
        self.header.setSectionResizeMode(QHeaderView.Interactive)

    def setup_results_table(self):
        # ใช้ MultiLineHeaderView แทน QHeaderView มาตรฐาน
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
    
        # เปิดการแสดงเส้นตาราง
        self.results_table.setShowGrid(True)
        self.results_table.setGridStyle(Qt.SolidLine)
    
        # กำหนดสีเส้นตาราง
        # self.results_table.setStyleSheet("""
        #     QTableWidget {
        #         gridline-color: #bbdefb;
        #         border: 1px solid #bbdefb;
        #     }
        #     QTableWidget::item {
        #         border-bottom: 1px solid #bbdefb;
        #     }
        #     QTableView::item:selected {
        #         background-color: #e3f2fd;
        #         color: #000000;
        #     }
        # """)
    
        # สร้างและกำหนด header view แบบ multi-line
        self.header = MultiLineHeaderView(Qt.Horizontal, self.results_table)
        self.results_table.setHorizontalHeader(self.header)

    def load_location_data(self):
        try:
            # Get the path to the Excel file
            # excel_path = os.path.join(
            #     os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            #     "assets",
            #     "reg_prov_dist_subdist.xlsx",
            # )
            excel_path = resource_path(os.path.join("assets", "reg_prov_dist_subdist.xlsx"))

            # Load the Excel file
            self.location_data = pd.read_excel(excel_path, sheet_name="Area_code")

            # Populate the region dropdown
            regions = sorted(self.location_data["RegName"].unique())
            self.region_combo.addItem("-- เลือกภาค --")
            for region in regions:
                self.region_combo.addItem(region)

            # Initialize other dropdowns
            self.province_combo.addItem("-- เลือกจังหวัด --")
            self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
            self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        except Exception as e:
            show_error_message(self, "Error", f"Failed to load location data: {str(e)}")

    def on_region_changed(self, index):
        # Clear subsequent dropdowns
        self.province_combo.clear()
        self.district_combo.clear()
        self.subdistrict_combo.clear()

        # Add default items
        self.province_combo.addItem("-- เลือกจังหวัด --")
        self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
        self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        # If the default item is selected, don't filter
        if index == 0:
            return

        # Get the selected region
        selected_region = self.region_combo.currentText()

        # Filter provinces by the selected region
        provinces = sorted(
            self.location_data[self.location_data["RegName"] == selected_region][
                "ProvName"
            ].unique()
        )
        for province in provinces:
            self.province_combo.addItem(province)

    def on_province_changed(self, index):
        # Clear subsequent dropdowns
        self.district_combo.clear()
        self.subdistrict_combo.clear()

        # Add default items
        self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
        self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        # If the default item is selected, don't filter
        if index == 0:
            return

        # Get the selected region and province
        selected_region = self.region_combo.currentText()
        selected_province = self.province_combo.currentText()

        # Filter districts by the selected region and province
        filtered_data = self.location_data[
            (self.location_data["RegName"] == selected_region)
            & (self.location_data["ProvName"] == selected_province)
        ]
        districts = sorted(filtered_data["DistName"].unique())
        for district in districts:
            self.district_combo.addItem(district)

    def on_district_changed(self, index):
        # Clear subdistrict dropdown
        self.subdistrict_combo.clear()

        # Add default item
        self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        # If the default item is selected, don't filter
        if index == 0:
            return

        # Get the selected region, province, and district
        selected_region = self.region_combo.currentText()
        selected_province = self.province_combo.currentText()
        selected_district = self.district_combo.currentText()

        # Filter subdistricts by the selected region, province, and district
        filtered_data = self.location_data[
            (self.location_data["RegName"] == selected_region)
            & (self.location_data["ProvName"] == selected_province)
            & (self.location_data["DistName"] == selected_district)
        ]
        subdistricts = sorted(filtered_data["SubDistName"].unique())
        for subdistrict in subdistricts:
            self.subdistrict_combo.addItem(subdistrict)

    def on_subdistrict_changed(self, index):
        # This method can be used if you need to perform any action when a subdistrict is selected
        pass

    def get_selected_codes(self):
        # Get codes from the Excel file based on selected names
        selected_region = self.region_combo.currentText()
        selected_province = self.province_combo.currentText()
        selected_district = self.district_combo.currentText()
        selected_subdistrict = self.subdistrict_combo.currentText()

        codes = {
            "RegCode": None,
            "ProvCode": None,
            "DistCode": None,
            "SubDistCode": None,
        }

        # Find the matching codes
        if selected_region != "-- เลือกภาค --":
            filtered_data = self.location_data[
                self.location_data["RegName"] == selected_region
            ]
            if not filtered_data.empty:
                codes["RegCode"] = filtered_data["RegCode"].iloc[0]

            if selected_province != "-- เลือกจังหวัด --":
                filtered_data = filtered_data[
                    filtered_data["ProvName"] == selected_province
                ]
                if not filtered_data.empty:
                    codes["ProvCode"] = filtered_data["ProvCode"].iloc[0]

                if selected_district != "-- เลือกอำเภอ/เขต --":
                    filtered_data = filtered_data[
                        filtered_data["DistName"] == selected_district
                    ]
                    if not filtered_data.empty:
                        codes["DistCode"] = filtered_data["DistCode"].iloc[0]

                    if selected_subdistrict != "-- เลือกตำบล/แขวง --":
                        filtered_data = filtered_data[
                            filtered_data["SubDistName"] == selected_subdistrict
                        ]
                        if not filtered_data.empty:
                            codes["SubDistCode"] = filtered_data["SubDistCode"].iloc[0]

        return codes

    def search_data(self):
        # Get selected codes
        codes = self.get_selected_codes()

        # แปลงค่า numpy.int64 เป็น int ปกติ
        if codes["RegCode"] is not None:
            codes["RegCode"] = int(codes["RegCode"])
        if codes["ProvCode"] is not None:
            codes["ProvCode"] = int(codes["ProvCode"])
        if codes["DistCode"] is not None:
            codes["DistCode"] = int(codes["DistCode"])
        if codes["SubDistCode"] is not None:
            codes["SubDistCode"] = int(codes["SubDistCode"])

        # Build SQL query based on selected criteria
        sql_conditions = []
        params = []

        if codes["RegCode"] is not None:
            sql_conditions.append("RegCode = ?")
            params.append(codes["RegCode"])

        if codes["ProvCode"] is not None:
            sql_conditions.append("ProvCode = ?")
            params.append(codes["ProvCode"])

        if codes["DistCode"] is not None:
            sql_conditions.append("DistCode = ?")
            params.append(codes["DistCode"])

        if codes["SubDistCode"] is not None:
            sql_conditions.append("SubDistCode = ?")
            params.append(codes["SubDistCode"])

        # If no conditions are selected, show a message and return
        if not sql_conditions:
            show_error_message(
                self, "Search Error", "กรุณาเลือกเงื่อนไขในการค้นหาอย่างน้อยหนึ่งรายการ"
            )
            return

        # ดึงเฉพาะฟิลด์ที่กำหนดในไฟล์ Excel
        select_fields = self.column_mapper.get_select_fields_sql()

        # สร้างคำสั่ง SQL โดยเลือกเฉพาะฟิลด์ที่กำหนด
        query = f"SELECT {select_fields} FROM r_alldata"

        # Add WHERE clause if conditions exist
        if sql_conditions:
            query += " WHERE " + " AND ".join(sql_conditions)

        # Add order by clause
        query += " ORDER BY RegName, ProvName, DistName, SubDistName"

        try:
            # Execute the query
            conn = get_connection()
            if not conn:
                show_error_message(self, "Database Error", "ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
                return

            self.cursor = conn.cursor()
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            # Update the results table
            self.display_results(results)

        except Exception as e:
            show_error_message(
                self, "Search Error", f"เกิดข้อผิดพลาดระหว่างการค้นหา: {str(e)}"
            )

    def display_results(self, results):
        # เคลียร์เฉพาะข้อมูลในตาราง แต่คงหัวตารางไว้
        self.results_table.setRowCount(0)

        # Check if any results were found
        if not results:
            show_error_message(self, "ผลการค้นหา", "ไม่พบข้อมูลตามเงื่อนไขที่ระบุ")
            return

        # Add results to the table
        for row_index, row_data in enumerate(results):
            self.results_table.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                # Convert None to empty string
                if cell_data is None:
                    cell_data = ""
                self.results_table.setItem(
                    row_index, col_index, QTableWidgetItem(str(cell_data))
                )

    # def show_row_details(self, index):
    #     # Get all data for the selected row
    #     row = index.row()

    #     # Create a dialog to show details
    #     dialog = QDialog(self)
    #     dialog.setWindowTitle("Record Details")
    #     dialog.setMinimumSize(600, 400)

    #     # Create layout
    #     layout = QVBoxLayout(dialog)

    #     # Create a text browser to display details
    #     details = QTextBrowser()

    #     # Collect all data from the selected row
    #     row_data = {}
    #     for col in range(self.results_table.columnCount()):
    #         header = self.results_table.horizontalHeaderItem(col).text()
    #         item = self.results_table.item(row, col)
    #         value = item.text() if item else ""
    #         row_data[header] = value

    #     # Format the details
    #     html = "<h2>Record Details</h2>"
    #     html += "<table style='width:100%; border-collapse: collapse;'>"
    #     for key, value in row_data.items():
    #         html += f"<tr><td style='padding:8px; border-bottom:1px solid #ddd; font-weight:bold;'>{key}</td>"
    #         html += f"<td style='padding:8px; border-bottom:1px solid #ddd;'>{value}</td></tr>"
    #     html += "</table>"

    #     details.setHtml(html)
    #     layout.addWidget(details)

    #     # Add close button
    #     close_button = QPushButton("Close")
    #     close_button.clicked.connect(dialog.accept)
    #     layout.addWidget(close_button)

    #     # Show the dialog
    #     dialog.exec_()

    def clear_search(self):
        # Reset all dropdowns
        self.region_combo.setCurrentIndex(0)
        self.province_combo.clear()
        self.district_combo.clear()
        self.subdistrict_combo.clear()

        self.province_combo.addItem("-- เลือกจังหวัด --")
        self.district_combo.addItem("-- เลือกอำเภอ/เขต --")
        self.subdistrict_combo.addItem("-- เลือกตำบล/แขวง --")

        # Clear results table
        self.results_table.setRowCount(0)

    def logout(self):
        self.parent_app.navigate_to("login")
