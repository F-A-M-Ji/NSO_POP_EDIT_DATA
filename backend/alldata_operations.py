import pyodbc
import datetime
from functools import lru_cache

from backend.db import get_connection

RECORDS_PER_PAGE = 500  # จำนวนรายการต่อหน้า


def fetch_all_r_alldata_fields():
    """ดึงรายชื่อ column ทั้งหมดจากตาราง r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return []

        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'r_alldata_edit'
            ORDER BY ORDINAL_POSITION
        """
        )

        columns = [row[0] for row in cursor.fetchall()]
        connection.close()
        return columns

    except Exception as e:
        print(f"Error fetching all fields: {e}")
        return []

def count_search_r_alldata(conditions):
    """นับจำนวนผลลัพธ์ทั้งหมดตามเงื่อนไขการค้นหา"""
    try:
        connection = get_connection()
        if not connection:
            return 0, "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"

        cursor = connection.cursor()
        where_conditions, params = build_where_clause(conditions)
        
        query = "SELECT COUNT(*) FROM [r_alldata_edit]"
        if where_conditions:
            query += f" WHERE {where_conditions}"
        
        cursor.execute(query, params)
        total_records = cursor.fetchone()[0]
        
        connection.close()
        return total_records, None
    except Exception as e:
        error_msg = f"Error counting records: {str(e)}"
        return 0, error_msg


def search_r_alldata(conditions, all_db_fields, logical_pk_fields, page=1):
    """ค้นหาข้อมูลจากตาราง r_alldata_edit ตามเงื่อนไขที่กำหนดและรองรับ Pagination"""
    try:
        connection = get_connection()
        if not connection:
            return [], [], "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"

        cursor = connection.cursor()
        where_conditions, params = build_where_clause(conditions)

        base_query = f"SELECT * FROM [r_alldata_edit]"
        
        if where_conditions:
            query = f"{base_query} WHERE {where_conditions}"
        else:
            query = base_query

        order_by_clause = ""
        if logical_pk_fields:
            order_fields = [
                f"[{field}]"
                for field in logical_pk_fields
                if field in all_db_fields
            ]
            if order_fields:
                order_by_clause = f" ORDER BY {', '.join(order_fields)}"
        
        # SQL Server บังคับให้มี ORDER BY เมื่อใช้ OFFSET
        if not order_by_clause:
                 order_by_clause = " ORDER BY (SELECT NULL)" # Fallback order

        offset = (page - 1) * RECORDS_PER_PAGE
        
        query += f"{order_by_clause} OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, RECORDS_PER_PAGE])

        cursor.execute(query, params)
        results = cursor.fetchall()
        
        connection.close()
        return results, all_db_fields, None

    except Exception as e:
        error_msg = f"Error searching r_alldata_edit: {str(e)}"
        return [], [], error_msg

def build_where_clause(conditions):
    """Helper function to build WHERE clause and parameters from combined conditions."""
    where_conditions = []
    params = []
    
    for key, value in conditions.items():
        if value is None:
            continue

        if key.startswith("filter_"):
            # This is a header filter
            field_name = key[len("filter_"):]
            filter_info = value  # which is a dict like {"text": ..., "show_blank": ...}
            
            filter_text = filter_info.get("text", "").strip()
            show_blank = filter_info.get("show_blank", False)

            if show_blank:
                # If show blank is checked, this is the only condition for this column
                where_conditions.append(f"([{field_name}] IS NULL OR LTRIM(RTRIM([{field_name}])) = '')")
            elif filter_text:
                # Only if show_blank is false and there is text
                # Use LIKE for text filtering, cast to handle non-string columns
                where_conditions.append(f"CAST([{field_name}] AS NVARCHAR(MAX)) LIKE ?")
                params.append(f"%{filter_text}%")
            # If both are false, the filter is effectively cleared for this column, so do nothing

        else:
            # This is a top search bar filter
            converted_value = convert_to_native_type(value)
            if converted_value in [None, "", "blank"]:
                where_conditions.append(f"([{key}] IS NULL OR [{key}] = '' OR LTRIM(RTRIM([{key}])) = '')")
            else:
                where_conditions.append(f"[{key}] = ?")
                params.append(converted_value)

    return " AND ".join(where_conditions), params


