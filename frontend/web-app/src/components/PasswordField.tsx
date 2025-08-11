import React, { useState } from "react";
import { TextField, IconButton, InputAdornment } from "@mui/material";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";

interface PasswordFieldProps {
  value: string;
  onChange(e: any): void;
}

function PasswordField(props: PasswordFieldProps) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <TextField
      value={props.value}
      onChange={props.onChange}
      required
      label="Password"
      placeholder="Password"
      type={showPassword ? "text" : "password"}
      slotProps={{
        input: {
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label="toggle password visibility"
                onClick={() => setShowPassword((prev) => !prev)}
                edge="end"
              >
                {showPassword ? <Visibility /> : <VisibilityOff />}
              </IconButton>
            </InputAdornment>
          ),
        },
      }}
    />
  );
}

export default PasswordField;
