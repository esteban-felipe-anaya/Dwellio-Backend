import BookmarksRoundedIcon from "@mui/icons-material/BookmarksRounded";
import CategoryRoundedIcon from "@mui/icons-material/CategoryRounded";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import EventAvailableRoundedIcon from "@mui/icons-material/EventAvailableRounded";
import ForumRoundedIcon from "@mui/icons-material/ForumRounded";
import HomeWorkRoundedIcon from "@mui/icons-material/HomeWorkRounded";
import NotificationsRoundedIcon from "@mui/icons-material/NotificationsRounded";
import PeopleRoundedIcon from "@mui/icons-material/PeopleRounded";
import StarRoundedIcon from "@mui/icons-material/StarRounded";
import SupportAgentRoundedIcon from "@mui/icons-material/SupportAgentRounded";
import type { SvgIconComponent } from "@mui/icons-material";

export interface NavItem {
  href: string;
  label: string;
  icon: SvgIconComponent;
  color: string;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: DashboardRoundedIcon, color: "#00696D" },
  { href: "/listings", label: "Listings", icon: HomeWorkRoundedIcon, color: "#2e7d32" },
  { href: "/agents", label: "Agents", icon: SupportAgentRoundedIcon, color: "#6a1b9a" },
  { href: "/property-types", label: "Property Types", icon: CategoryRoundedIcon, color: "#ef6c00" },
  { href: "/amenities", label: "Amenities", icon: StarRoundedIcon, color: "#c2185b" },
  { href: "/tours", label: "Tours", icon: EventAvailableRoundedIcon, color: "#0277bd" },
  { href: "/inquiries", label: "Inquiries", icon: ForumRoundedIcon, color: "#00838f" },
  { href: "/saved-searches", label: "Saved Searches", icon: BookmarksRoundedIcon, color: "#5d4037" },
  { href: "/users", label: "Users", icon: PeopleRoundedIcon, color: "#455a64" },
  { href: "/notifications", label: "Notifications", icon: NotificationsRoundedIcon, color: "#d32f2f" },
];
