from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.model.user_model import User
from app.services.auth_service import hash_password

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create default admin user on startup
@app.on_event("startup")
def create_default_admin():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("✅ Default admin user created: admin@example.com (password: admin123)")
    db.close()

@app.get("/")
def root():
    return {"message": "Backend is running"}

# include routers
from app.routes.auth_router import router as auth_router
from app.routes.recommend_router import router as recommend_router
from app.routes.sentiment_router import router as sentiment_router
from app.routes.category_router import router as category_router
from app.routes.compare_router import router as compare_router

app.include_router(auth_router, prefix="/api")
app.include_router(recommend_router, prefix="/api")
app.include_router(sentiment_router, prefix="/api")
app.include_router(category_router, prefix="/api")
app.include_router(compare_router, prefix="/api")
