import pyodbc
import datetime

from .db import get_connection


def fetch_all_r_alldata_fields():
    """Fetches all column names from r_alldata to know the complete structure."""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            # print("Database Error: Cannot get r_alldata fields: No connection.")
            return []
        with conn.cursor() as cursor:
            cursor.execute("SELECT TOP 0 * FROM r_alldata")
            return [col[0] for col in cursor.description]
    except pyodbc.Error as e:
        # print(f"Database Error: Error fetching r_alldata schema: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_r_alldata(codes, all_db_fields_r_alldata, logical_pk_fields):
    """
    Searches data from r_alldata_edit table only based on provided codes.
    """
    sql_conditions = []
    params = []

    if codes.get("RegCode") is not None:
        if codes["RegCode"] == 0:
            sql_conditions.append(
                "(rae.RegCode = ? AND rae.RegCode IS NOT NULL AND rae.RegCode <> '')"
            )
        else:
            sql_conditions.append("rae.RegCode = ?")
        params.append(codes["RegCode"])

    if codes["ProvCode"] is not None:
        sql_conditions.append("rae.ProvCode = ?")
        params.append(codes["ProvCode"])

    if codes["DistCode"] is not None:
        sql_conditions.append("rae.DistCode = ?")
        params.append(codes["DistCode"])

    if codes["SubDistCode"] is not None:
        sql_conditions.append("rae.SubDistCode = ?")
        params.append(codes["SubDistCode"])

    if not sql_conditions:
        return [], [], "No search criteria provided."

    # เปลี่ยนให้ดึงจาก r_alldata_edit เท่านั้น
    select_clauses = []
    for field in all_db_fields_r_alldata:
        quoted_field = f"[{field}]"
        select_clauses.append(f"rae.{quoted_field}")

    # เพิ่ม fullname และ time_edit
    select_clauses.append("rae.fullname")
    select_clauses.append("rae.time_edit")

    select_sql_part = ", ".join(select_clauses)

    query = f"""
    SELECT {select_sql_part}
    FROM r_alldata_edit rae
    """

    if sql_conditions:
        query += " WHERE " + " AND ".join(sql_conditions)
    query += " ORDER BY rae.RegName, rae.ProvName, rae.DistName, rae.SubDistName"

    conn = None
    try:
        conn = get_connection()
        if not conn:
            return [], [], "Cannot connect to the database."

        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            db_column_names = [col[0] for col in cursor.description]
            return results, db_column_names, None

    except pyodbc.Error as e:
        return [], [], f"Error during search: {e}"
    finally:
        if conn:
            conn.close()


def save_edited_r_alldata_rows(list_of_data_to_save_dicts, all_db_fields_r_alldata):
    """
    Updates multiple edited rows in the r_alldata_edit table.
    Each dictionary in list_of_data_to_save_dicts should be a complete record
    for one row to be updated, including 'fullname' and 'time_edit'.
    """
    conn = None
    updated_rows_count = 0

    LOGICAL_PK_FIELDS = ["EA_Code_15", "Building_No", "Household_No", "Population_No"]

    if not list_of_data_to_save_dicts:
        return 0, "No data provided to save."

    # เตรียม field สำหรับ UPDATE (ไม่รวม PK)
    update_fields = [
        col for col in all_db_fields_r_alldata if col not in LOGICAL_PK_FIELDS
    ]
    update_fields += ["fullname", "time_edit"]

    set_clause = ", ".join([f"[{field}] = ?" for field in update_fields])
    where_clause = " AND ".join([f"[{pk}] = ?" for pk in LOGICAL_PK_FIELDS])

    sql_update = f"UPDATE r_alldata_edit SET {set_clause} WHERE {where_clause}"

    try:
        conn = get_connection()
        if not conn:
            return 0, "Database connection failed for updating."

        with conn.cursor() as cursor:
            for data_to_save in list_of_data_to_save_dicts:
                update_values = [data_to_save.get(field) for field in update_fields]
                pk_values = [data_to_save.get(pk) for pk in LOGICAL_PK_FIELDS]
                all_values = update_values + pk_values
                cursor.execute(sql_update, all_values)
                updated_rows_count += cursor.rowcount

        if updated_rows_count > 0:
            conn.commit()
            return updated_rows_count, None
        else:
            return 0, "No rows were actually updated."

    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        return 0, f"Database error during update: {e}"
    except Exception as ex:
        if conn:
            conn.rollback()
        return 0, f"General error during update: {ex}"
    finally:
        if conn:
            conn.close()
