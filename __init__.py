from .app import create_app

# وقتی این پکیج ایمپورت بشه (مثلاً توی تست یا wsgi)،
# این متد به عنوان نقطه ورود اپ Flask استفاده می‌شه
__all__ = ["create_app"]
