"use client";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import StarRoundedIcon from "@mui/icons-material/StarRounded";
import {
  Box,
  Button,
  Card,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Rating,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import ConfirmDialog from "@/components/ConfirmDialog";
import { ImageCell, RowActions } from "@/components/gridHelpers";
import ImageUploadField from "@/components/ImageUploadField";
import { api } from "@/lib/api";
import { useToast } from "@/lib/toast";
import type { AdminAgent } from "@/lib/types";

interface Draft {
  name: string;
  agency: string;
  phone: string;
  rating: number;
  reviewCount: number;
  photo: string[];
}
const empty: Draft = { name: "", agency: "", phone: "", rating: 4, reviewCount: 0, photo: [] };

export default function AgentsPage() {
  const qc = useQueryClient();
  const { notify } = useToast();
  const { data = [], isLoading } = useQuery<AdminAgent[]>({
    queryKey: ["agents"],
    queryFn: async () => (await api.get<AdminAgent[]>("/admin-api/agents")).data,
  });

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<AdminAgent | null>(null);
  const [draft, setDraft] = useState<Draft>(empty);
  const [toDelete, setToDelete] = useState<AdminAgent | null>(null);

  function openCreate() {
    setEditing(null);
    setDraft(empty);
    setOpen(true);
  }
  function openEdit(a: AdminAgent) {
    setEditing(a);
    setDraft({
      name: a.name,
      agency: a.agency,
      phone: a.phone,
      rating: a.rating,
      reviewCount: a.reviewCount,
      photo: a.photo ? [a.photo] : [],
    });
    setOpen(true);
  }

  const save = useMutation({
    mutationFn: async () => {
      const payload = { ...draft, photo: draft.photo[0] ?? null };
      if (editing) await api.patch(`/admin-api/agents/${editing.id}`, payload);
      else await api.post("/admin-api/agents", payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["agents"] });
      notify(editing ? "Agent updated" : "Agent created");
      setOpen(false);
    },
    onError: () => notify("Save failed", "error"),
  });

  const remove = useMutation({
    mutationFn: async (id: string) => api.delete(`/admin-api/agents/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["agents"] });
      notify("Agent deleted");
    },
    onError: () => notify("Delete failed", "error"),
  });

  const columns: GridColDef<AdminAgent>[] = [
    {
      field: "photo",
      headerName: "",
      width: 70,
      sortable: false,
      renderCell: (p) => <ImageCell url={p.row.photo} />,
    },
    { field: "name", headerName: "Name", flex: 1, minWidth: 150 },
    { field: "agency", headerName: "Agency", flex: 1, minWidth: 150 },
    { field: "phone", headerName: "Phone", width: 160 },
    {
      field: "rating",
      headerName: "Rating",
      width: 160,
      renderCell: (p) => (
        <Stack direction="row" spacing={0.5} alignItems="center">
          <StarRoundedIcon sx={{ color: "#f5b301", fontSize: 18 }} />
          <span>
            {p.row.rating} ({p.row.reviewCount})
          </span>
        </Stack>
      ),
    },
    { field: "listingCount", headerName: "Listings", width: 100 },
    {
      field: "actions",
      headerName: "",
      width: 110,
      sortable: false,
      renderCell: (p) => (
        <RowActions onEdit={() => openEdit(p.row)} onDelete={() => setToDelete(p.row)} />
      ),
    },
  ];

  return (
    <Stack spacing={2}>
      <Stack direction="row" alignItems="center">
        <Typography variant="h5" fontWeight={800} flexGrow={1}>
          Agents
        </Typography>
        <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={openCreate}>
          New agent
        </Button>
      </Stack>
      <Card sx={{ height: 600 }}>
        <Box sx={{ height: "100%", width: "100%" }}>
          <DataGrid
            rows={data}
            columns={columns}
            loading={isLoading}
            rowHeight={60}
            disableRowSelectionOnClick
            initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
            pageSizeOptions={[25, 50, 100]}
          />
        </Box>
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editing ? "Edit agent" : "New agent"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <ImageUploadField
              label="Photo"
              value={draft.photo}
              onChange={(photo) => setDraft({ ...draft, photo })}
            />
            <TextField
              label="Name"
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
            />
            <TextField
              label="Agency"
              value={draft.agency}
              onChange={(e) => setDraft({ ...draft, agency: e.target.value })}
            />
            <TextField
              label="Phone"
              value={draft.phone}
              onChange={(e) => setDraft({ ...draft, phone: e.target.value })}
            />
            <Stack direction="row" spacing={3} alignItems="center">
              <Box>
                <Typography variant="caption">Rating</Typography>
                <Rating
                  value={draft.rating}
                  precision={0.1}
                  onChange={(_, v) => setDraft({ ...draft, rating: v ?? 0 })}
                />
              </Box>
              <TextField
                label="Reviews"
                type="number"
                value={draft.reviewCount}
                onChange={(e) =>
                  setDraft({ ...draft, reviewCount: Number(e.target.value) })
                }
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => save.mutate()}
            disabled={!draft.name || save.isPending}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={!!toDelete}
        message={`Delete agent "${toDelete?.name}"?`}
        onClose={() => setToDelete(null)}
        onConfirm={() => toDelete && remove.mutate(toDelete.id)}
      />
    </Stack>
  );
}
