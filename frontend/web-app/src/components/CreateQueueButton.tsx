import { Typography, Box, useTheme } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { IconButton } from "@mui/material";

function CreateQueueButton({ setOpen }: { setOpen: (open: boolean) => void }) {
  const theme = useTheme();
  return (
    <Box
      sx={{
        width: 220,
        height: 260,
        outlineColor: theme.palette.divider,
        backgroundColor: theme.palette.grey[100],
        "&:hover": {
          backgroundColor: theme.palette.grey[300],
          scale: 1.1,
          transform: "translate(-.05)",
          cursor: "pointer",
        },
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
      onClick={() => {
        setOpen(true);
      }}
    >
      <IconButton
        sx={{
          color: theme.palette.divider,
        }}
      >
        <AddIcon sx={{ width: 50, height: 50 }} />
      </IconButton>
      <Typography>New Queue</Typography>
    </Box>
  );
}

export default CreateQueueButton;
