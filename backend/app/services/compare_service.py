import json
import re
from typing import Optional
from urllib import error, request


TIKI_PRODUCT_API = "https://tiki.vn/api/v2/products/{product_id}"
N8N_COMPARE_WEBHOOK_URL = (
    "https://son-ardeid-dobsonfly.ngrok-free.dev/"
    "webhook-test/aa1abc5b-eb8d-446b-9357-5790557dcb00"
)


def extract_tiki_product_id(product_url: str) -> Optional[str]:
    match = re.search(r"p(\d+)(?:\.html)?", product_url)
    return match.group(1) if match else None


def build_compare_product_apis(
    product_url: str,
    product_url_2: Optional[str] = None,
    product_id_2: Optional[str] = None,
) -> dict:
    product_id_1 = extract_tiki_product_id(product_url)
    if not product_id_1:
        return {
            "status": "error",
            "message": "Khong tim thay product_id trong link Tiki thu nhat.",
        }

    if product_url_2:
        product_id_2 = extract_tiki_product_id(product_url_2)
        if not product_id_2:
            return {
                "status": "error",
                "message": "Khong tim thay product_id trong link Tiki thu hai.",
            }

    return {
        "product_1_api": TIKI_PRODUCT_API.format(product_id=product_id_1),
        "product_2_api": TIKI_PRODUCT_API.format(product_id=product_id_2 or "PRODUCT_ID_2"),
    }


def push_compare_result_to_n8n(compare_result: dict) -> dict:
    payload = json.dumps(compare_result).encode("utf-8")
    webhook_request = request.Request(
        N8N_COMPARE_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(webhook_request, timeout=15) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            return {
                "status": "success",
                "status_code": response.status,
                "response": response_body,
            }
    except error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        return {
            "status": "error",
            "status_code": exc.code,
            "message": response_body or exc.reason,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
        }
