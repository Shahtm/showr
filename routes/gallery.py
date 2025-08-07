 routes/gallery.py
import os, json
from flask import Blueprint, request, jsonify

gallery_bp = Blueprint("gallery", __name__)

DATA_FILE = os.environ.get("DATA_FILE", "./data/store.json")
os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)

def _load_db():
    if not os.path.exists(DATA_FILE):
        return {"posts": [], "comments": {}, "votes": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("posts", [])
            data.setdefault("comments", {})
            data.setdefault("votes", {})  # {post_id: {ip: "like"/"dislike"}}
            return data
    except Exception:
        return {"posts": [], "comments": {}, "votes": {}}

def _save_db(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@gallery_bp.route("", methods=["GET"])
def list_gallery():
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=12, type=int)
    sort = request.args.get("sort", default="-created_at", type=str)

    db = _load_db()
    items = list(db["posts"])

    # simple sort: -created_at or -id default
    if sort == "-created_at":
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort == "-id":
        items.sort(key=lambda x: x.get("id", 0), reverse=True)

    total = len(items)
    start = max(0, (page - 1) * limit)
    end = start + limit
    page_items = items[start:end]

    return jsonify({
        "items": page_items,
        "page": page,
        "limit": limit,
        "total": total
    })

@gallery_bp.route("/<int:item_id>", methods=["GET"])
def gallery_detail(item_id: int):
    db = _load_db()
    for it in db["posts"]:
        if it["id"] == item_id:
            return jsonify(it)
    return jsonify({"message": "Not found"}), 404

def _get_user_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)

@gallery_bp.route("/<int:item_id>/like", methods=["POST"])
def like_item(item_id: int):
    db = _load_db()
    ip = _get_user_ip()

    # پیدا کردن پست
    post = next((p for p in db["posts"] if p["id"] == item_id), None)
    if not post:
        return jsonify({"message": "Not found"}), 404

    post.setdefault("likes", 0)
    post.setdefault("dislikes", 0)
    db.setdefault("votes", {}).setdefault(str(item_id), {})

    # چک کردن رای قبلی
    prev_vote = db["votes"][str(item_id)].get(ip)
    if prev_vote == "like":
        return jsonify({"id": item_id, "likes": post["likes"], "dislikes": post["dislikes"], "message": "Already liked"}), 200
    elif prev_vote == "dislike":
        post["dislikes"] = max(0, post["dislikes"] - 1)
    elif

    # ثبت لایک
    post["likes"] += 1
    db["votes"][str(item_id)][ip] = "like"

    _save_db(db)
    return jsonify({"id": item_id, "likes": post["likes"], "dislikes": post["dislikes"]}), 200

@gallery_bp.route("/<int:item_id>/dislike", methods=["POST"])
def dislike_item(item_id: int):
    db = _load_db()
    ip = _get_user_ip()

    post = next((p for p in db["posts"] if p["id"] == item_id), None)
    if not post:
        return jsonify({"message": "Not found"}), 404

    post.setdefault("likes", 0)
    post.setdefault("dislikes", 0)
    db.setdefault("votes", {}).setdefault(str(item_id), {})

    prev_vote = db["votes"][str(item_id)].get(ip)
    if prev_vote == "dislike":
        return jsonify({"id": item_id, "likes": post["likes"], "dislikes": post["dislikes"], "message": "Already disliked"}), 200
    elif prev_vote == "like":
        post["likes"] = max(0, post["likes"] - 1)

    post["dislikes"] += 1
    db["votes"][str(item_id)][ip] = "dislike"

    _save_db(db)
    return jsonify({"id": item_id, "likes": post["likes"], "dislikes": post["dislikes"]}), 200