from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
# from pytesseract import image_to_string
# from PIL import Image
# import re
from django.db.models.functions import Lower
from django.utils.http import urlencode




def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the data.

    Args:
        data (dict): Dictionary of form data.
        required_fields (list): List of required field names.

    Returns:
        str: An error message if any required field is missing, else None.
    """
    for field in required_fields:
        if not data.get(field):
            return f"خانة {field} إلزامية، لكنها غير موجودة."
    return None


def validate_date_format(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False



# def extract_id_number(image_path):
#     # Use pytesseract to do OCR on the image
#     text = image_to_string(Image.open(image_path))

#     # Use regex to find all sequences of exactly 9 digits, ignoring spaces
#     potential_ids = findall(r'\b\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\b', text)

#     # Remove spaces from the extracted numbers
#     potential_ids = [id_number.replace(' ', '') for id_number in potential_ids]

#     # Filter the list to find IDs that start with 9, 8, or 4
#     valid_ids = [id_number for id_number in potential_ids if id_number.startswith(('9', '8', '4'))]

#     return valid_ids  



# Dates validation function
def validate_dates(birthday, entrydate, hostingStartDate):
    # Convert dates to datetime objects for comparison
    try:
        birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
        entrydate_date = datetime.strptime(entrydate, '%Y-%m-%d')
        hostingStartDate_date = datetime.strptime(hostingStartDate, '%Y-%m-%d')
    except ValueError as e:
        return False, f"خطأ في صيغة التاريخ: {str(e)}"

    current_date = datetime.now()

    # Check for future dates
    if birthday_date > current_date or entrydate_date > current_date or hostingStartDate_date > current_date:
        return False, 'التواريخ لا يجب أن تكون في المستقبل'

    # Validate the date order
    if birthday_date > entrydate_date or birthday_date > hostingStartDate_date:
        return False, 'تاريخ الميلاد لا يجب أن يكون بعد تاريخ الدخول أو تاريخ الاستضافة'
    if entrydate_date < birthday_date or entrydate_date > hostingStartDate_date:
        return False, 'تاريخ الدخول لا يجب أن يكون قبل تاريخ الميلاد أو بعد تاريخ الاستضافة'
    if hostingStartDate_date < birthday_date or hostingStartDate_date < entrydate_date:
        return False, 'تاريخ الاستضافة لا يجب أن يكون قبل تاريخ الميلاد أو تاريخ الدخول'

    return True, None


# def normalize_query(query):
#     query = re.sub(r'[\u064B-\u065F]', '', query)  # إزالة التشكيلات
#     query = query.replace('أ', '[أا]').replace('إ', '[إا]').replace('آ', '[آا]')
#     query = query.replace('ى', '[ىي]').replace('ه', '[هة]').replace(' ', '')
#     return query


#     if query:
#         normalized_query = normalize_query(query)
#         customersList = customersList.filter(
#             Q(name__iregex=normalized_query) |
#             Q(idNumber__iregex=normalized_query) |
#             Q(phoneNumber__iregex=normalized_query) |
#             Q(diagnosis__iregex=normalized_query)
#         )
