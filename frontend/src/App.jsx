import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Header } from "./components/Header";
import { PrivateRoute } from "./components/PrivateRoute";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SentimentPage } from "./pages/SentimentPage";
import { RecommendPage } from "./pages/RecommendPage";
import { AdminPage } from "./pages/AdminPage";
import "./App.css";

function App() {
 const [user, setUser] = useState(() => {
  try {
    const token = localStorage.getItem("token");
    const userStr = localStorage.getItem("user");

    if (token && userStr) {
      return JSON.parse(userStr);
    }

    return null;
  } catch {
    return null;
  }
});

  const handleLoginSuccess = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <Router>
      <div className="app">
        {user && <Header user={user} onLogout={handleLogout} />}
        <main className="main-content">
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                user ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <LoginPage onLoginSuccess={handleLoginSuccess} />
                )
              }
            />
            <Route
              path="/register"
              element={
                user ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <RegisterPage />
                )
              }
            />

            {/* User Routes */}
            <Route
              path="/dashboard"
              element={
                <PrivateRoute user={user}>
                  <DashboardPage user={user} />
                </PrivateRoute>
              }
            />
            <Route
              path="/sentiment"
              element={
                <PrivateRoute user={user}>
                  <SentimentPage user={user} />
                </PrivateRoute>
              }
            />
            <Route
              path="/recommend"
              element={
                <PrivateRoute user={user}>
                  <RecommendPage user={user} />
                </PrivateRoute>
              }
            />

            {/* Admin Routes */}
            <Route
              path="/admin"
              element={
                <PrivateRoute user={user} requiredRole="admin">
                  <AdminPage user={user} />
                </PrivateRoute>
              }
            />

            {/* Default Route */}
            <Route
              path="/"
              element={
                user ? (
                  user.role === "admin" ? (
                    <Navigate to="/admin" replace />
                  ) : (
                    <Navigate to="/dashboard" replace />
                  )
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
