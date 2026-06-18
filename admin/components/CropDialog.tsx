"use client";
import RotateRightIcon from "@mui/icons-material/RotateRight";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Slider,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { useCallback, useState } from "react";
import Cropper from "react-easy-crop";
import { getCroppedImg, type Area } from "@/lib/cropImage";

interface Props {
  open: boolean;
  src: string;
  onClose: () => void;
  onCropped: (blob: Blob) => void;
}

const ASPECTS: { label: string; value: number }[] = [
  { label: "4:3", value: 4 / 3 },
  { label: "16:9", value: 16 / 9 },
  { label: "1:1", value: 1 },
  { label: "3:4", value: 3 / 4 },
];

export default function CropDialog({ open, src, onClose, onCropped }: Props) {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [aspect, setAspect] = useState(4 / 3);
  const [pixels, setPixels] = useState<Area | null>(null);
  const [busy, setBusy] = useState(false);

  const onComplete = useCallback((_: Area, areaPixels: Area) => {
    setPixels(areaPixels);
  }, []);

  async function confirm() {
    if (!pixels) return;
    setBusy(true);
    try {
      const blob = await getCroppedImg(src, pixels, rotation);
      onCropped(blob);
    } catch {
      // CORS-tainted / SVG: fall back by fetching the original as a blob.
      try {
        const res = await fetch(src);
        onCropped(await res.blob());
      } catch {
        // give up silently; caller keeps existing value
      }
    } finally {
      setBusy(false);
      onClose();
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Crop image</DialogTitle>
      <DialogContent>
        <Box
          sx={{
            position: "relative",
            height: 320,
            bgcolor: "#000",
            borderRadius: 2,
            overflow: "hidden",
          }}
        >
          <Cropper
            image={src}
            crop={crop}
            zoom={zoom}
            rotation={rotation}
            aspect={aspect}
            onCropChange={setCrop}
            onZoomChange={setZoom}
            onRotationChange={setRotation}
            onCropComplete={onComplete}
          />
        </Box>
        <Stack spacing={1.5} mt={2}>
          <Box>
            <Typography variant="caption">Zoom</Typography>
            <Slider
              value={zoom}
              min={1}
              max={3}
              step={0.05}
              onChange={(_, v) => setZoom(v as number)}
            />
          </Box>
          <Stack direction="row" spacing={2} alignItems="center">
            <ToggleButtonGroup
              size="small"
              exclusive
              value={aspect}
              onChange={(_, v) => v && setAspect(v)}
            >
              {ASPECTS.map((a) => (
                <ToggleButton key={a.label} value={a.value}>
                  {a.label}
                </ToggleButton>
              ))}
            </ToggleButtonGroup>
            <IconButton onClick={() => setRotation((r) => (r + 90) % 360)}>
              <RotateRightIcon />
            </IconButton>
          </Stack>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={confirm} disabled={busy}>
          Use image
        </Button>
      </DialogActions>
    </Dialog>
  );
}
