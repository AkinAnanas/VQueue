import { Drawer, Button, Accordion, Badge } from "@mui/material";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import MailIcon from "@mui/icons-material/Mail";
import SettingsIcon from "@mui/icons-material/Settings";
import HelpIcon from "@mui/icons-material/Help";
import { useState } from "react";

function SideDrawer(width: any) {
  return (
    <Drawer
      anchor="left"
      variant="permanent"
      sx={{
        display: { xs: "none", sm: "block" },
        "& .MuiDrawer-paper": { boxSizing: "border-box", width: width },
      }}
    >
      <Accordion sx={{ padding: "8px" }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1-content"
          id="panel1-header"
        >
          <AnalyticsIcon />
          <Typography marginLeft={"16px"} component="span">
            Analytics
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          Coming Soon: view analytics related to the usage of your queues!
        </AccordionDetails>
      </Accordion>

      <Accordion sx={{ padding: "8px" }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1-content"
          id="panel1-header"
        >
          <Badge badgeContent={4} color="primary">
            <MailIcon />
          </Badge>
          <Typography marginLeft={"16px"} component="span">
            Inbox
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          Coming Soon: view reports from users!
        </AccordionDetails>
      </Accordion>

      <Accordion sx={{ padding: "8px" }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1-content"
          id="panel1-header"
        >
          <SettingsIcon />
          <Typography marginLeft={"16px"} component="span">
            Settings
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          Coming Soon: web-page settings (light-mode, dark-mode, etc)!
        </AccordionDetails>
      </Accordion>

      <Button sx={{ padding: "16px" }}>
        <HelpIcon />
        <Typography marginLeft={"8px"} component="span">
          Help
        </Typography>
      </Button>
    </Drawer>
  );
}

export default SideDrawer;
