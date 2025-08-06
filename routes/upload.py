# routes/upload.py
import os, time, json
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import requests

upload_bp = Blueprint("upload", __name__)

# ---------------------------
# Local storage config
# ---------------------------
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./uploads")
DATA_FILE = os.environ.get("DATA_FILE", "./data/store.json")
MAX_MB = int(os.environ.get("MAX_IMAGE_MB", "10"))

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)

# ---------------------------
# WebP options (env)
# ---------------------------
WEBP_QUALITY = int(os.environ.get("WEBP_QUALITY", "85"))           # 0..100
WEBP_LOSSLESS = os.environ.get("WEBP_LOSSLESS", "false").lower() == "true"
WEBP_MAX_W = int(os.environ.get("WEBP_MAX_WIDTH", "0"))            # 0 = no limit
WEBP_MAX_H = int(os.environ.get("WEBP_MAX_HEIGHT", "0"))           # 0 = no limit

# ---------------------------
# WordPress config (optional)
# ---------------------------
WP_BASE = os.environ.get("WP_BASE", "").rstrip("/")
WP_CPT_SLUG = os.environ.get("WP_CPT_SLUG", "showroom_uploads")
WP_MEDIA_ENDPOINT = f"{WP_BASE}/wp-json/wp/v2/media" if WP_BASE else None
WP_CPT_ENDPOINT = f"{WP_BASE}/wp-json/wp/v2/{WP_CPT_SLUG}" if WP_BASE and WP_CPT_SLUG else None
WP_JWT_TOKEN = os.environ.get("WP_JWT_TOKEN")
WP_VERIFY_SSL = (os.environ.get("WP_VERIFY_SSL", "True").lower() == "true")

# Meta keys (باید مطابق وردپرس/ACF خودت باشن)
META_IMAGE_KEY   = os.environ.get("WP_META_IMAGE_KEY", "sr_image")
META_NAME_KEY    = os.environ.get("WP_META_NAME_KEY", "sr_name")
META_DESC_KEY    = os.environ.get("WP_META_DESC_KEY", "sr_description")
META_PRODUCT_KEY = os.environ.get("WP_META_PRODUCT_KEY", "sr_product_id")
# اگر فیلد تصویرت در ACF مقدار ID می‌خواهد "id" بگذار؛ اگر URL می‌خواهد "url"
META_IMAGE_MODE  = (os.environ.get("WP_META_IMAGE_MODE", "id")).lower()  # "id" | "url"

# ---------------------------
# Helpers
# ---------------------------
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

def _next_post_id(posts):
    return (max([p["id"] for p in posts], default=0) + 1) if posts else 1

def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _wp_headers_json():
    if not WP_JWT_TOKEN:
        return None
    return {"Authorization": f"Bearer {WP_JWT_TOKEN}", "Accept": "application/json"}

def _maybe_resize(img: Image.Image) -> Image.Image:
    """اگر محدودیت ابعاد تعیین شده، تصویر را proportionally کوچک می‌کند."""
    if WEBP_MAX_W <= 0 and WEBP_MAX_H <= 0:
        return img
    w, h = img.size
    max_w = WEBP_MAX_W if WEBP_MAX_W > 0 else w
    max_h = WEBP_MAX_H if WEBP_MAX_H > 0 else h
    if w <= max_w and h <= max_h:
        return img
    img = img.copy()
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return img

def upload_media_to_wp(local_path: str, filename: str):
    """ارسال فایل webp به رسانه وردپرس"""
    if not (WP_MEDIA_ENDPOINT and WP_JWT_TOKEN):
        return None
    headers = _wp_headers_json()
    if headers is None:
        return None
    files = {"file": (filename, open(local_path, "rb"), "image/webp")}
    try:
        resp = requests.post(WP_MEDIA_ENDPOINT, headers=headers, files=files,
                             verify=WP_VERIFY_SSL, timeout=60)
        if resp.status_code not in (200, 201):
            print("[WP media error]", resp.status_code, resp.text)
            return None
        data = resp.json()
        return {"id": data.get("id"), "source_url": data.get("source_url")}
    except Exception as ex:
        print("[WP media exception]", ex)
        return None

