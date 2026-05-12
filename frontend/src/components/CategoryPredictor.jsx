import { useState } from 'react';
import apiClient from '../services/api';
import './CategoryPredictor.css';

export default function CategoryPredictor({ onPredictionComplete }) {
    const [productUrl, setProductUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [prediction, setPrediction] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!productUrl.trim()) {
            setError('Vui lòng nhập URL sản phẩm');
            return;
        }

        setLoading(true);
        setError(null);
        setPrediction(null);

        try {
            const result = await apiClient.predictCategory(productUrl);
            setPrediction(result);
            onPredictionComplete(result);
        } catch (err) {
            setError(err.message || 'Lỗi khi dự đoán danh mục. Vui lòng thử lại.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="predictor-container">
            <div className="predictor-card">
                <h2>🔍 Phân Loại Sản Phẩm</h2>
                <p className="subtitle">Nhập link sản phẩm Tiki để xác định danh mục</p>

                <form onSubmit={handleSubmit} className="predictor-form">
                    <div className="form-group">
                        <label htmlFor="productUrl">URL Sản Phẩm:</label>
                        <input
                            id="productUrl"
                            type="url"
                            placeholder="https://tiki.vn/..."
                            value={productUrl}
                            onChange={(e) => setProductUrl(e.target.value)}
                            disabled={loading}
                            className="url-input"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="submit-btn"
                    >
                        {loading ? 'Đang xử lý...' : 'Phân Loại'}
                    </button>
                </form>

                {error && (
                    <div className="error-message">
                        ❌ {error}
                    </div>
                )}

                {prediction && (
                    <div className="prediction-result">
                        <h3>📊 Kết Quả Phân Loại</h3>

                        {prediction.input && (
                            <div className="result-section">
                                <label>Sản Phẩm:</label>
                                <p className="result-value">{prediction.input.title || prediction.input.product_url}</p>
                            </div>
                        )}

                        {prediction.prediction && (
                            <>
                                <div className="result-section">
                                    <label>Danh Mục:</label>
                                    <p className="result-value category-name">
                                        {prediction.prediction.category}
                                    </p>
                                </div>

                                <div className="result-section">
                                    <label>Độ Tin Cậy:</label>
                                    <div className="confidence-bar">
                                        <div
                                            className="confidence-fill"
                                            style={{
                                                width: `${prediction.prediction.confidence * 100}%`,
                                            }}
                                        ></div>
                                    </div>
                                    <p className="confidence-text">
                                        {(prediction.prediction.confidence * 100).toFixed(2)}%
                                    </p>
                                </div>

                                <div className="result-section">
                                    <label>Mô Hình:</label>
                                    <p className="result-value">
                                        {prediction.prediction.model || 'BiLSTM'}
                                    </p>
                                </div>
                            </>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
