from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# -----------------------------------------
# 📤 فرم آپلود تجربه کاربر (عکس + توضیح + محصول)
# -----------------------------------------

class UploadFormSchema(BaseModel):
    image_url: HttpUrl  # آدرس آپلود شده‌ی عکس (بعد از ارسال به وردپرس)
    description: str = Field(..., max_length=500)
    related_product_id: int  # ID محصول ووکامرس
    uploaded_by: Optional[int] = None  # اگر کاربر لاگین کرده بود
    username: Optional[str] = None     # برای نمایش اسم کاربر در شو‌روم


# -----------------------------------------
# 🔐 احراز هویت - گرفتن توکن JWT از وردپرس
# -----------------------------------------

class AuthRequestSchema(BaseModel):
    username: str
    password: str

class AuthResponseSchema(BaseModel):
    token: str
    user_email: EmailStr
    user_nicename: str
    user_display_name: str


# -----------------------------------------
# 🖼 واکشی گالری تجربه‌ها برای یک محصول
# -----------------------------------------

class PhotoItem(BaseModel):
    id: int
    image_url: HttpUrl
    description: Optional[str]
    username: Optional[str]
    uploaded_at: datetime
    likes: Optional[int] = 0

class GalleryResponseSchema(BaseModel):
    product_id: int
    photos: List[PhotoItem]


# -----------------------------------------
# 💬 کامنت‌ها
# -----------------------------------------

class CommentCreateSchema(BaseModel):
    photo_id: int
    message: str
    name: Optional[str]
    email: Optional[EmailStr] = None

class CommentSchema(BaseModel):
    id: int
    photo_id: int
    name: Optional[str]
    message: str
    created_at: datetime


# -----------------------------------------
# 🔥 مشارکت‌کنندگان فعال
# -----------------------------------------

class ContributorSchema(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[HttpUrl]
    total_uploads: int
    total_likes: int
