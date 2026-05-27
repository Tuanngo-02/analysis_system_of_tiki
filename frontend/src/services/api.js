// API service để gọi backend
const API_BASE_URL = "http://localhost:8000/api";
const RASA_WEBHOOK_URL =
  import.meta.env.VITE_RASA_WEBHOOK_URL ||
  "http://localhost:5005/webhooks/rest/webhook";

export const apiService = {
  // Auth APIs
  register: async (username, email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, email, password, role: "user" }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Registration failed");
    }
    return response.json();
  },

  login: async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }
    return response.json();
  },

  // Sentiment API
  analyzeSentiment: async (productUrl, token) => {
    const response = await fetch(`${API_BASE_URL}/sentiment`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ product_url: productUrl }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Analysis failed");
    }
    return response.json();
  },

  // Recommend API
  // getRecommendations: async (productUrl, token) => {
  //   const response = await fetch(`${API_BASE_URL}/recommend`, {
  //     method: "POST",
  //     headers: {
  //       "Content-Type": "application/json",
  //       "Authorization": `Bearer ${token}`,
  //     },
  //     body: JSON.stringify({ product_url: productUrl }),
  //   });
  //   if (!response.ok) {
  //     const error = await response.json();
  //     throw new Error(error.detail || "Recommendation failed");
  //   }
  //   return response.json();
  // },
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

    async sendChatMessage(message, senderId) {
        try {
            const response = await fetch(RASA_WEBHOOK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sender: senderId,
                    message,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Chatbot error:', error);
            throw error;
        }
    },
};
