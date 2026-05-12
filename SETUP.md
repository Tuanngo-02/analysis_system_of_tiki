# 🚀 Setup Hệ Thống Tiki Recommendation - Hướng Dẫn Chạy Toàn Bộ

## 📋 Điều Kiện Tiên Quyết

- Python 3.8+
- Node.js 16+ 
- pip package manager
- Windows/Mac/Linux

## 🎯 Phần 1: Chuẩn Bị Backend

### 1.1 Cài Đặt Python Dependencies

```bash
# Điều hướng đến thư mục project
cd e:\VKU\Ki8\XLNNTN\final\project\analysis_system_of_tiki

# Kích hoạt virtual environment
.\env\Scripts\Activate.ps1

# Cài đặt dependencies (nếu chưa có)
pip install -r requirements.txt
```

### 1.2 Cấu Hình CORS cho FastAPI

Mở file `backend/app/main.py` và thêm CORS middleware:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import recommend_router, category_router

app = FastAPI(title="Tiki Recommendation API")

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(recommend_router, prefix="/api")
app.include_router(category_router, prefix="/api")
```

### 1.3 Kiểm Tra Files Cần Thiết

Đảm bảo các file model & data tồn tại:

```
backend/app/modelcategory/
├── bilstm_category_model.h5
├── tokenizer.pkl
├── label_encoder.pkl
└── tiki_word2vec.model (optional)

Root level:
├── tiki_products_info.csv
├── tiki_reviews_category.csv
└── reviews_with_sentiment.csv
```

## 🎯 Phần 2: Chạy Backend

### 2.1 Khởi Động FastAPI Server

```bash
# Từ thư mục project root (với virtual env active)
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Output mong đợi:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 2.2 Kiểm Tra API

Mở browser truy cập:
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Phần 3: Chuẩn Bị & Chạy Frontend

### 3.1 Cài Đặt Node Dependencies

Từ terminal mới (không cần python env):

```bash
# Điều hướng đến frontend
cd e:\VKU\Ki8\XLNNTN\final\project\analysis_system_of_tiki\frontend

# Cài đặt dependencies
npm install

# Hoặc nếu dùng yarn
yarn install
```

### 3.2 Khởi Động Vite Dev Server

```bash
# Chạy dev server
npm run dev

# Hoặc
yarn dev
```

**Output mong đợi:**
```
  VITE v8.0.10  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

## ✅ Phần 4: Kiểm Tra Hệ Thống

### 4.1 Backend API Test

**Test Category Prediction:**
```bash
curl -X POST "http://localhost:8000/api/category/predict" \
  -H "Content-Type: application/json" \
  -d '{"product_url":"https://tiki.vn/ao-phuong-tay-nam-giai-thoat-tay-nam-ngan-tay-gio-dong-1m24-p123456.html"}'
```

**Expected Response:**
```json
{
  "input": {
    "product_url": "https://...",
    "title": "Áo phượng tây nam..."
  },
  "prediction": {
    "category": "thoi trang",
    "confidence": 0.95,
    "model": "BiLSTM"
  }
}
```

### 4.2 Frontend Test

1. Mở browser: http://localhost:5173
2. Nhập URL sản phẩm Tiki
3. Click "Phân Loại"
4. Kiểm tra kết quả phân loại
5. Click "Tìm Gợi Ý" để xem recommendations

## 🎨 Giao Diện Frontend

### Components chính:
1. **CategoryPredictor**: Form input URL & hiện kết quả phân loại
2. **RecommendationResults**: Grid sản phẩm được gợi ý theo danh mục

### Features:
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Gradient backgrounds
- ✅ Loading states
- ✅ Error handling
- ✅ Direct links to Tiki products
- ✅ Real-time API integration

## 🔧 Troubleshooting

### Lỗi: "Connection refused" khi frontend gọi API
**Giải pháp:**
- Kiểm tra backend chạy trên port 8000
- Xác nhận CORS middleware được thêm
- Kiểm tra firewall settings

### Lỗi: "Module not found" trong Python
**Giải pháp:**
```bash
pip install tensorflow keras scikit-learn beautifulsoup4 requests numpy joblib
```

### Lỗi: "Cannot find module" trong React
**Giải pháp:**
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Backend chậm lần đầu
- BiLSTM model load lần đầu có thể mất 5-10s
- Bình thường sau lần đầu

## 📊 Performance Tips

1. **Backend:**
   - Model loaded once, reused for requests
   - CSV cached in memory
   - TF-IDF search optimized with sklearn

2. **Frontend:**
   - Components use React.memo for optimization
   - Lazy loading for recommendations
   - CSS transitions for smooth animations

## 🚨 Chú Ý Quan Trọng

1. **Tiki Crawler**
   - Thêm delay giữa requests để avoid being blocked
   - Fallback to CSV lookup nếu crawling fail

2. **Đường Dẫn File**
   - Models phải trong `backend/app/modelcategory/`
   - CSV files phải accessible từ project root
   - Dùng `_find_file()` function nếu cần

3. **Database**
   - Hiện tại không dùng SQL database
   - Tất cả data từ CSV files
   - Future: migrate to PostgreSQL/MongoDB

## 📱 Ports Sử Dụng

- **Backend**: http://127.0.0.1:8000
- **Frontend**: http://localhost:5173
- **Docs**: http://127.0.0.1:8000/docs

## 🎯 Quy Trình Sử Dụng Hàng Ngày

```bash
# Terminal 1: Backend
cd backend
.\env\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser: http://localhost:5173
```

## 📚 Tài Liệu Thêm

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- Vite Docs: https://vitejs.dev/

---

**Chúc bạn thành công! 🎉**
