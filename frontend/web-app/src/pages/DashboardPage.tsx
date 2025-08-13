import { Pagination } from "@mui/material";
import NavBar from "../components/NavBar";
import { Box, Container } from "@mui/material";
import QueuePanel from "../components/QueuePanel";
import SideDrawer from "../components/SideDrawer";
import { useEffect } from "react";

function DashboardPage() {
  useEffect(() => {
    document.title = "VQueue | Dashboard";
  }, []);

  return (
    <Box
      sx={{
        width: "100%",
        height: "calc(100vh - 64px)",
        display: "flex",
        flexDirection: "row",
      }}
    >
      <SideDrawer width="20%" />
      <Box
        sx={{
          margin: 0,
          width: "80%",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <NavBar />
        <Container maxWidth="xl" sx={{ flexGrow: 1, py: 4 }}>
          <QueuePanel />
        </Container>
        <Pagination count={10} disabled />
      </Box>
    </Box>
  );
}

export default DashboardPage;
