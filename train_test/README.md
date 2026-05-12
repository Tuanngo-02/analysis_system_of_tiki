# 📊 Product Review Analysis - Hướng dẫn Chạy Dự Án

## 📋 Mục lục

1. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
2. [Cài đặt](#cài-đặt)
3. [Chạy ứng dụng](#chạy-ứng-dụng)
4. [Đăng nhập](#đăng-nhập)
5. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
6. [Deploy](#deploy)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Yêu cầu hệ thống

- **Python**: 3.8 hoặc cao hơn
- **OS**: Windows, macOS, hoặc Linux
- **RAM**: Tối thiểu 2GB
- **Dung lượng**: ~500MB (bao gồm dependencies)

Kiểm tra phiên bản Python:
```bash
python --version
```

---

## ⚙️ Cài đặt

### 1️⃣ Clone hoặc Download Project

```bash
# Nếu dùng Git
git clone <repository-url>
cd Scratch_review

# Hoặc download ZIP và giải nén
cd Scratch_review
```

### 2️⃣ Tạo Virtual Environment

#### **Trên Windows:**
```bash
python -m venv env

# Kích hoạt virtual environment
env\Scripts\activate
```

#### **Trên macOS/Linux:**
```bash
python3 -m venv env

# Kích hoạt virtual environment
source env/bin/activate
```

### 3️⃣ Cài đặt Dependencies

```bash
# Nâng cấp pip
pip install --upgrade pip

# Cài đặt các package
pip install -r requirements.txt
```

**Nội dung requirements.txt:**
```
streamlit
tensorflow==2.20.0
keras==3.13.2
underthesea
pandas
numpy
matplotlib
scikit-learn
```

✅ Quá trình cài đặt sẽ mất khoảng 5-10 phút

---

## 🚀 Chạy Ứng Dụng

### Cách 1: Command Line (Đơn giản nhất)

```bash
# Đảm bảo virtual environment đã kích hoạt
streamlit run app.py
```

App sẽ tự động mở ở: **http://localhost:8501**

### Cách 2: Chỉ định Port Tùy chỉnh

```bash
streamlit run app.py --server.port 8080
```

### Cách 3: Tắt Port Validation

```bash
streamlit run app.py --server.enableCORS false
```

---

## 🔐 Đăng nhập

### Tài Khoản Demo

| Role | Username | Password |
|------|----------|----------|
| 👑 Admin | `admin` | `admin123` |
| 👤 User | `user1` | `user123` |
| 👤 User | `user2` | `user123` |

---

## 📱 Hướng dẫn Sử Dụng

### 👑 Giao diện Admin

**Chức năng:**
- 📊 Xem tổng quan (tổng sản phẩm, reviews, positive/negative)
- 📋 Danh sách sản phẩm với thông tin đầy đủ
- 🔍 Tìm kiếm theo:
  - Product ID
  - Product Name
  - Category
- 📊 Sắp xếp theo bất kỳ cột nào (tăng/giảm)
- 📈 Biểu đồ Sentiment tổng thể
- 📊 Top 10 sản phẩm có điểm cao nhất
- 🔍 Xem chi tiết từng sản phẩm

### 👤 Giao diện User

**Tính năng:**
1. **Phân tích sản phẩm**
   - Nhập Product ID
   - Xem thống kê Positive/Negative %
   - Xem biểu đồ Pie chart
   - Danh sách toàn bộ reviews

2. **So sánh sản phẩm**
   - Nhập 2 Product ID
   - Metrics so sánh song song
   - Biểu đồ Pie đôi
   - Biểu đồ cột so sánh
   - Kết luận tự động
   - Tab reviews riêng cho từng sản phẩm

---

## 🌐 Deploy

### Option 1: Streamlit Cloud (⭐ Khuyên dùng)

**Bước 1:** Tạo GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/streamlit_app.git
git push -u origin main
```

**Bước 2:** Deploy trên Streamlit Cloud

1. Truy cập: https://share.streamlit.io
2. Đăng nhập bằng GitHub
3. Click "New app"
4. Chọn repository và `app.py`
5. Chờ deploy (2-5 phút)

✅ App sẽ có URL: `https://your-app-name.streamlit.app`

### Option 2: Docker + Render/Railway

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

**Deploy:**
```bash
# Push lên GitHub
git push origin main

# Truy cập Render.com hoặc Railway.app
# Kết nối với GitHub repo
# Deploy!
```

### Option 3: Heroku

```bash
heroku login
heroku create your-app-name
git push heroku main
```

---

## 🐛 Troubleshooting

### ❌ Lỗi: "ModuleNotFoundError"

**Giải pháp:**
```bash
# Kiểm tra virtual environment đã kích hoạt
which python  # macOS/Linux
where python  # Windows

# Cài lại dependencies
pip install -r requirements.txt
```

### ❌ Lỗi: "Port 8501 đang bị sử dụng"

**Giải pháp:**
```bash
# Dùng port khác
streamlit run app.py --server.port 8502

# Hoặc kill process
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8501
kill -9 <PID>
```

### ❌ Lỗi: "reviews_with_sentiment.csv not found"

**Giải pháp:**
```bash
# Đảm bảo file CSV nằm cùng folder app.py
# Hoặc chỉ đường dẫn tuyệt đối trong code:
df = pd.read_csv("D:/Scratch_review/reviews_with_sentiment.csv")
```

### ❌ Lỗi: "tensorflow/keras import error"

**Giải pháp:**
```bash
# Cài lại
pip uninstall tensorflow keras -y
pip install tensorflow==2.20.0 keras==3.13.2
```

### ⚠️ App chạy chậm

**Giải pháp:**
```bash
# Xóa cache
streamlit cache clear

# Hoặc restart
streamlit run app.py --logger.level=debug
```

---

## 📝 Cấu trúc Project

```
Scratch_review/
├── app.py                          # Main app file
├── reviews_with_sentiment.csv      # Dataset
├── bilstm_sentiment.h5             # Model (optional)
├── bilstm_sentiment.keras          # Model (optional)
├── requirements.txt                # Dependencies
├── README.md                       # Hướng dẫn này
└── env/                            # Virtual environment
    ├── bin/
    ├── lib/
    └── pyvenv.cfg
```

---

## ✨ Các Tính Năng Chính

### 🎨 UI/UX
- ✅ Thiết kế hiện đại với gradient colors
- ✅ Loading spinner cho mọi thao tác
- ✅ Toast notifications (thông báo trạng thái)
- ✅ Responsive design

### 🔐 Security
- ✅ Login/Logout system
- ✅ Role-based access (Admin/User)
- ✅ Session management

### 📊 Features
- ✅ Phân tích sentiment sản phẩm
- ✅ So sánh hai sản phẩm
- ✅ Tìm kiếm & lọc nâng cao
- ✅ Sắp xếp linh hoạt
- ✅ Biểu đồ trực quan

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề:

1. Kiểm tra Internet connection
2. Xóa cache: `streamlit cache clear`
3. Restart app: `Ctrl+C` rồi chạy lại
4. Cập nhật packages: `pip install -r requirements.txt --upgrade`
5. Báo cáo issue trên GitHub

---

## 📄 License

MIT License - Tự do sử dụng cho mục đích học tập và thương mại

---

## 🎓 Tác giả

**Ứng dụng Phân tích Review Sản phẩm** - Product Review Analysis System

---

**🌟 Chúc bạn sử dụng vui vẻ!** 🌟
