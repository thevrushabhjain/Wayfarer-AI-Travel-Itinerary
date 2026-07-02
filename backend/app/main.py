"""FastAPI application factory and lifecycle wiring."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.logging_config import configure_logging, get_logger
from app.routes import chat, health, itinerary

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up. LLM provider: %s", settings.llm_provider)
    await init_db()
    yield
    logger.info("Shutting down.")
    await close_db()


app = FastAPI(
    title="Travel Itinerary Generator API",
    description="An agentic AI travel planning backend with a pluggable LLM provider layer.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router_prefix = "/api"
app.include_router(health.router, prefix=f"{api_router_prefix}/health", tags=["health"])
app.include_router(chat.router, prefix=f"{api_router_prefix}/chat", tags=["chat"])
app.include_router(itinerary.router, prefix=f"{api_router_prefix}/itinerary", tags=["itinerary"])