def save_edited_r_alldata_rows(records_to_save, all_db_fields):
    """บันทึกข้อมูลที่แก้ไขลงในตาราง r_alldata_edit"""
    if not records_to_save:
        return 0, "ไม่มีข้อมูลที่จะบันทึก"

    try:
        connection = get_connection()
        if not connection:
            return 0, "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"

        cursor = connection.cursor()
        saved_count = 0

        for record in records_to_save:
            update_fields = []
            update_values = []
            where_conditions = []
            where_values = []

            pk_fields = [
                "EA_Code_15",
                "Building_No",
                "Household_No",
                "Population_No",
            ]

            for field_name, field_value in record.items():
                converted_value = convert_to_native_type(field_value)

                if field_name in pk_fields:
                    where_conditions.append(f"[{field_name}] = ?")
                    where_values.append(converted_value)
                elif field_name in all_db_fields:
                    update_fields.append(f"[{field_name}] = ?")
                    update_values.append(converted_value)

            if not where_conditions or not update_fields:
                continue

            query = f"""
                UPDATE [r_alldata_edit] 
                SET {', '.join(update_fields)} 
                WHERE {' AND '.join(where_conditions)}
            """

            cursor.execute(query, update_values + where_values)

            if cursor.rowcount > 0:
                saved_count += 1

        connection.commit()
        connection.close()

        return saved_count, None

    except Exception as e:
        error_msg = f"Error saving to r_alldata_edit: {str(e)}"
        return 0, error_msg


def convert_to_native_type(value):
    """แปลงค่า numpy types เป็น native Python types"""
    if value is None:
        return None

    if hasattr(value, "item"):
        return value.item()
    elif str(type(value)).startswith("<class 'numpy."):
        try:
            return value.item()
        except (AttributeError, ValueError):
            return str(value)
    else:
        return value


@lru_cache(maxsize=256)
def get_distinct_values(
    field_name, where_conditions=None, where_params=None, include_blank_separately=False
):
    """ดึงค่าที่ไม่ซ้ำจากฟิลด์ที่กำหนดในตาราง r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return []

        cursor = connection.cursor()

        base_query = f"""
            SELECT DISTINCT [{field_name}] 
            FROM [r_alldata_edit] 
        """

        if where_conditions:
            query = f"{base_query} WHERE {where_conditions}"
            converted_params = [
                convert_to_native_type(param) for param in (where_params or [])
            ]
            cursor.execute(query, converted_params)
        else:
            cursor.execute(base_query)

        results = cursor.fetchall()
        values = []
        has_blank = False

        for row in results:
            value = row[0]
            if value is None or str(value).strip() == "":
                has_blank = True
            else:
                converted_value = convert_to_native_type(value)
                clean_value = str(converted_value).strip()
                if clean_value and clean_value not in values:
                    values.append(clean_value)

        values.sort()

        if has_blank:
            values.append("")

        connection.close()
        return values

    except Exception as e:
        return []


@lru_cache(maxsize=1)
def get_area_name_mapping():
    """ดึงการเชื่อมโยง AreaCode กับ AreaName จากตาราง r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return {}

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT DISTINCT [AreaCode], [AreaName] 
            FROM [r_alldata_edit] 
            WHERE [AreaCode] IS NOT NULL OR [AreaName] IS NOT NULL
        """
        )

        mapping = {}
        results = cursor.fetchall()

        for row in results:
            area_code = convert_to_native_type(row[0])
            area_name = convert_to_native_type(row[1])

            code_key = "" if area_code is None else str(area_code).strip()
            name_value = "" if area_name is None else str(area_name).strip()

            mapping[code_key] = name_value

        if "" not in mapping:
            mapping[""] = ""
        if "1" not in mapping:
            mapping["1"] = "ในเขตเทศบาล"
        if "2" not in mapping:
            mapping["2"] = "นอกเขตเทศบาล"

        connection.close()
        return mapping

    except Exception as e:
        return {"": "", "1": "ในเขตเทศบาล", "2": "นอกเขตเทศบาล"}


@lru_cache(maxsize=1)
def get_regions_from_db():
    """ดึงข้อมูลภาคจากฐานข้อมูล r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return []

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT DISTINCT [RegCode], [RegName] 
            FROM [r_alldata_edit] 
            WHERE [RegCode] IS NOT NULL AND [RegName] IS NOT NULL
            ORDER BY [RegCode]
        """
        )

        results = cursor.fetchall()
        regions = []

        for row in results:
            reg_code = convert_to_native_type(row[0])
            reg_name = convert_to_native_type(row[1])

            if reg_code and reg_name:
                display_text = f"{reg_code} : {reg_name.strip()}"
                regions.append(
                    {
                        "code": str(reg_code).strip(),
                        "name": reg_name.strip(),
                        "display": display_text,
                    }
                )

        connection.close()
        return regions

    except Exception as e:
        print(f"Error getting regions from database: {e}")
        return []


@lru_cache(maxsize=32)
def get_provinces_from_db(reg_code=None):
    """ดึงข้อมูลจังหวัดจากฐานข้อมูล r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return []

        cursor = connection.cursor()

        base_query = """
            SELECT DISTINCT [ProvCode], [ProvName] 
            FROM [r_alldata_edit] 
            WHERE [ProvCode] IS NOT NULL AND [ProvName] IS NOT NULL
        """

        if reg_code:
            query = f"{base_query} AND [RegCode] = ? ORDER BY [ProvCode]"
            cursor.execute(query, [convert_to_native_type(reg_code)])
        else:
            query = f"{base_query} ORDER BY [ProvCode]"
            cursor.execute(query)

        results = cursor.fetchall()
        provinces = []

        for row in results:
            prov_code = convert_to_native_type(row[0])
            prov_name = convert_to_native_type(row[1])

            if prov_code and prov_name:
                display_text = f"{prov_code} : {prov_name.strip()}"
                provinces.append(
                    {
                        "code": str(prov_code).strip(),
                        "name": prov_name.strip(),
                        "display": display_text,
                    }
                )

        connection.close()
        return provinces

    except Exception as e:
        print(f"Error getting provinces from database: {e}")
        return []


