import { useNavigate } from "react-router-dom";
import "../styles/Dashboard.css";

export function DashboardPage({ user }) {
  const navigate = useNavigate();

  const features = [
    {
      id: 1,
      title: "📊 Phân Tích Cảm Xúc",
      description: "Phân tích cảm xúc từ các đánh giá sản phẩm trên Tiki/Shopee",
      icon: "😊",
      path: "/sentiment",
      color: "#3498db",
    },
    {
      id: 2,
      title: "🎯 Gợi Ý Sản Phẩm",
      description: "Nhận gợi ý sản phẩm tương tự dựa trên phân loại",
      icon: "🔍",
      path: "/recommend",
      color: "#e74c3c",
    },
    {
      id: 3,
      title: "So Sanh San Pham",
      description: "Nhap 2 link Tiki de tao API lay du lieu so sanh",
      icon: "SS",
      path: "/compare",
      color: "#16a34a",
    },
  ];

  return (
    <div className="dashboard-container">
      <div className="welcome-section">
        <h2>👋 Xin chào, {user?.username}!</h2>
        <p>Chọn một tính năng để bắt đầu</p>
      </div>

      <div className="features-grid">
        {features.map((feature) => (
          <div
            key={feature.id}
            className="feature-card"
            style={{ borderLeft: `4px solid ${feature.color}` }}
            onClick={() => navigate(feature.path)}
          >
            <div className="feature-icon">{feature.icon}</div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
            <button className="feature-btn">
              Sử dụng →
            </button>
          </div>
        ))}
      </div>

      <div className="stats-section">
        <h3>📈 Thống Kê Sử Dụng</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">0</div>
            <div className="stat-label">Lần phân tích</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">0</div>
            <div className="stat-label">Lần gợi ý</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">0</div>
            <div className="stat-label">Yêu thích</div>
          </div>
        </div>
      </div>
    </div>
  );
}
