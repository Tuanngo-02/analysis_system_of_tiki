import { useState } from "react";
import { apiService } from "../services/api";
import "../styles/Features.css";

export function SentimentPage() {
  const [productUrl, setProductUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const data = await apiService.analyzeSentiment(productUrl, token);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentType = (label) => {
    if (label === "Tích cực" || label === "Positive") return "positive";
    if (label === "Tiêu cực" || label === "Negative") return "negative";
    return "neutral";
  };

  const getSentimentColor = (label) => {
    const type = getSentimentType(label);

    if (type === "positive") return "#22c55e";
    if (type === "negative") return "#ef4444";
    return "#f59e0b";
  };

  const getSentimentEmoji = (label) => {
    const type = getSentimentType(label);

    if (type === "positive") return "😊";
    if (type === "negative") return "😞";
    return "😐";
  };

  const reviews = Array.isArray(result?.data) ? result.data : [];

  const positiveCount = reviews.filter(
    (item) => getSentimentType(item.label) === "positive"
  ).length;

  const negativeCount = reviews.filter(
    (item) => getSentimentType(item.label) === "negative"
  ).length;

  const neutralCount = reviews.filter(
    (item) => getSentimentType(item.label) === "neutral"
  ).length;

  return (
    <div className="feature-container">
      <div className="feature-header">
        <h2>📊 Phân Tích Cảm Xúc Sản Phẩm</h2>
        <p>Nhập URL sản phẩm để phân tích cảm xúc từ đánh giá của khách hàng</p>
      </div>

      <form onSubmit={handleAnalyze} className="feature-form">
        <div className="form-group">
          <label htmlFor="productUrl">URL Sản Phẩm:</label>
          <input
            type="url"
            id="productUrl"
            value={productUrl}
            onChange={(e) => setProductUrl(e.target.value)}
            placeholder="https://tiki.vn/... hoặc https://shopee.vn/..."
            required
          />
        </div>

        <button type="submit" disabled={loading} className="analyze-btn">
          {loading ? "⏳ Đang phân tích..." : "🔍 Phân Tích"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className="result-container">
          <div className="result-card">
            <div className="result-header">
              <h3>📈 Kết Quả Phân Tích</h3>

              <span className="total-review">
                {reviews.length} đánh giá
              </span>
            </div>

            <div className="stats-grid">
              <div className="stat-card positive-stat">
                <span className="stat-icon">😊</span>
                <div>
                  <h4>{positiveCount}</h4>
                  <p>Tích cực</p>
                </div>
              </div>

              <div className="stat-card negative-stat">
                <span className="stat-icon">😞</span>
                <div>
                  <h4>{negativeCount}</h4>
                  <p>Tiêu cực</p>
                </div>
              </div>

              <div className="stat-card neutral-stat">
                <span className="stat-icon">😐</span>
                <div>
                  <h4>{neutralCount}</h4>
                  <p>Trung lập</p>
                </div>
              </div>
            </div>

            {reviews.length > 0 && (
              <div className="reviews-grid">
                {reviews.map((item, index) => {
                  const confidence = Number(item.confidence || 0);
                  const sentimentType = getSentimentType(item.label);

                  return (
                    <div
                      className={`review-card ${sentimentType}-card`}
                      key={index}
                    >
                      <div className="review-top">
                        <span className="review-index">#{index + 1}</span>

                        <div
                          className={`sentiment-badge ${sentimentType}-badge`}
                        >
                          <span className="emoji">
                            {getSentimentEmoji(item.label)}
                          </span>
                          <span className="sentiment-text">
                            {item.label}
                          </span>
                        </div>
                      </div>

                      <p className="review-text">{item.review}</p>

                      <div className="metric">
                        <div className="metric-row">
                          <span className="label">Độ tin cậy:</span>
                          <span className="value">
                            {(confidence * 100).toFixed(2)}%
                          </span>
                        </div>

                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${confidence * 100}%`,
                              backgroundColor: getSentimentColor(item.label),
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {!result && !error && !loading && (
        <div className="info-box">
          <p>💡 Hãy nhập URL sản phẩm để bắt đầu phân tích cảm xúc</p>
        </div>
      )}
    </div>
  );
}