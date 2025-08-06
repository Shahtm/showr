import mimetypes
import requests

# فرمت‌های مجاز برای گالری
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

def validate_image_url(image_url: str) -> bool:
    """
    بررسی اینکه آیا URL داده‌شده مربوط به یک فایل عکس معتبر هست یا نه
    """
    try:
        response = requests.head(image_url, allow_redirects=True, timeout=5)

        if response.status_code != 200:
            return False

        content_type = response.headers.get("Content-Type", "")
        return content_type.lower() in ALLOWED_IMAGE_TYPES

    except requests.RequestException:
        return False


def get_file_extension(image_url: str) -> str:
    """
    استخراج پسوند فایل از URL یا mime-type
    """
    # ابتدا تلاش با mime-type
    try:
        response = requests.head(image_url, allow_redirects=True, timeout=5)
        content_type = response.headers.get("Content-Type", "").lower()
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext.lstrip('.')  # بدون نقطه
    except:
        pass

    # fallback: گرفتن از انتهای URL
    url_parts = image_url.split("?")[0].split("/")
    filename = url_parts[-1]
    if '.' in filename:
        return filename.split(".")[-1].lower()

    return "jpg"  # پیش‌فرض

def is_supported_format(image_url: str) -> bool:
    """
    چک کنه آیا فرمت URL جزو فرمت‌های مجازه یا نه
    """
    ext = get_file_extension(image_url)
    return ext in ["jpg", "jpeg", "png", "webp"]
