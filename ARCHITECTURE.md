# 📚 Kiến Trúc & Hướng Dẫn Phát Triển - Tiki Recommendation System

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│                   (Vite + React 19)                        │
│  ┌────────────────────────────────────────────────────┐   │
│  │ CategoryPredictor  │  RecommendationResults         │   │
│  └────────────────────────────────────────────────────┘   │
│             │                           │                   │
│             └─────────────┬─────────────┘                   │
│                           │                                 │
│                    API Service Layer                        │
│                    (fetch + async)                          │
└─────────────────────────────────────────────────────────────┘
                           │
                  ╔════════╩════════╗
                  │                 │
          ┌───────▼────────┐  ┌────▼──────────┐
          │ /api/category/ │  │ /api/recommend│
          │    predict     │  │                │
          └────────────────┘  └────────────────┘
                  │                 │
          ┌───────▼──────────────────▼────────┐
          │   FastAPI Backend                 │
          │  (Python + TensorFlow)            │
          │  ┌──────────────────────────────┐ │
          │  │ CategoryPredictor Service    │ │
          │  │ - BiLSTM Model               │ │
          │  │ - Tokenizer + LabelEncoder   │ │
          │  └──────────────────────────────┘ │
          │  ┌──────────────────────────────┐ │
          │  │ RecommendationService        │ │
          │  │ - Web Crawler                │ │
          │  │ - TF-IDF Search              │ │
          │  │ - Complementary Rules        │ │
          │  └──────────────────────────────┘ │
          └───────┬──────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
    ┌───▼───────┐    ┌─────▼──────┐
    │  CSV Files│    │ ML Models  │
    │ - Products│    │ - BiLSTM   │
    │ - Reviews │    │ - Word2Vec │
    │ - Category│    │ - Embeddings
    └───────────┘    └────────────┘
```

## 📂 Cấu Trúc Thư Mục Chi Tiết

```
project/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                  # Entry point, CORS config
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── routes/
│   │   │   ├── category_router.py   # GET /api/category/predict
│   │   │   └── recommend_router.py  # GET /api/recommend
│   │   ├── services/
│   │   │   ├── category_service.py  # BiLSTM classification
│   │   │   └── recommend_service.py # Full recommendation pipeline
│   │   ├── schemas/
│   │   │   └── auth_schema.py       # Pydantic models
│   │   ├── model/
│   │   │   └── user_model.py
│   │   └── modelcategory/
│   │       ├── bilstm_category_model.h5
│   │       ├── tokenizer.pkl
│   │       ├── label_encoder.pkl
│   │       ├── tiki_word2vec.model
│   │       └── tiki_phobert_full_embeddings.npy
│   ├── dev.ps1                      # Dev startup script
│   └── requirements.txt
│
├── frontend/                        # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CategoryPredictor.jsx
│   │   │   ├── CategoryPredictor.css
│   │   │   ├── RecommendationResults.jsx
│   │   │   └── RecommendationResults.css
│   │   ├── services/
│   │   │   └── api.js               # API client
│   │   ├── App.jsx                  # Main component
│   │   ├── App.css
│   │   ├── main.jsx                 # React entry
│   │   ├── index.css                # Global styles
│   │   └── assets/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── eslint.config.js
│
├── tiki_products_info.csv           # Product database
├── tiki_reviews_category.csv        # Category mapping
├── reviews_with_sentiment.csv       # Review sentiment data
├── SETUP.md                         # Setup guide
├── quick-start.ps1                  # Windows quick start
└── quick-start.sh                   # Linux/Mac quick start
```

## 🔄 Data Flow

### 1. Category Prediction Flow

```
User Input (URL)
    │
    ▼
Frontend: CategoryPredictor
    │ POST /api/category/predict
    ▼
Backend: category_router
    │
    ▼
category_service.predict_category_from_url()
    ├─ Crawl product title from URL
    ├─ Tokenize text
    ├─ Load BiLSTM model
    ├─ Predict category
    ├─ Get confidence score
    └─ Return prediction
    │
    ▼
Frontend: Display category + confidence
```

### 2. Recommendation Flow

```
User Input (URL)
    │
    ▼
Frontend: RecommendationResults
    │ POST /api/recommend
    ▼
Backend: recommend_router
    │
    ▼
recommend_service.recommend_product()
    ├─ Crawl product title
    ├─ Classify with BiLSTM
    ├─ Map to complementary categories
    ├─ Search TF-IDF in each category
    ├─ Rank by similarity score
    ├─ Return top products per category
    └─ Format response
    │
    ▼
Frontend: Display recommendations grid
```

## 🛠️ Key Technologies

### Backend
- **FastAPI**: Web framework, async support
- **TensorFlow/Keras**: BiLSTM model inference
- **scikit-learn**: TF-IDF vectorization, MinMaxScaler
- **BeautifulSoup**: HTML parsing/crawling
- **Joblib**: Model persistence

### Frontend
- **React 19**: UI framework with hooks
- **Vite**: Build tool & dev server
- **CSS3**: Styling with gradients, flexbox, grid
- **Fetch API**: HTTP requests

### Data
- **CSV Files**: Product catalog, reviews, categories
- **Pickle Files**: Tokenizer, LabelEncoder persistence
- **Numpy**: Embedding storage/loading
- **HDF5**: Keras model format

## 📊 Data Structures

### API Request

```javascript
// Category Prediction
POST /api/category/predict
{
  "product_url": "https://tiki.vn/ao-thun-nam-p123.html"
}

