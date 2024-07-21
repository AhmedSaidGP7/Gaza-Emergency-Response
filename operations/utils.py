from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

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