import {
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Button,
} from "@mui/material";

import type { QueueInfo } from "../hooks/useQueues";

function QueueCard(props: QueueInfo) {
  return (
    <Card
      sx={{
        width: 220,
        height: 260,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
    >
      <CardContent>
        <Typography>{props.code}</Typography>
        <Typography>{props.name}</Typography>
        <Typography>{props.wait_time_estimate}</Typography>
        <Typography>{props.is_open}</Typography>
      </CardContent>
      <CardActionArea>
        <Button>View</Button>
      </CardActionArea>
    </Card>
  );
}

export default QueueCard;
