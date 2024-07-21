from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
# try:
#     import pytesseract
#     from PIL import Image
#     import re
# except ImportError as e:
#     print(f"Error importing modules: {e}")


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
#     text = pytesseract.image_to_string(Image.open(image_path))

#     # Use regex to find all sequences of exactly 9 digits, ignoring spaces
#     potential_ids = re.findall(r'\b\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\b', text)

#     # Remove spaces from the extracted numbers
#     potential_ids = [id_number.replace(' ', '') for id_number in potential_ids]

#     # Filter the list to find IDs that start with 9, 8, or 4
#     valid_ids = [id_number for id_number in potential_ids if id_number.startswith(('9', '8', '4'))]

#     return valid_ids  