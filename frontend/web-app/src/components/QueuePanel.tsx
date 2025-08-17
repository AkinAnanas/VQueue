import CreateQueueButton from "./CreateQueueButton";
import QueueCard from "./QueueCard";
import { useQueues } from "../hooks/useQueues";
import { useAuth } from "../hooks/useAuth";
import { useEffect, useState } from "react";
import type { QueueInfo } from "../hooks/useQueues";
import CreateQueueModal from "./CreateQueueModal";
import { useNavigate } from "react-router-dom";
import { Typography, Grid, Pagination, Stack } from "@mui/material";

const ITEMS_PER_PAGE = 5;

function QueuePanel() {
  const { accessToken, refresh } = useAuth();
  const { fetchQueues, loading, error } = useQueues();
  const [queues, setQueues] = useState<QueueInfo[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [pageCount, setPageCount] = useState(1);
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  if (!accessToken && !refresh()[0]) {
    navigate("/login");
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchQueues({
          limit: ITEMS_PER_PAGE,
          offset: (page - 1) * ITEMS_PER_PAGE,
          token: accessToken!!,
        });
        console.log("Fetched queues:", data.queues);
        setQueues(data.queues);
        setPageCount(Math.ceil(data.total / ITEMS_PER_PAGE));
      } catch (err) {
        console.error("Error in fetchData:", err);
      }
    };

    fetchData();
  }, [modalOpen, page]);

  return (
    <div
      style={{
        width: "80%",
        height: "calc(100vh - 64px)",
        position: "absolute",
        padding: "16px",
        top: 64,
        right: 0,
      }}
    >
      {loading && (
        <Typography
          color={"black"}
          sx={{
            height: "calc(100% - 64px)",
            justifyContent: "center",
            alignItems: "center",
            p: 2,
          }}
        >
          Loading...
        </Typography>
      )}
      {error && (
        <Typography
          color={"red"}
          sx={{
            height: "calc(100% - 64px)",
            justifyContent: "center",
            alignItems: "center",
            p: 2,
          }}
        >
          Error: {error}
        </Typography>
      )}
      {!error && !loading && queues.length === 0 && (
        <Typography
          color={"black"}
          sx={{
            height: "calc(100% - 64px)",
            justifyContent: "center",
            alignItems: "center",
            p: 2,
          }}
        >
          No queues available. Create one!
        </Typography>
      )}
      {!error && !loading && queues.length > 0 && (
        <Grid
          container
          spacing={2}
          my={1}
          sx={{
            justifyContent: "center",
            height: "calc(100% - 64px)",
            overflowY: "auto",
          }}
        >
          <CreateQueueModal open={modalOpen} setOpen={setModalOpen} />
          <CreateQueueButton setOpen={setModalOpen} />
          {queues.map((queue) => (
            <QueueCard key={queue.code} {...queue} />
          ))}
        </Grid>
      )}
      <Stack alignItems={"center"} sx={{ height: 64 }}>
        <Pagination
          count={pageCount}
          page={page}
          onChange={(_, value) => setPage(value)}
          variant="outlined"
          shape="rounded"
          showFirstButton
          showLastButton
          disabled={loading || pageCount <= 1}
          sx={{ m: 2 }}
        />
      </Stack>
    </div>
  );
}

export default QueuePanel;
