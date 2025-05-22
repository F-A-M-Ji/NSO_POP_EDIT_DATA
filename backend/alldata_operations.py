import pyodbc
import datetime

from .db import get_connection

def fetch_all_r_alldata_fields():
    """Fetches all column names from r_alldata to know the complete structure."""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            print("Database Error: Cannot get r_alldata fields: No connection.")
            return []
        with conn.cursor() as cursor:
            cursor.execute("SELECT TOP 0 * FROM r_alldata")
            return [col[0] for col in cursor.description]
    except pyodbc.Error as e:
        print(f"Database Error: Error fetching r_alldata schema: {e}")
        return []
    finally:
        if conn:
            conn.close()

def search_r_alldata(codes, all_db_fields_r_alldata, logical_pk_fields):
    """
    Searches data from r_alldata and r_alldata_edit based on provided codes.
    """
    sql_conditions = []
    params = []
    if codes["RegCode"] is not None: sql_conditions.append("ra.RegCode = ?"); params.append(codes["RegCode"])
    if codes["ProvCode"] is not None: sql_conditions.append("ra.ProvCode = ?"); params.append(codes["ProvCode"])
    if codes["DistCode"] is not None: sql_conditions.append("ra.DistCode = ?"); params.append(codes["DistCode"])
    if codes["SubDistCode"] is not None: sql_conditions.append("ra.SubDistCode = ?"); params.append(codes["SubDistCode"])

    if not sql_conditions:
        return [], [], "No search criteria provided."

    select_clauses = []
    for field in all_db_fields_r_alldata:
        quoted_field = f"[{field}]"
        select_clauses.append(f"COALESCE(le.{quoted_field}, ra.{quoted_field}) AS {quoted_field}")
    select_sql_part = ", ".join(select_clauses)
    
    pk_join_condition = " AND ".join([f"ra.[{pk_f}] = le.[{pk_f}]" for pk_f in logical_pk_fields])
    pk_partition_by = ", ".join([f"[{pk_f}]" for pk_f in logical_pk_fields])

    query = f"""
    WITH LatestEdits AS (
        SELECT *, ROW_NUMBER() OVER(PARTITION BY {pk_partition_by} ORDER BY time_edit DESC) as rn
        FROM r_alldata_edit
    )
    SELECT {select_sql_part}
    FROM r_alldata ra
    LEFT JOIN LatestEdits le ON {pk_join_condition} AND le.rn = 1
    """
    
    if sql_conditions:
        query += " WHERE " + " AND ".join(sql_conditions)
    query += " ORDER BY ra.RegName, ra.ProvName, ra.DistName, ra.SubDistName"

    conn = None
    try:
        conn = get_connection()
        if not conn:
            return [], [], "Cannot connect to the database."
        
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            db_column_names = [col[0] for col in cursor.description]
            return results, db_column_names, None # No error
            
    except pyodbc.Error as e:
        return [], [], f"Error during search: {e}"
    finally:
        if conn:
            conn.close()

def save_edited_r_alldata_rows(list_of_data_to_save_dicts, all_db_fields_r_alldata):
    """
    Saves multiple edited rows to the r_alldata_edit table.
    Each dictionary in list_of_data_to_save_dicts should be a complete record
    for one row to be inserted, including 'fullname' and 'time_edit'.
    """
    conn = None
    saved_rows_count = 0
    
    if not list_of_data_to_save_dicts:
        return 0, "No data provided to save."

    r_alldata_edit_columns = all_db_fields_r_alldata + ["fullname", "time_edit"]
    cols_for_sql = ", ".join([f"[{col}]" for col in r_alldata_edit_columns])
    placeholders = ", ".join(["?"] * len(r_alldata_edit_columns))
    sql_insert = f"INSERT INTO r_alldata_edit ({cols_for_sql}) VALUES ({placeholders})"

    try:
        conn = get_connection()
        if not conn:
            return 0, "Database connection failed for saving."

        with conn.cursor() as cursor:
            for data_to_save in list_of_data_to_save_dicts:
                values_for_insert = []
                for col_name in r_alldata_edit_columns:
                    values_for_insert.append(data_to_save.get(col_name))
                
                cursor.execute(sql_insert, values_for_insert)
                saved_rows_count += 1
        
        if saved_rows_count > 0:
            conn.commit()
            return saved_rows_count, None # Success
        else:
            return 0, "No rows were actually processed for saving."

    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        return 0, f"Database error during save: {e}"
    except Exception as ex:
        if conn:
            conn.rollback()
        return 0, f"General error during save: {ex}"
    finally:
        if conn:
            conn.close()