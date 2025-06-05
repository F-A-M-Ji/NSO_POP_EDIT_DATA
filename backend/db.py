import pyodbc
from .config import DB_CONFIG

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
            conn = pyodbc.connect(conn_str)
            return conn
        except pyodbc.Error as e:
            continue
    
    return None
