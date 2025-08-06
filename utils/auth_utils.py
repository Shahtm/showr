import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY

# مدت زمان اعتبار توکن‌ها (مثلاً ۷ روز)
TOKEN_EXPIRY_DAYS = 7

def generate_token(payload: dict, expiry_days: int = TOKEN_EXPIRY_DAYS) -> str:
    """
    ساخت یک JWT توکن با داده دلخواه (payload)
    """
    payload_copy = payload.copy()
    payload_copy["exp"] = datetime.utcnow() + timedelta(days=expiry_days)
    return jwt.encode(payload_copy, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    """
    بررسی صحت و دیکد کردن توکن
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {
            "valid": True,
            "payload": decoded
        }
    except jwt.ExpiredSignatureError:
        return {
            "valid": False,
            "error": "Token expired"
        }
    except jwt.InvalidTokenError:
        return {
            "valid": False,
            "error": "Invalid token"
        }
