import { Navigate } from "react-router-dom";

export function ProtectedRoute({ children }: { children: JSX.Element }) {
  const access_token = localStorage.getItem("access_token");

  return access_token ? children : <Navigate to="/login" replace />;
}
