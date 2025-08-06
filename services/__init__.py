# این فایل فقط برای تبدیل پوشه services به ماژول پایتون استفاده میشه
# می‌تونیم توش importهای کلیدی رو جمع کنیم برای راحتی استفاده

from .wordpress_api import get_wp, post_wp
from .media_upload import upload_image_to_wp
from .post_creator import create_cpt_post
from .comment_service import submit_comment, fetch_comments

__all__ = [
    "get_wp",
    "post_wp",
    "upload_image_to_wp",
    "create_cpt_post",
    "submit_comment",
    "fetch_comments"
]
