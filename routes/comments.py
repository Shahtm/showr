# routes/comments.py
import os, json, time
from datetime import datetime
from flask import Blueprint, request, jsonify

comments_bp = Blueprint("comments", __name__)

DATA_FILE = os.environ.get("DATA_FILE", "./data/store.json")
os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)

def _load_db():
    if not os.path.exists(DATA_FILE):
        return {"posts": [], "comments": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("posts", [])
            data.setdefault("comments", {})
            return data
    except Exception:
        return {"posts": [], "comments": {}}

def _save_db(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _next_comment_id(all_comments: dict):
    max_id = 0
    for arr in all_comments.values():
        for c in arr:
            if int(c.get("id", 0)) > max_id:
                max_id = int(c["id"])
    return max_id + 1

# GET /api/comments?post_id=123
@comments_bp.route("", methods=["GET"])
def list_comments():
    post_id = request.args.get("post_id", type=int)
    if not post_id:
        return jsonify({"message": "post_id is required"}), 400
    db = _load_db()
    arr = db["comments"].get(str(post_id), [])
    # map to frontend shape
    items = [
        {
            "id": c["id"],
            "author_name": c.get("author_name") or "Guest",
            "text": c.get("text") or "",
            "created_at": c.get("created_at") or _now_iso(),
            "avatar_url": c.get("avatar_url") or "",
        }
        for c in arr
    ]
    return jsonify({"items": items})

# POST /api/comments  { post_id, author_name, text }
@comments_bp.route("", methods=["POST"])
def create_comment():
    data = request.get_json(silent=True) or {}
    post_id = data.get("post_id")
    text = (data.get("text") or "").strip()
    author = (data.get("author_name") or "").strip()

    if not post_id or not text:
        return jsonify({"message": "post_id and text are required"}), 400

    db = _load_db()
    cid = _next_comment_id(db["comments"])
    comment = {
        "id": cid,
        "post_id": int(post_id),
        "author_name": author or "Guest",
        "text": text,
        "created_at": _now_iso(),
        "avatar_url": "",  # optional
    }
    db["comments"].setdefault(str(post_id), []).append(comment)
    _save_db(db)

    # return single comment in frontend shape
    return jsonify({
        "id": comment["id"],
        "author_name": comment["author_name"],
        "text": comment["text"],
        "created_at": comment["created_at"],
        "avatar_url": comment["avatar_url"],
    }), 201
