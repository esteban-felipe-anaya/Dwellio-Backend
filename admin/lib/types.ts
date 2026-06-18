// API response types (camelCase, matching the FastAPI backend).

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  phone: string;
  photo?: string | null;
  isStaff: boolean;
  isSuperuser: boolean;
}

export interface AdminListing {
  id: string;
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
  agentId?: string | null;
  agentName?: string | null;
  ownerId?: string | null;
  description: string;
  featured: boolean;
  listedAt?: string | null;
}

export interface AdminAgent {
  id: string;
  name: string;
  photo?: string | null;
  agency: string;
  phone: string;
  rating: number;
  reviewCount: number;
  listingCount: number;
}

export interface Lookup {
  id: string;
  name: string;
  icon: string;
}

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  phone: string;
  photo?: string | null;
  isStaff: boolean;
  isSuperuser: boolean;
  isActive: boolean;
  createdAt?: string | null;
  favoritesCount: number;
  savedSearchesCount: number;
}

export interface AdminTour {
  id: string;
  listingId: string;
  listingTitle?: string | null;
  userId: string;
  userName?: string | null;
  date: string;
  slot: string;
  status: string;
  scheduledFor?: string | null;
  createdAt?: string | null;
}

export interface AdminInquiry {
  id: string;
  listingId: string;
  listingTitle?: string | null;
  userId: string;
  userName?: string | null;
  type: string;
  lastMessage: string;
  status: string;
  date?: string | null;
}

export interface AdminSavedSearch {
  id: string;
  label: string;
  filters: Record<string, unknown>;
  createdAt?: string | null;
  userId: string;
  userName?: string | null;
  newMatches: number;
}

export interface AdminNotification {
  id: string;
  title: string;
  body: string;
  type: string;
  read: boolean;
  date?: string | null;
  listingId?: string | null;
}

export interface LabelCount {
  label: string;
  value: number;
}
export interface CityAvg {
  city: string;
  avgPrice: number;
}
export interface AgentCount {
  name: string;
  value: number;
}
export interface RecentListing {
  id: string;
  title: string;
  price: number;
  city: string;
  dealType: string;
  listedAt?: string | null;
}
export interface RecentInquiry {
  id: string;
  listingTitle?: string | null;
  type: string;
  status: string;
  date?: string | null;
}

export interface Stats {
  totalListings: number;
  activeListings: number;
  toursScheduled: number;
  openInquiries: number;
  totalUsers: number;
  totalAgents: number;
  listingsOverTime: LabelCount[];
  byPropertyType: LabelCount[];
  byDealType: LabelCount[];
  avgPriceByCity: CityAvg[];
  topAgents: AgentCount[];
  recentListings: RecentListing[];
  recentInquiries: RecentInquiry[];
}
