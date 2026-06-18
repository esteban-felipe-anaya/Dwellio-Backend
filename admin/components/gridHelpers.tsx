"use client";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import DeleteRoundedIcon from "@mui/icons-material/DeleteRounded";
import EditRoundedIcon from "@mui/icons-material/EditRounded";
import VisibilityRoundedIcon from "@mui/icons-material/VisibilityRounded";
import { Avatar, IconButton, Stack, Tooltip } from "@mui/material";
import { mediaUrl } from "@/lib/media";

// The `.MuiDataGrid-booleanCell` CSS overrides the SvgIcon `color` prop, so we
// color these via inline `style` instead.
export const booleanSlots = {
  booleanCellTrueIcon: () => (
    <CheckCircleRoundedIcon style={{ color: "#2e7d32" }} fontSize="small" />
  ),
  booleanCellFalseIcon: () => (
    <CloseRoundedIcon style={{ color: "#d32f2f" }} fontSize="small" />
  ),
};

export function ImageCell({ url }: { url?: string | null }) {
  return (
    <Avatar
      variant="rounded"
      src={mediaUrl(url)}
      sx={{ width: 44, height: 44, bgcolor: "action.hover" }}
    />
  );
}

interface RowActionsProps {
  onEdit?: () => void;
  onDelete?: () => void;
  onView?: () => void;
}

export function RowActions({ onEdit, onDelete, onView }: RowActionsProps) {
  return (
    <Stack direction="row" spacing={0.5}>
      {onView && (
        <Tooltip title="View">
          <IconButton size="small" color="info" onClick={onView}>
            <VisibilityRoundedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}
      {onEdit && (
        <Tooltip title="Edit">
          <IconButton size="small" color="primary" onClick={onEdit}>
            <EditRoundedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}
      {onDelete && (
        <Tooltip title="Delete">
          <IconButton size="small" color="error" onClick={onDelete}>
            <DeleteRoundedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}
    </Stack>
  );
}
