LOGICAL_PK_FIELDS_CONFIG = [
    "EA_Code_15",
    "Building_No",
    "Household_No",
    "Population_No",
]

NON_EDITABLE_FIELDS_CONFIG = ["FirstName", "LastName", "HouseholdMemberNumber"]

FIELD_VALIDATION_RULES_CONFIG = {
    "BuildingType": {
        "type": "range",
        "allowed_values": [f"{i:02d}" for i in range(1, 20)],  # 01-19
        "allow_blank": False,
        "description": "ต้องเป็น 01-19",
    },
    "BuildingTypeOther": {
        "type": "text",
        "max_length": 50,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
    },
    "Residing": {
        "type": "options",
        "allowed_values": ["1", "2"],
        "allow_blank": False,
        "description": "ต้องเป็น 1 หรือ 2",
    },
    "HouseholdEnumeration": {
        "type": "custom",
        "allowed_values": ["11", "12", "13", "20", "21", "22", "23"],
        "allow_blank": True,
        "description": "ต้องเป็น 11-13 หรือ 20-23",
    },
    "HouseholdEnumerationOther": {
        "type": "text",
        "max_length": 255,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 255 ตัวอักษร",
    },
    "HouseholdType": {
        "type": "range",
        "allowed_values": ["1", "2", "3"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-3",
    },
    "NumberOfHousehold": {
        "type": "int_range",
        "min_value": 1,
        "max_value": 99,
        "allow_blank": True,
        "description": "ต้องเป็นตัวเลข 1-99",
    },
    "TotalRoom": {
        "type": "padded_number",
        "length": 4,
        "min_value": 1,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็น 0001-9999",
    },
    "RoomVacant": {
        "type": "padded_number",
        "length": 4,
        "min_value": 1,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็น 0001-9999",
    },
    "RoomResidence": {
        "type": "padded_number",
        "length": 4,
        "min_value": 1,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็น 0001-9999",
    },
    "Language": {
        "type": "custom",
        "allowed_values": ["1", "2", "3", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-3 หรือ 9",
    },
    # "LanguageOther": {
    #     "type": "custom",
    #     "allowed_values": [f"{i:02d}" for i in range(2, 81)] + ["99"],
    #     "allow_blank": True,
    #     "description": "ต้องเป็น 02-80 หรือ 99",
    # },
    "HouseholdNumber": {
        "type": "padded_number",
        "length": 4,
        "min_value": 1,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็น 0001-9999",
    },
    "ConstructionMaterial": {
        "type": "range",
        "allowed_values": ["1", "2", "3", "4", "5", "6"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-6",
    },
    "ConstructionMaterialOther": {
        "type": "text",
        "max_length": 50,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
    },
    "TenureResidence": {
        "type": "range",
        "allowed_values": ["1", "2", "3", "4", "5", "6", "7"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-7",
    },
    "TenureResidenceOther": {
        "type": "text",
        "max_length": 30,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 30 ตัวอักษร",
    },
    "TenureLand": {
        "type": "range",
        "allowed_values": ["1", "2", "3", "4", "5"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-5",
    },
    "TenureLandOther": {
        "type": "text",
        "max_length": 255,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 255 ตัวอักษร",
    },
    "NumberOfHousueholdMember": {
        "type": "int_range",
        "min_value": 1,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็นตัวเลข 1-9999",
    },
    "HouseholdMemberNumber": {
        "type": "padded_number",
        "length": 5,
        "min_value": 1,
        "max_value": 99998,
        "allow_blank": True,
        "description": "ต้องเป็น 00001-99998",
    },
    "Title": {
        "type": "custom",
        "allowed_values": ["01", "02", "03", "04", "05", "09"],
        "allow_blank": True,
        "description": "ต้องเป็น 01-05 หรือ 09",
    },
    "TitleOther": {
        "type": "text",
        "max_length": 50,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
    },
    "Relationship": {
        "type": "range",
        "allowed_values": [f"{i:02d}" for i in range(0, 17)],  # 00-16
        "allow_blank": True,
        "description": "ต้องเป็น 00-16",
    },
    "Sex": {
        "type": "options",
        "allowed_values": ["1", "2"],
        "allow_blank": True,
        "description": "ต้องเป็น 1 หรือ 2",
    },
    "MonthOfBirth": {
        "type": "custom",
        "allowed_values": [f"{i:02d}" for i in range(1, 13)] + ["99"],
        "allow_blank": True,
        "description": "ต้องเป็น 01-12 หรือ 99",
    },
    "YearOfBirth": {
        "type": "custom",
        "allowed_values": [str(i) for i in range(2419, 2569)] + ["9999"],
        "allow_blank": True,
        "description": "ต้องเป็น 2419-2568 หรือ 9999",
    },
    "Age_01": {
        "type": "padded_number",
        "length": 3,
        "min_value": 0,
        "max_value": 150,
        "allow_blank": True,
        "description": "ต้องเป็น 000-150",
    },
    "Religion": {
        "type": "range",
        "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-9",
    },
    "ReligionOther": {
        "type": "text",
        "max_length": 50,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 50 ตัวอักษร",
    },
    # "NationalityNumeric": {
    #     "type": "custom",
    #     "allowed_values": [f"{i:03d}" for i in range(4, 910)]
    #     + ["997", "998", "999"],
    #     "allow_blank": True,
    #     "description": "ต้องเป็น 004-909 หรือ 997-999",
    # },
    "MaritalStatus": {
        "type": "custom",
        "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-7 หรือ 9",
    },
    "EducationalAttainment": {
        "type": "custom",
        "allowed_values": [f"{i:02d}" for i in range(1, 13)] + ["98", "99"],
        "allow_blank": True,
        "description": "ต้องเป็น 01-12 หรือ 98-99",
    },
    "EmploymentStatus": {
        "type": "range",
        "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-9",
    },
    "NameInHouseholdRegister": {
        "type": "custom",
        "allowed_values": ["1", "2", "3", "4", "5", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-5 หรือ 9",
    },
    "NameInHouseholdRegisterOther": {
        "type": "custom",
        "allowed_values": (
            ["10"]
            + [str(i) for i in range(11, 20)]
            + [str(i) for i in range(70, 78)]
            + [str(i) for i in range(80, 87)]
            + [str(i) for i in range(90, 97)]
            + [str(i) for i in range(20, 28)]
            + [str(i) for i in range(30, 50)]
            + [str(i) for i in range(50, 59)]
            + [str(i) for i in range(60, 68)]
            + ["99"]
        ),
        "allow_blank": True,
        "description": "ต้องเป็นรหัสจังหวัดที่กำหนด",
    },
    "DurationOfResidence": {
        "type": "custom",
        "allowed_values": ["0", "1", "2", "3", "4", "5", "6", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 0-6 หรือ 9",
    },
    "MigrationCharecteristics": {
        "type": "custom",
        "allowed_values": ["1", "2", "3", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-3 หรือ 9",
    },
    "MovedFromProvince": {
        "type": "custom",
        "allowed_values": (
            ["10"]
            + [str(i) for i in range(11, 20)]
            + [str(i) for i in range(70, 78)]
            + [str(i) for i in range(80, 87)]
            + [str(i) for i in range(90, 97)]
            + [str(i) for i in range(20, 28)]
            + [str(i) for i in range(30, 50)]
            + [str(i) for i in range(50, 59)]
            + [str(i) for i in range(60, 68)]
            + ["99"]
        ),
        "allow_blank": True,
        "description": "ต้องเป็นรหัสจังหวัดที่กำหนด",
    },
    # "MovedFromAbroad": {
    #     "type": "padded_number",
    #     "length": 3,
    #     "min_value": 0,
    #     "max_value": 999,
    #     "allow_blank": True,
    #     "description": "ต้องเป็น 000-999",
    # },
    "MigrationReason": {
        "type": "custom",
        "allowed_values": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-8 หรือ 9",
    },
    "MigrationReasonOther": {
        "type": "text",
        "max_length": 255,
        "allow_blank": True,
        "description": "ข้อความได้สูงสุด 255 ตัวอักษร",
    },
    "Gender": {
        "type": "range",
        "allowed_values": ["1", "2", "3", "4", "5"],
        "allow_blank": True,
        "description": "ต้องเป็น 1-5",
    },
    "TotalPopulation": {
        "type": "padded_number",
        "length": 4,
        "min_value": 1,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็น 0001-9999",
    },
    "TotalMale": {
        "type": "padded_number",
        "length": 4,
        "min_value": 0,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็น 0000-9999",
    },
    "TotalFemale": {
        "type": "padded_number",
        "length": 4,
        "min_value": 0,
        "max_value": 9999,
        "allow_blank": True,
        "description": "ต้องเป็น 0000-9999",
    },
}


def update_rules_from_excel_data(screen_instance):
    """อัปเดตกฎการตรวจสอบ FIELD_VALIDATION_RULES ของ screen_instance ด้วยข้อมูลจากไฟล์ Excel"""

    if not hasattr(screen_instance, "validation_data_from_excel") or not hasattr(
        screen_instance, "FIELD_VALIDATION_RULES"
    ):
        print(
            "Error: screen_instance is missing required attributes for validation update."
        )
        return

    if "LanguageOther" in screen_instance.validation_data_from_excel:
        screen_instance.FIELD_VALIDATION_RULES["LanguageOther"] = {
            "type": "custom",
            "allowed_values": screen_instance.validation_data_from_excel[
                "LanguageOther"
            ],
            "allow_blank": True,
            "description": "ต้องเป็นรหัสภาษาอื่นที่กำหนด",
        }

    if "NationalityNumeric" in screen_instance.validation_data_from_excel:
        screen_instance.FIELD_VALIDATION_RULES["NationalityNumeric"] = {
            "type": "custom",
            "allowed_values": screen_instance.validation_data_from_excel[
                "NationalityNumeric"
            ],
            "allow_blank": True,
            "description": "ต้องเป็นรหัสสัญชาติที่กำหนด",
        }

    if "MovedFromAbroad" in screen_instance.validation_data_from_excel:
        screen_instance.FIELD_VALIDATION_RULES["MovedFromAbroad"] = {
            "type": "excel_padded_number",
            "length": 3,
            "allowed_values": screen_instance.validation_data_from_excel[
                "MovedFromAbroad"
            ],
            "allow_blank": True,
            "description": "ต้องเป็นรหัสประเทศที่กำหนด",
        }
