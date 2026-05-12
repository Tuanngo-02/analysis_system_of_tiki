// API Service for Tiki Recommendation System
const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = {
    // Predict category for a product
    async predictCategory(productUrl) {
        try {
            const response = await fetch(`${API_BASE_URL}/category/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_url: productUrl,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Category prediction error:', error);
            throw error;
        }
    },

    // Get product recommendations
    async getRecommendations(productUrl) {
        try {
            const response = await fetch(`${API_BASE_URL}/recommend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_url: productUrl,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Recommendation error:', error);
            throw error;
        }
    },
};

export default apiClient;
