# ==========================================================
# TIKI MULTI CATEGORY CRAWLER (20 DANH MỤC CHẠY 1 LẦN)
# - Chạy 1 lần nhiều link danh mục
# - Skip product đã có trong CSV
# - Save liên tục
# - platform = tiki
#
# pip install requests pandas
# ==========================================================

import re
import os
import time
import requests
import pandas as pd

# ==========================================================
# FILE CSV
# ==========================================================
csv_file = "tiki_reviews_category.csv"

# ==========================================================
# DANH SÁCH LINK DANH MỤC
# THÊM 20 LINK CỦA BẠN TẠI ĐÂY
# ==========================================================
category_urls = [
    "https://tiki.vn/nha-cua-doi-song/c1883",
    "https://tiki.vn/dien-thoai-may-tinh-bang/c1789",
    "https://tiki.vn/do-choi-me-be/c2549",
    "https://tiki.vn/thiet-bi-kts-phu-kien-so/c1815",
    "https://tiki.vn/dien-gia-dung/c1882",
    "https://tiki.vn/lam-dep-suc-khoe/c1520",
    "https://tiki.vn/o-to-xe-may-xe-dap/c8594",
    "https://tiki.vn/thoi-trang-nu/c931",
    "https://tiki.vn/bach-hoa-online/c4384",
    "https://tiki.vn/the-thao-da-ngoai/c1975",
    "https://tiki.vn/thoi-trang-nam/c915",
    "https://tiki.vn/laptop-may-vi-tinh-linh-kien/c1846",
    "https://tiki.vn/giay-dep-nam/c1686",
    "https://tiki.vn/dien-tu-dien-lanh/c4221",
    "https://tiki.vn/giay-dep-nu/c1703",
    "https://tiki.vn/may-anh/c1801",
    "https://tiki.vn/phu-kien-thoi-trang/c27498",
    "https://tiki.vn/dong-ho-va-trang-suc/c8371",
    "https://tiki.vn/balo-va-vali/c6000",
    "https://tiki.vn/tui-vi-nu/c976",
    "https://tiki.vn/tui-thoi-trang-nam/c27616",
    "https://tiki.vn/cham-soc-nha-cua/c15078"
]

# ==========================================================
# LOAD FILE CŨ
# ==========================================================
if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
    try:
        old_df = pd.read_csv(csv_file, encoding="utf-8-sig")

        if "product_id" in old_df.columns:
            crawled_products = set(old_df["product_id"].astype(str).unique())
        else:
            crawled_products = set()

        rows = old_df.to_dict("records")

        print("Đã load file cũ:", len(old_df), "dòng")
        print("Đã crawl:", len(crawled_products), "sản phẩm")

    except:
        rows = []
        crawled_products = set()

else:
    rows = []
    crawled_products = set()

# ==========================================================
# HEADERS
# ==========================================================
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

product_api = "https://tiki.vn/api/personalish/v1/blocks/listings"

# ==========================================================
# DUYỆT TẤT CẢ DANH MỤC
# ==========================================================
for cat_index, category_url in enumerate(category_urls, start=1):

    print("\n" + "=" * 70)
    print(f"[{cat_index}/{len(category_urls)}] Đang xử lý danh mục:")
    print(category_url)

    # ------------------------------------------------------
    # TÁCH category_id
    # ------------------------------------------------------
    match = re.search(r'/c(\d+)', category_url)

    if not match:
        print("Sai link danh mục -> bỏ qua")
        continue

    category_id = match.group(1)

    # ------------------------------------------------------
    # LẤY TÊN DANH MỤC TỪ URL
    # ------------------------------------------------------
    slug_match = re.search(r'tiki\.vn/([^/]+)/c\d+', category_url)

    if slug_match:
        slug = slug_match.group(1)
        category_name = slug.replace("-", " ").title()
    else:
        category_name = "Unknown"

    print("Category:", category_name)

    # ------------------------------------------------------
    # PAGE SẢN PHẨM
    # ------------------------------------------------------
    page = 15
    max_page = 30

    while page <= max_page:

        params = {
            "limit": 20,
            "page": page,
            "category": category_id
        }

        r = requests.get(product_api, headers=headers, params=params)

        if r.status_code != 200:
            print("Lỗi page", page)
            break

        data = r.json()
        products = data.get("data", [])

        if not products:
            print("Hết sản phẩm")
            break

        print(f"\nPage {page}: {len(products)} sản phẩm")

        # ==================================================
        # DUYỆT SẢN PHẨM
        # ==================================================
        for product in products:

            product_id = str(product.get("id"))
            product_name = product.get("name", "")
            price = product.get("price", "")
            platform = "tiki"

            # ------------------------------------------------
            # NẾU ĐÃ CRAWL -> BỎ QUA
            # ------------------------------------------------
            if product_id in crawled_products:
                print("Bỏ qua:", product_name)
                continue

            print("Đang crawl:", product_name)

            review_api = f"https://tiki.vn/api/v2/reviews?product_id={product_id}"

            page_review = 1
            has_review = False

            while page_review <= 3:

                params_review = {
                    "page": page_review,
                    "limit": 10
                }

                rr = requests.get(review_api,
                                  headers=headers,
                                  params=params_review)

                if rr.status_code != 200:
                    break

                review_data = rr.json()
                reviews = review_data.get("data", [])

                if not reviews:
                    break

                for rv in reviews:

                    rows.append({
                        "platform": platform,
                        "category": category_name,
                        "product_id": product_id,
                        "product_name": product_name,
                        "rating": rv.get("rating", ""),
                        "review_text": rv.get("content", "").strip(),
                        "created_at": rv.get("created_at", ""),
                        "price": price
                    })

                has_review = True
                page_review += 1
                time.sleep(0.5)

            # ----------------------------------------------
            # ĐÁNH DẤU ĐÃ CRAWL
            # ----------------------------------------------
            crawled_products.add(product_id)

            # ----------------------------------------------
            # SAVE NGAY
            # ----------------------------------------------
            df = pd.DataFrame(rows)
            df.to_csv(csv_file,
                      index=False,
                      encoding="utf-8-sig")

            if has_review:
                print("Đã lưu:", product_name)
            else:
                print("Không có review:", product_name)

        page += 1
        time.sleep(1)

print("\nHoàn tất toàn bộ 20 danh mục.")
print("Tổng dòng:", len(rows))