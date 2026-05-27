"""Shared constants for Tiki chatbot actions."""

from __future__ import annotations

import os
from pathlib import Path


MODEL_NAME = os.getenv(
    "TIKI_EMBEDDING_MODEL", "bkai-foundation-models/vietnamese-bi-encoder"
)
TOP_K_FAISS = int(os.getenv("TIKI_FAISS_TOP_K", "200"))
TOP_K_RESPONSE = int(os.getenv("TIKI_RESPONSE_TOP_K", "5"))

CHATBOT_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = Path(os.getenv("TIKI_CHATBOT_INDEX_DIR", CHATBOT_DIR / "storage"))
INDEX_PATH = INDEX_DIR / "products.faiss"
METADATA_PATH = INDEX_DIR / "products_metadata.pkl"

CATEGORY_BY_PRODUCT = {
    "dien thoai": "Dien Thoai May Tinh Bang",
    "may tinh bang": "Dien Thoai May Tinh Bang",
    "chuot": "Thiet Bi Kts Phu Kien So",
    "ban phim": "Thiet Bi Kts Phu Kien So",
    "tai nghe": "Thiet Bi Kts Phu Kien So",
    "man hinh": "Laptop May Vi Tinh Linh Kien",
    "usb": "Laptop May Vi Tinh Linh Kien",
    "o cung": "Laptop May Vi Tinh Linh Kien",
    "ram": "Laptop May Vi Tinh Linh Kien",
    "cap ket noi": "Thiet Bi Kts Phu Kien So",
    "sac laptop": "Laptop May Vi Tinh Linh Kien",
    "pin laptop": "Laptop May Vi Tinh Linh Kien",
    "loa may tinh": "Thiet Bi Kts Phu Kien So",
    "gia do laptop": "Thiet Bi Kts Phu Kien So",
    "tui laptop": "Balo Va Vali",
    "sach": "Nha Sach Tiki",
}

DISPLAY_PRODUCT = {
    "dien thoai": "điện thoại",
    "may tinh bang": "máy tính bảng",
    "chuot": "chuột",
    "ban phim": "bàn phím",
    "tai nghe": "tai nghe",
    "man hinh": "màn hình",
    "usb": "USB",
    "o cung": "ổ cứng",
    "ram": "RAM máy tính",
    "cap ket noi": "cáp kết nối",
    "sac laptop": "sạc laptop",
    "pin laptop": "pin laptop",
    "loa may tinh": "loa máy tính",
    "gia do laptop": "giá đỡ laptop",
    "tui laptop": "túi/balo laptop",
    "sach": "sách",
}

NO_PREFERENCE = {"khong", "khong can", "bat ky", "hang nao cung duoc", "sao cung duoc"}
CANCEL_WORDS = {"huy", "huy bo", "bo qua", "lam lai", "bat dau lai", "reset", "nhap lai"}

PHONE_BRANDS = [
    "apple",
    "iphone",
    "ipad",
    "samsung",
    "xiaomi",
    "oppo",
    "vivo",
    "honor",
    "realme",
    "nokia",
]

COMPUTER_ACCESSORY_BRANDS = [
    "apple",
    "macbook",
    "dell",
    "asus",
    "hp",
    "lenovo",
    "acer",
    "msi",
    "lg",
    "gigabyte",
    "huawei",
    "microsoft",
    "logitech",
    "rapoo",
    "razer",
    "corsair",
    "kingston",
    "sandisk",
    "wd",
    "toshiba",
    "transcend",
    "tp-link",
    "tplink",
    "canon",
    "brother",
    "epson",
    "viewsonic",
    "orico",
    "ugreen",
    "kaspersky",
    "bkav",
    "sony",
    "rockspace",
    "rock space",
    "jbl",
    "hxsj",
    "e-dra",
    "edra",
    "e dra",
    "dareu",
    "dareu",
]

DEVICE_BRANDS = list(dict.fromkeys(PHONE_BRANDS + COMPUTER_ACCESSORY_BRANDS))

BRAND_DISPLAY_NAMES = {
    "apple": "Apple",
    "iphone": "Apple",
    "ipad": "Apple",
    "macbook": "Apple",
    "samsung": "Samsung",
    "xiaomi": "Xiaomi",
    "oppo": "Oppo",
    "vivo": "Vivo",
    "honor": "Honor",
    "realme": "Realme",
    "nokia": "Nokia",
    "sony": "Sony",
    "rockspace": "RockSpace",
    "rock space": "RockSpace",
    "jbl": "JBL",
    "logitech": "Logitech",
    "razer": "Razer",
    "hxsj": "HXSJ",
    "e-dra": "E-DRA",
    "e dra": "E-DRA",
    "edra": "E-DRA",
    "dareu": "DareU",
    "rapoo": "Rapoo",
    "wd": "WD",
    "lg": "LG",
    "kingston": "Kingston",
    "sandisk": "SanDisk",
    "ugreen": "UGREEN",
}
