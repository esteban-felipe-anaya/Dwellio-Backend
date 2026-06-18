"use client";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import {
  Box,
  Button,
  Card,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import ConfirmDialog from "@/components/ConfirmDialog";
import { booleanSlots, ImageCell, RowActions } from "@/components/gridHelpers";
import ImageUploadField from "@/components/ImageUploadField";
import { api } from "@/lib/api";
import { useToast } from "@/lib/toast";
import type { AdminAgent, AdminListing, Lookup } from "@/lib/types";

interface Draft {
  title: string;
  dealType: string;
  price: number;
  currency: string;
  propertyType: string;
  beds: number;
  baths: number;
  areaSqm: number;
  parking: number;
  address: string;
  city: string;
  lat: number;
  lng: number;
  amenities: string[];
  photos: string[];
  agentId: string;
  description: string;
  featured: boolean;
}

const empty: Draft = {
  title: "",
  dealType: "buy",
  price: 0,
  currency: "USD",
  propertyType: "",
  beds: 1,
  baths: 1,
  areaSqm: 0,
  parking: 0,
  address: "",
  city: "",
  lat: 0,
  lng: 0,
  amenities: [],
  photos: [],
  agentId: "",
  description: "",
  featured: false,
};

const fmtMoney = (n: number) => `$${Math.round(n).toLocaleString()}`;

export default function ListingsPage() {
  const qc = useQueryClient();
  const { notify } = useToast();

  const { data = [], isLoading } = useQuery<AdminListing[]>({
    queryKey: ["listings"],
    queryFn: async () => (await api.get<AdminListing[]>("/admin-api/listings")).data,
  });
  const { data: types = [] } = useQuery<Lookup[]>({
    queryKey: ["property-types"],
    queryFn: async () => (await api.get<Lookup[]>("/admin-api/property-types")).data,
  });
  const { data: amenities = [] } = useQuery<Lookup[]>({
    queryKey: ["amenities"],
    queryFn: async () => (await api.get<Lookup[]>("/admin-api/amenities")).data,
  });
  const { data: agents = [] } = useQuery<AdminAgent[]>({
    queryKey: ["agents"],
    queryFn: async () => (await api.get<AdminAgent[]>("/admin-api/agents")).data,
  });

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<AdminListing | null>(null);
  const [draft, setDraft] = useState<Draft>(empty);
  const [toDelete, setToDelete] = useState<AdminListing | null>(null);

  function set<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((d) => ({ ...d, [key]: value }));
  }

  function openCreate() {
    setEditing(null);
    setDraft({ ...empty, propertyType: types[0]?.id ?? "" });
    setOpen(true);
  }
  function openEdit(l: AdminListing) {
    setEditing(l);
    setDraft({
      title: l.title,
      dealType: l.dealType,
      price: l.price,
      currency: l.currency,
      propertyType: l.propertyType,
      beds: l.beds,
      baths: l.baths,
      areaSqm: l.areaSqm,
      parking: l.parking,
      address: l.address,
      city: l.city,
      lat: l.lat,
      lng: l.lng,
      amenities: l.amenities,
      photos: l.photos,
      agentId: l.agentId ?? "",
      description: l.description,
      featured: l.featured,
    });
    setOpen(true);
  }

  const save = useMutation({
    mutationFn: async () => {
      const payload = { ...draft, agentId: draft.agentId || null };
      if (editing) await api.patch(`/admin-api/listings/${editing.id}`, payload);
      else await api.post("/admin-api/listings", payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["listings"] });
      notify(editing ? "Listing updated" : "Listing created");
      setOpen(false);
    },
    onError: () => notify("Save failed", "error"),
  });

  const remove = useMutation({
    mutationFn: async (id: string) => api.delete(`/admin-api/listings/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["listings"] });
      notify("Listing deleted");
    },
    onError: () => notify("Delete failed", "error"),
  });

  const columns: GridColDef<AdminListing>[] = [
    {
      field: "photos",
      headerName: "",
      width: 70,
      sortable: false,
      renderCell: (p) => <ImageCell url={p.row.photos[0]} />,
    },
    { field: "title", headerName: "Title", flex: 1, minWidth: 200 },
    {
      field: "dealType",
      headerName: "Deal",
      width: 90,
      renderCell: (p) => (
        <Chip
          size="small"
          label={p.row.dealType === "rent" ? "Rent" : "Buy"}
          color={p.row.dealType === "rent" ? "secondary" : "primary"}
        />
      ),
    },
    {
      field: "price",
      headerName: "Price",
      width: 120,
      renderCell: (p) => <strong>{fmtMoney(p.row.price)}</strong>,
    },
    { field: "propertyType", headerName: "Type", width: 120 },
    { field: "city", headerName: "City", width: 110 },
    { field: "agentName", headerName: "Agent", width: 150 },
    { field: "featured", headerName: "Featured", width: 100, type: "boolean" },
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
          Listings
        </Typography>
        <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={openCreate}>
          New listing
        </Button>
      </Stack>
      <Card sx={{ height: 640 }}>
        <Box sx={{ height: "100%", width: "100%" }}>
          <DataGrid
            rows={data}
            columns={columns}
            loading={isLoading}
            rowHeight={60}
            slots={booleanSlots}
            disableRowSelectionOnClick
            initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
            pageSizeOptions={[25, 50, 100]}
          />
        </Box>
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{editing ? "Edit listing" : "New listing"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <ImageUploadField
              label="Photos"
              multiple
              value={draft.photos}
              onChange={(photos) => set("photos", photos)}
            />
            <TextField
              label="Title"
              value={draft.title}
              onChange={(e) => set("title", e.target.value)}
              fullWidth
            />
            <Box
              sx={{
                display: "grid",
                gap: 2,
                gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
              }}
            >
              <Select value={draft.dealType} onChange={(e) => set("dealType", e.target.value)}>
                <MenuItem value="buy">For sale</MenuItem>
                <MenuItem value="rent">For rent</MenuItem>
              </Select>
              <Select
                value={draft.propertyType}
                displayEmpty
                onChange={(e) => set("propertyType", e.target.value)}
              >
                <MenuItem value="" disabled>
                  Property type
                </MenuItem>
                {types.map((t) => (
                  <MenuItem key={t.id} value={t.id}>
                    {t.name}
                  </MenuItem>
                ))}
              </Select>
              <TextField
                label="Price"
                type="number"
                value={draft.price}
                onChange={(e) => set("price", Number(e.target.value))}
              />
              <TextField
                label="Area (m²)"
                type="number"
                value={draft.areaSqm}
                onChange={(e) => set("areaSqm", Number(e.target.value))}
              />
              <TextField
                label="Beds"
                type="number"
                value={draft.beds}
                onChange={(e) => set("beds", Number(e.target.value))}
              />
              <TextField
                label="Baths"
                type="number"
                value={draft.baths}
                onChange={(e) => set("baths", Number(e.target.value))}
              />
              <TextField
                label="Parking"
                type="number"
                value={draft.parking}
                onChange={(e) => set("parking", Number(e.target.value))}
              />
              <Select
                value={draft.agentId}
                displayEmpty
                onChange={(e) => set("agentId", e.target.value)}
              >
                <MenuItem value="">No agent</MenuItem>
                {agents.map((a) => (
                  <MenuItem key={a.id} value={a.id}>
                    {a.name}
                  </MenuItem>
                ))}
              </Select>
            </Box>
            <TextField
              label="Address"
              value={draft.address}
              onChange={(e) => set("address", e.target.value)}
              fullWidth
            />
            <Box
              sx={{
                display: "grid",
                gap: 2,
                gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr 1fr" },
              }}
            >
              <TextField
                label="City"
                value={draft.city}
                onChange={(e) => set("city", e.target.value)}
              />
              <TextField
                label="Latitude"
                type="number"
                value={draft.lat}
                onChange={(e) => set("lat", Number(e.target.value))}
              />
              <TextField
                label="Longitude"
                type="number"
                value={draft.lng}
                onChange={(e) => set("lng", Number(e.target.value))}
              />
            </Box>
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Amenities
              </Typography>
              <Select
                multiple
                fullWidth
                value={draft.amenities}
                onChange={(e) =>
                  set(
                    "amenities",
                    typeof e.target.value === "string"
                      ? e.target.value.split(",")
                      : e.target.value,
                  )
                }
                input={<OutlinedInput />}
                renderValue={(selected) => (
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                    {selected.map((id) => (
                      <Chip
                        key={id}
                        size="small"
                        label={amenities.find((a) => a.id === id)?.name ?? id}
                      />
                    ))}
                  </Box>
                )}
              >
                {amenities.map((a) => (
                  <MenuItem key={a.id} value={a.id}>
                    {a.name}
                  </MenuItem>
                ))}
              </Select>
            </Box>
            <TextField
              label="Description"
              multiline
              minRows={3}
              value={draft.description}
              onChange={(e) => set("description", e.target.value)}
              fullWidth
            />
            <FormControlLabel
              control={
                <Switch
                  checked={draft.featured}
                  onChange={(e) => set("featured", e.target.checked)}
                />
              }
              label="Featured"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => save.mutate()}
            disabled={!draft.title || save.isPending}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={!!toDelete}
        message={`Delete "${toDelete?.title}"?`}
        onClose={() => setToDelete(null)}
        onConfirm={() => toDelete && remove.mutate(toDelete.id)}
      />
    </Stack>
  );
}
