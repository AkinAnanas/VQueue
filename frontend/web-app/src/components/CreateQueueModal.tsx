import {
  Modal,
  Checkbox,
  TextField,
  FormControlLabel,
  IconButton,
  Button,
  Box,
} from "@mui/material";
import { Close } from "@mui/icons-material";
import { useState } from "react";
import type { QueueInfo } from "../hooks/useQueues";
import { useQueues } from "../hooks/useQueues";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

function CreateQueueModal({
  open,
  setOpen,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
}) {
  const [blockCapacity, setBlockCapacity] = useState(100);
  const [description, setDescription] = useState("");
  const [manualDispatch, setManualDispatch] = useState(true);
  const [queueOpen, setQueueOpen] = useState(true);
  const [name, setName] = useState("");
  const { createQueue, loading, error } = useQueues();
  const { accessToken, refresh } = useAuth();
  const navigate = useNavigate();

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const params: QueueInfo = {
      name: name,
      is_open: true,
      max_block_capacity: blockCapacity,
      max_party_capacity: 10,
      size: 0,
      wait_time_estimate: "0 mins",
      manual_dispatch: true,
      description: description,
      image_url: "",
    };

    if (!accessToken && !refresh()[0]) {
      navigate("/login");
      return;
    }

    createQueue({ info: params, token: accessToken!! });

    if (!loading && !error) {
      setOpen(false);
    } else if (error) {
      alert(error);
      console.log(error);
      console.log(JSON.parse(error.substring(error.indexOf("{"))));
    }
  }

  return (
    <Modal
      sx={{
        width: 500,
        height: 550,
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        borderRadius: 4,
        backdropFilter: "blur(4px)",
        bgcolor: "white",
      }}
      open={open}
      onClose={() => {
        navigate(0);
        setOpen(false);
      }}
    >
      <Box
        sx={{
          backgroundColor: "white",
          width: "100%",
          height: "100%",
          padding: 4,
          margin: "auto",
          boxShadow: 8,
          outline: "black solid 1px",
          borderRadius: 4,
        }}
      >
        <form onSubmit={handleSubmit}>
          <IconButton
            sx={{
              width: 50,
              height: 50,
              position: "absolute",
              right: 5,
              top: 5,
            }}
            onClick={() => setOpen(false)}
          >
            <Close />
          </IconButton>
          <h2>Create Queue</h2>
          <TextField
            label="Queue Name"
            required
            fullWidth
            margin="normal"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <TextField
            label="Description"
            fullWidth
            margin="normal"
            multiline
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <FormControlLabel
            control={
              <TextField
                type="number"
                value={blockCapacity}
                onChange={(e) => setBlockCapacity(Number(e.target.value))}
              />
            }
            label="Max Block Capacity"
            labelPlacement="start"
            sx={{ p: 2, width: "100%", marginLeft: 0, gap: 2 }}
          />
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              margin: "auto",
            }}
          >
            <FormControlLabel
              control={
                <Checkbox
                  checked={manualDispatch}
                  onChange={(e) => setManualDispatch(e.target.checked)}
                />
              }
              label="Manual Dispatch"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={queueOpen}
                  onChange={(e) => setQueueOpen(e.target.checked)}
                />
              }
              label="Open"
            />
          </div>
          <Button sx={{ my: 2 }} variant="contained" fullWidth type="submit">
            Submit
          </Button>
        </form>
      </Box>
    </Modal>
  );
}

export default CreateQueueModal;
