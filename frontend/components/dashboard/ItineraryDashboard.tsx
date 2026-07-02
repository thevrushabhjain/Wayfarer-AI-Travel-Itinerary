"use client";

import { motion } from "framer-motion";

import { BudgetBreakdownSection } from "@/components/dashboard/BudgetBreakdownSection";
import { DayTimeline } from "@/components/dashboard/DayTimeline";
import { FoodExperiencesSection } from "@/components/dashboard/FoodExperiencesSection";
import { HotelsSection } from "@/components/dashboard/HotelsSection";
import { PackingChecklistSection } from "@/components/dashboard/PackingChecklistSection";
import { TransportationSection } from "@/components/dashboard/TransportationSection";
import { TravelTipsSection } from "@/components/dashboard/TravelTipsSection";
import { TripOverviewCard } from "@/components/dashboard/TripOverviewCard";
import type { TravelItinerary } from "@/lib/types";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

export function ItineraryDashboard({ itinerary }: { itinerary: TravelItinerary }) {
  const currency = itinerary.overview.currency;

  return (
    <motion.div
      data-testid="itinerary-dashboard"
      variants={container}
      initial="hidden"
      animate="show"
      className="mx-auto max-w-5xl space-y-16 px-6 py-10"
    >
      <motion.div variants={item}>
        <TripOverviewCard overview={itinerary.overview} />
      </motion.div>

      <motion.div variants={item}>
        <DayTimeline days={itinerary.day_plans} currency={currency} />
      </motion.div>

      <motion.div variants={item}>
        <BudgetBreakdownSection budget={itinerary.budget_breakdown} />
      </motion.div>

      <motion.div variants={item}>
        <HotelsSection hotels={itinerary.hotels} />
      </motion.div>

      <motion.div variants={item}>
        <TransportationSection options={itinerary.transportation} currency={currency} />
      </motion.div>

      <motion.div variants={item}>
        <FoodExperiencesSection items={itinerary.food_experiences} />
      </motion.div>

      <motion.div variants={item}>
        <PackingChecklistSection items={itinerary.packing_checklist} />
      </motion.div>

      <motion.div variants={item}>
        <TravelTipsSection tips={itinerary.travel_tips} />
      </motion.div>
    </motion.div>
  );
}
