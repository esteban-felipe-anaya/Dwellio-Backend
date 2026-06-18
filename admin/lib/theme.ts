"use client";
import { createTheme, type PaletteMode, type Theme } from "@mui/material/styles";
// Enables the `MuiDataGrid` key in theme `components` (type augmentation).
import type {} from "@mui/x-data-grid/themeAugmentation";

// Dwellio brand seed.
const SEED = "#00696D";

export function buildTheme(mode: PaletteMode): Theme {
  return createTheme({
    palette: {
      mode,
      primary: { main: SEED },
      secondary: { main: "#4A6365" },
      success: { main: "#2e7d32" },
      error: { main: "#d32f2f" },
      warning: { main: "#ed6c02" },
      info: { main: "#0288d1" },
      background:
        mode === "light"
          ? { default: "#f6f8f8", paper: "#ffffff" }
          : { default: "#0f1414", paper: "#161d1d" },
    },
    shape: { borderRadius: 12 },
    typography: {
      fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
      h4: { fontWeight: 700 },
      h5: { fontWeight: 700 },
      h6: { fontWeight: 600 },
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: { borderRadius: 16, backgroundImage: "none" },
        },
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: { root: { textTransform: "none", borderRadius: 10 } },
      },
      MuiDataGrid: {
        styleOverrides: {
          root: { border: "none" },
          // Vertically center cell content (needed for image cells).
          cell: { display: "flex", alignItems: "center" },
        },
      },
    },
  });
}
