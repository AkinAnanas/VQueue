import { Container, Modal, useTheme } from "@mui/material";
import theme from "../themes/theme";

function LoginPage() {
  const theme = useTheme();
  return (
    <Container sx={{ width: "100%", height: "100%", margin: 0 }}>
      <Modal
        open={true}
        sx={{
          backgroundColor: theme.palette.background.paper,
          margin: 8,
          padding: 4,
        }}
      >
        <h1>Login</h1>
      </Modal>
    </Container>
  );
}

export default LoginPage;
