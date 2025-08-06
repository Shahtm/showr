from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# -----------------------------------------
# 📥 پاسخ موفق از وردپرس هنگام آپلود عکس
# -----------------------------------------

class WPMediaUploadResponse(BaseModel):
    id: int
    date: datetime
    slug: str
    link: HttpUrl
    title: dict
    media_type: str  # e.g. "image"
    mime_type: str   # e.g. "image/jpeg"
    source_url: HttpUrl  # آدرس نهایی عکس قابل استفاده


# -----------------------------------------
# 📝 ساخت پست در CPT (مثل user_gadget_photos)
# -----------------------------------------

class WPPostCreatePayload(BaseModel):
    title: str
    status: str = "publish"
    fields: dict  # meta fields for JetEngine or ACF

class WPPostResponse(BaseModel):
    id: int
    date: datetime
    title: dict
    status: str
    link: HttpUrl


# -----------------------------------------
# 💬 ساخت و واکشی کامنت از REST API
# -----------------------------------------

class WPCommentCreatePayload(BaseModel):
    post: int  # post ID (photo ID)
    author_name: Optional[str]
    author_email: Optional[EmailStr]
    content: dict  # { "rendered": "text" }

class WPCommentResponse(BaseModel):
    id: int
    post: int
    author_name: Optional[str]
    content: dict
    date: datetime


# -----------------------------------------
# 🛒 محصول ووکامرس (در صورت استفاده از فیلتر محصول)
# -----------------------------------------

class WooProduct(BaseModel):
    id: int
    name: str
    slug: str
    permalink: HttpUrl
    images: List[dict]  # [{id, src, alt}]