def create_cpt_post_in_wp(title: str, featured_media_id: int = None, meta: dict = None, content: str = ""):
    """ساخت پست در CPT و پرکردن meta"""
    if not (WP_CPT_ENDPOINT and WP_JWT_TOKEN):
        return None
    headers = _wp_headers_json()
    if headers is None:
        return None
    payload = {"status": "publish", "title": title or "Untitled"}
    if content:
        payload["content"] = content
    if featured_media_id:
        payload["featured_media"] = featured_media_id
    if meta and isinstance(meta, dict):
        payload["meta"] = meta
    try:
        resp = requests.post(
            WP_CPT_ENDPOINT,
            headers={**headers, "Content-Type": "application/json"},
            json=payload,
            verify=WP_VERIFY_SSL,
            timeout=60
        )
        if resp.status_code not in (200, 201):
            print("[WP CPT error]", resp.status_code, resp.text)
            return None
        return resp.json()
    except Exception as ex:
        print("[WP CPT exception]", ex)
        return None

# ---------------------------
# Upload endpoint
# ---------------------------
@upload_bp.route("", methods=["POST"])
def upload():
    """
    ورودی:
      multipart/form-data: file, caption, author_name, (اختیاری) product_id
    خروجی:
      201 JSON با اطلاعات پست لوکال + در صورت اتصال به WP، خلاصه وردپرسی
    """
    f = request.files.get("file")
    caption = (request.form.get("caption") or "").strip()
    author_name = (request.form.get("author_name") or "").strip()
    product_id = request.form.get("product_id")

    if not f or not f.filename:
        return jsonify({"message": "file is required"}), 400

    # محدودیت حجم (بر اساس فایل ورودی، قبل از تبدیل)
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > MAX_MB * 1024 * 1024:
        return jsonify({"message": f"file too large (>{MAX_MB}MB)"}), 413

    # خواندن با Pillow و تبدیل به WebP
    try:
        img = Image.open(f.stream)
        # تبدیل Mode برای پشتیبانی WebP (آلفا حفظ می‌شود)
        if img.mode not in ("RGB", "RGBA"):
            # اگر پالت/سیاه‌سفید و ... بود
            img = img.convert("RGBA") if "A" in img.getbands() else img.convert("RGB")

        # resize در صورت نیاز
        img = _maybe_resize(img)

        # نام نهایی webp
        fname_only = f"{int(time.time()*1000)}"
        fname = f"{fname_only}.webp"
        local_path = os.path.join(UPLOAD_DIR, secure_filename(fname))

        save_kwargs = {
            "format": "WEBP",
            "quality": WEBP_QUALITY,
            "method": 6,
        }
        if WEBP_LOSSLESS:
            save_kwargs["lossless"] = True

        # ذخیره خروجی webp
        img.save(local_path, **save_kwargs)

    except Exception as e:
        return jsonify({"message": f"Image conversion failed: {str(e)}"}), 400

    # URL عمومی فایل webp
    base = os.environ.get("PUBLIC_BASE") or f"{request.scheme}://{request.host}"
    image_url_local = f"{base}/uploads/{fname}"

    # ثبت در دیتابیس JSON لوکال
    db = _load_db()
    pid = _next_post_id(db["posts"])
    item = {
        "id": pid,
        "image_url": image_url_local,
        "title": caption or "Untitled",
        "author_name": author_name or "Guest",
        "likes": 0,
        "dislikes": 0,
        "created_at": _now_iso(),
    }
    if product_id:
        try:
            item["product_id"] = int(product_id)
        except ValueError:
            item["product_id"] = product_id

    db["posts"].append(item)
    _save_db(db)

    # ---- Push to WordPress (optional) ----
    wp_summary = None
    if WP_BASE and WP_JWT_TOKEN:
        media = upload_media_to_wp(local_path, fname)
        # مقدار متای تصویر بر اساس MODE
        if media:
            meta_image_value = media.get("id") if META_IMAGE_MODE == "id" else media.get("source_url")
        else:
            meta_image_value = image_url_local if META_IMAGE_MODE == "url" else None

        meta_payload = {
            META_NAME_KEY: author_name or "Guest",
            META_DESC_KEY: caption or "",
            META_IMAGE_KEY: meta_image_value,
        }
        if product_id and META_PRODUCT_KEY:
            meta_payload[META_PRODUCT_KEY] = item.get("product_id")

        cpt = create_cpt_post_in_wp(
            title=item["title"],
            featured_media_id=(media or {}).get("id"),
            meta=meta_payload,
            content=caption or ""
        )
        if cpt and cpt.get("id"):
            wp_summary = {
                "post_id": cpt["id"],
                "featured_media": (media or {}).get("id"),
                "wp_link": cpt.get("link"),
                "wp_image_url": (media or {}).get("source_url"),
            }

    # پاسخ
    resp = {
        "id": item["id"],
        "image_url": item["image_url"],
        "caption": caption,
        "author_name": item["author_name"],
    }
    if wp_summary:
        resp["wordpress"] = wp_summary

    return jsonify(resp), 201
