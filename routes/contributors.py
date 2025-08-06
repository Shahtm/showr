from flask import Blueprint, jsonify
import requests
from collections import defaultdict
from models.schemas import ContributorSchema
from config import WP_CPT_ENDPOINT

contributors_bp = Blueprint("contributors", __name__)

@contributors_bp.route("/", methods=["GET"])
def get_top_contributors():
    try:
        # مرحله ۱: واکشی همه پست‌های CPT (شوروم)
        # می‌تونیم به مرور اینو page-by-page کنیم، ولی فعلاً همه رو می‌گیریم
        wp_response = requests.get(f"{WP_CPT_ENDPOINT}?per_page=100")

        if wp_response.status_code != 200:
            return jsonify({
                "success": False,
                "message": "Failed to fetch posts from WordPress.",
                "details": wp_response.json()
            }), wp_response.status_code

        posts = wp_response.json()

        # مرحله ۲: گروه‌بندی بر اساس uploaded_by
        contributors = defaultdict(lambda: {
            "total_uploads": 0,
            "total_likes": 0,
            "username": None,
            "avatar_url": None
        })

        for post in posts:
            meta = post.get("meta", {})
            user_id = meta.get("uploaded_by") or post.get("author")
            if not user_id:
                continue

            username = post.get("author_name", f"User {user_id}")
            avatar = post.get("author_avatar_urls", {}).get("96")  # یا از meta اختصاصی بگیر

            likes = int(meta.get("likes", 0))

            contributors[user_id]["total_uploads"] += 1
            contributors[user_id]["total_likes"] += likes
            contributors[user_id]["username"] = username
            contributors[user_id]["avatar_url"] = avatar

        # مرحله ۳: تبدیل به ساختار استاندارد و مرتب‌سازی بر اساس likes
        contributor_list = []
        for user_id, info in contributors.items():
            contributor_list.append(ContributorSchema(
                user_id=int(user_id),
                username=info["username"] or f"User {user_id}",
                avatar_url=info["avatar_url"],
                total_uploads=info["total_uploads"],
                total_likes=info["total_likes"]
            ).dict())

        sorted_list = sorted(contributor_list, key=lambda x: x["total_likes"], reverse=True)

        return jsonify({
            "success": True,
            "count": len(sorted_list),
            "contributors": sorted_list
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal error while fetching top contributors.",
            "error": str(e)
        }), 500
