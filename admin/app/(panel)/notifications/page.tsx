"use client";
import CampaignRoundedIcon from "@mui/icons-material/CampaignRounded";
import {
  Box,
  Button,
  Card,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { booleanSlots } from "@/components/gridHelpers";
import { api } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import { useToast } from "@/lib/toast";
import type { AdminNotification, AdminUser } from "@/lib/types";

const TYPES = ["system", "price_drop", "tour", "match"];

export default function NotificationsPage() {
  const qc = useQueryClient();
  const { notify } = useToast();
  const { data = [], isLoading } = useQuery<AdminNotification[]>({
    queryKey: ["notifications"],
    queryFn: async () =>
      (await api.get<AdminNotification[]>("/admin-api/notifications")).data,
  });
  const { data: users = [] } = useQuery<AdminUser[]>({
    queryKey: ["users"],
    queryFn: async () => (await api.get<AdminUser[]>("/admin-api/users")).data,
  });

  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [type, setType] = useState("system");
  const [userId, setUserId] = useState("");

  const send = useMutation({
    mutationFn: async () =>
      api.post("/admin-api/notifications", {
        title,
        body,
        type,
        userId: userId || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      notify("Notification sent");
      setOpen(false);
      setTitle("");
      setBody("");
    },
    onError: () => notify("Send failed", "error"),
  });

  const columns: GridColDef<AdminNotification>[] = [
    { field: "title", headerName: "Title", flex: 1, minWidth: 180 },
    { field: "body", headerName: "Body", flex: 2, minWidth: 240 },
    { field: "type", headerName: "Type", width: 120 },
    { field: "read", headerName: "Read", width: 90, type: "boolean" },
    {
      field: "date",
      headerName: "Date",
      width: 170,
      valueFormatter: (v) => fmtDate(v as string | null),
    },
  ];

  return (
    <Stack spacing={2}>
      <Stack direction="row" alignItems="center">
        <Typography variant="h5" fontWeight={800} flexGrow={1}>
          Notifications
        </Typography>
        <Button
          variant="contained"
          startIcon={<CampaignRoundedIcon />}
          onClick={() => setOpen(true)}
        >
          Compose
        </Button>
      </Stack>
      <Card sx={{ height: 600 }}>
        <Box sx={{ height: "100%", width: "100%" }}>
          <DataGrid
            rows={data}
            columns={columns}
            loading={isLoading}
            getRowId={(r) => r.id}
            slots={booleanSlots}
            disableRowSelectionOnClick
            initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
            pageSizeOptions={[25, 50, 100]}
          />
        </Box>
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Compose notification</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              fullWidth
            />
            <TextField
              label="Body"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              multiline
              minRows={2}
              fullWidth
            />
            <Select value={type} onChange={(e) => setType(e.target.value)}>
              {TYPES.map((t) => (
                <MenuItem key={t} value={t}>
                  {t}
                </MenuItem>
              ))}
            </Select>
            <Select
              value={userId}
              displayEmpty
              onChange={(e) => setUserId(e.target.value)}
            >
              <MenuItem value="">Broadcast to all users</MenuItem>
              {users.map((u) => (
                <MenuItem key={u.id} value={u.id}>
                  {u.name} ({u.email})
                </MenuItem>
              ))}
            </Select>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => send.mutate()}
            disabled={!title || send.isPending}
          >
            Send
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
