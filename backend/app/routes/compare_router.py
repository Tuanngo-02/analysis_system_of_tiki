from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.services.compare_service import (
    build_compare_product_apis,
    push_compare_result_to_n8n,
)


router = APIRouter(prefix="/compare", tags=["compare"])
latest_compare_data = None


class CompareProductRequest(BaseModel):
    product_url: str
    product_url_2: Optional[str] = None
    product_id_2: Optional[str] = None


@router.post("/product-apis")
def get_compare_product_apis(request: CompareProductRequest):
    try:
        result = build_compare_product_apis(
            request.product_url,
            request.product_url_2,
            request.product_id_2,
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        result["webhook"] = push_compare_result_to_n8n(result)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/receive")
async def receive_data(request: Request):
    global latest_compare_data
    data = await request.json()
    latest_compare_data = data
    print("Data from n8n:", data)
    return {
        "ok": True,
        "received": data
    }


@router.get("/result")
def get_latest_compare_result():
    if latest_compare_data is None:
        raise HTTPException(status_code=404, detail="Chua co ket qua so sanh tu n8n.")

    return {
        "ok": True,
        "data": latest_compare_data,
    }