@lru_cache(maxsize=128)
def get_districts_from_db(prov_code=None):
    """ดึงข้อมูลอำเภอ/เขตจากฐานข้อมูล r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return []

        cursor = connection.cursor()

        base_query = """
            SELECT DISTINCT [DistCode], [DistName] 
            FROM [r_alldata_edit] 
            WHERE [DistCode] IS NOT NULL AND [DistName] IS NOT NULL
        """

        if prov_code:
            query = f"{base_query} AND [ProvCode] = ? ORDER BY [DistCode]"
            cursor.execute(query, [convert_to_native_type(prov_code)])
        else:
            query = f"{base_query} ORDER BY [DistCode]"
            cursor.execute(query)

        results = cursor.fetchall()
        districts = []

        for row in results:
            dist_code = convert_to_native_type(row[0])
            dist_name = convert_to_native_type(row[1])

            if dist_code and dist_name:
                display_text = f"{dist_code} : {dist_name.strip()}"
                districts.append(
                    {
                        "code": str(dist_code).strip(),
                        "name": dist_name.strip(),
                        "display": display_text,
                    }
                )

        connection.close()
        return districts

    except Exception as e:
        print(f"Error getting districts from database: {e}")
        return []


@lru_cache(maxsize=256)
def get_subdistricts_from_db(dist_code=None, prov_code=None):
    """ดึงข้อมูลตำบล/แขวงจากฐานข้อมูล r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return []

        cursor = connection.cursor()

        base_query = """
            SELECT DISTINCT [SubDistCode], [SubDistName] 
            FROM [r_alldata_edit] 
            WHERE [SubDistCode] IS NOT NULL AND [SubDistName] IS NOT NULL
        """

        params = []
        conditions = []

        if prov_code:
            conditions.append("[ProvCode] = ?")
            params.append(convert_to_native_type(prov_code))

        if dist_code:
            conditions.append("[DistCode] = ?")
            params.append(convert_to_native_type(dist_code))

        if conditions:
            query = f"{base_query} AND {' AND '.join(conditions)} ORDER BY [SubDistCode]"
            cursor.execute(query, params)
        else:
            query = f"{base_query} ORDER BY [SubDistCode]"
            cursor.execute(query)

        results = cursor.fetchall()
        subdistricts = []

        for row in results:
            subdist_code = convert_to_native_type(row[0])
            subdist_name = convert_to_native_type(row[1])

            if subdist_code and subdist_name:
                display_text = f"{subdist_code} : {subdist_name.strip()}"
                subdistricts.append(
                    {
                        "code": str(subdist_code).strip(),
                        "name": subdist_name.strip(),
                        "display": display_text,
                    }
                )

        connection.close()
        return subdistricts

    except Exception as e:
        print(f"Error getting subdistricts from database: {e}")
        return []
