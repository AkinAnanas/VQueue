import { Container, Paper, TextField, useTheme, Button } from "@mui/material";
import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import PasswordField from "../components/PasswordField";
import { Navigate, useNavigate } from "react-router-dom";

function LoginPage() {
  const { login, error, loading } = useAuth();
  const theme = useTheme();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    document.title = "VQueue | Login";
  }, []);

  const handleSubmit = async () => {
    await login({ email, password });
    setEmail("");
    setPassword("");
    navigate("/");
  };

  return (
    <Container>
      <Paper
        sx={{
          color: theme.palette.text.primary,
          backgroundColor: theme.palette.background.paper,
          borderRadius: 8,
          padding: 4,
          width: "500px",
        }}
      >
        <h2>Welcome back!</h2>
        <form
          action="submit"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          }}
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          <TextField
            required
            label="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@organization.com"
          />
          <PasswordField
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p style={{ color: "red" }}>{error}</p>}
          <Button
            type="submit"
            disabled={email.length == 0 || password.length == 0 || loading}
          >
            {loading ? "Logging in..." : "Login"}
          </Button>
        </form>
      </Paper>
    </Container>
  );
}

export default LoginPage;
