"""Rasa action entrypoint for Tiki product recommendation.

Rasa still loads this module with `rasa run actions --actions actions`.
Business logic is split into smaller modules so new categories can be added
without growing this file.
"""

from __future__ import annotations

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .catalog import canonical_product, display_product, infer_brand, infer_config, infer_product
from .constants import CANCEL_WORDS, CATEGORY_BY_PRODUCT, NO_PREFERENCE
from .formatters import format_products, products_payload, slot_number, slot_product_ids
from .ranking import build_query, rank_products
from .resources import load_resources
from .text_utils import latest_entity, normalize_text, parse_price


def brand_prompt(product: Any) -> str:
    """Return brand question examples that match the selected product group."""
    if product in {"dien thoai", "may tinh bang"}:
        return (
            "Bạn muốn hãng nào? Ví dụ: Samsung, Xiaomi, Apple. "
            "Nếu không yêu cầu hãng, nhắn 'bất kỳ'."
        )
    if product == "tai nghe":
        return (
            "Bạn muốn hãng nào? Ví dụ: Sony, RockSpace, JBL, Logitech. "
            "Nếu không yêu cầu hãng, nhắn 'bất kỳ'."
        )
    if product == "chuot":
        return (
            "Bạn muốn hãng nào? Ví dụ: Razer, HXSJ, Logitech. "
            "Nếu không yêu cầu hãng, nhắn 'bất kỳ'."
        )
    if product == "ban phim":
        return (
            "Bạn muốn hãng nào? Ví dụ: Logitech, E-DRA, DareU. "
            "Nếu không yêu cầu hãng, nhắn 'bất kỳ'."
        )
    return (
        "Bạn muốn hãng nào? Ví dụ: Logitech, Dell, LG, WD, Kingston, SanDisk, UGREEN. "
        "Nếu không yêu cầu hãng, nhắn 'bất kỳ'."
    )


