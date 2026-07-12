"""
app/utils/validators.py
────────────────────────
Reusable field validators for Pydantic schemas.
"""

import re


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{6,14}$")


def validate_email_format(email: str) -> str:
    if not EMAIL_REGEX.match(email):
        raise ValueError(f"Invalid email address: {email}")
    return email.lower()


def validate_phone_format(phone: str) -> str:
    if not PHONE_REGEX.match(phone):
        raise ValueError(f"Invalid phone number: {phone}")
    return phone


def validate_password_strength(password: str) -> str:
    """
    Enforce minimum password requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one digit
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit.")
    return password
