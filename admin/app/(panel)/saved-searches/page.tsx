"use client";
import { Box, Card, Chip, Stack, Typography } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import type { AdminSavedSearch } from "@/lib/types";

function filtersSummary(filters: Record<string, unknown>): string {
  return Object.entries(filters)
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join("/") : String(v)}`)
    .join(" · ");
}

export default function SavedSearchesPage() {
  const { data = [], isLoading } = useQuery<AdminSavedSearch[]>({
    queryKey: ["saved-searches"],
    queryFn: async () =>
      (await api.get<AdminSavedSearch[]>("/admin-api/saved-searches")).data,
  });

  const columns: GridColDef<AdminSavedSearch>[] = [
    { field: "label", headerName: "Label", flex: 1, minWidth: 200 },
    { field: "userName", headerName: "User", width: 160 },
    {
      field: "filters",
      headerName: "Filters",
      flex: 2,
      minWidth: 240,
      sortable: false,
      renderCell: (p) => (
        <Typography variant="body2" color="text.secondary" noWrap>
          {filtersSummary(p.row.filters)}
        </Typography>
      ),
    },
    {
      field: "newMatches",
      headerName: "Live matches",
      width: 130,
      renderCell: (p) => (
        <Chip size="small" color="primary" label={p.row.newMatches} />
      ),
    },
    {
      field: "createdAt",
      headerName: "Created",
      width: 170,
      valueFormatter: (v) => fmtDate(v as string | null),
    },
  ];

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>
        Saved Searches
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
    </Stack>
  );
}
