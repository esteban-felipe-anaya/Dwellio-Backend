"use client";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import type { SvgIconComponent } from "@mui/icons-material";
import { animate, motion, useMotionValue, useTransform } from "framer-motion";
import { useEffect } from "react";

function Counter({ value, prefix = "" }: { value: number; prefix?: string }) {
  const mv = useMotionValue(0);
  const text = useTransform(mv, (v) => `${prefix}${Math.round(v).toLocaleString()}`);
  useEffect(() => {
    const controls = animate(mv, value, { duration: 0.9, ease: "easeOut" });
    return () => controls.stop();
  }, [value, mv]);
  return <motion.span>{text}</motion.span>;
}

interface Props {
  title: string;
  value: number;
  icon: SvgIconComponent;
  color: string;
  prefix?: string;
  delay?: number;
}

export default function KpiCard({
  title,
  value,
  icon: Icon,
  color,
  prefix,
  delay = 0,
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      style={{ height: "100%" }}
    >
      <Card sx={{ height: "100%" }}>
        <CardContent>
          <Stack direction="row" alignItems="center" spacing={2}>
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: 2,
                display: "grid",
                placeItems: "center",
                bgcolor: `${color}1f`,
                color,
              }}
            >
              <Icon />
            </Box>
            <Box>
              <Typography variant="h4" fontWeight={800} lineHeight={1.1}>
                <Counter value={value} prefix={prefix} />
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {title}
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
}
