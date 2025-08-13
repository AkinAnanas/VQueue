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
        width: 240,
        height: 240,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
    >
      <CardContent>
        <img src={props.image_url} alt="" />
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
