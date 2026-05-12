import { Navigate } from "react-router-dom";

export function PrivateRoute({ children, user, requiredRole }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
