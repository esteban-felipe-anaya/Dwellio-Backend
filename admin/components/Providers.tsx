"use client";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { PaletteMode } from "@mui/material";
import { AuthProvider } from "@/lib/auth";
import { buildTheme } from "@/lib/theme";
import { ToastProvider } from "@/lib/toast";

interface ColorModeState {
  mode: PaletteMode;
  toggle: () => void;
}
const ColorModeContext = createContext<ColorModeState>({
  mode: "light",
  toggle: () => {},
});
export const useColorMode = () => useContext(ColorModeContext);

const MODE_KEY = "dwellio_admin_mode";

export default function Providers({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<PaletteMode>("light");
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { refetchOnWindowFocus: false, retry: 1 } },
      }),
  );

  useEffect(() => {
    // Hydrate the persisted color-mode preference once on mount.
    const saved = window.localStorage.getItem(MODE_KEY) as PaletteMode | null;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (saved === "light" || saved === "dark") setMode(saved);
  }, []);

  const colorMode = useMemo<ColorModeState>(
    () => ({
      mode,
      toggle: () =>
        setMode((prev) => {
          const next = prev === "light" ? "dark" : "light";
          window.localStorage.setItem(MODE_KEY, next);
          return next;
        }),
    }),
    [mode],
  );

  const theme = useMemo(() => buildTheme(mode), [mode]);

  return (
    <AppRouterCacheProvider options={{ key: "mui" }}>
      <ColorModeContext.Provider value={colorMode}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <QueryClientProvider client={queryClient}>
            <ToastProvider>
              <AuthProvider>{children}</AuthProvider>
            </ToastProvider>
          </QueryClientProvider>
        </ThemeProvider>
      </ColorModeContext.Provider>
    </AppRouterCacheProvider>
  );
}
