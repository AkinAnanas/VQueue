import { Container, Paper, TextField, useTheme, Button } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginPage() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  async function handleLogin() {
    const params = { email: email, password: password };
    console.log(`Attempting to login with credentials ${email} ${password}`);
    fetch("http://localhost:8000/auth/provider/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })
      .then((response) => {
        if (response.status != 200) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        localStorage.setItem("access_token", data.access_token);
        navigate("/home");
      })
      .catch((error) => {
        alert("Failed to login! " + error);
        setEmail("");
        setPassword("");
      });
  }

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
        <h2>Login</h2>
        <form
          action="submit"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          }}
        >
          <TextField
            required
            label="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@organization.com"
          />
          <TextField
            required
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <Button
            onSubmit={(e) => {
              e.preventDefault();
              handleLogin();
            }}
            disabled={email.length == 0 || password.length == 0}
          >
            Login
          </Button>
        </form>
      </Paper>
    </Container>
  );
}

export default LoginPage;
