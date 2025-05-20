import pandas as pd
import os

class LocationData:
    _instance = None
    _data = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = LocationData()
        return cls._instance
    
    def __init__(self):
        if LocationData._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            LocationData._instance = self
            self.load_data()
    
    def load_data(self):
        try:
            # Get the path to the Excel file
            excel_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets", "reg_prov.xlsx"
            )
            
            # Load the Excel file
            LocationData._data = pd.read_excel(excel_path, sheet_name="รหัสเขตการปกครอง")
            return True
        except Exception as e:
            print(f"Error loading location data: {str(e)}")
            return False
    
    def get_data(self):
        return LocationData._data
    
    def get_regions(self):
        if LocationData._data is None:
            return []
        return sorted(LocationData._data["RegName"].unique())
    
    def get_provinces(self, region_name=None):
        if LocationData._data is None:
            return []
            
        if region_name:
            filtered = LocationData._data[LocationData._data["RegName"] == region_name]
            return sorted(filtered["ProvName"].unique())
        else:
            return sorted(LocationData._data["ProvName"].unique())
    
    def get_districts(self, region_name=None, province_name=None):
        if LocationData._data is None:
            return []
            
        filtered = LocationData._data
        if region_name:
            filtered = filtered[filtered["RegName"] == region_name]
        if province_name:
            filtered = filtered[filtered["ProvName"] == province_name]
            
        return sorted(filtered["DistName"].unique())
    
    def get_subdistricts(self, region_name=None, province_name=None, district_name=None):
        if LocationData._data is None:
            return []
            
        filtered = LocationData._data
        if region_name:
            filtered = filtered[filtered["RegName"] == region_name]
        if province_name:
            filtered = filtered[filtered["ProvName"] == province_name]
        if district_name:
            filtered = filtered[filtered["DistName"] == district_name]
            
        return sorted(filtered["SubDistName"].unique())
    
    def get_code(self, name_type, name, region_name=None, province_name=None, district_name=None):
        if LocationData._data is None:
            return None
            
        filtered = LocationData._data
        if region_name and name_type != "RegCode":
            filtered = filtered[filtered["RegName"] == region_name]
        if province_name and name_type != "ProvCode":
            filtered = filtered[filtered["ProvName"] == province_name]
        if district_name and name_type != "DistCode":
            filtered = filtered[filtered["DistName"] == district_name]
            
        name_to_code = {
            "RegCode": ("RegName", name),
            "ProvCode": ("ProvName", name),
            "DistCode": ("DistName", name),
            "SubDistCode": ("SubDistName", name)
        }
        
        if name_type in name_to_code:
            name_field, value = name_to_code[name_type]
            result = filtered[filtered[name_field] == value]
            if not result.empty:
                return result[name_type].iloc[0]
                
        return None
