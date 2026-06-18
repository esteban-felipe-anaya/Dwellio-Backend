"use client";
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
  Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import StatusChip from "@/components/StatusChip";
import { RowActions } from "@/components/gridHelpers";
import { api } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import { useToast } from "@/lib/toast";
import type { AdminInquiry } from "@/lib/types";

const STATUS_OPTIONS = ["open", "pending", "confirmed", "closed"];

export default function InquiriesPage() {
  const qc = useQueryClient();
  const { notify } = useToast();
  const { data = [], isLoading } = useQuery<AdminInquiry[]>({
    queryKey: ["inquiries"],
    queryFn: async () => (await api.get<AdminInquiry[]>("/admin-api/inquiries")).data,
  });

  const [editing, setEditing] = useState<AdminInquiry | null>(null);
  const [status, setStatus] = useState("open");

  const save = useMutation({
    mutationFn: async () => {
      if (editing) await api.patch(`/admin-api/inquiries/${editing.id}`, { status });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["inquiries"] });
      notify("Inquiry updated");
      setEditing(null);
    },
    onError: () => notify("Update failed", "error"),
  });

  const columns: GridColDef<AdminInquiry>[] = [
    { field: "listingTitle", headerName: "Listing", flex: 1, minWidth: 200 },
    { field: "userName", headerName: "From", width: 160 },
    { field: "type", headerName: "Type", width: 100 },
    { field: "lastMessage", headerName: "Last message", flex: 1, minWidth: 200 },
    {
      field: "date",
      headerName: "Date",
      width: 170,
      valueFormatter: (v) => fmtDate(v as string | null),
    },
    {
      field: "status",
      headerName: "Status",
      width: 130,
      renderCell: (p) => <StatusChip status={p.row.status} />,
    },
    {
      field: "actions",
      headerName: "",
      width: 80,
      sortable: false,
      renderCell: (p) => (
        <RowActions
          onEdit={() => {
            setEditing(p.row);
            setStatus(p.row.status);
          }}
        />
      ),
    },
  ];

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>
        Inquiries
      </Typography>
      <Card sx={{ height: 600 }}>
        <Box sx={{ height: "100%", width: "100%" }}>
          <DataGrid
            rows={data}
            columns={columns}
            loading={isLoading}
            disableRowSelectionOnClick
            initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
            pageSizeOptions={[25, 50, 100]}
          />
        </Box>
      </Card>

      <Dialog open={!!editing} onClose={() => setEditing(null)} maxWidth="xs" fullWidth>
        <DialogTitle>Update inquiry status</DialogTitle>
        <DialogContent>
          <Select
            fullWidth
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            sx={{ mt: 1 }}
          >
            {STATUS_OPTIONS.map((s) => (
              <MenuItem key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditing(null)}>Cancel</Button>
          <Button variant="contained" onClick={() => save.mutate()}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
