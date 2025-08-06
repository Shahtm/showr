import unittest
from flask import Flask
from app import create_app
from config import WP_USERNAME, WP_PASSWORD

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        # ساخت اپ Flask برای تست
        self.app: Flask = create_app()
        self.client = self.app.test_client()

        # یوزر و پسورد تستی از config
        self.valid_creds = {
            "username": WP_USERNAME,
            "password": WP_PASSWORD
        }

        self.invalid_creds = {
            "username": "wronguser",
            "password": "wrongpass"
        }

    def test_get_token_success(self):
        """تست گرفتن موفق JWT از وردپرس"""
        response = self.client.post("/api/auth/get-token", json=self.valid_creds)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertIn("user_email", data["user"])
        print("✅ Token success test passed.")

    def test_get_token_fail(self):
        """تست گرفتن توکن با یوزر اشتباه"""
        response = self.client.post("/api/auth/get-token", json=self.invalid_creds)
        self.assertNotEqual(response.status_code, 200)

        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("message", data)
        print("✅ Token failure test passed.")

if __name__ == '__main__':
    unittest.main()
