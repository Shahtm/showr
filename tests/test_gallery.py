import unittest
from flask import Flask
from app import create_app

class GalleryTestCase(unittest.TestCase):
    def setUp(self):
        self.app: Flask = create_app()
        self.client = self.app.test_client()

        # آیدی محصولی که توی وردپرس واقعاً براش عکس آپلود شده
        # می‌تونی توی config جدا بذاری
        self.valid_product_id = 123  # 👈 اینو خودت ست کن
        self.invalid_product_id = 999999  # محصولی که هیچ عکس نداره

    def test_get_gallery_success(self):
        """تست گرفتن گالری برای محصولی که عکس داره"""
        response = self.client.get(f"/api/gallery/{self.valid_product_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], self.valid_product_id)

        self.assertIn("photos", data)
        self.assertIsInstance(data["photos"], list)

        if data["photos"]:  # اگه عکس داره
            first = data["photos"][0]
            self.assertIn("id", first)
            self.assertIn("image_url", first)
            self.assertIn("uploaded_at", first)
            self.assertIn("username", first)
            print("✅ Gallery success with photos passed.")
        else:
            print("⚠️ Gallery success passed but no photos found (empty list).")

    def test_get_gallery_empty(self):
        """تست محصولی که هیچ گالری نداره"""
        response = self.client.get(f"/api/gallery/{self.invalid_product_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["product_id"], self.invalid_product_id)
        self.assertIsInstance(data["photos"], list)
        self.assertEqual(len(data["photos"]), 0)
        print("✅ Gallery empty state passed.")

if __name__ == '__main__':
    unittest.main()
