import requests
from typing import Optional, Dict
from config import WP_CPT_ENDPOINT

def create_cpt_post(
    title: str,
    meta: Dict,
    featured_media_id: Optional[int] = None
) -> dict:
    """
    ساخت پست جدید در وردپرس (در CPT اختصاصی مثل user_gadget_photos)

    Args:
        title (str): عنوان پست
        meta (dict): اطلاعات meta (description, username, likes, etc)
        featured_media_id (int): آیدی تصویر آپلودشده (در صورت وجود)

    Returns:
        dict: شامل id پست ساخته‌شده، وضعیت، لینک و...
    """

    try:
        payload = {
            "title": title,
            "status": "publish",
            "meta": meta
        }

        if featured_media_id:
            payload["featured_media"] = featured_media_id

        response = requests.post(WP_CPT_ENDPOINT, json=payload)

        if response.status_code not in [200, 201]:
            return {
                "success": False,
                "message": "Failed to create CPT post.",
                "details": response.json()
            }

        post_data = response.json()

        return {
            "success": True,
            "post_id": post_data["id"],
            "status": post_data["status"],
            "link": post_data["link"],
            "meta": post_data.get("meta", {})
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Exception while creating CPT post.",
            "error": str(e)
        }
