export interface Activity {
  time: string;
  title: string;
  description: string;
  category: string;
  location: string;
  estimated_cost: number;
  duration_hours: number;
}

export interface DayPlan {
  day_number: number;
  date: string;
  theme: string;
  activities: Activity[];
}

export interface BudgetItem {
  category: string;
  amount: number;
  percentage: number;
  notes: string;
}

export interface BudgetBreakdown {
  total_budget: number;
  currency: string;
  items: BudgetItem[];
  daily_average: number;
}

export interface Hotel {
  name: string;
  area: string;
  price_range: string;
  rating: number;
  tier: string;
  why_recommended: string;
}

export interface TransportOption {
  mode: string;
  description: string;
  estimated_cost: number;
  tips: string;
}

export interface FoodExperience {
  name: string;
  type: string;
  description: string;
  price_range: string;
  must_try: boolean;
}

export interface PackingItem {
  item: string;
  category: string;
  essential: boolean;
}

export interface TravelTip {
  category: string;
  tip: string;
}

export interface TripOverview {
  destination: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  travelers: number;
  total_budget: number;
  currency: string;
  trip_summary: string;
  best_time_note: string;
}

export interface TravelItinerary {
  overview: TripOverview;
  day_plans: DayPlan[];
  budget_breakdown: BudgetBreakdown;
  hotels: Hotel[];
  transportation: TransportOption[];
  food_experiences: FoodExperience[];
  packing_checklist: PackingItem[];
  travel_tips: TravelTip[];
}

export interface TripInfo {
  destination: string | null;
  origin_city: string | null;
  start_date: string | null;
  end_date: string | null;
  duration_days: number | null;
  travel_month: string | null;
  travelers: number | null;
  budget: number | null;
  budget_currency: string;
  interests: string[] | null;
  pace: string | null;
  hotel_preference: string | null;
  dietary_preferences: string[] | null;
}

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: number;
}

export type ProgressStage = "understanding" | "planning" | "finalizing" | null;

export interface StreamResult {
  type: "question" | "itinerary";
  session_id: string;
  reply: string;
  trip_info?: TripInfo;
  itinerary?: TravelItinerary;
  missing_fields?: string[];
}

export interface SessionHistory {
  session_id: string;
  status: string;
  trip_info: TripInfo;
  messages: { role: MessageRole; content: string; created_at: string }[];
  itinerary: TravelItinerary | null;
}
