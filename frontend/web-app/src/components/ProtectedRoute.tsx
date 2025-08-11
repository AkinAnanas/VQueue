import type { JSX } from "react";
import { Navigate } from "react-router-dom";

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    console.log(token);
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default ProtectedRoute;
