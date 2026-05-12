import { useState } from 'react';
import CategoryPredictor from './components/CategoryPredictor';
import RecommendationResults from './components/RecommendationResults';
import './App.css';

function App() {
  const [page, setPage] = useState('home');

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🛍️ Hệ Thống Gợi Ý Sản Phẩm Tiki</h1>
          <p>Chọn chức năng phân loại hoặc gợi ý sản phẩm</p>
        </div>
      </header>

      <main className="app-main">
        {page === 'home' && (
          <section className="home-screen">
            <div className="hero-panel">
              <p className="eyebrow">FastAPI + React</p>
              <h2>Chọn một chức năng để bắt đầu</h2>
              <p className="hero-description">
                Trang phân loại sẽ dự đoán danh mục từ link sản phẩm.
                Trang gợi ý sẽ trả về các sản phẩm tương đồng ngay từ một URL Tiki.
              </p>

              <div className="home-actions">
                <button type="button" className="home-btn primary" onClick={() => setPage('category')}>
                  Phân Loại
                </button>
                <button type="button" className="home-btn secondary" onClick={() => setPage('recommend')}>
                  Gợi Ý
                </button>
              </div>
            </div>
          </section>
        )}

        {page === 'category' && (
          <section className="section-page">
            <div className="page-toolbar">
              <button type="button" className="back-btn" onClick={() => setPage('home')}>
                ← Trang chủ
              </button>
            </div>
            <CategoryPredictor />
          </section>
        )}

        {page === 'recommend' && (
          <section className="section-page">
            <div className="page-toolbar">
              <button type="button" className="back-btn" onClick={() => setPage('home')}>
                ← Trang chủ
              </button>
            </div>
            <RecommendationResults />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2024 Tiki Recommendation System | Powered by BiLSTM & TF-IDF</p>
      </footer>
    </div>
  );
}

export default App;
