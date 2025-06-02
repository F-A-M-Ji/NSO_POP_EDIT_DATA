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
from frontend.widgets.multi_line_header import FilterableMultiLineHeaderView
from frontend.utils.error_message import show_error_message, show_info_message
from frontend.utils.shadow_effect import add_shadow_effect
from frontend.utils.resource_path import resource_path
from frontend.data_rules.edit_data_rules import (
    LOGICAL_PK_FIELDS_CONFIG,
    NON_EDITABLE_FIELDS_CONFIG,
    FIELD_VALIDATION_RULES_CONFIG,
)


def apply_table_filter(
    eds_instance, column, text, show_blank_only
):  # เปลี่ยน self เป็น eds_instance เพื่อความชัดเจน
    """ใช้ฟิลเตอร์กับตาราง"""
    if not eds_instance.original_data_cache:
        return

    if text or show_blank_only:
        eds_instance.active_filters[column] = {
            "text": text.lower(),
            "show_blank": show_blank_only,
        }
    else:
        if column in eds_instance.active_filters:
            del eds_instance.active_filters[column]

    filter_table_data(eds_instance)  # <--- แก้ไข: เรียกฟังก์ชันโดยตรง ส่ง instance ไป


def clear_table_filter(eds_instance, column):  # เปลี่ยน self เป็น eds_instance
    """ล้างฟิลเตอร์ของคอลัมน์"""
    if column in eds_instance.active_filters:
        del eds_instance.active_filters[column]
    filter_table_data(eds_instance)  # <--- แก้ไข: เรียกฟังก์ชันโดยตรง ส่ง instance ไป


def filter_table_data(eds_instance):  # เปลี่ยน self เป็น eds_instance
    """กรองข้อมูลในตารางตามฟิลเตอร์ที่ใช้งานอยู่"""
    if not eds_instance.original_data_cache:
        return

    # displayed_fields ควรมาจาก eds_instance.column_mapper
    displayed_fields = eds_instance.column_mapper.get_fields_to_show()
    filtered_data_list = []  # เปลี่ยนชื่อตัวแปรเพื่อไม่ให้ซ้ำกับชื่อฟังก์ชัน display_filtered_results

    for row_data in eds_instance.original_data_cache:
        should_include = True
        for (
            col_idx,
            filter_info,
        ) in eds_instance.active_filters.items():  # ใช้ col_idx จาก active_filters
            if col_idx == 0:
                continue

            field_index = col_idx - 1  # active_filters key คือ visual column index
            if not (0 <= field_index < len(displayed_fields)):
                continue

            field_name = displayed_fields[field_index]
            field_value = row_data.get(field_name)
            value_str = str(field_value).strip() if field_value is not None else ""

            if filter_info.get("show_blank", False):
                if value_str != "":
                    should_include = False
                    break

            # ตรวจสอบ filter_text ต่อแม้ว่า show_blank จะเป็นจริง (กรณีต้องการทั้งค่าว่างและมี text บางอย่าง)
            # หรือถ้า show_blank เป็น false ก็ตรวจสอบ filter_text ตามปกติ
            # ที่ถูกต้องคือ ถ้า show_blank เป็น true และ value_str ไม่ใช่ "" ก็คือไม่ผ่านแล้ว
            # ถ้า show_blank เป็น true และ value_str เป็น "" ก็อาจจะต้องเช็ค text ต่อ (ถ้า text ไม่ว่าง) หรือให้ผ่านเลย
            # โค้ดเดิม: ถ้า show_blank จริง แล้ว value_str ไม่ใช่ "" -> should_include = False, break
            # ถ้า show_blank เป็นเท็จ หรือ value_str เป็น "" (ผ่านเงื่อนไข show_blank) -> เช็ค filter_text
            # เพื่อให้เหมือนเดิม:
            if filter_info.get("show_blank", False) and value_str != "":
                # should_include = False (ทำไปแล้วด้านบน)
                pass  # เงื่อนไขนี้ถูกจัดการไปแล้ว
            else:  # check text if not excluded by show_blank or if show_blank is false
                filter_text_val = filter_info.get("text", "").strip()
                if filter_text_val:  # only filter by text if text is provided
                    if filter_text_val.lower() not in value_str.lower():
                        should_include = False
                        break

        if should_include:
            filtered_data_list.append(row_data)

    display_filtered_results(
        eds_instance, filtered_data_list
    )  # <--- แก้ไข: เรียกฟังก์ชันโดยตรง ส่ง instance ไป


