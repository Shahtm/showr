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
            "likes": c.get("likes", 0),
            "dislikes": c.get("dislikes", 0),
            "reaction": c.get("reaction", "")  # just for debug/testing
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
        "avatar_url": "",
        "likes": 0,
        "dislikes": 0,
        "reaction": ""  # reaction by this user
    }
    db["comments"].setdefault(str(post_id), []).append(comment)
    _save_db(db)

    return jsonify({
        "id": comment["id"],
        "author_name": comment["author_name"],
        "text": comment["text"],
        "created_at": comment["created_at"],
        "avatar_url": comment["avatar_url"],
        "likes": comment["likes"],
        "dislikes": comment["dislikes"]
    }), 201

# POST /api/comments/react { comment_id, action }  where action = "like" or "dislike"
@comments_bp.route("/react", methods=["POST"])
def react_comment():
    data = request.get_json(silent=True) or {}
    comment_id = data.get("comment_id")
    action = data.get("action")

    if not comment_id or action not in ["like", "dislike"]:
        return jsonify({"message": "comment_id and valid action required"}), 400

    db = _load_db()
    updated = False
    for comments in db["comments"].values():
        for c in comments:
            if str(c["id"]) == str(comment_id):
                prev_reaction = c.get("reaction", "")
                if prev_reaction == action:
                    # toggle off
                    c[action + "s"] = max(0, c.get(action + "s", 0) - 1)
                    c["reaction"] = ""
                else:
                    # switch
                    if prev_reaction:
                        c[prev_reaction + "s"] = max(0, c.get(prev_reaction + "s", 0) - 1)
                    c[action + "s"] = c.get(action + "s", 0) + 1
                    c["reaction"] = action
                updated = True
                break

    if updated:
        _save_db(db)
        return jsonify({"message": "reaction updated"})
    else:
        return jsonify({"message": "comment not found"}), 404
