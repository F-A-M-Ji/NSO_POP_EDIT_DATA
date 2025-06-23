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

def apply_table_filter(eds_instance, column, text, show_blank_only):
    """
    Updates the active filters and triggers a database re-query.
    """
    if text or show_blank_only:
        eds_instance.active_filters[column] = {
            "text": text,  # Keep original case for backend
            "show_blank": show_blank_only,
        }
    else:
        if column in eds_instance.active_filters:
            del eds_instance.active_filters[column]

    # Reset to the first page and re-execute the search
    eds_instance.current_page = 1
    # This method now handles DB query and display refresh
    eds_instance.execute_search_and_update_view()


def clear_table_filter(eds_instance, column):
    """
    Clears a specific column's filter and triggers a database re-query.
    """
    if column in eds_instance.active_filters:
        del eds_instance.active_filters[column]
    
    # Reset to the first page and re-execute the search
    eds_instance.current_page = 1
    eds_instance.execute_search_and_update_view()

# The old filter_table_data and display_filtered_results are no longer needed
# as filtering is now done server-side (database query).
# They can be safely removed from this file.
def filter_table_data(eds_instance):
    pass

def display_filtered_results(eds_instance, filtered_data):
    pass
