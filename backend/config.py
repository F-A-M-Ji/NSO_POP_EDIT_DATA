# Database configuration
DB_CONFIG = {
    'host': '172.20.3.22',
    'port': 1433,
    'username': 'sa',
    'password': 'regdbadmin123@',
    'database': 'pop68T'
}


# import os
# import json

# CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".pop_edit_data_config.json")

# # ค่าเริ่มต้น
# DEFAULT_CONFIG = {
#     "host": "172.20.3.22",
#     "port": 1433,
#     "username": "sa",
#     "password": "regdbadmin123@",
#     "database": "pop68T",
# }

# def load_config():
#     """โหลดค่า config จากไฟล์หรือใช้ค่าเริ่มต้น"""
#     if os.path.exists(CONFIG_FILE):
#         try:
#             with open(CONFIG_FILE, "r") as f:
#                 return json.load(f)
#         except:
#             pass
#     return DEFAULT_CONFIG

# def save_config(config):
#     """บันทึกค่า config ลงไฟล์"""
#     try:
#         with open(CONFIG_FILE, "w") as f:
#             json.dump(config, f)
#         return True
#     except:
#         return False

# # โหลดค่าสำหรับใช้งาน
# DB_CONFIG = load_config()