def display_filtered_results(
    eds_instance, filtered_data
):  # เปลี่ยน self เป็น eds_instance และชื่อ filtered_data_list เป็น filtered_data
    """แสดงผลข้อมูลที่ถูกฟิลเตอร์"""
    eds_instance.results_table.setUpdatesEnabled(False)
    try:
        eds_instance.results_table.itemChanged.disconnect(
            eds_instance.handle_item_changed
        )
    except TypeError:
        pass

    # existing_edits = eds_instance.edited_items.copy() # การ map edit items คืนหลัง filter มีความซับซ้อน
    eds_instance.edited_items.clear()  # เพื่อความเรียบง่าย จะล้างการแก้ไขเมื่อมีการกรอง

    if hasattr(
        eds_instance, "setup_table_headers_text_and_widths"
    ):  # ตรวจสอบว่า eds_instance มี method นี้
        eds_instance.setup_table_headers_text_and_widths()

    eds_instance.results_table.setRowCount(0)
    eds_instance.filtered_data_cache = filtered_data

    if not filtered_data:
        if eds_instance.active_filters:  # แสดงเมื่อมีการกรองแล้วไม่พบข้อมูล
            show_info_message(eds_instance, "ผลการกรอง", "ไม่พบข้อมูลที่ตรงกับเงื่อนไขการกรอง")
    else:
        eds_instance.results_table.setRowCount(len(filtered_data))
        displayed_db_fields_in_table = eds_instance.column_mapper.get_fields_to_show()

        for row_idx, row_data in enumerate(filtered_data):
            sequence_text = str(row_idx + 1)
            sequence_item = QTableWidgetItem(sequence_text)
            sequence_item.setTextAlignment(Qt.AlignCenter)
            flags = sequence_item.flags()
            sequence_item.setFlags(flags & ~Qt.ItemIsEditable)
            sequence_item.setBackground(QColor("#f0f0f0"))
            eds_instance.results_table.setItem(row_idx, 0, sequence_item)

            # original_row_index = -1 # การหา original_row_index สำหรับ mapping edit items ที่ซับซ้อน
            # ... (ส่วนการหา original_row_index และคืนค่า edited_items ถูกละไว้เพื่อความเรียบง่าย)

            for db_field_idx, displayed_field_name in enumerate(
                displayed_db_fields_in_table
            ):
                visual_col_idx_table = db_field_idx + 1
                cell_value = ""
                if displayed_field_name in row_data:
                    raw_value = row_data[displayed_field_name]
                    cell_value = str(raw_value) if raw_value is not None else ""

                item = QTableWidgetItem(cell_value)
                if displayed_field_name in ["FirstName", "LastName"]:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter)

                is_editable = not (
                    displayed_field_name in eds_instance.LOGICAL_PK_FIELDS
                    or displayed_field_name in eds_instance.NON_EDITABLE_FIELDS
                )
                if is_editable:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    # ตรวจสอบ edit_key ที่ map มา (ถ้าทำ)
                    # edit_key_mapped = (row_idx, visual_col_idx_table) # index ใหม่ในตารางที่ filter แล้ว
                    # if edit_key_mapped in eds_instance.edited_items:
                    #    item.setText(eds_instance.edited_items[edit_key_mapped])
                    #    item.setBackground(QColor("lightyellow"))

                else:  # Not editable
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setBackground(QColor("#f0f0f0"))

                eds_instance.results_table.setItem(row_idx, visual_col_idx_table, item)

    eds_instance.results_table.itemChanged.connect(eds_instance.handle_item_changed)
    eds_instance.results_table.setUpdatesEnabled(True)
    if hasattr(
        eds_instance, "update_save_button_state"
    ):  # ตรวจสอบว่า instance มี method นี้
        eds_instance.update_save_button_state()
