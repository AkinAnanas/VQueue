import { Container, Paper, TextField, useTheme, Button } from "@mui/material";
import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import PasswordField from "../components/PasswordField";
import { useNavigate } from "react-router-dom";

function RegisterPage() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const { register, loading, error } = useAuth();

  const handleSubmit = async () => {
    await register({ email, password, name, location });
    setEmail("");
    setPassword("");
    setName("");
    setLocation("");
    navigate("/login");
  };

  useEffect(() => {
    document.title = "VQueue | Register";
  }, []);

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
        <h2>Join us!</h2>
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
            label="Organization Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Organization"
          />
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
          <TextField
            required
            label="Location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="City, State"
          />
          {error && <p style={{ color: "red" }}>{error}</p>}
          <Button
            type="submit"
            disabled={
              email.length == 0 ||
              password.length == 0 ||
              location.length == 0 ||
              name.length == 0 ||
              loading
            }
          >
            {loading ? "Registering..." : "Register"}
          </Button>
        </form>
      </Paper>
    </Container>
  );
}

export default RegisterPage;
