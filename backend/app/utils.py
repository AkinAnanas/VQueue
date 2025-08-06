import secrets
import string

def format_response(code, data):
    return {
        'status_code': code,
        'body': data,
    }

def generate_code():
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(6))
