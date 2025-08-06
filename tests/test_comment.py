import unittest
from flask import Flask
from app import create_app

class CommentTestCase(unittest.TestCase):
    def setUp(self):
        self.app: Flask = create_app()
        self.client = self.app.test_client()

        # آیدی یک عکس واقعی توی وردپرس که از قبل آپلود شده
        self.valid_photo_id = 321  # ⚠️ باید واقعی باشه
        self.invalid_photo_id = 99999999  # فرض بر اینه وجود نداره

        self.valid_comment = {
            "photo_id": self.valid_photo_id,
            "message": "واقعاً تجربه باحالی بود 😍",
            "name": "Shahrooz",
            "email": "shahrooz@email.com"
        }

        self.invalid_comment = {
            "photo_id": "",  # یا حذف کامل فیلدها
            "message": ""
        }

    def test_post_comment_success(self):
        """تست ثبت کامنت موفق"""
        response = self.client.post("/api/comments/", json=self.valid_comment)
        self.assertIn(response.status_code, [200, 201])

        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("comment", data)
        print("✅ Post comment success test passed.")

    def test_post_comment_fail(self):
        """تست ثبت کامنت با داده ناقص"""
        response = self.client.post("/api/comments/", json=self.invalid_comment)
        self.assertIn(response.status_code, [400, 422, 500])  # بسته به هندل داخلی

        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("message", data)
        print("✅ Post comment fail (invalid input) test passed.")

    def test_get_comments_success(self):
        """تست واکشی کامنت‌های عکس با آیدی درست"""
        response = self.client.get(f"/api/comments/{self.valid_photo_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("comments", data)
        self.assertIsInstance(data["comments"], list)

        if data["comments"]:
            first = data["comments"][0]
            self.assertIn("id", first)
            self.assertIn("message", first)
            self.assertIn("name", first)
            print("✅ Get comments success (with results) test passed.")
        else:
            print("⚠️ Get comments success passed (but no comments found).")

    def test_get_comments_empty(self):
        """تست واکشی کامنت برای عکس نامعتبر (بدون کرش)"""
        response = self.client.get(f"/api/comments/{self.invalid_photo_id}")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["comments"], [])
        print("✅ Get comments empty state test passed.")

if __name__ == '__main__':
    unittest.main()
