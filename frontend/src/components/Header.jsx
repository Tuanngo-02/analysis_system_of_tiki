import { useNavigate } from "react-router-dom";
import "../styles/Header.css";

export function Header({ user, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    onLogout();
    navigate("/login");
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <h1>📊 Smart Analytics</h1>
        </div>

        {user && (
          <nav className="nav">
            <div className="nav-links">
              {user.role === "admin" && (
                <>
                  <a href="/dashboard">Dashboard</a>
                  <a href="/admin">Admin Panel</a>
                </>
              )}
              {user.role === "user" && (
                <>
                  <a href="/dashboard">Dashboard</a>
                  <a href="/sentiment">Sentiment</a>
                  <a href="/recommend">Recommend</a>
                </>
              )}
            </div>

            <div className="user-info">
              <span>👤 {user.username}</span>
              <span className="role-badge">{user.role}</span>
              <button className="logout-btn" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
