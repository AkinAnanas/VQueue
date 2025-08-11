import secrets
import string
import phonenumbers
import re
import html

def generate_code():
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(6))

def normalize_email(email: str) -> str:
    return email.strip().lower()

def normalize_phone(phone: str, region: str = "US") -> str:
    parsed = phonenumbers.parse(phone, region)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

def sanitize_str(string: str) -> str:
    if not string:
        return ""

    # Trim whitespace
    string = string.strip()

    # Unescape HTML entities (e.g. &lt; → <)
    string = html.unescape(string)

    # Remove HTML tags
    string = re.sub(r"<[^>]+>", "", string)

    # Remove control characters
    string = re.sub(r"[\x00-\x1F\x7F]", "", string)

    # Normalize whitespace (collapse multiple spaces)
    string = re.sub(r"\s+", " ", string)

    return string

