import { Routes, BrowserRouter, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import NotFoundPage from "./pages/NotFoundPage";
import "./App.css";
import { CssBaseline } from "@mui/material";
import RegisterPage from "./pages/RegisterPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./hooks/useAuth";
import Logout from "./components/Logout";

function App() {
  return (
    <AuthProvider>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logout"
            element={
              <ProtectedRoute>
                <Logout />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
