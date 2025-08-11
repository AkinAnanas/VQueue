import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

function Logout() {
  const navigate = useNavigate();
  const { logout, loading, error } = useAuth();

  useEffect(() => {
    logout();
    navigate("/login");
  }, []);

  return (
    <div>
      <h1>{loading ? "Logging out" : ""}</h1>
      <p color="red">{error}</p>
    </div>
  );
}

export default Logout;
