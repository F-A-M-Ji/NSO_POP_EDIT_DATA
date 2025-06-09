from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton,
    QScrollArea, QWidget, QFrame
)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt, pyqtSignal

class ColumnSelectorPopup(QDialog):
    """
    A dialog window that allows users to select which columns to display in a table.
    Includes "Select All / Deselect All" functionality and horizontal scrolling for long names.
    """
    visibility_changed = pyqtSignal(list)

    def __init__(self, all_columns, visible_columns, parent=None):
        """
        Initializes the popup.
        Args:
            all_columns (list): A list of tuples, where each tuple contains
                                (field_name, display_name) for all possible columns.
            visible_columns (list): A list of field_names that are currently visible.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("เลือกคอลัมน์ที่จะแสดง")
        # --- CHANGE START: Increased width and added max height ---
        self.setMinimumWidth(550) 
        self.setMaximumHeight(700)
        # --- CHANGE END ---
        self.all_columns = all_columns
        self.visible_columns = set(visible_columns)
        self.checkboxes = []
        self.setup_ui()
        self.update_select_all_state()

    def setup_ui(self):
        """Sets up the user interface of the dialog."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Scroll Area for the list of checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # --- CHANGE START: Enabled horizontal scrollbar ---
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # --- CHANGE END ---
        
        container_widget = QWidget()
        self.checkbox_layout = QVBoxLayout(container_widget)
        self.checkbox_layout.setSpacing(8)
        self.checkbox_layout.setAlignment(Qt.AlignTop)

        # Determine the maximum width needed for the labels
        max_width = 0
        fm = QFontMetrics(self.font())
        for _, display_name in self.all_columns:
            # Add some padding to the width calculation
            width = fm.horizontalAdvance(display_name) + 40 
            if width > max_width:
                max_width = width

        # Create a checkbox for each column
        for field_name, display_name in self.all_columns:
            # --- CHANGE START: Removed text shortening ---
            checkbox = QCheckBox(display_name)
            # --- CHANGE END ---
            checkbox.setToolTip(f"{display_name}\n(Field: {field_name})")
            checkbox.setProperty("field_name", field_name)
            checkbox.setChecked(field_name in self.visible_columns)
            checkbox.stateChanged.connect(self.update_select_all_state)
            self.checkboxes.append(checkbox)
            self.checkbox_layout.addWidget(checkbox)
        
        # Set the minimum width of the container to ensure horizontal scrollbar appears
        container_widget.setMinimumWidth(max_width)
            
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)

        # Separator Line for better visual structure
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Bottom controls layout (Select All, OK, Cancel)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        
        self.select_all_checkbox = QCheckBox("เลือกทั้งหมด / ยกเลิกทั้งหมด")
        self.select_all_checkbox.setTristate(True)
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_toggled)
        bottom_layout.addWidget(self.select_all_checkbox)

        bottom_layout.addStretch()
        
        self.ok_button = QPushButton("ตกลง")
        self.ok_button.setObjectName("primaryButton")
        self.ok_button.clicked.connect(self.apply_changes)
        
        self.cancel_button = QPushButton("ยกเลิก")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(bottom_layout)
        main_layout.addLayout(button_layout)

    def on_select_all_toggled(self, state):
        """
        Handles the state change of the 'Select All' checkbox.
        This will check or uncheck all column checkboxes.
        """
        if state == Qt.PartiallyChecked:
            return

        for cb in self.checkboxes:
            cb.blockSignals(True)

        is_checked = (state == Qt.Checked)
        for checkbox in self.checkboxes:
            checkbox.setChecked(is_checked)

        for cb in self.checkboxes:
            cb.blockSignals(False)

    def update_select_all_state(self):
        """
        Updates the 'Select All' checkbox based on the state of individual column checkboxes.
        """
        self.select_all_checkbox.blockSignals(True)

        checked_count = sum(1 for cb in self.checkboxes if cb.isChecked())
        
        if checked_count == 0:
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif checked_count == len(self.checkboxes):
            self.select_all_checkbox.setCheckState(Qt.Checked)
        else:
            self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        
        self.select_all_checkbox.blockSignals(False)

    def apply_changes(self):
        """
        Gathers the list of visible columns and emits a signal before closing.
        """
        new_visible_fields = [
            cb.property("field_name") for cb in self.checkboxes if cb.isChecked()
        ]
        self.visibility_changed.emit(new_visible_fields)
        self.accept()
