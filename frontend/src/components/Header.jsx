import { NavLink, useNavigate } from "react-router-dom";
import "../styles/Header.css";

export function Header({ user, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    onLogout();
    navigate("/login");
  };

  const links = user?.role === "admin"
    ? [["/dashboard", "Tổng quan"], ["/admin", "Vận hành"]]
    : [
        ["/dashboard", "Tổng quan"],
        ["/sentiment", "Cảm xúc"],
        ["/recommend", "Gợi ý"],
        ["/compare", "So sánh"],
      ];

  return (
    <header className="header">
      <div className="header-container">
        <NavLink className="logo" to="/dashboard" aria-label="Commerce Signal — Tổng quan">
          <span className="logo-mark" aria-hidden="true"><i /><i /><i /></span>
          <span>
            <strong>Commerce Signal</strong>
            <small>Product intelligence</small>
          </span>
        </NavLink>

        <nav className="nav" aria-label="Điều hướng chính">
          <div className="nav-links">
            {links.map(([path, label]) => (
              <NavLink key={path} to={path} className={({ isActive }) => isActive ? "active" : ""}>
                {label}
              </NavLink>
            ))}
          </div>

          <div className="user-info">
            <span className="user-avatar" aria-hidden="true">{user?.username?.charAt(0).toUpperCase()}</span>
            <span className="user-copy"><strong>{user?.username}</strong><small>{user?.role}</small></span>
            <button className="logout-btn" onClick={handleLogout}>Đăng xuất</button>
          </div>
        </nav>
      </div>
    </header>
  );
}
