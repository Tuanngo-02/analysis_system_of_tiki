import { useState, useEffect } from "react";
import "../styles/Admin.css";

export function AdminPage({ user }) {
  const [users, setUsers] = useState([
    {
      id: 1,
      username: "admin",
      email: "admin@example.com",
      role: "admin",
      is_active: true,
      created_at: "2024-01-01",
    },
  ]);

  const [stats, setStats] = useState({
    total_users: 1,
    active_users: 1,
    total_analyses: 0,
    system_health: "Healthy",
  });

  const [newUser, setNewUser] = useState({
    username: "",
    email: "",
    password: "",
    role: "user",
  });

  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddUser = () => {
    if (!newUser.username || !newUser.email || !newUser.password) {
      alert("Vui lòng điền đầy đủ thông tin");
      return;
    }

    const user = {
      id: users.length + 1,
      ...newUser,
      is_active: true,
      created_at: new Date().toISOString().split("T")[0],
    };

    setUsers([...users, user]);
    setNewUser({ username: "", email: "", password: "", role: "user" });
    setShowAddForm(false);
    alert("Thêm người dùng thành công!");
  };

  const toggleUserStatus = (userId) => {
    setUsers(
      users.map((u) =>
        u.id === userId ? { ...u, is_active: !u.is_active } : u
      )
    );
  };

  const deleteUser = (userId) => {
    if (userId === 1) {
      alert("Không thể xóa tài khoản admin");
      return;
    }
    setUsers(users.filter((u) => u.id !== userId));
    alert("Xóa người dùng thành công!");
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h2>⚙️ Bảng Điều Khiển Admin</h2>
        <p>Quản lý hệ thống và người dùng</p>
      </div>

      {/* Stats Section */}
      <div className="stats-overview">
        <div className="stat-box">
          <div className="stat-icon">👥</div>
          <div className="stat-info">
            <div className="stat-label">Tổng Người Dùng</div>
            <div className="stat-value">{stats.total_users}</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-label">Người Dùng Hoạt Động</div>
            <div className="stat-value">{stats.active_users}</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <div className="stat-label">Tổng Phân Tích</div>
            <div className="stat-value">{stats.total_analyses}</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon">🟢</div>
          <div className="stat-info">
            <div className="stat-label">Trạng Thái Hệ Thống</div>
            <div className="stat-value">{stats.system_health}</div>
          </div>
        </div>
      </div>

      {/* User Management Section */}
      <div className="user-management">
        <div className="section-header">
          <h3>📋 Quản Lý Người Dùng</h3>
          <button
            className="add-user-btn"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? "❌ Hủy" : "➕ Thêm Người Dùng"}
          </button>
        </div>

        {/* Add User Form */}
        {showAddForm && (
          <div className="add-user-form">
            <div className="form-group">
              <input
                type="text"
                placeholder="Tên đăng nhập"
                value={newUser.username}
                onChange={(e) =>
                  setNewUser({ ...newUser, username: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <input
                type="email"
                placeholder="Email"
                value={newUser.email}
                onChange={(e) =>
                  setNewUser({ ...newUser, email: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                placeholder="Mật khẩu"
                value={newUser.password}
                onChange={(e) =>
                  setNewUser({ ...newUser, password: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <select
                value={newUser.role}
                onChange={(e) =>
                  setNewUser({ ...newUser, role: e.target.value })
                }
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button className="confirm-btn" onClick={handleAddUser}>
              💾 Lưu
            </button>
          </div>
        )}

        {/* Users Table */}
        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tên Đăng Nhập</th>
                <th>Email</th>
                <th>Vai Trò</th>
                <th>Trạng Thái</th>
                <th>Ngày Tạo</th>
                <th>Hành Động</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className={u.is_active ? "" : "inactive"}>
                  <td>{u.id}</td>
                  <td>
                    <strong>{u.username}</strong>
                  </td>
                  <td>{u.email}</td>
                  <td>
                    <span className={`role-badge role-${u.role}`}>
                      {u.role}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${u.is_active ? "active" : "inactive"}`}>
                      {u.is_active ? "✅ Hoạt động" : "❌ Vô hiệu"}
                    </span>
                  </td>
                  <td>{u.created_at}</td>
                  <td className="action-buttons">
                    <button
                      className="btn-toggle"
                      onClick={() => toggleUserStatus(u.id)}
                      title={u.is_active ? "Vô hiệu" : "Kích hoạt"}
                    >
                      {u.is_active ? "🔒" : "🔓"}
                    </button>
                    <button
                      className="btn-delete"
                      onClick={() => deleteUser(u.id)}
                      title="Xóa"
                      disabled={u.id === 1}
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* System Information */}
      <div className="system-info">
        <h3>ℹ️ Thông Tin Hệ Thống</h3>
        <div className="info-grid">
          <div className="info-item">
            <span>Version:</span>
            <strong>1.0.0</strong>
          </div>
          <div className="info-item">
            <span>Environment:</span>
            <strong>Production</strong>
          </div>
          <div className="info-item">
            <span>Last Update:</span>
            <strong>{new Date().toLocaleDateString("vi-VN")}</strong>
          </div>
          <div className="info-item">
            <span>Uptime:</span>
            <strong>24/7</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
