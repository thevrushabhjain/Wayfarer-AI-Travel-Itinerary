# Wayfarer — AI Travel Itinerary Generator — PRD / Memory

## Original problem statement

Build a production-quality AI Travel Itinerary Generator.

- Frontend: Next.js 15 + TypeScript + Tailwind CSS
- Backend: FastAPI
- Database: PostgreSQL (conversation/session storage)
- LLM: Gemini API by default, pluggable to OpenAI or Groq via env vars only
- Only public/open-source PyPI & npm packages — no Emergent libraries, no
  proprietary SDKs, no "Made with..." branding anywhere
- Modular architecture: routes, services, models, prompts, utils, config
- Agent behaviour: multi-step reasoning, planning before execution, memory
  (conversation state), validation/reflection, structured outputs, multiple
  collaborating service modules acting as agents
- No chain-of-thought exposed to the user; only simple progress states
  ("Understanding your request", "Planning itinerary", "Finalizing itinerary")
- Frontend: premium monochrome SaaS interface (not a generic chatbot),
  conversational experience that resolves into a polished dashboard with
  Trip Overview, Day-wise Timeline, Budget Breakdown, Hotels, Transportation,
  Food & Local Experiences, Packing Checklist, Travel Tips
- Must be runnable locally: `pip install -r requirements.txt`, PostgreSQL,
  `npm install`, `uvicorn`, `npm run dev`

## User choices gathered

1. Exact stack confirmed: Next.js 15 + TS + Tailwind, FastAPI, PostgreSQL
   (not SQLite), only public packages, no Emergent branding.
2. LLM: Gemini as default provider (user-provided API key), clean provider
   abstraction to switch to OpenAI/Groq via env vars only. OpenAI/Groq
   implemented architecturally (no live keys provided/needed for MVP).
3. PostgreSQL required (not SQLite).
4. Design: strictly monochrome (black/white/gray only), premium
   developer/SaaS aesthetic, subtle grid pattern, elegant typography, smooth
   animations, no colorful gradients, no generic-chatbot look.
5. Agent should ask one question at a time, in natural language, remembering
   prior answers, covering: budget, dates/duration, travelers, interests,
   pace, hotel preference, dietary preferences.

## Architecture implemented

- **Backend** (`/app/backend`): FastAPI app (`app/main.py`), SQLAlchemy async
  + asyncpg for PostgreSQL (`app/core/database.py`, `app/models/`), Pydantic
  schemas for structured LLM I/O (`app/schemas/travel.py`, `app/schemas/chat.py`).
  - LLM provider abstraction (`app/llm/`): `LLMProvider` base class,
    `GeminiProvider` (google-genai SDK, default & fully tested),
    `OpenAIProvider` (openai SDK, strict JSON schema), `GroqProvider` (groq
    SDK, JSON-object mode). Selected via `LLM_PROVIDER` env var only.
  - Collaborating agents (`app/services/`): `ExtractorService`,
    `ClarifierService`, `PlannerService` (skeleton before execution),
    `RecommendationService` (full itinerary + revisions),
    `ValidatorService` (deterministic checks + 1 LLM repair pass),
    orchestrated by `OrchestratorService` which streams SSE progress events.
  - Conversation memory persisted in PostgreSQL (`conversation_sessions`,
    `messages`, `itinerary_records` tables).
  - Endpoints: `POST /api/chat/stream` (SSE), `GET /api/chat/{id}/history`,
    `GET /api/itinerary/{id}`, `GET /api/health`.

- **Frontend** (`/app/frontend`): Next.js 15 App Router + TypeScript +
  Tailwind, strictly monochrome dark theme per `/app/design_guidelines.json`.
  - `hooks/use-chat.ts`: manages conversation state, SSE streaming client,
    localStorage session persistence.
  - `components/chat/*`: conversational hero + message list + progress
    stepper (Understanding/Planning/Finalizing).
  - `components/dashboard/*`: Trip Overview (hero card + Calendar popover),
    Day Timeline, Budget Breakdown (bars), Hotels, Transportation, Food &
    Local Experiences, Packing Checklist (Select filter + Checkbox), Travel
    Tips.
  - shadcn/ui components used: Card, Badge, Select, Checkbox, Popover,
    Calendar, Sonner (Toast).
  - No Next.js/Vercel/React branding, dev indicator disabled.

