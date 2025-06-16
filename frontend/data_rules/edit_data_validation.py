import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from frontend.utils.resource_path import resource_path

_validation_data_cache = None

def load_validation_data_from_excel(screen_instance):
    global _validation_data_cache
    if _validation_data_cache is not None:
        return _validation_data_cache

    validation_data = {}
    default_values = {
        "LanguageOther": [f"{i:02d}" for i in range(2, 81)] + ["99"],
        "NationalityNumeric": [f"{i:03d}" for i in range(4, 910)] + ["000", "910", "920", "930", "940", "990", "997", "998", "999"],
        "MovedFromAbroad": [f"{i:03d}" for i in range(0, 1000)],
    }
    for key, default_val in default_values.items():
        validation_data[key] = list(default_val)

    def _load_codes_from_excel_util(file_key, file_name, column_name):
        try:
            file_path = resource_path(os.path.join("assets", file_name))
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
                if column_name in df.columns:
                    loaded_codes = [str(c).strip() for c in df[column_name].dropna().tolist() if str(c).strip()]
                    if loaded_codes:
                        if file_key == "NationalityNumeric":
                            special_nationality_codes = default_values["NationalityNumeric"]
                            validation_data[file_key] = list(set(loaded_codes + special_nationality_codes))
                        else:
                            validation_data[file_key] = list(set(loaded_codes))
        except Exception as e:
            print(f"Error loading Excel for {file_key} from {file_name}: {e}")

    _load_codes_from_excel_util("LanguageOther", "language_other.xlsx", "LanguageOther_Code")
    _load_codes_from_excel_util("NationalityNumeric", "nationality.xlsx", "Nationality_Code_Numeric-3")
    _load_codes_from_excel_util("MovedFromAbroad", "country.xlsx", "Countries_Code_Num-3")

    _validation_data_cache = validation_data
    return validation_data

def validate_field_value(screen_instance, field_name, value, row_number):
    if field_name not in screen_instance.FIELD_VALIDATION_RULES:
        return None
    rule = screen_instance.FIELD_VALIDATION_RULES[field_name]
    field_display_name = screen_instance.column_mapper.get_column_name(field_name)
    value_str = str(value).strip() if value is not None else ""

    if not value_str:
        return None if rule.get("allow_blank", True) else f"แถว {row_number}, คอลัมน์ '{field_display_name}': ไม่สามารถเป็นค่าว่างได้"

    validation_type = rule.get("type", "text")
    validators = {
        "text": _validate_text, "options": _validate_options, "range": _validate_range,
        "custom": _validate_custom, "int_range": _validate_int_range,
        "padded_number": _validate_padded_number, "excel_padded_number": _validate_excel_padded_number,
    }
    validator_func = validators.get(validation_type)
    if validator_func:
        return validator_func(field_name, value_str, rule, field_display_name, row_number)
    return None

def _validate_excel_padded_number(field_name, value_str, rule, field_display_name, row_number):
    length = rule.get("length", 3)
    allowed_values = rule.get("allowed_values", [])
    if len(value_str) != length:
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องมีความยาว {length} หลัก"
    if not value_str.isdigit():
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลขเท่านั้น"
    if value_str not in allowed_values:
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
    return None

def _validate_text(field_name, value_str, rule, field_display_name, row_number):
    max_length = rule.get("max_length")
    if max_length and len(value_str) > max_length:
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ความยาวเกิน {max_length} ตัวอักษร (ปัจจุบัน: {len(value_str)})"
    return None

def _validate_options(field_name, value_str, rule, field_display_name, row_number):
    if value_str not in rule.get("allowed_values", []):
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
    return None

def _validate_range(field_name, value_str, rule, field_display_name, row_number):
    if value_str not in rule.get("allowed_values", []):
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
    return None

def _validate_custom(field_name, value_str, rule, field_display_name, row_number):
    if value_str not in rule.get("allowed_values", []):
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
    return None

def _validate_int_range(field_name, value_str, rule, field_display_name, row_number):
    try:
        int_value = int(value_str)
        min_value = rule.get("min_value", -float("inf"))
        max_value = rule.get("max_value", float("inf"))
        if not (min_value <= int_value <= max_value):
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
    except ValueError:
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลข"
    return None

def _validate_padded_number(field_name, value_str, rule, field_display_name, row_number):
    length = rule.get("length", 4)
    min_value = rule.get("min_value", 0)
    max_value = rule.get("max_value", int("9" * length) if length > 0 else 0)
    if len(value_str) != length:
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องมีความยาว {length} หลัก"
    if not value_str.isdigit():
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลขเท่านั้น"
    try:
        int_value = int(value_str)
        if not (min_value <= int_value <= max_value):
            return f"แถว {row_number}, คอลัมน์ '{field_display_name}': {rule.get('description', 'ค่าไม่ถูกต้อง')}"
    except ValueError:
        return f"แถว {row_number}, คอลัมน์ '{field_display_name}': ต้องเป็นตัวเลข"
    return None

def validate_edited_data(screen_instance):
    """ตรวจสอบข้อมูลที่แก้ไขทั้งหมดก่อนบันทึก โดยใช้โครงสร้าง edited_items แบบใหม่"""
    validation_errors = []
    
    # สร้าง map จาก PK ไปยัง visual row index เพื่อใช้ในข้อความ error
    current_view_data = (
        screen_instance.filtered_data_cache if screen_instance.active_filters
        else screen_instance.original_data_cache
    )
    pk_to_visual_row_map = {
        tuple(row.get(pk) for pk in screen_instance.LOGICAL_PK_FIELDS): i + 1
        for i, row in enumerate(current_view_data)
    }

    for pk_tuple, edit_info in screen_instance.edited_items.items():
        # หากแถวที่แก้ไขไม่ได้อยู่ในหน้าปัจจุบัน ให้ใช้ '?' เป็นเลขแถว
        visual_row_number = pk_to_visual_row_map.get(pk_tuple, "?")
        
        for field_name, new_value in edit_info['edits'].items():
            error = validate_field_value(screen_instance, field_name, new_value, visual_row_number)
            if error:
                validation_errors.append(error)
                
    return validation_errors

class CustomMessageBox(QDialog):
    def __init__(self, parent=None, title="Message", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QVBoxLayout(self)
        self.label = QLabel(message)
        self.label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.label)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        self.setMinimumWidth(400)

def show_validation_errors(screen_instance, errors):
    if not errors: return
    max_errors_to_show = 20
    errors_to_show = errors[:max_errors_to_show]
    error_message = "พบข้อผิดพลาดในข้อมูลที่แก้ไข:\n\n" + "\n".join(
        [f"{i}. {error}" for i, error in enumerate(errors_to_show, 1)]
    )
    if len(errors) > max_errors_to_show:
        error_message += f"\n\n... และอีก {len(errors) - max_errors_to_show} ข้อผิดพลาด"
    error_message += "\n\nกรุณาแก้ไขข้อมูลให้ถูกต้องก่อนบันทึก"
    dialog = CustomMessageBox(screen_instance, "ข้อมูลไม่ถูกต้อง", error_message)
    dialog.exec_()
