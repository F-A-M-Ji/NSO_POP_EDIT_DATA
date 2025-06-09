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

    if not eds_instance.active_filters:
        # ถ้าไม่มีฟิลเตอร์เลย ให้ใช้ข้อมูลดั้งเดิมทั้งหมด
        filtered_data_list = eds_instance.original_data_cache[:]
    else:
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
                
                filter_text_val = filter_info.get("text", "").strip()
                if filter_text_val:
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

    # === CHANGE START: ไม่ล้าง edited_items ที่นี่ ===
    # eds_instance.edited_items.clear()
    # === CHANGE END ===

    if hasattr(
        eds_instance, "setup_table_headers_text_and_widths"
    ):
        eds_instance.setup_table_headers_text_and_widths()

    eds_instance.results_table.setRowCount(0)
    eds_instance.filtered_data_cache = filtered_data

    if not filtered_data:
        if eds_instance.active_filters:
            show_info_message(eds_instance, "ผลการกรอง", "ไม่พบข้อมูลที่ตรงกับเงื่อนไขการกรอง")
    else:
        eds_instance.results_table.setRowCount(len(filtered_data))
        displayed_db_fields_in_table = eds_instance.column_mapper.get_fields_to_show()

        # สร้าง map สำหรับค้นหา original_row_idx จาก primary key เพื่อประสิทธิภาพ
        pk_to_original_idx_map = {
            tuple(row.get(pk) for pk in eds_instance.LOGICAL_PK_FIELDS): i
            for i, row in enumerate(eds_instance.original_data_cache)
        }

        for row_idx, row_data in enumerate(filtered_data):
            # ตั้งค่าคอลัมน์ลำดับ
            sequence_text = str(row_idx + 1)
            sequence_item = QTableWidgetItem(sequence_text)
            sequence_item.setTextAlignment(Qt.AlignCenter)
            flags = sequence_item.flags()
            sequence_item.setFlags(flags & ~Qt.ItemIsEditable)
            sequence_item.setBackground(QColor("#f0f0f0"))
            eds_instance.results_table.setItem(row_idx, 0, sequence_item)
            
            # หา original index ของแถวนี้
            pk_tuple = tuple(row_data.get(pk) for pk in eds_instance.LOGICAL_PK_FIELDS)
            original_row_idx = pk_to_original_idx_map.get(pk_tuple)

            if original_row_idx is None:
                continue # ไม่ควรเกิดขึ้นถ้าข้อมูลถูกต้อง

            for db_field_idx, displayed_field_name in enumerate(
                displayed_db_fields_in_table
            ):
                visual_col_idx_table = db_field_idx + 1
                
                edit_key = (original_row_idx, visual_col_idx_table)
                is_edited = edit_key in eds_instance.edited_items

                if is_edited:
                    # ถ้า cell นี้ถูกแก้ไข ให้ใช้ค่าจาก edited_items
                    cell_value = eds_instance.edited_items[edit_key]
                else:
                    # มิฉะนั้นใช้ค่าจากข้อมูลที่กรองมา
                    raw_value = row_data.get(displayed_field_name)
                    cell_value = str(raw_value) if raw_value is not None else ""

                item = QTableWidgetItem(cell_value)
                
                # ตั้งค่าการจัดเรียง
                if displayed_field_name in ["FirstName", "LastName"]:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter)

                # ตั้งค่าการแก้ไขได้
                is_editable = not (
                    displayed_field_name in eds_instance.LOGICAL_PK_FIELDS
                    or displayed_field_name in eds_instance.NON_EDITABLE_FIELDS
                )
                
                if is_editable:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    if is_edited:
                        # ถ้าแก้ไขแล้ว ให้เปลี่ยนสีพื้นหลัง
                        item.setBackground(QColor("lightyellow"))
                else:  # Not editable
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setBackground(QColor("#f0f0f0"))

                eds_instance.results_table.setItem(row_idx, visual_col_idx_table, item)

    eds_instance.results_table.itemChanged.connect(eds_instance.handle_item_changed)
    eds_instance.results_table.setUpdatesEnabled(True)
    
    # ไม่ต้องอัปเดตสถานะปุ่มบันทึกที่นี่ เพราะการแก้ไขยังคงอยู่
    # if hasattr(eds_instance, "update_save_button_state"):
    #     eds_instance.update_save_button_state()
    
    if hasattr(eds_instance, "apply_column_visibility"):
        eds_instance.apply_column_visibility()

