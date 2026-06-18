"use client";
import AddPhotoAlternateRoundedIcon from "@mui/icons-material/AddPhotoAlternateRounded";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import LinkRoundedIcon from "@mui/icons-material/LinkRounded";
import {
  Box,
  Button,
  CircularProgress,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useRef, useState } from "react";
import { api } from "@/lib/api";
import { mediaUrl } from "@/lib/media";
import CropDialog from "./CropDialog";

interface Props {
  label: string;
  value: string[];
  onChange: (urls: string[]) => void;
  multiple?: boolean;
}

export default function ImageUploadField({
  label,
  value,
  onChange,
  multiple = false,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [cropSrc, setCropSrc] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [urlInput, setUrlInput] = useState("");

  function pick() {
    inputRef.current?.click();
  }

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setCropSrc(reader.result as string);
    reader.readAsDataURL(file);
    e.target.value = "";
  }

  async function onCropped(blob: Blob) {
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", new File([blob], "upload.jpg", { type: "image/jpeg" }));
      const { data } = await api.post<{ url: string }>(
        "/admin-api/upload",
        form,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      onChange(multiple ? [...value, data.url] : [data.url]);
    } finally {
      setBusy(false);
    }
  }

  function addUrl() {
    const u = urlInput.trim();
    if (!u) return;
    onChange(multiple ? [...value, u] : [u]);
    setUrlInput("");
  }

  function removeAt(i: number) {
    onChange(value.filter((_, idx) => idx !== i));
  }

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        {label}
      </Typography>
      <Stack direction="row" flexWrap="wrap" gap={1} mb={1}>
        {value.map((url, i) => (
          <Box
            key={`${url}-${i}`}
            sx={{
              position: "relative",
              width: 96,
              height: 96,
              borderRadius: 2,
              overflow: "hidden",
              border: (t) => `1px solid ${t.palette.divider}`,
            }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={mediaUrl(url)}
              alt=""
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
            <IconButton
              size="small"
              onClick={() => removeAt(i)}
              sx={{
                position: "absolute",
                top: 2,
                right: 2,
                bgcolor: "rgba(0,0,0,0.55)",
                color: "#fff",
                "&:hover": { bgcolor: "rgba(0,0,0,0.75)" },
              }}
            >
              <CloseRoundedIcon fontSize="small" />
            </IconButton>
          </Box>
        ))}
        {(multiple || value.length === 0) && (
          <Button
            variant="outlined"
            onClick={pick}
            disabled={busy}
            sx={{
              width: 96,
              height: 96,
              flexDirection: "column",
              borderStyle: "dashed",
            }}
          >
            {busy ? (
              <CircularProgress size={22} />
            ) : (
              <>
                <AddPhotoAlternateRoundedIcon />
                <Typography variant="caption">Upload</Typography>
              </>
            )}
          </Button>
        )}
      </Stack>
      <Stack direction="row" spacing={1} alignItems="center">
        <TextField
          size="small"
          fullWidth
          placeholder="…or paste an image URL"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          InputProps={{ startAdornment: <LinkRoundedIcon sx={{ mr: 1, opacity: 0.6 }} /> }}
        />
        <Button onClick={addUrl} variant="text">
          Add
        </Button>
      </Stack>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        hidden
        onChange={onFile}
      />
      {cropSrc && (
        <CropDialog
          open={!!cropSrc}
          src={cropSrc}
          onClose={() => setCropSrc(null)}
          onCropped={onCropped}
        />
      )}
    </Box>
  );
}
