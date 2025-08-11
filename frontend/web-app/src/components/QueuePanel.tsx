import CreateQueueButton from "./CreateQueueButton";
import QueueCard from "./QueueCard";

function QueuePanel() {
  return (
    <div
      style={{
        display: "flex",
        gap: "4em",
        marginBottom: "2em",
        marginTop: "2em",
      }}
    >
      <CreateQueueButton />
      <QueueCard name={"Superman Ride"} code={12345} />
    </div>
  );
}

export default QueuePanel;
