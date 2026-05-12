# 🚀 Quick Start Guide - Smart Analytics System

Hướng dẫn nhanh để bắt đầu sử dụng hệ thống trong 5 phút!

## 📋 Yêu Cầu Tối Thiểu

- Python 3.13+ ✅
- Node.js 14+ ✅  
- Terminal/PowerShell ✅

---

## 🎯 Chạy Ứng Dụng
## Tạo env
```bash
pip install -r requirements.txt
```
### Terminal 1 - Backend

```bash
cd backend
.\dev
```

✅ Khi thấy dòng này, backend đã chạy:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 - Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ Khi thấy dòng này, frontend đã chạy:
```
VITE v8.0.10  ready in XXX ms

➜  Local:   http://localhost:5173/
```

---

## 🔐 Đăng Nhập

**Mở trình duyệt:** http://localhost:5173

**Tài khoản mặc định:**
- 📧 Username: `admin`
- 🔑 Password: `admin123`

---

## ✨ Chức Năng Chính

### 👤 Cho Người Dùng

1. **Đăng Ký** - Tạo tài khoản mới
2. **Phân Tích Cảm Xúc** - Nhập URL sản phẩm Tiki/Shopee
   - Kết quả: Cảm xúc (😊/😐/😞), Độ tin cậy %, Số đánh giá
3. **Gợi Ý Sản Phẩm** - Nhập URL sản phẩm
   - Kết quả: Danh sách sản phẩm tương tự

### ⚙️ Cho Admin

1. **Dashboard** - Xem thống kê hệ thống
2. **Quản Lý Người Dùng**
   - Thêm người dùng mới ➕
   - Kích hoạt/Vô hiệu người dùng 🔒/🔓
   - Xóa người dùng 🗑️

---

## 🧪 Thử Nghiệm

### Test Sentiment (Ví dụ)

```
URL: https://tiki.vn/iphone-15-pro-max-256gb-p123456.html
Kết quả:
- Sentiment: Positive
- Confidence: 85.2%
- Reviews: 1250
- Rating: 4.5/5
```

### Test Recommend

```
URL: https://tiki.vn/samsung-galaxy-s24-p789012.html
Kết quả:
- Category: Điện thoại
- Recommendations: 
  #1 iPhone 15 Pro - 92% tương tự
  #2 Google Pixel 8 - 88% tương tự
  #3 OnePlus 12 - 85% tương tự
```

---

## 📱 Giao Diện

### Thanh Navigation (Header)
```
[Logo] | Dashboard | Sentiment | Recommend | 👤 admin | Logout
```

### Trang Chính (Dashboard)
```
┌─────────────────────────────────┐
│ Xin chào, admin!                │
│ Chọn một tính năng để bắt đầu   │
├─────────────────────────────────┤
│ 📊 Sentiment  │  🎯 Recommend   │
├─────────────────────────────────┤
│ Thống Kê Sử Dụng                │
│ • 0 Lần phân tích               │
│ • 0 Lần gợi ý                   │
│ • 0 Yêu thích                   │
└─────────────────────────────────┘
```

---

## 🐛 Khắc Phục Nhanh

### Lỗi: "Port 8000 already in use"
```bash
python -m uvicorn app.main:app --reload --port 8001
```

### Lỗi: "Cannot find module"
```bash
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

### Lỗi: Database
```bash
# Xóa database cũ
rm backend/app.db

# Chạy lại
python -m uvicorn app.main:app --reload
```

---

## 📚 Tài Liệu Đầy Đủ

- **Hướng dẫn chi tiết**: [README.md](README.md)
- **Danh sách kiểm tra**: [CHECKLIST.md](CHECKLIST.md)
- **API Docs**: http://localhost:8000/docs
- **Interactive UI**: http://localhost:8000/redoc

---

## 🎓 Cấu Trúc Thư Mục

```
project/
├── backend/         ← FastAPI + SQLAlchemy
│   ├── app.main.py
│   ├── app/core/    ← Database config
│   ├── app/model/   ← User model
│   ├── app/routes/  ← API endpoints
│   └── requirements.txt
│
├── frontend/        ← React + Vite
│   ├── src/App.jsx
│   ├── src/pages/   ← Login, Dashboard, etc.
│   ├── src/components/ ← Header, Routes
│   ├── src/services/   ← API calls
│   ├── src/styles/     ← CSS files
│   └── package.json
│
├── README.md        ← Hướng dẫn đầy đủ
├── CHECKLIST.md     ← Danh sách kiểm tra
└── setup.ps1        ← Auto setup script
```

---

## 💡 Mẹo Hữu Ích

1. **Xem API docs** 📖
   - Mở http://localhost:8000/docs
   - Thử nghiệm API trực tiếp

2. **Debug Frontend** 🔧
   - Mở DevTools: F12
   - Tab Network: Xem API calls
   - Tab Console: Xem lỗi

3. **Tạo tài khoản test** 👥
   - Đăng ký username mới
   - Hoặc dùng Admin Panel tạo

4. **Reset database** 🔄
   - Xóa `backend/app.db`
   - Restart server

---

## ✅ Kiểm Tra Sau Khi Setup

- [ ] Backend chạy tại http://localhost:8000
- [ ] Frontend chạy tại http://localhost:5173
- [ ] Có thể đăng nhập bằng admin/admin123
- [ ] Dashboard hiển thị bình thường
- [ ] Có thể vào trang Sentiment
- [ ] Có thể vào trang Recommend
- [ ] Thanh navigation hiển thị đầy đủ
- [ ] Logout button hoạt động

---

## 🆘 Cần Giúp?

1. Xem error message trong console
2. Kiểm tra backend logs
3. Mở DevTools (F12) xem Network errors
4. Đọc README.md chi tiết hơn
5. Kiểm tra API docs tại /docs

---

**🎉 Thành công! Bây giờ bạn đã sẵn sàng sử dụng Smart Analytics System!**

---

*Tài liệu cập nhật: 2024*
*Phiên bản: 1.0*
