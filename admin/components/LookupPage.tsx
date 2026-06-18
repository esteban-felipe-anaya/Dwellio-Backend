"use client";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import {
  Box,
  Button,
  Card,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import ConfirmDialog from "@/components/ConfirmDialog";
import { RowActions } from "@/components/gridHelpers";
import { api } from "@/lib/api";
import { useToast } from "@/lib/toast";
import type { Lookup } from "@/lib/types";

export default function LookupPage({
  resource,
  title,
}: {
  resource: "property-types" | "amenities";
  title: string;
}) {
  const qc = useQueryClient();
  const { notify } = useToast();
  const base = `/admin-api/${resource}`;

  const { data = [], isLoading } = useQuery<Lookup[]>({
    queryKey: [resource],
    queryFn: async () => (await api.get<Lookup[]>(base)).data,
  });

  const [editing, setEditing] = useState<Lookup | null>(null);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [icon, setIcon] = useState("");
  const [toDelete, setToDelete] = useState<Lookup | null>(null);

  function openCreate() {
    setEditing(null);
    setName("");
    setIcon("");
    setOpen(true);
  }
  function openEdit(row: Lookup) {
    setEditing(row);
    setName(row.name);
    setIcon(row.icon);
    setOpen(true);
  }

  const save = useMutation({
    mutationFn: async () => {
      const payload = { name, icon };
      if (editing) await api.patch(`${base}/${editing.id}`, payload);
      else await api.post(base, payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [resource] });
      notify(editing ? "Updated" : "Created");
      setOpen(false);
    },
    onError: () => notify("Save failed", "error"),
  });

  const remove = useMutation({
    mutationFn: async (id: string) => api.delete(`${base}/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [resource] });
      notify("Deleted");
    },
    onError: () => notify("Delete failed", "error"),
  });

  const columns: GridColDef<Lookup>[] = [
    { field: "id", headerName: "Slug", width: 180 },
    { field: "name", headerName: "Name", flex: 1, minWidth: 160 },
    { field: "icon", headerName: "Icon", width: 200 },
    {
      field: "actions",
      headerName: "",
      width: 120,
      sortable: false,
      filterable: false,
      renderCell: (p) => (
        <RowActions
          onEdit={() => openEdit(p.row)}
          onDelete={() => setToDelete(p.row)}
        />
      ),
    },
  ];

  return (
    <Stack spacing={2}>
      <Stack direction="row" alignItems="center">
        <Typography variant="h5" fontWeight={800} flexGrow={1}>
          {title}
        </Typography>
        <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={openCreate}>
          New
        </Button>
      </Stack>
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

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>{editing ? "Edit" : "New"} {title}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
            />
            <TextField
              label="Material icon name"
              value={icon}
              onChange={(e) => setIcon(e.target.value)}
              helperText="e.g. apartment, pool, fitness_center"
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => save.mutate()}
            disabled={!name || save.isPending}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={!!toDelete}
        message={`Delete "${toDelete?.name}"?`}
        onClose={() => setToDelete(null)}
        onConfirm={() => toDelete && remove.mutate(toDelete.id)}
      />
    </Stack>
  );
}
