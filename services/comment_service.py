import requests
from typing import List
from config import WP_COMMENTS_ENDPOINT
from models.schemas import CommentCreateSchema, CommentSchema
from datetime import datetime

# -----------------------------
# 📥 ارسال کامنت به وردپرس
# -----------------------------
def submit_comment(data: CommentCreateSchema) -> dict:
    try:
        payload = {
            "post": data.photo_id,
            "content": data.message
        }

        if data.name:
            payload["author_name"] = data.name
        if data.email:
            payload["author_email"] = data.email

        response = requests.post(WP_COMMENTS_ENDPOINT, json=payload)

        if response.status_code != 201:
            return {
                "success": False,
                "message": "Failed to submit comment.",
                "details": response.json()
            }

        return {
            "success": True,
            "message": "Comment submitted successfully.",
            "comment": response.json()
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Error in submit_comment.",
            "error": str(e)
        }

# -----------------------------
# 📤 واکشی کامنت‌های یک پست خاص (photo_id)
# -----------------------------
def fetch_comments(photo_id: int) -> List[CommentSchema]:
    try:
        response = requests.get(f"{WP_COMMENTS_ENDPOINT}?post={photo_id}")

        if response.status_code != 200:
            return []

        raw_comments = response.json()

        result = []
        for item in raw_comments:
            result.append(CommentSchema(
                id=item["id"],
                photo_id=item["post"],
                name=item.get("author_name", "Anonymous"),
                message=item["content"]["rendered"],
                created_at=datetime.fromisoformat(item["date"])
            ))

        return result

    except Exception:
        return []
