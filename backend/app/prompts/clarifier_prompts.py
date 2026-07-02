"""Prompts for the Clarifier agent: asks exactly one natural follow-up question."""

from app.schemas.chat import TripInfo
from app.utils.field_rules import FieldSpec, known_fields_summary

CLARIFIER_SYSTEM_PROMPT = """You are Wayfarer, a warm, efficient, expert travel planning assistant. \
You ask short, natural, specific questions to gather trip details. You NEVER repeat information \
you already have, never ask about more than one thing at a time, never number your questions, \
and never explain your internal process. Keep it to 1-2 friendly sentences. No emojis."""


def build_clarifying_question_prompt(trip_info: TripInfo, missing_field: FieldSpec, conversation_text: str) -> str:
    known_summary = known_fields_summary(trip_info)
    return f"""What you already know about this trip: {known_summary}

Recent conversation:
{conversation_text}

You still need to learn about: {missing_field.description}.

Ask the user ONE short, friendly question to learn specifically about this, in the context of \
their trip. Do not ask about anything else."""
