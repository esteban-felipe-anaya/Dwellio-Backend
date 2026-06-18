"use client";
import CottageRoundedIcon from "@mui/icons-material/CottageRounded";
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ITEMS } from "./nav";

export const EXPANDED_WIDTH = 248;
export const COLLAPSED_WIDTH = 76;

export default function Sidebar({ open }: { open: boolean }) {
  const pathname = usePathname();
  const width = open ? EXPANDED_WIDTH : COLLAPSED_WIDTH;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,
        whiteSpace: "nowrap",
        "& .MuiDrawer-paper": {
          width,
          overflowX: "hidden",
          transition: "width 200ms ease",
          borderRight: (t) => `1px solid ${t.palette.divider}`,
        },
      }}
    >
      <Stack
        direction="row"
        alignItems="center"
        spacing={1.5}
        sx={{ px: 2, height: 64, minHeight: 64 }}
      >
        <CottageRoundedIcon color="primary" />
        {open && (
          <Typography variant="h6" fontWeight={800} noWrap>
            Dwellio
          </Typography>
        )}
      </Stack>
      <List sx={{ px: 1 }}>
        {NAV_ITEMS.map((item, i) => {
          const selected =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <Tooltip title={open ? "" : item.label} placement="right" arrow>
                <ListItemButton
                  component={Link}
                  href={item.href}
                  selected={selected}
                  sx={{
                    borderRadius: 2,
                    mb: 0.5,
                    minHeight: 46,
                    justifyContent: open ? "initial" : "center",
                    px: 2,
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: open ? 2 : "auto",
                      justifyContent: "center",
                      color: selected ? item.color : "text.secondary",
                    }}
                  >
                    <Icon />
                  </ListItemIcon>
                  {open && (
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontWeight: selected ? 700 : 500,
                        noWrap: true,
                      }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            </motion.div>
          );
        })}
      </List>
      <Box flexGrow={1} />
    </Drawer>
  );
}
