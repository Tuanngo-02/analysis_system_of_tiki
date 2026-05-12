from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.category_service import predict_category_from_url

router = APIRouter(prefix="/category", tags=["category"])


class ProductURLRequest(BaseModel):
    product_url: str


@router.post("/predict")
def predict_category(request: ProductURLRequest):
    try:
        return predict_category_from_url(request.product_url)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
