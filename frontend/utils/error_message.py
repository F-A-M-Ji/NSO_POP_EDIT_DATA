from PyQt5.QtWidgets import (QMessageBox)


def show_error_message(parent, title, message):
    """Show an error message box."""
    QMessageBox.critical(parent, title, message)


def show_info_message(parent, title, message):
    """Show an information message box."""
    QMessageBox.information(parent, title, message)