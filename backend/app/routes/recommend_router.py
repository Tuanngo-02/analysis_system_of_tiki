from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.recommend_service import recommend_product

router = APIRouter()


class ProductURLRequest(BaseModel):
    product_url: str


@router.post("/recommend")
def recommend(request: ProductURLRequest):
    try:
        result = recommend_product(request.product_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
