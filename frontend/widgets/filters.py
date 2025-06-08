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
):
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

    filter_table_data(eds_instance)


def clear_table_filter(eds_instance, column):
    """ล้างฟิลเตอร์ของคอลัมน์"""
    if column in eds_instance.active_filters:
        del eds_instance.active_filters[column]
    filter_table_data(eds_instance)


def filter_table_data(eds_instance):
    """กรองข้อมูลในตารางตามฟิลเตอร์ที่ใช้งานอยู่"""
    if not eds_instance.original_data_cache:
        eds_instance.filtered_data_cache = []
        display_filtered_results(eds_instance, [])
        return
    
    # === CHANGE START: ตรรกะการกรองข้อมูลโดยยังคงการแก้ไขไว้ ===
    # 1. สร้างข้อมูลชั่วคราวโดยรวมการแก้ไขล่าสุดเข้าไปก่อน
    temp_data_for_filtering = []
    
    # สร้าง map จาก PK ไปยัง original_row_idx เพื่อความเร็ว
    pk_to_original_idx_map = {
        tuple(row.get(pk) for pk in eds_instance.LOGICAL_PK_FIELDS): i
        for i, row in enumerate(eds_instance.original_data_cache)
    }

    edited_rows_map = {key[0]: {} for key in eds_instance.edited_items.keys()}
    for (original_row, col), value in eds_instance.edited_items.items():
        edited_rows_map[original_row][col] = value

    displayed_fields = eds_instance.column_mapper.get_fields_to_show()

    for original_idx, row_data in enumerate(eds_instance.original_data_cache):
        # สร้างสำเนาของแถวเพื่อไม่ให้กระทบข้อมูล original cache
        current_row = row_data.copy()
        
        # หากแถวนี้มีการแก้ไข ให้ปรับปรุงข้อมูลในแถวสำเนานี้
        if original_idx in edited_rows_map:
            for col, new_value in edited_rows_map[original_idx].items():
                if 0 < col <= len(displayed_fields):
                    field_name = displayed_fields[col - 1]
                    current_row[field_name] = new_value
        
        temp_data_for_filtering.append(current_row)
    
    # 2. ทำการกรองข้อมูลจากข้อมูลชั่วคราวที่รวมการแก้ไขแล้ว
    if not eds_instance.active_filters:
        filtered_data_list = temp_data_for_filtering
    else:
        filtered_data_list = []
        for row_data in temp_data_for_filtering:
            should_include = True
            for col_idx, filter_info in eds_instance.active_filters.items():
                if col_idx == 0: continue
                
                field_index = col_idx - 1
                if not (0 <= field_index < len(displayed_fields)): continue

                field_name = displayed_fields[field_index]
                field_value = row_data.get(field_name)
                value_str = str(field_value).strip() if field_value is not None else ""
                
                filter_text_val = filter_info.get("text", "").strip().lower()
                show_blank_only = filter_info.get("show_blank", False)

                if show_blank_only:
                    if value_str != "":
                        should_include = False
                        break
                elif filter_text_val and filter_text_val not in value_str.lower():
                    should_include = False
                    break
            
            if should_include:
                filtered_data_list.append(row_data)
    # === CHANGE END ===

    display_filtered_results(eds_instance, filtered_data_list)


def display_filtered_results(eds_instance, filtered_data):
    """แสดงผลข้อมูลที่ถูกฟิลเตอร์พร้อมกับคงสถานะการแก้ไข"""
    eds_instance.results_table.setUpdatesEnabled(False)
    try:
        eds_instance.results_table.itemChanged.disconnect(
            eds_instance.handle_item_changed
        )
    except TypeError:
        pass

    # === CRITICAL CHANGE: ไม่ล้างข้อมูล edited_items ที่นี่ ===
    # eds_instance.edited_items.clear() 

    if hasattr(eds_instance, "setup_table_headers_text_and_widths"):
        eds_instance.setup_table_headers_text_and_widths()

    eds_instance.results_table.setRowCount(0)
    eds_instance.filtered_data_cache = filtered_data

    if not filtered_data:
        if eds_instance.active_filters:
            show_info_message(eds_instance, "ผลการกรอง", "ไม่พบข้อมูลที่ตรงกับเงื่อนไขการกรอง")
    else:
        eds_instance.results_table.setRowCount(len(filtered_data))
        displayed_db_fields = eds_instance.column_mapper.get_fields_to_show()

        # สร้าง map จาก PK ไปยัง original_row_idx เพื่อความเร็วในการค้นหา
        pk_to_original_idx_map = {
            tuple(row.get(pk) for pk in eds_instance.LOGICAL_PK_FIELDS): i
            for i, row in enumerate(eds_instance.original_data_cache)
        }

        for visual_row_idx, row_data in enumerate(filtered_data):
            # หา original_row_idx ของแถวที่กำลังจะแสดงผล
            pk_values = tuple(row_data.get(pk) for pk in eds_instance.LOGICAL_PK_FIELDS)
            original_row_idx = pk_to_original_idx_map.get(pk_values, -1)

            if original_row_idx == -1:
                continue

            sequence_text = str(visual_row_idx + 1)
            sequence_item = QTableWidgetItem(sequence_text)
            sequence_item.setTextAlignment(Qt.AlignCenter)
            flags = sequence_item.flags()
            sequence_item.setFlags(flags & ~Qt.ItemIsEditable)
            sequence_item.setBackground(QColor("#f0f0f0"))
            eds_instance.results_table.setItem(visual_row_idx, 0, sequence_item)

            for db_field_idx, field_name in enumerate(displayed_db_fields):
                visual_col_idx = db_field_idx + 1
                
                edit_key = (original_row_idx, visual_col_idx)
                is_edited = edit_key in eds_instance.edited_items

                cell_value = row_data.get(field_name, "")
                item = QTableWidgetItem(str(cell_value))

                if field_name in ["FirstName", "LastName"]:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter)

                is_editable = not (
                    field_name in eds_instance.LOGICAL_PK_FIELDS
                    or field_name in eds_instance.NON_EDITABLE_FIELDS
                )

                if not is_editable:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setBackground(QColor("#f0f0f0"))
                elif is_edited:
                    # ถ้าเซลล์นี้มีการแก้ไข ให้ tô màuพื้นหลัง
                    item.setBackground(QColor("lightyellow"))
                
                eds_instance.results_table.setItem(visual_row_idx, visual_col_idx, item)

    eds_instance.results_table.itemChanged.connect(eds_instance.handle_item_changed)
    eds_instance.results_table.setUpdatesEnabled(True)
    
    if hasattr(eds_instance, "update_save_button_state"):
        eds_instance.update_save_button_state()
