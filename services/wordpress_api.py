import requests
from typing import Optional, Dict, Any

def get_wp(
    url: str,
    token: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None
) -> dict:
    """
    ارسال درخواست GET به وردپرس با پشتیبانی از توکن
    """
    try:
        headers = {
            "Accept": "application/json"
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": "GET request to WordPress failed.",
                "details": response.json()
            }

        return {
            "success": True,
            "data": response.json()
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Exception during GET request.",
            "error": str(e)
        }

# ---------------------------------------

def post_wp(
    url: str,
    payload: dict,
    token: Optional[str] = None,
    content_type: str = "application/json"
) -> dict:
    """
    ارسال POST به وردپرس با پشتیبانی از توکن و انتخاب نوع content-type
    """
    try:
        headers = {
            "Content-Type": content_type
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code not in [200, 201]:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": "POST request to WordPress failed.",
                "details": response.json()
            }

        return {
            "success": True,
            "data": response.json()
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Exception during POST request.",
            "error": str(e)
        }
