"""Orchestrator: coordinates the collaborating agents into one conversational turn.

This is the only module that knows the overall pipeline order. It never talks to the
LLM directly - it delegates to the Extractor, Clarifier, Planner, Recommendation and
Validator agents, and streams simple progress events (never chain-of-thought) that the
frontend renders as "Understanding your request" / "Planning itinerary" / "Finalizing
itinerary".
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.llm.base import LLMProvider, LLMProviderError
from app.models.conversation import ConversationSession
from app.schemas.chat import TripInfo
from app.services import conversation_service
from app.services.clarifier_service import ClarifierService
from app.services.extractor_service import ExtractorService
from app.services.planner_service import PlannerService
from app.services.recommendation_service import RecommendationService
from app.services.validator_service import ValidatorService
from app.utils.field_rules import get_missing_fields

logger = get_logger(__name__)


class OrchestratorService:
    def __init__(self, provider: LLMProvider) -> None:
        self.extractor = ExtractorService(provider)
        self.clarifier = ClarifierService(provider)
        self.planner = PlannerService(provider)
        self.recommendation = RecommendationService(provider)
        self.validator = ValidatorService(provider)

    async def process_turn(
        self, db: AsyncSession, session: ConversationSession, user_message: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        try:
            await conversation_service.save_message(db, session.id, "user", user_message)
            history = await conversation_service.get_recent_messages(db, session.id)
            conversation_text = conversation_service.format_conversation_text(history[:-1])
            current_trip_info = TripInfo.model_validate(session.trip_info)

            yield {"event": "progress", "stage": "understanding"}
            updated_trip_info = await self.extractor.extract(current_trip_info, conversation_text, user_message)
            await conversation_service.update_trip_info(db, session, updated_trip_info)

            if session.status == "completed":
                async for event in self._handle_refinement(db, session, updated_trip_info, user_message):
                    yield event
                return

            missing_fields = get_missing_fields(updated_trip_info)
            if missing_fields:
                async for event in self._handle_clarification(db, session, updated_trip_info, missing_fields):
                    yield event
                return

            async for event in self._handle_generation(db, session, updated_trip_info):
                yield event

        except LLMProviderError as exc:
            logger.error("LLM provider error during conversation turn: %s", exc)
            yield {
                "event": "error",
                "detail": "The planning assistant is temporarily unavailable. Please try again in a moment.",
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error during conversation turn")
            yield {
                "event": "error",
                "detail": "Something went wrong while processing your request. Please try again.",
            }

    async def _handle_clarification(
        self,
        db: AsyncSession,
        session: ConversationSession,
        trip_info: TripInfo,
        missing_fields: list[str],
    ) -> AsyncGenerator[dict[str, Any], None]:
        history = await conversation_service.get_recent_messages(db, session.id)
        conversation_text = conversation_service.format_conversation_text(history)
        next_field = missing_fields[0]
        question = await self.clarifier.ask(trip_info, next_field, conversation_text)
        await conversation_service.save_message(db, session.id, "assistant", question)
        yield {
            "event": "result",
            "type": "question",
            "session_id": session.id,
            "reply": question,
            "trip_info": trip_info.model_dump(),
            "missing_fields": missing_fields,
        }

    async def _handle_generation(
        self, db: AsyncSession, session: ConversationSession, trip_info: TripInfo
    ) -> AsyncGenerator[dict[str, Any], None]:
        yield {"event": "progress", "stage": "planning"}
        skeleton = await self.planner.create_skeleton(trip_info)

        yield {"event": "progress", "stage": "finalizing"}
        itinerary = await self.recommendation.build_itinerary(trip_info, skeleton)
        final_itinerary, is_valid, remaining_issues = await self.validator.validate_and_repair(trip_info, itinerary)

        await conversation_service.save_itinerary(db, session.id, final_itinerary, is_valid)
        await conversation_service.set_status(db, session, "completed")

        if remaining_issues:
            logger.warning("Itinerary saved with unresolved validation notes: %s", remaining_issues)

        reply = (
            f"Your {trip_info.duration_days}-day trip to {trip_info.destination} is ready. "
            "I've put together a full day-by-day plan, budget breakdown, hotel picks, and more below."
        )
        await conversation_service.save_message(db, session.id, "assistant", reply)

        yield {
            "event": "result",
            "type": "itinerary",
            "session_id": session.id,
            "reply": reply,
            "trip_info": trip_info.model_dump(),
            "itinerary": final_itinerary.model_dump(mode="json"),
        }

    async def _handle_refinement(
        self, db: AsyncSession, session: ConversationSession, trip_info: TripInfo, user_message: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        existing_itinerary = await conversation_service.get_latest_itinerary(db, session.id)
        if existing_itinerary is None:
            async for event in self._handle_generation(db, session, trip_info):
                yield event
            return

        yield {"event": "progress", "stage": "finalizing"}
        revised = await self.recommendation.revise_itinerary(trip_info, existing_itinerary, user_message)
        final_itinerary, is_valid, remaining_issues = await self.validator.validate_and_repair(trip_info, revised)

        await conversation_service.save_itinerary(db, session.id, final_itinerary, is_valid)

        if remaining_issues:
            logger.warning("Revised itinerary saved with unresolved validation notes: %s", remaining_issues)

        reply = "I've updated your itinerary based on your feedback."
        await conversation_service.save_message(db, session.id, "assistant", reply)

        yield {
            "event": "result",
            "type": "itinerary",
            "session_id": session.id,
            "reply": reply,
            "trip_info": trip_info.model_dump(),
            "itinerary": final_itinerary.model_dump(mode="json"),
        }
