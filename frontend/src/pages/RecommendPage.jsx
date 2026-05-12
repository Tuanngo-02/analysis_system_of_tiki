import { useState } from "react";
import { apiService } from "../services/api";
import "../styles/Features.css";

export function RecommendPage() {
  const [productUrl, setProductUrl] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const normalizeGroups = (suggestions) => {
    if (!suggestions) return [];

    if (Array.isArray(suggestions)) {
      return suggestions;
    }

    return Object.entries(suggestions).map(([category, products]) => ({
      category,
      products: Array.isArray(products) ? products : [products],
    }));
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined || price === "") {
      return "N/A";
    }

    const numericPrice = Number(String(price).replace(/[^\d]/g, ""));

    if (Number.isNaN(numericPrice) || numericPrice <= 0) {
      return String(price);
    }

    return `${numericPrice.toLocaleString("vi-VN")}đ`;
  };

  const handleRecommend = async (e) => {
    e.preventDefault();

    if (!productUrl.trim()) {
      setError("Vui lòng nhập URL sản phẩm");
      return;
    }

    setError("");
    setRecommendations(null);
    setLoading(true);

    try {
      const data = await apiService.getRecommendations(productUrl);
      console.log(data);
      setRecommendations(data);
    } catch (err) {
      setError(err.message || "Lỗi khi lấy gợi ý. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  const groups = normalizeGroups(recommendations?.suggestions);

  return (
    <div className="feature-container">
      <div className="feature-header">
        <h2>🎯 Gợi Ý Sản Phẩm Tương Tự</h2>
        <p>Nhập URL sản phẩm để nhận gợi ý những sản phẩm liên quan</p>
      </div>

      {!recommendations && (
        <form onSubmit={handleRecommend} className="feature-form">
          <div className="form-group">
            <label htmlFor="productUrl">URL Sản Phẩm:</label>
            <input
              type="url"
              id="productUrl"
              value={productUrl}
              onChange={(e) => setProductUrl(e.target.value)}
              placeholder="https://tiki.vn/..."
              required
              disabled={loading}
            />
          </div>

          <button type="submit" disabled={loading} className="analyze-btn">
            {loading ? "⏳ Đang tìm gợi ý..." : "🔍 Tìm Gợi Ý"}
          </button>
        </form>
      )}

      {error && <div className="error-message">❌ {error}</div>}

      {recommendations && (
        <div className="result-container">
          <div className="result-card">
            <div className="result-header">
              <h3>📋 Sản Phẩm Được Gợi Ý</h3>

              <span className="total-review">
                {groups.reduce((sum, group) => sum + group.products.length, 0)} sản phẩm
              </span>
            </div>

            {recommendations.input && (
              <div className="input-section">
                <h3>📦 Sản Phẩm Đầu Vào</h3>

                <div className="product-info">
                  <p>
                    <strong>Tên:</strong> {recommendations.input.title}
                  </p>

                  <p>
                    <strong>URL:</strong>{" "}
                    <a
                      href={recommendations.input.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {recommendations.input.product_url}
                    </a>
                  </p>
                </div>
              </div>
            )}

            {groups.length > 0 ? (
              <div className="suggestions-section">
                <h3>✨ Danh Mục & Gợi Ý</h3>

                {groups.map((group, idx) => (
                  <div key={`${group.category}-${idx}`} className="category-group">
                    <h4 className="category-title">📂 {group.category}</h4>

                    <div className="products-grid">
                      {group.products.map((product, pidx) => {
                        const productName =
                          product.name ?? product.title ?? "Sản phẩm";

                        const productLink =
                          product.product_url ?? product.url ?? "#";

                        const rating =
                          product.rating ?? product.rating_average ?? "N/A";

                        const reviewCount =
                          product.review_count ?? product.reviews ?? 0;

                        const similarity = Number(product.similarity ?? 0);

                        return (
                          <div
                            key={`${group.category}-${pidx}`}
                            className="product-card"
                          >
                            <div className="product-rank">#{pidx + 1}</div>

                            <h4 className="product-name">{productName}</h4>

                            <div className="product-meta">
                              <span className="price">
                                💰 {formatPrice(product.price)}
                              </span>
                            </div>

                            <div className="product-meta">
                              <span className="rating">⭐ {rating}</span>
                              <span className="reviews">
                                ({reviewCount} reviews)
                              </span>
                            </div>

                            {product.similarity !== undefined && (
                              <div className="similarity-box">
                                <div className="similarity-row">
                                  <span>Độ tương tự</span>
                                  <strong>{(similarity * 100).toFixed(1)}%</strong>
                                </div>

                                <div className="progress-bar">
                                  <div
                                    className="progress-fill"
                                    style={{
                                      width: `${similarity * 100}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            )}

                            <a
                              href={productLink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="product-link"
                            >
                              Xem Chi Tiết →
                            </a>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-suggestions">
                ℹ️ Không tìm thấy gợi ý nào cho sản phẩm này. Vui lòng thử với sản phẩm khác.
              </div>
            )}

            <button
              className="reset-btn"
              style={{color: "red"}}
              onClick={() => {
                setRecommendations(null);
                setError("");
                setProductUrl("");
              }}
            >
              🔄 Tìm Sản Phẩm Khác
            </button>
          </div>
        </div>
      )}

      {!recommendations && !error && !loading && (
        <div className="info-box">
          <p>💡 Hãy nhập URL sản phẩm để nhận gợi ý những sản phẩm tương tự</p>
        </div>
      )}
    </div>
  );
}