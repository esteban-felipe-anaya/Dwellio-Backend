"use client";
import {
  Box,
  Card,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
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
import type { AdminTour } from "@/lib/types";

const STATUS_OPTIONS = [
  { value: "", label: "Auto (time-based)" },
  { value: "confirmed", label: "Confirmed" },
  { value: "cancelled", label: "Cancelled" },
];

export default function ToursPage() {
  const qc = useQueryClient();
  const { notify } = useToast();
  const { data = [], isLoading } = useQuery<AdminTour[]>({
    queryKey: ["tours"],
    queryFn: async () => (await api.get<AdminTour[]>("/admin-api/tours")).data,
  });

  const [editing, setEditing] = useState<AdminTour | null>(null);
  const [status, setStatus] = useState("");

  const save = useMutation({
    mutationFn: async () => {
      if (editing) await api.patch(`/admin-api/tours/${editing.id}`, { status });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tours"] });
      notify("Tour updated");
      setEditing(null);
    },
    onError: () => notify("Update failed", "error"),
  });

  const columns: GridColDef<AdminTour>[] = [
    { field: "listingTitle", headerName: "Listing", flex: 1, minWidth: 200 },
    { field: "userName", headerName: "Requested by", width: 160 },
    { field: "date", headerName: "Date", width: 120 },
    { field: "slot", headerName: "Time", width: 100 },
    {
      field: "scheduledFor",
      headerName: "Scheduled",
      width: 170,
      valueFormatter: (v) => fmtDate(v as string | null),
    },
    {
      field: "status",
      headerName: "Status",
      width: 140,
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
            setStatus("");
          }}
        />
      ),
    },
  ];

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>
        Tours
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
        <DialogTitle>Update tour status</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {editing?.listingTitle}
          </Typography>
          <Select
            fullWidth
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            sx={{ mt: 1 }}
          >
            {STATUS_OPTIONS.map((o) => (
              <MenuItem key={o.value} value={o.value}>
                {o.label}
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
