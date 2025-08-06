# این فایل همه‌ی مسیرهای (روت‌های) اصلی API رو جمع می‌کنه تا توی app.py راحت رجیستر کنیم

from .auth import auth_bp
from .upload import upload_bp
from .gallery import gallery_bp
from .comments import comments_bp
from .contributors import contributors_bp

__all__ = [
    "auth_bp",
    "upload_bp",
    "gallery_bp",
    "comments_bp",
    "contributors_bp"
]
