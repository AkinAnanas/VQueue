import CreateQueueButton from "./CreateQueueButton";
import QueueCard from "./QueueCard";
import { useQueues } from "../hooks/useQueues";
import { useAuth } from "../hooks/useAuth";
import { QueueProvider } from "../hooks/useQueues";
import { useEffect, useState } from "react";
import type { QueueInfo } from "../hooks/useQueues";
import CreateQueueModal from "./CreateQueueModal";
import { useNavigate } from "react-router-dom";

function QueuePanel() {
  const { accessToken, refresh } = useAuth();
  const { fetchQueues, loading, error } = useQueues();
  const [queues, setQueues] = useState<QueueInfo[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const navigate = useNavigate();

  if (!accessToken) {
    if (!refresh()[0]) {
      navigate("/login");
    }
    return <div>Loading...</div>;
  }

  useEffect(() => {
    fetchQueues({ limit: 10, offset: 0, token: accessToken!! }).then((data) => {
      console.log(data);
      setQueues(data);
    });
  }, []);

  return (
    <QueueProvider>
      <div
        style={{
          display: "flex",
          gap: "4em",
          marginBottom: "2em",
          marginTop: "2em",
        }}
      >
        <CreateQueueModal open={modalOpen} setOpen={setModalOpen} />
        <CreateQueueButton setOpen={setModalOpen} />
        {loading && <div>Loading...</div>}
        {error && <div>Error: {error}</div>}
        {queues.map((queue) => (
          <QueueCard key={queue.code} {...queue} />
        ))}
      </div>
    </QueueProvider>
  );
}

export default QueuePanel;
