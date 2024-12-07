import re
from datetime import datetime
from typing import Optional, Tuple

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email:
        return False, "Email is required"
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, None

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, None

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, None

def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date string format (YYYY-MM-DD)
    Returns: (is_valid, error_message)
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

def validate_amount(amount: str) -> Tuple[bool, Optional[str]]:
    """
    Validate monetary amount
    Returns: (is_valid, error_message)
    """
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            return False, "Amount must be greater than 0"
        return True, None
    except ValueError:
        return False, "Invalid amount format"

def validate_quantity(quantity: str) -> Tuple[bool, Optional[str]]:
    """
    Validate quantity
    Returns: (is_valid, error_message)
    """
    try:
        quantity_int = int(quantity)
        if quantity_int < 0:
            return False, "Quantity cannot be negative"
        return True, None
    except ValueError:
        return False, "Invalid quantity format"