// Recommendation
POST /api/recommend
{
  "product_url": "https://tiki.vn/ao-thun-nam-p123.html"
}
```

### API Response

```javascript
// Category Prediction Response
{
  "input": {
    "product_url": "https://tiki.vn/ao-thun-nam-p123.html",
    "title": "Áo thun nam cotton..."
  },
  "prediction": {
    "category": "thoi trang",
    "confidence": 0.95,
    "model": "BiLSTM"
  }
}

// Recommendation Response
{
  "input": {
    "product_url": "...",
    "title": "..."
  },
  "suggestions": {
    "Quần Jean": [
      {
        "product_id": "12345",
        "name": "Quần Jean nam...",
        "price": 250000,
        "rating": 4.8,
        "reviews": 1250,
        "product_url": "https://..."
      },
      ...
    ],
    "Giày Dép": [...],
    "Phụ Kiện": [...]
  }
}
```

## 🎨 Component Structure

### CategoryPredictor Component
```jsx
├── State
│   ├── productUrl
│   ├── loading
│   ├── error
│   └── prediction
├── Handlers
│   └── handleSubmit()
├── JSX
│   ├── Form Input
│   ├── Submit Button
│   └── Confidence Bar
```

### RecommendationResults Component
```jsx
├── State
│   ├── recommendations
│   ├── loading
│   └── error
├── Handlers
│   ├── handleGetRecommendations()
│   └── handleReset()
├── JSX
│   ├── Get Recommendations Button
│   ├── Category Groups
│   ├── Product Cards Grid
│   └── Product Links
```

## 🔌 API Integration Points

### Frontend `services/api.js`

```javascript
apiClient.predictCategory(productUrl)
  └─ Returns: { input, prediction }

apiClient.getRecommendations(productUrl)
  └─ Returns: { input, suggestions }
```

### Backend Routes

```python
@router.post("/category/predict")
def predict_category(request: ProductURLRequest)

@router.post("/recommend")
def recommend_product(request: ProductURLRequest)
```

## 🚀 Performance Considerations

### Backend
- **Model Loading**: BiLSTM loaded once on service init
- **CSV Caching**: Products/reviews cached in memory
- **TF-IDF**: Pre-fitted on startup
- **Crawler Fallback**: Uses CSV if web crawling fails

### Frontend
- **Component Memoization**: Components only re-render on needed
- **Lazy API Calls**: Recommendations loaded on demand
- **CSS Transitions**: Hardware-accelerated animations
- **Responsive Images**: CSS Grid auto-sizing

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS Error | Backend missing middleware | Add CORSMiddleware to FastAPI |
| 503 Timeout | Model loading too slow | First request slower than others |
| Empty suggestions | Category normalization | Ensure lowercase matching |
| 403 from Tiki | Anti-crawler protection | Use fallback CSV lookup |
| Node modules missing | npm install not run | Run `npm install` in frontend |

## 🧪 Testing

### Backend Testing
```bash
# Test with curl
curl -X POST http://localhost:8000/api/category/predict \
  -H "Content-Type: application/json" \
  -d '{"product_url":"https://tiki.vn/ao-thun-nam-p123.html"}'

# Swagger UI
http://localhost:8000/docs
```

### Frontend Testing
```bash
# Check API calls in DevTools
# Network tab shows requests/responses
# Console shows error messages
```

## 📈 Scaling Considerations

### For Production
1. **Database**: Replace CSV with PostgreSQL/MongoDB
2. **Caching**: Redis for model inference results
3. **Async Processing**: Celery for long-running tasks
4. **Load Balancing**: nginx/gunicorn for multiple workers
5. **Containerization**: Docker + Docker Compose

### Configuration for Scale
```python
# backend/app/core/config.py
class Settings:
    CACHE_ENABLED = True
    CACHE_TTL = 3600
    MAX_WORKERS = 4
    CRAWLER_TIMEOUT = 10
    CRAWLER_RETRIES = 3
```

## 📝 Development Workflow

### Adding New Feature

1. **Backend** (if API change needed)
   ```python
   # 1. Create/update route
   # 2. Add service logic
   # 3. Test with Swagger UI
   ```

2. **Frontend** (if UI change needed)
   ```jsx
   // 1. Create/update component
   // 2. Add API integration
   // 3. Test in browser DevTools
   ```

3. **Integration**
   ```bash
   # Run both backend & frontend
   # Test end-to-end flow
   ```

## 🎯 Future Improvements

- [ ] User authentication
- [ ] Search history/favorites
- [ ] Export recommendations
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Advanced filters
- [ ] Price comparison
- [ ] Product reviews display
- [ ] Collaborative filtering
- [ ] Real-time updates with WebSocket

---

**Tham khảo thêm:**
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Guide](https://vitejs.dev/)
- [TensorFlow.js](https://www.tensorflow.org/js)