def numeric_entity(tracker: Tracker, entity_name: str) -> float | None:
    """Read a numeric entity from the latest message when Rasa extracts one."""
    value = latest_entity(tracker, entity_name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


class ActionRecommendProduct(Action):
    """Collect missing fields and recommend products for supported categories."""

    def name(self) -> Text:
        return "action_recommend_product"

    @staticmethod
    def reset_events() -> List[Dict[Text, Any]]:
        return [
            SlotSet("loai_san_pham", None),
            SlotSet("gia_toi_thieu", None),
            SlotSet("gia_toi_da", None),
            SlotSet("thuong_hieu", None),
            SlotSet("cau_hinh", None),
            SlotSet("requested_field", "loai_san_pham"),
            SlotSet("previous_results", None),
            SlotSet("last_query", None),
            SlotSet("last_error", None),
        ]

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text = tracker.latest_message.get("text") or ""
        text_norm = normalize_text(text)
        requested = tracker.get_slot("requested_field")

        if text_norm in CANCEL_WORDS:
            dispatcher.utter_message(
                text="Mình đã hủy thông tin cũ. Bạn muốn mua điện thoại, máy tính bảng, sách hay phụ kiện máy tính như chuột, bàn phím, tai nghe, ổ cứng, RAM, USB, cáp, sạc, pin, màn hình, loa, giá đỡ, túi laptop?"
            )
            return self.reset_events()

        generic_start = text_norm in {
            "toi muon mua san pham",
            "minh muon mua san pham",
            "mua san pham",
            "tu van mua hang",
            "toi can tu van",
        }
        if generic_start:
            dispatcher.utter_message(text="Bạn muốn mua điện thoại, máy tính bảng, sách hay phụ kiện máy tính như chuột, bàn phím, tai nghe, ổ cứng, RAM, USB, cáp, sạc, pin, màn hình, loa, giá đỡ, túi laptop?")
            return self.reset_events()

        product = canonical_product(latest_entity(tracker, "loai_san_pham")) or infer_product(text)
        brand = latest_entity(tracker, "thuong_hieu") or infer_brand(text)
        price_min, price_max = parse_price(text)
        price_min = price_min if price_min is not None else numeric_entity(tracker, "gia_toi_thieu")
        price_max = price_max if price_max is not None else numeric_entity(tracker, "gia_toi_da")
        config = latest_entity(tracker, "cau_hinh") or infer_config(text, product)

        if requested == "loai_san_pham" and not product:
            product = canonical_product(text) or text.strip()
        if requested == "gia_toi_da" and price_min is None and price_max is None:
            price_min, price_max = parse_price(f"giá {text}")
            if price_min is None and price_max is None:
                _, price_max = parse_price(f"giá khoảng {text}")
        if requested == "thuong_hieu" and not brand:
            brand = "any" if text_norm in NO_PREFERENCE else text.strip()
        if requested == "cau_hinh" and not config:
            config = "any" if text_norm in NO_PREFERENCE else text.strip()

        if requested == "thuong_hieu":
            product = tracker.get_slot("loai_san_pham") or product
            price_min = tracker.get_slot("gia_toi_thieu")
            price_max = tracker.get_slot("gia_toi_da")
            config = tracker.get_slot("cau_hinh")
        elif requested == "cau_hinh":
            product = tracker.get_slot("loai_san_pham") or product
            price_min = tracker.get_slot("gia_toi_thieu")
            price_max = tracker.get_slot("gia_toi_da")
            brand = tracker.get_slot("thuong_hieu") or brand
        else:
            price_min = price_min if price_min is not None else tracker.get_slot("gia_toi_thieu")
            price_max = price_max if price_max is not None else tracker.get_slot("gia_toi_da")
            brand = brand or tracker.get_slot("thuong_hieu")
            config = config or tracker.get_slot("cau_hinh")

        product = canonical_product(product) or canonical_product(tracker.get_slot("loai_san_pham")) or product

        events: List[Dict[Text, Any]] = [
            SlotSet("loai_san_pham", product),
            SlotSet("gia_toi_thieu", slot_number(price_min)),
            SlotSet("gia_toi_da", slot_number(price_max)),
            SlotSet("thuong_hieu", brand),
            SlotSet("cau_hinh", config),
        ]

        if product not in CATEGORY_BY_PRODUCT:
            dispatcher.utter_message(
                text="Hiện tại mình hỗ trợ điện thoại, máy tính bảng, sách và phụ kiện máy tính như chuột, bàn phím, tai nghe, ổ cứng, RAM, USB, cáp kết nối, sạc/pin laptop, màn hình, loa, giá đỡ, túi laptop. Bạn muốn mua loại nào?"
            )
            return events + [SlotSet("loai_san_pham", None), SlotSet("requested_field", "loai_san_pham")]

        if product == "sach" and not config:
            dispatcher.utter_message(
                text="Bạn muốn loại sách/chủ đề/tên sách nào? Ví dụ: tiểu thuyết, kinh doanh, Conan, IELTS. Nếu không yêu cầu, nhắn 'bất kỳ'."
            )
            return events + [SlotSet("requested_field", "cau_hinh")]

        if price_min is None and price_max is None:
            dispatcher.utter_message(text=f"Bạn muốn mua {display_product(product)} giá tầm bao nhiêu?")
            return events + [SlotSet("requested_field", "gia_toi_da")]

        if product != "sach" and not brand:
            dispatcher.utter_message(text=brand_prompt(product))
            return events + [SlotSet("requested_field", "thuong_hieu")]

        if product != "sach" and not config:
            if CATEGORY_BY_PRODUCT.get(str(product)) in {
                "Laptop May Vi Tinh Linh Kien",
                "Thiet Bi Kts Phu Kien So",
                "Balo Va Vali",
            }:
                dispatcher.utter_message(
                    text="Bạn cần loại/nhu cầu gì thêm? Ví dụ: không dây, bluetooth, gaming, chống ồn, USB 3.0, Type-C, HDMI, SSD, DDR4. Nếu không yêu cầu, nhắn 'bất kỳ'."
                )
            else:
                dispatcher.utter_message(
                    text="Bạn cần cấu hình hoặc nhu cầu gì? Ví dụ: iPhone 15 Pro, RAM 8GB, pin trâu, camera tốt. Nếu không yêu cầu, nhắn 'bất kỳ'."
                )
            return events + [SlotSet("requested_field", "cau_hinh")]

        if product == "sach" and not brand:
            brand = "any"
            events[3] = SlotSet("thuong_hieu", brand)

        try:
            model, index, products = load_resources()
            ranked = rank_products(
                model=model,
                index=index,
                products=products,
                product=str(product),
                price_min=int(price_min) if price_min else None,
                price_max=int(price_max) if price_max else None,
                brand=str(brand) if brand else None,
                config=str(config) if config else None,
            )
        except Exception as exc:
            dispatcher.utter_message(text=f"Mình chưa đọc được dữ liệu sản phẩm: {exc}")
            return events + [SlotSet("last_error", str(exc))]

        if ranked.empty:
            dispatcher.utter_message(
                text="Mình chưa tìm được sản phẩm phù hợp. Bạn thử đổi ngân sách hoặc mô tả nhu cầu rộng hơn nhé."
            )
            return events + [SlotSet("requested_field", None)]

        category = CATEGORY_BY_PRODUCT[str(product)]
        dispatcher.utter_message(
            text=format_products(ranked, category),
            json_message={
                "type": "product_recommendations",
                "category": category,
                "products": products_payload(ranked),
            },
        )
        return events + [
            SlotSet("requested_field", None),
            SlotSet("previous_results", slot_product_ids(ranked["product_id"])),
            SlotSet("last_query", build_query(str(product), category, price_max, str(brand), str(config))),
            SlotSet("last_error", None),
        ]
