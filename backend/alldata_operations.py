import pyodbc
import datetime

from backend.db import get_connection


def fetch_all_r_alldata_fields():
    """ดึงรายชื่อ column ทั้งหมดจากตาราง r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'r_alldata_edit'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = [row[0] for row in cursor.fetchall()]
        connection.close()
        return columns
        
    except Exception as e:
        return []


def search_r_alldata(location_codes, all_db_fields, logical_pk_fields):
    """ค้นหาข้อมูลจากตาราง r_alldata_edit ตามเงื่อนไขที่กำหนด"""
    try:
        connection = get_connection()
        if not connection:
            return [], [], "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"
        
        cursor = connection.cursor()
        
        where_conditions = []
        params = []
        
        for key, value in location_codes.items():
            if value is not None:
                converted_value = convert_to_native_type(value)
                
                if converted_value is None or converted_value == "" or converted_value == "blank":
                    where_conditions.append(f"([{key}] IS NULL OR [{key}] = '' OR LTRIM(RTRIM([{key}])) = '')")
                else:
                    where_conditions.append(f"[{key}] = ?")
                    params.append(converted_value)
        
        base_query = f"SELECT * FROM [r_alldata_edit]"
        
        if where_conditions:
            query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
        else:
            query = base_query
        
        if logical_pk_fields:
            order_fields = [f"[{field}]" for field in logical_pk_fields if field in all_db_fields]
            if order_fields:
                query += f" ORDER BY {', '.join(order_fields)}"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        connection.close()
        return results, all_db_fields, None
        
    except Exception as e:
        error_msg = f"Error searching r_alldata_edit: {str(e)}"
        return [], [], error_msg



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
            
            pk_fields = ["EA_Code_15", "Building_No", "Household_No", "Population_No"]
            
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
    
    if hasattr(value, 'item'):
        return value.item()
    elif str(type(value)).startswith('<class \'numpy.'):
        try:
            return value.item()
        except (AttributeError, ValueError):
            return str(value)
    else:
        return value


def get_distinct_values(field_name, where_conditions=None, where_params=None, include_blank_separately=False):
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
            converted_params = [convert_to_native_type(param) for param in (where_params or [])]
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


def get_area_name_mapping():
    """ดึงการเชื่อมโยง AreaCode กับ AreaName จากตาราง r_alldata_edit"""
    try:
        connection = get_connection()
        if not connection:
            return {}
        
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT DISTINCT [AreaCode], [AreaName] 
            FROM [r_alldata_edit] 
            WHERE [AreaCode] IS NOT NULL OR [AreaName] IS NOT NULL
        """)
        
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