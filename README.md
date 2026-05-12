# 📊 Smart Analytics System

## Hệ Thống Phân Tích Cảm Xúc và Gợi Ý Sản Phẩm

Một ứng dụng web full-stack với các chức năng phân tích cảm xúc từ đánh giá sản phẩm và gợi ý sản phẩm tương tự. Hệ thống hỗ trợ hai vai trò: Admin (quản lý người dùng) và User (sử dụng tính năng phân tích).

---

## 🚀 Các Tính Năng Chính

### ✨ Cho Người Dùng (User)
- **📊 Phân Tích Cảm Xúc**: Phân tích cảm xúc từ đánh giá sản phẩm (Positive/Negative/Neutral)
- **🎯 Gợi Ý Sản Phẩm**: Nhận gợi ý các sản phẩm tương tự dựa trên phân loại
- **👤 Quản Lý Tài Khoản**: Đăng nhập, đăng ký tài khoản
- **📈 Dashboard**: Xem thống kê sử dụng

### ⚙️ Cho Quản Trị Viên (Admin)
- **👥 Quản Lý Người Dùng**: Thêm, xóa, kích hoạt/vô hiệu người dùng
- **📊 Thống Kê Hệ Thống**: Xem tổng quan các chỉ số quan trọng
- **🔐 Quản Lý Quyền**: Phân quyền giữa Admin và User
- **ℹ️ Thông Tin Hệ Thống**: Xem trang thái hoạt động của hệ thống

---

## 📋 Yêu Cầu Hệ Thống

- Python 3.8+
- Node.js 14+ (cho frontend)
- npm hoặc yarn

---

## ⚙️ Cài Đặt và Chạy

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

## 🔐 Tài Khoản Mặc Định

Khi lần đầu chạy, hệ thống sẽ tự động tạo tài khoản admin:

**Admin Account:**
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Role**: Admin

**Để tạo tài khoản Admin thủ công** (nếu cần):

1. Mở Python shell trong thư mục backend:
```bash
python
```

2. Chạy các lệnh sau:
```python
from app.core.database import SessionLocal, Base, engine
from app.model.user_model import User
from app.services.auth_service import hash_password

# Tạo tables
Base.metadata.create_all(bind=engine)

# Tạo session
db = SessionLocal()

# Tạo admin user
admin_user = User(
    username="admin",
    email="admin@example.com",
    hashed_password=hash_password("admin123"),
    role="admin"
)
db.add(admin_user)
db.commit()
print("Admin user created successfully!")
```

---

## 📱 Hướng Dẫn Sử Dụng

### Cho Người Dùng (User)

1. **Đăng Ký Tài Khoản**
   - Nhấp vào "Đăng ký ngay" trên trang login
   - Nhập username, email, và password
   - Xác nhận mật khẩu
   - Nhấp "Đăng Ký"

2. **Đăng Nhập**
   - Nhập username và password
   - Nhấp "Đăng Nhập"

3. **Phân Tích Cảm Xúc**
   - Chọn "Sentiment" từ menu
   - Nhập URL sản phẩm (Tiki/Shopee)
   - Nhấp "Phân Tích"
   - Xem kết quả: cảm xúc, độ tin cậy, số đánh giá, rating

4. **Gợi Ý Sản Phẩm**
   - Chọn "Recommend" từ menu
   - Nhập URL sản phẩm
   - Nhấp "Tìm Gợi Ý"
   - Xem danh sách sản phẩm được gợi ý

### Cho Quản Trị Viên (Admin)

1. **Đăng Nhập Admin**
   - Đăng nhập với tài khoản admin
   - Tự động chuyển đến Admin Panel

2. **Quản Lý Người Dùng**
   - Xem danh sách tất cả người dùng
   - Thêm người dùng mới: Nhấp "Thêm Người Dùng"
   - Vô hiệu/Kích hoạt người dùng: Nhấp biểu tượng 🔒/🔓
   - Xóa người dùng: Nhấp biểu tượng 🗑️

3. **Xem Thống Kê**
   - Tổng người dùng
   - Người dùng hoạt động
   - Tổng phân tích
   - Trạng thái hệ thống

---

## 🗄️ Cấu Trúc Cơ Sở Dữ Liệu

### Bảng Users
```
- id: Integer (Primary Key)
- username: String (Unique)
- email: String (Unique)
- hashed_password: String
- role: String (admin/user)
- is_active: Boolean
- created_at: DateTime
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký tài khoản
- `POST /api/auth/login` - Đăng nhập

### Features
- `POST /api/sentiment` - Phân tích cảm xúc
- `POST /api/recommend` - Gợi ý sản phẩm

---

## 🛠️ Công Nghệ Sử Dụng

### Backend
- **FastAPI**: Framework web hiệu suất cao
- **SQLAlchemy**: ORM cho database
- **Pydantic**: Validation dữ liệu
- **Passlib + Bcrypt**: Mã hóa mật khẩu
- **PyJWT**: JWT token authentication
- **SQLite**: Database nhẹ

### Frontend
- **React 19**: UI library
- **React Router DOM**: Navigation
- **CSS**: Styling

---

## 📊 Dữ Liệu Mẫu

Sau khi tạo tài khoản Admin, bạn có thể:

1. **Đăng nhập bằng Admin** để truy cập Admin Panel
2. **Tạo tài khoản User mới** thông qua:
   - Admin Panel > Thêm Người Dùng
   - Hoặc tự đăng ký trên trang Register

3. **Thử nghiệm các tính năng**:
   - Phân tích cảm xúc: Sử dụng URL sản phẩm thực từ Tiki/Shopee
   - Gợi ý sản phẩm: Nhập URL sản phẩm để nhận gợi ý

---

## ⚠️ Lưu Ý Quan Trọng

1. **Database**: Ứng dụng sử dụng SQLite (`app.db`), tự động tạo khi chạy lần đầu
2. **CORS**: Đã bật cho phép frontend gọi API từ localhost
3. **Token**: Access token hết hạn sau 30 phút
4. **Password**: Tối thiểu 6 ký tự khi đăng ký

---

## 🐛 Khắc Phục Sự Cố

### Backend không chạy
```bash
# Kiểm tra port 8000 có bị chiếm không
# Hoặc chạy trên port khác:
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend không kết nối được backend
- Kiểm tra URL backend trong `src/services/api.js`
- Đảm bảo backend đang chạy tại `http://localhost:8000`

### Database bị lỗi
```bash
# Xóa file database và chạy lại
rm backend/app.db
python -m uvicorn app.main:app --reload
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs trong terminal
2. Xem API docs tại `http://localhost:8000/docs`
3. Kiểm tra Network tab trong browser developer tools

---

## 📄 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại

---

## 🎯 Phát Triển Tiếp Theo

- [ ] Lưu trữ lịch sử phân tích
- [ ] Export kết quả thành PDF
- [ ] Biểu đồ thống kê chi tiết
- [ ] Gợi ý sản phẩm thông minh hơn
- [ ] Multi-language support
- [ ] Mobile app version

---

**Được tạo với ❤️ bằng React, FastAPI, và SQLAlchemy**
