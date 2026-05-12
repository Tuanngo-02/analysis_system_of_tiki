import { useState } from 'react';
import apiClient from '../services/api';
import './RecommendationResults.css';

export default function RecommendationResults() {
    const [productUrl, setProductUrl] = useState('');
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const normalizeGroups = (suggestions) => {
        if (!suggestions) return [];
        if (Array.isArray(suggestions)) return suggestions;

        return Object.entries(suggestions).map(([category, products]) => ({
            category,
            products: Array.isArray(products) ? products : [products],
        }));
    };

    const formatPrice = (price) => {
        if (price === null || price === undefined || price === '') {
            return 'N/A';
        }

        const numericPrice = Number(String(price).replace(/[^\d]/g, ''));
        if (Number.isNaN(numericPrice) || numericPrice <= 0) {
            return String(price);
        }

        return `${numericPrice.toLocaleString('vi-VN')}đ`;
    };

    const groups = normalizeGroups(recommendations?.suggestions);

    const handleGetRecommendations = async (e) => {
        e.preventDefault();

        if (!productUrl.trim()) {
            setError('Vui lòng nhập URL sản phẩm');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const result = await apiClient.getRecommendations(productUrl);
            setRecommendations(result);
        } catch (err) {
            setError(err.message || 'Lỗi khi lấy gợi ý. Vui lòng thử lại.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="recommendations-container">
            <div className="recommendations-card">
                <h2>💡 Gợi Ý Sản Phẩm</h2>
                <p className="subtitle">Nhập link sản phẩm Tiki để lấy danh sách gợi ý</p>

                {!recommendations && (
                    <form className="recommendation-form" onSubmit={handleGetRecommendations}>
                        <div className="form-group">
                            <label htmlFor="recommendationUrl">URL Sản Phẩm:</label>
                            <input
                                id="recommendationUrl"
                                type="url"
                                placeholder="https://tiki.vn/..."
                                value={productUrl}
                                onChange={(e) => setProductUrl(e.target.value)}
                                disabled={loading}
                                className="url-input"
                            />
                        </div>

                        <button type="submit" className="get-recommendations-btn" disabled={loading}>
                            {loading ? 'Đang tìm gợi ý...' : '🔎 Gợi Ý'}
                        </button>
                    </form>
                )}

                {error && (
                    <div className="error-message">
                        ❌ {error}
                    </div>
                )}

                {recommendations && (
                    <div className="recommendations-result">
                        {recommendations.input && (
                            <div className="input-section">
                                <h3>📦 Sản Phẩm Đầu Vào</h3>
                                <div className="product-info">
                                    <p><strong>Tên:</strong> {recommendations.input.title}</p>
                                    <p><strong>URL:</strong> <a href={recommendations.input.product_url} target="_blank" rel="noopener noreferrer">{recommendations.input.product_url}</a></p>
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
                                                const rating = product.rating ?? product.rating_average ?? 'N/A';
                                                const reviewCount = product.review_count ?? product.reviews ?? 0;
                                                const productName = product.name ?? product.title ?? 'Sản phẩm';
                                                const productUrl = product.product_url ?? product.url ?? '#';

                                                return (
                                                    <div key={`${group.category}-${pidx}`} className="product-card">
                                                        <div className="product-name">{productName}</div>
                                                        <div className="product-meta">
                                                            <span className="price">💰 {formatPrice(product.price)}</span>
                                                        </div>
                                                        <div className="product-meta">
                                                            <span className="rating">⭐ {rating}</span>
                                                            <span className="reviews">({reviewCount} reviews)</span>
                                                        </div>
                                                        {product.similarity !== undefined && (
                                                            <div className="product-meta">
                                                                <span className="similarity">
                                                                    Similarity: {(Number(product.similarity) * 100).toFixed(1)}%
                                                                </span>
                                                            </div>
                                                        )}
                                                        <a
                                                            href={productUrl}
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
                            onClick={() => {
                                setRecommendations(null);
                                setError(null);
                                setProductUrl('');
                            }}
                        >
                            🔄 Tìm Sản Phẩm Khác
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
