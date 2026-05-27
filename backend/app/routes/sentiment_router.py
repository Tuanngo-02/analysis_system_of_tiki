from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sentiment_service import analyze_sentiment_logic
import traceback
router = APIRouter()

class ProductURLRequest(BaseModel):
    product_url: str

@router.post("/sentiment")
async def analyze_sentiment(request: ProductURLRequest):
    try:
        # Gọi logic xử lý từ service
        result = analyze_sentiment_logic(request.product_url)
        # bỏ qua
        if result is None:
            return {
                "status": "skip",
                "message": "Sản phẩm không có review text."
            }
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")