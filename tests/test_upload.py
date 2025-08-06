import unittest
from flask import Flask
from app import create_app

class UploadTestCase(unittest.TestCase):
    def setUp(self):
        self.app: Flask = create_app()
        self.client = self.app.test_client()

        # عکس واقعی (موجود) توی اینترنت که وردپرس بتونه فچ کنه
        self.valid_data = {
            "image_url": "https://via.placeholder.com/600x400.jpg",
            "description": "تجربه من با این گجت عالی بود 😎",
            "related_product_id": 123,  # اینو با یه آی‌دی واقعی محصول عوض کن
            "uploaded_by": 7,
            "username": "Shahrooz"
        }

        self.invalid_data = {
            "image_url": "",  # تصویر نامعتبر
            "description": "ناقصه"
            # related_product_id حذف شده
        }

    def test_upload_success(self):
        """تست آپلود موفق تجربه"""
        response = self.client.post("/api/upload/", json=self.valid_data)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("photo_id", data)
        self.assertIn("image_url", data)
        print("✅ Upload success test passed.")

    def test_upload_fail_invalid_input(self):
        """تست آپلود با ورودی ناقص یا اشتباه"""
        response = self.client.post("/api/upload/", json=self.invalid_data)
        self.assertEqual(response.status_code, 500)

        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("message", data)
        print("✅ Upload fail test (invalid input) passed.")

if __name__ == '__main__':
    unittest.main()
