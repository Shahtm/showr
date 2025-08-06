import os

# -------------------------------
# 🔐 احراز هویت وردپرس
# -------------------------------
JWT_AUTH_URL = os.getenv("WP_JWT_AUTH_URL", "https://gadgetrox.com/wp-json/jwt-auth/v1/token")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "WpKqrRWQxF")  # برای تولید و چک توکن سمت Flask اگه نیاز شد

# -------------------------------
# 🌐 آدرس‌های اصلی وردپرس
# -------------------------------
WP_BASE_URL = os.getenv("WP_BASE_URL", "https://gadgetrox.com")
WP_MEDIA_ENDPOINT = f"{WP_BASE_URL}/wp-json/wp/v2/media"
WP_CPT_ENDPOINT = f"{WP_BASE_URL}/wp-json/wp/v2/user_gadget_photos"
WP_COMMENTS_ENDPOINT = f"{WP_BASE_URL}/wp-json/wp/v2/comments"
WP_PRODUCTS_ENDPOINT = f"{WP_BASE_URL}/wp-json/wp/v2/products"  # اگه بخوایم لیست محصولات بگیریم

# -------------------------------
# 🧾 اطلاعات یوزر API وردپرس (تست)
# -------------------------------
WP_USERNAME = os.getenv("WP_USERNAME", "your-wp-api-user")
WP_PASSWORD = os.getenv("WP_PASSWORD", "your-wp-api-password")

# -------------------------------
# ⚙️ تنظیمات عمومی Flask
# -------------------------------
DEBUG = True
PORT = int(os.getenv("PORT", 5000))
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # حداکثر حجم عکس: ۱۰ مگابایت
UPLOAD_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

# -------------------------------
# 📦 مسیر ذخیره فایل موقتی (در صورت نیاز)
# -------------------------------
TEMP_UPLOAD_FOLDER = os.getenv("TEMP_UPLOAD_FOLDER", "/tmp/uploads")

# -------------------------------
# 🧠 تنظیمات کش ساده (در آینده برای Redis یا مشابه)
# -------------------------------
USE_CACHE = False
CACHE_TIMEOUT = 300  # ثانیه
