"""Structured schemas describing a complete, structured travel itinerary.

These Pydantic models serve double duty:
1. They are passed directly as ``response_schema`` to the LLM provider so
   the model returns JSON that conforms to this exact structure.
2. They validate the LLM's output before it is persisted or sent to the
   frontend, guaranteeing type safety end-to-end.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Activity(BaseModel):
    time: str = Field(description="Local time of the activity, e.g. '09:00' or '14:30'")
    title: str = Field(description="Short title of the activity, e.g. 'Visit Senso-ji Temple'")
    description: str = Field(description="1-2 sentence description of what happens and why it's worth it")
    category: str = Field(
        description="One of: sightseeing, food, culture, adventure, leisure, transport, shopping, nightlife"
    )
    location: str = Field(description="Neighborhood or exact venue name")
    estimated_cost: float = Field(description="Estimated cost per person in the trip's budget currency")
    duration_hours: float = Field(description="Approximate duration of the activity in hours")


class DayPlan(BaseModel):
    day_number: int = Field(description="1-indexed day of the trip")
    date: str = Field(description="Calendar date for this day, ISO format YYYY-MM-DD if known, else 'Day N'")
    theme: str = Field(description="A short theme/title for the day, e.g. 'Historic Old Town & River Cruise'")
    activities: list[Activity] = Field(description="Ordered list of activities for the day, at least 3")


class BudgetItem(BaseModel):
    category: str = Field(
        description="One of: Accommodation, Food, Transportation, Activities, Shopping, Miscellaneous"
    )
    amount: float = Field(description="Estimated total amount allocated to this category for the whole trip")
    percentage: float = Field(description="Percentage of total budget this category represents (0-100)")
    notes: str = Field(description="Short note explaining the estimate")


class BudgetBreakdown(BaseModel):
    total_budget: float = Field(description="The total trip budget provided by the traveler")
    currency: str = Field(description="ISO currency code, e.g. USD, EUR, INR")
    items: list[BudgetItem] = Field(description="Breakdown of the budget across categories")
    daily_average: float = Field(description="Average estimated spend per day")


class Hotel(BaseModel):
    name: str = Field(description="Hotel or accommodation name (can be a realistic representative example)")
    area: str = Field(description="Neighborhood/area where it is located and why that area is convenient")
    price_range: str = Field(description="Nightly price range in the trip's currency, e.g. '$120-180/night'")
    rating: float = Field(description="Approximate guest rating out of 5")
    tier: str = Field(description="One of: budget, mid-range, luxury")
    why_recommended: str = Field(description="1-2 sentence justification tailored to the traveler's preferences")


class TransportOption(BaseModel):
    mode: str = Field(description="One of: flight, train, bus, metro, taxi, rideshare, rental car, ferry, walking")
    description: str = Field(description="What this option covers, e.g. getting from airport to city center")
    estimated_cost: float = Field(description="Estimated cost per person")
    tips: str = Field(description="A practical tip for using this transport option")


class FoodExperience(BaseModel):
    name: str = Field(description="Name of the dish, restaurant, or food experience")
    type: str = Field(description="One of: restaurant, street food, cafe, local market, fine dining, dessert")
    description: str = Field(description="What makes it special or worth trying")
    price_range: str = Field(description="Approximate price range per person")
    must_try: bool = Field(description="Whether this is a signature, unmissable experience")


class PackingItem(BaseModel):
    item: str = Field(description="Name of the item to pack")
    category: str = Field(description="One of: clothing, documents, electronics, health, toiletries, misc")
    essential: bool = Field(description="Whether this item is essential vs. nice-to-have")


class TravelTip(BaseModel):
    category: str = Field(description="One of: culture, safety, money, language, weather, connectivity, etiquette")
    tip: str = Field(description="The practical tip itself, 1-2 sentences")


class TripOverview(BaseModel):
    destination: str
    start_date: str = Field(description="ISO date YYYY-MM-DD if known, else empty string")
    end_date: str = Field(description="ISO date YYYY-MM-DD if known, else empty string")
    duration_days: int
    travelers: int
    total_budget: float
    currency: str
    trip_summary: str = Field(description="2-3 sentence engaging summary of the overall trip")
    best_time_note: str = Field(description="A short note on weather/season expectations for the travel dates")


class TravelItinerary(BaseModel):
    """The complete, structured itinerary rendered on the dashboard."""

    overview: TripOverview
    day_plans: list[DayPlan]
    budget_breakdown: BudgetBreakdown
    hotels: list[Hotel] = Field(description="2-4 hotel recommendations across different tiers")
    transportation: list[TransportOption] = Field(description="3-6 transportation options/tips for the trip")
    food_experiences: list[FoodExperience] = Field(description="4-8 food and local experience recommendations")
    packing_checklist: list[PackingItem] = Field(description="8-15 packing checklist items")
    travel_tips: list[TravelTip] = Field(description="5-10 practical travel tips")


class DaySkeleton(BaseModel):
    day_number: int
    theme: str = Field(description="A short working theme for this day, e.g. 'Arrival & Old Town'")
    location_focus: str = Field(description="Primary neighborhood/area or day-trip destination for this day")
    notes: str = Field(description="Brief planning notes: pacing, must-see anchor, or logistics consideration")


class PlanSkeleton(BaseModel):
    """A high-level day-by-day plan created BEFORE the detailed itinerary is written.

    This is the explicit 'planning before execution' step: a lightweight
    outline that guides the more expensive, detailed generation step.
    """

    overall_strategy: str = Field(description="2-3 sentences on the overall approach/flow of the trip")
    days: list[DaySkeleton]
