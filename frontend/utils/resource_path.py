import os
import sys

def resource_path(relative_path):
    """รับพาธสัมบูรณ์ที่ใช้ได้ทั้งในโหมดพัฒนาและ PyInstaller"""
    try:
        # PyInstaller สร้างโฟลเดอร์ชั่วคราวและเก็บพาธใน _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)