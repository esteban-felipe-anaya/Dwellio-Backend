"use client";
import CancelRoundedIcon from "@mui/icons-material/CancelRounded";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import HourglassTopRoundedIcon from "@mui/icons-material/HourglassTopRounded";
import MarkChatReadRoundedIcon from "@mui/icons-material/MarkChatReadRounded";
import PendingRoundedIcon from "@mui/icons-material/PendingRounded";
import UpcomingRoundedIcon from "@mui/icons-material/UpcomingRounded";
import { Chip, type ChipProps } from "@mui/material";
import type { SvgIconComponent } from "@mui/icons-material";

type Spec = { color: ChipProps["color"]; icon: SvgIconComponent };

const MAP: Record<string, Spec> = {
  requested: { color: "default", icon: HourglassTopRoundedIcon },
  pending: { color: "warning", icon: PendingRoundedIcon },
  open: { color: "info", icon: PendingRoundedIcon },
  confirmed: { color: "primary", icon: CheckCircleRoundedIcon },
  upcoming: { color: "info", icon: UpcomingRoundedIcon },
  completed: { color: "success", icon: CheckCircleRoundedIcon },
  closed: { color: "success", icon: MarkChatReadRoundedIcon },
  cancelled: { color: "error", icon: CancelRoundedIcon },
};

export default function StatusChip({ status }: { status: string }) {
  const spec = MAP[status] ?? { color: "default" as const, icon: PendingRoundedIcon };
  const Icon = spec.icon;
  return (
    <Chip
      size="small"
      color={spec.color}
      variant={spec.color === "default" ? "outlined" : "filled"}
      icon={<Icon style={{ fontSize: 16 }} />}
      label={status.charAt(0).toUpperCase() + status.slice(1)}
    />
  );
}
