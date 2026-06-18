"use client";
import {
  Box,
  Card,
  Chip,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { booleanSlots, ImageCell, RowActions } from "@/components/gridHelpers";
import { api } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import type { AdminSavedSearch, AdminUser } from "@/lib/types";

export default function UsersPage() {
  const { data = [], isLoading } = useQuery<AdminUser[]>({
    queryKey: ["users"],
    queryFn: async () => (await api.get<AdminUser[]>("/admin-api/users")).data,
  });

  const [selected, setSelected] = useState<AdminUser | null>(null);

  const { data: savedSearches = [] } = useQuery<AdminSavedSearch[]>({
    queryKey: ["user-saved-searches", selected?.id],
    queryFn: async () =>
      (await api.get<AdminSavedSearch[]>(`/admin-api/saved-searches?user=${selected?.id}`)).data,
    enabled: !!selected,
  });
  const { data: favorites = [] } = useQuery<string[]>({
    queryKey: ["user-favorites", selected?.id],
    queryFn: async () =>
      (await api.get<string[]>(`/admin-api/favorites?user=${selected?.id}`)).data,
    enabled: !!selected,
  });

  const columns: GridColDef<AdminUser>[] = [
    {
      field: "photo",
      headerName: "",
      width: 70,
      sortable: false,
      renderCell: (p) => <ImageCell url={p.row.photo} />,
    },
    { field: "name", headerName: "Name", flex: 1, minWidth: 150 },
    { field: "email", headerName: "Email", flex: 1, minWidth: 200 },
    { field: "phone", headerName: "Phone", width: 150 },
    { field: "isStaff", headerName: "Staff", width: 90, type: "boolean" },
    { field: "isSuperuser", headerName: "Super", width: 90, type: "boolean" },
    { field: "favoritesCount", headerName: "Favorites", width: 100 },
    { field: "savedSearchesCount", headerName: "Searches", width: 100 },
    {
      field: "actions",
      headerName: "",
      width: 70,
      sortable: false,
      renderCell: (p) => <RowActions onView={() => setSelected(p.row)} />,
    },
  ];

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>
        Users
      </Typography>
      <Card sx={{ height: 600 }}>
        <Box sx={{ height: "100%", width: "100%" }}>
          <DataGrid
            rows={data}
            columns={columns}
            loading={isLoading}
            rowHeight={56}
            slots={booleanSlots}
            disableRowSelectionOnClick
            initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
            pageSizeOptions={[25, 50, 100]}
          />
        </Box>
      </Card>

      <Drawer anchor="right" open={!!selected} onClose={() => setSelected(null)}>
        <Box sx={{ width: 360, p: 3 }}>
          <Typography variant="h6" fontWeight={700}>
            {selected?.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {selected?.email}
          </Typography>
          <Stack direction="row" spacing={1} mt={1}>
            {selected?.isStaff && <Chip size="small" color="primary" label="Staff" />}
            {selected?.isSuperuser && (
              <Chip size="small" color="secondary" label="Superuser" />
            )}
          </Stack>
          <Typography variant="caption" color="text.secondary">
            Joined {fmtDate(selected?.createdAt)}
          </Typography>

          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>
            Saved searches ({savedSearches.length})
          </Typography>
          <List dense>
            {savedSearches.map((s) => (
              <ListItem key={s.id} disableGutters>
                <ListItemText primary={s.label} secondary={`${s.newMatches} live matches`} />
              </ListItem>
            ))}
            {savedSearches.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                None
              </Typography>
            )}
          </List>

          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>
            Favorites ({favorites.length})
          </Typography>
          <Stack direction="row" flexWrap="wrap" gap={0.5}>
            {favorites.map((id) => (
              <Chip key={id} size="small" variant="outlined" label={id} />
            ))}
            {favorites.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                None
              </Typography>
            )}
          </Stack>
        </Box>
      </Drawer>
    </Stack>
  );
}
