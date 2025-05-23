# import pyodbc
# from .config import DB_CONFIG

# def get_connection():
#     """Create and return a connection to the database."""
#     conn_str = (
#         f"DRIVER={{ODBC Driver 18 for SQL Server}};"
#         f"SERVER={DB_CONFIG['host']},{DB_CONFIG['port']};"
#         f"DATABASE={DB_CONFIG['database']};"
#         f"UID={DB_CONFIG['username']};"
#         f"PWD={DB_CONFIG['password']};"
#     )
    
#     try:
#         conn = pyodbc.connect(conn_str)
#         return conn
#     except pyodbc.Error as e:
#         print(f"Database connection error: {e}")
#         return None



import pyodbc
from .config import DB_CONFIG

# รายการไดรเวอร์ที่อาจมีในระบบต่างๆ
POSSIBLE_DRIVERS = [
    "ODBC Driver 18 for SQL Server", 
    "ODBC Driver 17 for SQL Server",
    "ODBC Driver 13 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server"
]

def get_connection():
    """เชื่อมต่อกับฐานข้อมูลโดยลองหลายไดรเวอร์"""
    host = DB_CONFIG['host']
    port = DB_CONFIG['port']
    database = DB_CONFIG['database']
    username = DB_CONFIG['username']
    password = DB_CONFIG['password']
    
    # ลองใช้ไดรเวอร์ทีละตัวจนกว่าจะเชื่อมต่อได้
    for driver in POSSIBLE_DRIVERS:
        try:
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={host},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Connection Timeout=5;"
            )
            # print(f"Trying to connect with driver: {driver}")
            conn = pyodbc.connect(conn_str)
            # print(f"Successfully connected with driver: {driver}")
            return conn
        except pyodbc.Error as e:
            # print(f"Failed to connect with driver {driver}: {e}")
            continue
    
    # ถ้าไม่สามารถเชื่อมต่อได้ด้วยไดรเวอร์ใดๆ
    # print("All connection attempts failed")
    return None
