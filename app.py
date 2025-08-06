# app.py
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# --- Blueprints ---
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.gallery import gallery_bp
from routes.comments import comments_bp
from routes.contributors import contributors_bp


def create_app():
    app = Flask(__name__)

    # Optional config file (won't error if missing)
    app.config.from_pyfile("config.py", silent=True)

    # ---------- CORS ----------
    # اگر CORS_ORIGINS="*" باشد همه مجازند (برای تست).
    # در غیر اینصورت با کاما چند دامنه بده: https://showroom.gadgetrox.com,https://xxx.loca.lt,http://localhost:3000
    raw_origins = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).strip()

    cors_kwargs = {
        "resources": {r"/api/*": {"origins": "*"}},
        "supports_credentials": False,
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 86400,  # cache preflight
    }

    if raw_origins and raw_origins != "*":
        origin_list = [o.strip() for o in raw_origins.split(",") if o.strip()]
        cors_kwargs["resources"] = {r"/api/*": {"origins": origin_list}}

    CORS(app, **cors_kwargs)

    # ---------- Register API blueprints ----------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(gallery_bp, url_prefix="/api/gallery")
    app.register_blueprint(comments_bp, url_prefix="/api/comments")
    app.register_blueprint(contributors_bp, url_prefix="/api/contributors")

    # Health endpoint
    @app.get("/api/status")
    def status_check():
        return {"status": "Showroom API is running ✅"}

    # Serve uploaded files (public)
    upload_dir = os.environ.get("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)

    @app.get("/uploads/<path:filename>")
    def serve_uploads(filename):
        return send_from_directory(upload_dir, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