## What's been implemented (2026-07-02)

- Full conversational pipeline: natural language → structured extraction →
  one-question-at-a-time clarification → planning skeleton → detailed
  itinerary generation → validation/repair → polished dashboard.
- Refinement flow: after itinerary exists, further chat messages are treated
  as revision requests against the existing itinerary.
- Verified end-to-end via curl (Gemini) and Playwright screenshots: full
  Rome/Lisbon trip generation flows working, dashboard renders correctly.
- PostgreSQL running locally in this environment (`travel_itinerary` db).

## Testing notes (2026-07-02)

- Full pipeline verified live end-to-end via curl and Playwright with the
  real Gemini API (Lisbon, Rome trips): extraction, one-question-at-a-time
  clarification, planning skeleton, full itinerary generation, and
  deterministic budget/day-count validation all passed.
- The user's Gemini key is on the free tier (20 requests/day) and was
  exhausted during testing. Per user instruction, all remaining UI/dashboard/
  interaction verification (packing filter, calendar popover, session
  persistence, reset, error toast) was completed against a seeded mock
  session (bypassing the LLM only for this verification) — the live Gemini
  integration code itself was never touched or mocked, and remains fully
  wired for the user's own final live test once quota is available.
- Fixed 2 bugs found by the testing agent: (1) raw provider error strings
  were leaking to the frontend on failures — now sanitized to a generic
  message with full detail logged server-side; (2) retry logic was retrying
  non-retryable errors (quota/auth/bad request) — now only retries transient
  5xx/network errors via `app/llm/retry_utils.py`.
- Production build verified: `npm run build` compiles and type-checks
  successfully (fixed a stray root-level `yarn.lock` confusing Next's
  workspace root detection, pinned `typescript` to a stable 5.7.3 release,
  and converted all shadcn/ui primitives actually in use — badge, button,
  calendar, checkbox, popover, select, sonner — to properly typed `.tsx`
  files, resolving TS build errors that only surfaced under strict
  `next build` type-checking).
- Full repo swept for TODO/FIXME/placeholder/dead code: none found.
- Backend module import and AST syntax sweep: no errors across `app/`.
- Both services (backend on :8001, frontend on :3000) confirmed healthy and
  running via supervisor.

## Status: Complete

All features from the problem statement are implemented and verified to the
extent possible without live LLM quota (per user's explicit instruction to
finalize now; user will run the final live end-to-end pass themselves once
a working Gemini key/quota is available). No known bugs, TODOs, or
incomplete code paths remain.

## Bug fix pass (2026-07-02, follow-up)

- User reported `backend/services/llm_client.py` importing
  `emergentintegrations.llm.chat`. Investigation (full-repo grep, git log
  across all history, `pip show`) conclusively found this file/import never
  existed in this repository. The unused `emergentintegrations` PyPI package
  (present-but-never-imported in the shared venv) was uninstalled entirely
  for full cleanliness. Verified by `testing_agent_v3` (iteration_2 and
  iteration_3): zero references anywhere, `ModuleNotFoundError` on import,
  clean `requirements.txt`.
- Testing surfaced a real, separate regression: the dev server (port 3000)
  rendered a blank page due to an unpinned `"next": "15"` dependency
  resolving to 15.5.20, which has a buggy internal Next.js DevTools
  "Segment Explorer" feature that crashes dev-mode SSR. Fixed by pinning
  `next` to an exact stable `15.3.3` in `package.json` and doing a full
  clean `node_modules` reinstall. Verified fixed and stable across multiple
  restarts by `testing_agent_v3` (iteration_3), and `npm run build`
  continues to pass.

## Test credentials

No authentication is implemented in this MVP (no login required). See
`/app/memory/test_credentials.md` (N/A — no accounts).
