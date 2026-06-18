"use client";
import ForumRoundedIcon from "@mui/icons-material/ForumRounded";
import HomeWorkRoundedIcon from "@mui/icons-material/HomeWorkRounded";
import EventAvailableRoundedIcon from "@mui/icons-material/EventAvailableRounded";
import VisibilityRoundedIcon from "@mui/icons-material/VisibilityRounded";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";
import { BarChart } from "@mui/x-charts/BarChart";
import { LineChart } from "@mui/x-charts/LineChart";
import { PieChart } from "@mui/x-charts/PieChart";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import KpiCard from "@/components/KpiCard";
import StatusChip from "@/components/StatusChip";
import { api } from "@/lib/api";
import type { Stats } from "@/lib/types";

const fmtMoney = (n: number) =>
  `$${n >= 1000000 ? (n / 1000000).toFixed(1) + "M" : Math.round(n).toLocaleString()}`;

export default function DashboardPage() {
  const { data, isLoading } = useQuery<Stats>({
    queryKey: ["stats"],
    queryFn: async () => (await api.get<Stats>("/admin-api/stats")).data,
  });

  if (isLoading || !data) {
    return (
      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", lg: "repeat(4,1fr)" },
        }}
      >
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} variant="rounded" height={104} />
        ))}
      </Box>
    );
  }

  const kpis = [
    { title: "Total listings", value: data.totalListings, icon: HomeWorkRoundedIcon, color: "#2e7d32" },
    { title: "Featured / active", value: data.activeListings, icon: VisibilityRoundedIcon, color: "#00696D" },
    { title: "Tours scheduled", value: data.toursScheduled, icon: EventAvailableRoundedIcon, color: "#0277bd" },
    { title: "Open inquiries", value: data.openInquiries, icon: ForumRoundedIcon, color: "#ed6c02" },
  ];

  return (
    <Stack spacing={3}>
      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", lg: "repeat(4,1fr)" },
        }}
      >
        {kpis.map((k, i) => (
          <KpiCard key={k.title} {...k} delay={i * 0.08} />
        ))}
      </Box>

      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", md: "2fr 1fr" },
        }}
      >
        <ChartCard title="Listings over time">
          <LineChart
            height={280}
            xAxis={[
              {
                scaleType: "point",
                data: data.listingsOverTime.map((p) => p.label),
              },
            ]}
            series={[
              {
                data: data.listingsOverTime.map((p) => p.value),
                area: true,
                color: "#00696D",
                showMark: false,
                label: "Listings",
              },
            ]}
            sx={{
              "& .MuiAreaElement-root": { fillOpacity: 0.18 },
            }}
          />
        </ChartCard>
        <ChartCard title="By property type">
          <PieChart
            height={280}
            series={[
              {
                innerRadius: 50,
                paddingAngle: 2,
                cornerRadius: 4,
                data: data.byPropertyType.map((p, i) => ({
                  id: i,
                  value: p.value,
                  label: p.label,
                })),
              },
            ]}
          />
        </ChartCard>
      </Box>

      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", md: "1fr 1fr 1fr" },
        }}
      >
        <ChartCard title="Buy vs Rent">
          <BarChart
            height={260}
            xAxis={[
              {
                scaleType: "band",
                data: data.byDealType.map((d) =>
                  d.label === "rent" ? "Rent" : "Buy",
                ),
              },
            ]}
            series={[
              {
                data: data.byDealType.map((d) => d.value),
                color: "#4A6365",
              },
            ]}
          />
        </ChartCard>
        <ChartCard title="Avg price by city">
          <BarChart
            height={260}
            xAxis={[
              { scaleType: "band", data: data.avgPriceByCity.map((c) => c.city) },
            ]}
            series={[
              {
                data: data.avgPriceByCity.map((c) => Math.round(c.avgPrice)),
                color: "#2e7d32",
                valueFormatter: (v) => (v == null ? "" : fmtMoney(v)),
              },
            ]}
          />
        </ChartCard>
        <ChartCard title="Top agents">
          <BarChart
            height={260}
            layout="horizontal"
            yAxis={[{ scaleType: "band", data: data.topAgents.map((a) => a.name) }]}
            series={[{ data: data.topAgents.map((a) => a.value), color: "#6a1b9a" }]}
          />
        </ChartCard>
      </Box>

      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
        }}
      >
        <Card>
          <CardHeader title="Recent listings" />
          <Divider />
          <List dense>
            {data.recentListings.map((l) => (
              <ListItem key={l.id} divider>
                <ListItemText
                  primary={l.title}
                  secondary={`${l.city} · ${l.dealType === "rent" ? "Rent" : "Buy"}`}
                />
                <Typography fontWeight={700}>{fmtMoney(l.price)}</Typography>
              </ListItem>
            ))}
          </List>
        </Card>
        <Card>
          <CardHeader title="Recent inquiries" />
          <Divider />
          <List dense>
            {data.recentInquiries.map((q) => (
              <ListItem key={q.id} divider>
                <ListItemText
                  primary={q.listingTitle ?? q.id}
                  secondary={q.type}
                />
                <StatusChip status={q.status} />
              </ListItem>
            ))}
          </List>
        </Card>
      </Box>
    </Stack>
  );
}

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={700} mb={1}>
            {title}
          </Typography>
          {children}
        </CardContent>
      </Card>
    </motion.div>
  );
}
