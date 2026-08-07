import { useNavigate } from "react-router-dom";
import "../styles/Dashboard.css";

export function DashboardPage({ user }) {
  const navigate = useNavigate();
  const features = [
    {
      id: "01",
      eyebrow: "Voice of customer",
      title: "Đọc cảm xúc đánh giá",
      description: "Biến hàng trăm nhận xét thành tín hiệu tích cực, tiêu cực và mức độ tin cậy dễ đọc.",
      path: "/sentiment",
      meta: "BiLSTM · Tiki reviews",
    },
    {
      id: "02",
      eyebrow: "Product discovery",
      title: "Tìm sản phẩm phù hợp",
      description: "Phân loại sản phẩm và đề xuất lựa chọn liên quan từ dữ liệu danh mục thực tế.",
      path: "/recommend",
      meta: "Category model · Similarity",
    },
    {
      id: "03",
      eyebrow: "Decision support",
      title: "Đặt hai sản phẩm lên bàn cân",
      description: "Đối chiếu khác biệt, ưu điểm và khuyến nghị trước khi đưa ra quyết định mua.",
      path: "/compare",
      meta: "Tiki API · Structured compare",
    },
  ];

  return (
    <div className="dashboard-container">
      <section className="welcome-section">
        <div className="welcome-copy">
          <span className="page-kicker">Bàn phân tích / hôm nay</span>
          <h2>Chào {user?.username},<br />bạn muốn hiểu sản phẩm theo hướng nào?</h2>
          <p>Mỗi công cụ biến dữ liệu mua sắm thành một quyết định rõ ràng hơn.</p>
        </div>
        <div className="signal-display" aria-label="Hệ thống sẵn sàng">
          <span className="signal-status"><i /> Hệ thống sẵn sàng</span>
          <div className="signal-chart" aria-hidden="true">
            {[24, 38, 31, 54, 46, 70, 62, 84, 72, 94].map((height, index) => (
              <i key={index} style={{ height: `${height}%` }} />
            ))}
          </div>
          <small>Luồng dữ liệu trực tiếp</small>
        </div>
      </section>

      <section className="features-grid" aria-label="Công cụ phân tích">
        {features.map((feature) => (
          <article key={feature.id} className="feature-card" onClick={() => navigate(feature.path)}>
            <div className="feature-index">{feature.id}</div>
            <div className="feature-card-copy">
              <span>{feature.eyebrow}</span>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <small>{feature.meta}</small>
            </div>
            <button className="feature-btn" aria-label={`Mở ${feature.title}`}>Mở công cụ <span>↗</span></button>
          </article>
        ))}
      </section>

      <section className="stats-section">
        <div className="stats-heading">
          <span className="page-kicker">Nhật ký sử dụng</span>
          <h3>Hoạt động trong phiên</h3>
        </div>
        <div className="stats-grid">
          <div className="stat-card"><span className="stat-number">00</span><span className="stat-label">Phân tích cảm xúc</span></div>
          <div className="stat-card"><span className="stat-number">00</span><span className="stat-label">Lượt gợi ý</span></div>
          <div className="stat-card"><span className="stat-number">00</span><span className="stat-label">Lượt so sánh</span></div>
        </div>
      </section>
    </div>
  );
}
