import requests
from config import WP_MEDIA_ENDPOINT
from typing import Optional

def upload_image_to_wp(image_url: str, username: Optional[str] = "User") -> dict:
    """
    آپلود تصویر به وردپرس از طریق یک URL عمومی
    اگر بخوای از base64 یا فایل استفاده کنی هم قابل گسترشه.

    Returns:
        dict {
            success: bool,
            media_id: int,
            image_url: str
        }
    """
    try:
        headers = {
            "Content-Disposition": f"attachment; filename={username.lower()}-upload.jpg",
            "Content-Type": "application/json"
        }

        payload = {
            "title": f"Showroom Upload - {username}",
            "source_url": image_url  # مهم: وردپرس باید اجازه فچ از این URL رو داشته باشه
        }

        response = requests.post(WP_MEDIA_ENDPOINT, headers=headers, json=payload)

        if response.status_code not in [200, 201]:
            return {
                "success": False,
                "message": "Upload to WordPress failed.",
                "details": response.json()
            }

        data = response.json()
        return {
            "success": True,
            "media_id": data["id"],
            "image_url": data["source_url"]
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Exception occurred while uploading media.",
            "error": str(e)
        }
