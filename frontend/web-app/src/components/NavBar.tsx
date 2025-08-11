import { styled, alpha } from "@mui/material/styles";
import IconButton from "@mui/material/IconButton";
import InputBase from "@mui/material/InputBase";
import { Button, Box, AppBar, Toolbar, Typography } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import AccountCircle from "@mui/icons-material/AccountCircle";
import MenuIcon from "@mui/icons-material/Menu";
import { useTheme } from "@mui/material";
import { useNavigate } from "react-router-dom";

const Search = styled("div")(({ theme }) => ({
  position: "relative",
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  "&:hover": {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: "100%",
  [theme.breakpoints.up("sm")]: {
    marginLeft: theme.spacing(3),
    width: "auto",
  },
}));

const SearchIconWrapper = styled("div")(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: "100%",
  position: "absolute",
  pointerEvents: "none",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: "inherit",
  "& .MuiInputBase-input": {
    padding: theme.spacing(1, 1, 1, 0),
    // vertical padding + font size from searchIcon
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create("width"),
    width: "100%",
    [theme.breakpoints.up("md")]: {
      width: "20ch",
    },
  },
}));

function NavBar() {
  const navigate = useNavigate();

  return (
    <AppBar
      position="static"
      sx={{ position: "absolute", top: 0, right: 0, width: "80%" }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{ display: { xs: "none", sm: "block" } }}
        >
          VQueue
        </Typography>
        <Search>
          <SearchIconWrapper>
            <SearchIcon />
          </SearchIconWrapper>
          <StyledInputBase
            placeholder="Search…"
            inputProps={{ "aria-label": "search" }}
          />
        </Search>
        <Box sx={{ display: { xs: "none", sm: "block", flexGrow: 1 } }}>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="open profile"
            sx={{ mr: 2 }}
          >
            <AccountCircle />
          </IconButton>
          <Button color="inherit" onClick={() => navigate("/logout")}>
            Logout
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default NavBar;
