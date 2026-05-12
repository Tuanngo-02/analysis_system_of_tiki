from fastapi import FastAPI

app = FastAPI(title="FastAPI Backend")

@app.get("/")
def root():
    return {"message": "Backend is running"}

# include recommend router
from app.routes.recommend_router import router as recommend_router

app.include_router(recommend_router, prefix="/api")