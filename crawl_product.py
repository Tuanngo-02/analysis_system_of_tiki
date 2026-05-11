import pandas as pd
import requests
import time
import os

from bs4 import BeautifulSoup

# =========================
# CONFIG
# =========================
INPUT_FILE = "tiki_reviews_category.csv"
OUTPUT_FILE = "tiki_products_info.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# LOAD PRODUCT IDS
# =========================
df = pd.read_csv(INPUT_FILE)

# Xóa null + trùng ID
product_ids = (
    df["product_id"]
    .dropna()
    .drop_duplicates()
    .astype(str)
    .tolist()
)

print(f"Tổng product_id duy nhất: {len(product_ids)}")

# =========================
# TẠO FILE NẾU CHƯA CÓ
# =========================
if not os.path.exists(OUTPUT_FILE):
    pd.DataFrame(columns=[
        "product_id",
        "name",
        "price",
        "original_price",
        "rating_average",
        "review_count",
        "inventory_status",
        "brand",
        "seller",
        "short_description",
        "description",
        "thumbnail_url",
        "category_id",
        "product_url"
    ]).to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

# =========================
# LOAD PRODUCT IDS ĐÃ CÀO
# =========================
existing_ids = set()

if os.path.exists(OUTPUT_FILE):
    try:
        existing_df = pd.read_csv(
            OUTPUT_FILE,
            usecols=["product_id"],
            dtype={"product_id": str}
        )
        existing_ids = set(existing_df["product_id"].dropna().astype(str))
        print(f"Đã có sẵn {len(existing_ids)} product_id trong {OUTPUT_FILE}")
    except Exception as e:
        print(f"Không thể đọc product_id đã có từ {OUTPUT_FILE}: {e}")

# =========================
# HÀM LÀM SẠCH HTML
# =========================
def clean_html(html_text):
    if not html_text:
        return ""

    soup = BeautifulSoup(html_text, "html.parser")

    # Xóa script/style
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    # Xóa khoảng trắng thừa
    text = " ".join(text.split())

    return text

# =========================
# CRAWL TỪNG SẢN PHẨM
# =========================
for index, pid in enumerate(product_ids):

    if pid in existing_ids:
        print(f"[{index+1}] SKIP {pid} - đã có trong {OUTPUT_FILE}")
        continue

    try:
        api_url = f"https://tiki.vn/api/v2/products/{pid}"

        response = requests.get(
            api_url,
            headers=HEADERS,
            timeout=15
        )

        if response.status_code != 200:
            print(f"[{index+1}] FAIL {pid} - Status: {response.status_code}")
            continue

        data = response.json()

        # =========================
        # LẤY MÔ TẢ + CLEAN HTML
        # =========================
        short_description = clean_html(
            data.get("short_description", "")
        )

        description = clean_html(
            data.get("description", "")
        )

        # =========================
        # PRODUCT INFO
        # =========================
        product_info = {
            "product_id": pid,
            "name": data.get("name"),
            "price": data.get("price"),
            "original_price": data.get("original_price"),
            "rating_average": data.get("rating_average"),
            "review_count": data.get("review_count"),
            "inventory_status": data.get("inventory_status"),

            "brand": (
                data.get("brand", {})
                .get("name")
                if data.get("brand")
                else None
            ),

            "seller": (
                data.get("current_seller", {})
                .get("name")
                if data.get("current_seller")
                else None
            ),

            "short_description": short_description,
            "description": description,

            "thumbnail_url": data.get("thumbnail_url"),

            "category_id": (
                data.get("categories", {}).get("id")
                if isinstance(data.get("categories"), dict)
                else None
            ),

            "product_url": f"https://tiki.vn/p{pid}.html"
        }

        # =========================
        # LƯU NGAY SAU MỖI SẢN PHẨM
        # =========================
        pd.DataFrame([product_info]).to_csv(
            OUTPUT_FILE,
            mode="a",
            header=False,
            index=False,
            encoding="utf-8-sig"
        )

        existing_ids.add(pid)

        print(f"[{index+1}] DONE {pid}")

    except Exception as e:
        print(f"[{index+1}] ERROR {pid}: {e}")

    time.sleep(0.5)

print("\nHoàn thành crawl!")