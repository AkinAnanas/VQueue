import {
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Button,
} from "@mui/material";

type QueueInfo = {
  code: number;
  name: string;
};

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
        <Typography>{props.code}</Typography>
        <Typography>{props.name}</Typography>
      </CardContent>
      <CardActionArea>
        <Button>View</Button>
      </CardActionArea>
    </Card>
  );
}

export default QueueCard;
