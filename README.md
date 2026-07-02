# Wayfarer — AI Travel Itinerary Generator

Wayfarer is a production-quality, agentic AI travel planning application. It has a
genuine conversation with the traveler, extracts structured trip requirements,
asks only for what's still missing, plans a trip strategy, generates a fully
detailed itinerary, and validates its own output before showing it — all
rendered as a polished, monochrome dashboard.

This is a standalone application with its own identity: no references to any
AI builder platform, no framework branding, and no third-party/proprietary
SDKs. Only public packages from PyPI and npm are used.

## Architecture

```
┌─────────────────────┐        SSE / HTTPS        ┌──────────────────────────┐
│   Next.js 15 (TS)    │ ─────────────────────────▶│  FastAPI backend         │
│   Frontend           │◀───────────────────────── │  (agentic pipeline)      │
└─────────────────────┘                            └──────────────────────────┘
                                                              │
                                                              ▼
                                                    ┌──────────────────────┐
                                                    │  PostgreSQL           │
                                                    │  (conversation memory)│
                                                    └──────────────────────┘
                                                              │
                                                              ▼
                                                    ┌──────────────────────┐
                                                    │  LLM Provider Layer   │
                                                    │  Gemini / OpenAI /Groq│
                                                    └──────────────────────┘
```

### Agentic pipeline (backend)

Each stage below is an independent, collaborating service module — the
backend is not a single prompt, it is a small pipeline of specialized agents
orchestrated by `OrchestratorService`:

1. **Extractor agent** (`services/extractor_service.py`) — turns natural
   language + conversation history into structured `TripInfo` (destination,
   dates, travelers, budget, interests, pace, hotel preference, dietary
   preferences), merging with what's already known.
2. **Clarifier agent** (`services/clarifier_service.py`) — if required
   information is missing, asks exactly one natural, context-aware question
   for the next missing field (never repeats known info).
3. **Planner agent** (`services/planner_service.py`) — "planning before
   execution": produces a lightweight day-by-day strategy/skeleton before any
   detailed content is written.
4. **Recommendation agent** (`services/recommendation_service.py`) — the
   itinerary architect: expands the skeleton into the full structured
   itinerary (day plans, hotels, transportation, food, budget, packing,
   tips), and later handles revision requests.
5. **Validator agent** (`services/validator_service.py`) — a reflection step:
   runs deterministic checks (day count, budget sums, missing sections) and,
   if issues are found, performs a single LLM repair pass before the result
   is ever returned to the user.

The user only ever sees three simple progress states — `Understanding your
request`, `Planning itinerary`, `Finalizing itinerary` — streamed over
Server-Sent Events. No chain-of-thought or internal reasoning is ever exposed.

### LLM provider abstraction

`app/llm/base.py` defines an `LLMProvider` interface with two methods:
`generate_structured` (schema-constrained JSON, used for extraction/planning/
itinerary generation) and `generate_text` (free-form, used for clarifying
questions). `GeminiProvider`, `OpenAIProvider`, and `GroqProvider` all
implement this exact interface. Switching providers is one environment
variable — **no application code changes required**:

```bash
LLM_PROVIDER=gemini   # or: openai, groq
```

## Prerequisites

- Python 3.11+
- Node.js 20+ and npm
- PostgreSQL 14+

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` (see `backend/.env.example`):

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/travel_itinerary
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

Get a free Gemini API key at https://aistudio.google.com/apikey.

Create the database (tables are created automatically on startup):

```bash
createdb travel_itinerary
# or: psql -c "CREATE DATABASE travel_itinerary;"
```

Run the backend:

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The API is now available at `http://localhost:8001/api`, with interactive
docs at `http://localhost:8001/docs`.

## Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
```

Run the dev server:

```bash
npm run dev
```

Open `http://localhost:3000`.

For a production build:

```bash
npm run build
npm run start:prod
```

## Switching LLM providers

Set `LLM_PROVIDER` to `openai` or `groq` and provide the matching API key —
no code changes needed:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
```

## API overview

| Method | Path                          | Description                                              |
|--------|-------------------------------|------------------------------------------------------------|
| POST   | `/api/chat/stream`            | Main conversational endpoint. Server-Sent Events stream of `progress` and `result` events. |
| GET    | `/api/chat/{session_id}/history` | Full conversation history, trip info, and latest itinerary for a session. |
| GET    | `/api/itinerary/{session_id}` | The latest generated itinerary for a session. |
| GET    | `/api/health`                 | Health check. |

## Project structure

```
backend/
  server.py                # uvicorn entrypoint
  app/
    core/                   # settings, database, logging
    models/                 # SQLAlchemy ORM models (conversation memory)
    schemas/                # Pydantic schemas (structured LLM I/O + API contracts)
    llm/                    # provider abstraction (base, gemini, openai, groq, factory)
    prompts/                # prompt templates per agent
    services/               # collaborating agents + orchestrator
    routes/                 # FastAPI routers
    utils/                  # field rules, schema conversion helpers

frontend/
  app/                      # Next.js App Router pages, layout, global styles
  components/
    chat/                   # conversational UI
    dashboard/              # itinerary dashboard sections
    layout/                 # background/grid
    ui/                     # shadcn/ui primitives
  hooks/                    # use-chat (conversation state + SSE client)
  lib/                      # api client, types, session, utils
```

## Notes on data persistence

Conversation memory (trip requirements, message history) and generated
itineraries are stored in PostgreSQL via SQLAlchemy's async engine. Tables
are created automatically on startup via `Base.metadata.create_all` — this is
intentional for a project of this scope; introduce Alembic if you need
versioned migrations later.
