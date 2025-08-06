from flask import Blueprint, request, jsonify
import requests
from models.schemas import AuthRequestSchema, AuthResponseSchema
from config import JWT_AUTH_URL, WP_USERNAME, WP_PASSWORD

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/get-token", methods=["POST"])
def get_token():
    """
    دریافت JWT توکن از وردپرس با username و password
    یا استفاده از یوزر پیش‌فرض تستی در config.py
    """

    try:
        # گرفتن داده از بدنه‌ی POST
        data = request.json or {}

        # اگر بدنه خالی بود از یوزر تست استفاده کن
        if "username" not in data or "password" not in data:
            data = {
                "username": WP_USERNAME,
                "password": WP_PASSWORD
            }

        # اعتبارسنجی ورودی با Pydantic
        auth_input = AuthRequestSchema(**data)

        # ارسال درخواست به وردپرس برای دریافت توکن
        wp_response = requests.post(JWT_AUTH_URL, json={
            "username": auth_input.username,
            "password": auth_input.password
        })

        if wp_response.status_code != 200:
            return jsonify({
                "success": False,
                "message": "Authentication with WordPress failed.",
                "details": wp_response.json()
            }), wp_response.status_code

        wp_data = wp_response.json()

        # اعتبارسنجی خروجی
        token_data = AuthResponseSchema(**wp_data)

        return jsonify({
            "success": True,
            "token": token_data.token,
            "user": {
                "name": token_data.user_display_name,
                "email": token_data.user_email,
                "nicename": token_data.user_nicename
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal error during authentication.",
            "error": str(e)
        }), 500
