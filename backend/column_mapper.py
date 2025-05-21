import pandas as pd
import os
import re
from frontend.utils.resource_path import resource_path

class ColumnMapper:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ColumnMapper()
        return cls._instance

    def __init__(self):
        if ColumnMapper._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ColumnMapper._instance = self
            self.column_mappings = {}
            self.fields_to_show = []
            self.load_mappings()

    def load_mappings(self):
        """โหลดข้อมูลการแมปคอลัมน์จากไฟล์ Excel"""
        try:
            # excel_path = os.path.join(
            #     os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            #     "assets",
            #     "column_name.xlsx",
            # )
            excel_path = resource_path(os.path.join("assets", "column_name.xlsx"))

            # โหลดข้อมูลจากไฟล์ Excel
            column_df = pd.read_excel(excel_path)

            # เก็บรายชื่อฟิลด์ที่ต้องแสดง
            self.fields_to_show = column_df["Field_name"].tolist()

            # สร้าง dictionary สำหรับการแมประหว่าง Field_name และ Column_name
            for _, row in column_df.iterrows():
                self.column_mappings[row["Field_name"]] = row["Column_name"]

            return True
        except Exception as e:
            print(f"Failed to load column mappings: {str(e)}")
            return False

    def get_column_name(self, field_name):
        """ดึงชื่อคอลัมน์สำหรับแสดงผลจากชื่อฟิลด์ในฐานข้อมูล"""
        return self.column_mappings.get(field_name, field_name)

    def get_fields_to_show(self):
        """ดึงรายชื่อฟิลด์ที่ต้องการแสดง"""
        return self.fields_to_show

    def get_select_fields_sql(self):
        """สร้างส่วน SELECT ของคำสั่ง SQL"""
        return ", ".join(self.fields_to_show)

    def format_column_header(self, column_name):
        """แยกข้อความในวงเล็บและนอกวงเล็บ"""
        # ค้นหาข้อความในวงเล็บ
        paren_match = re.search(r"\(([^)]+)\)", column_name)

        if paren_match:
            # หากพบข้อความในวงเล็บ
            paren_text = f"({paren_match.group(1)})"
            main_text = column_name[: paren_match.start()].strip()
            return main_text, paren_text
        else:
            # หากไม่พบข้อความในวงเล็บ
            return column_name, ""
