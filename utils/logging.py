import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

# مسیر ذخیره لاگ‌ها
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# اسم فایل لاگ بر اساس تاریخ روز
log_filename = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# فرمت مشترک برای لاگ فایل
file_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# هندلر فایل چرخشی (حداکثر 5MB)
file_handler = RotatingFileHandler(log_filename, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

# کنسول هندلر با رنگ (اگه colorlog نصب باشه)
if COLORLOG_AVAILABLE:
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s | %(cyan)s%(message)s",
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
else:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(file_formatter)

console_handler.setLevel(logging.DEBUG)

# logger نهایی
logger = logging.getLogger("showroom-logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False  # تکرار نکن

