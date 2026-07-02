# ✈️ Wayfarer – AI Travel Itinerary Generator

An intelligent AI-powered travel planning assistant that interacts naturally with users, understands their travel preferences through conversation, asks only the necessary follow-up questions, and generates personalized day-wise travel itineraries.

The application follows an **agentic workflow**, where multiple specialized AI agents collaborate to understand the user's requirements, plan the trip, validate the itinerary, and present everything inside a modern interactive dashboard.

---

# 📸 Screenshots

## 🏠 Home Page

> Add your homepage screenshot here.

![Home Page](images/home.png)

---

## 🗺️ Generated Itinerary

> Add your generated itinerary screenshot here.

![Generated Itinerary](images/itinerary.png)

---

# ✨ Features

- 🤖 Natural conversational AI assistant
- 🧠 Agentic multi-step reasoning pipeline
- 💬 Context-aware follow-up questions
- 📍 Intelligent destination planning
- 📅 Day-wise itinerary generation
- 💰 Budget estimation & breakdown
- 🏨 Hotel recommendations
- 🚆 Transportation planning
- 🍽️ Food recommendations
- 🎒 Smart packing checklist
- 🌦️ Travel tips & local suggestions
- 💾 Conversation memory using PostgreSQL
- 🔄 Itinerary refinement through follow-up prompts
- ⚡ Streaming responses using Server-Sent Events (SSE)
- 🔌 Supports Gemini, Groq and OpenAI with a provider abstraction layer

---

# 🛠 Tech Stack

## Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

## AI

- Google Gemini
- Groq
- OpenAI

## Deployment

- Vercel
- Railway

---

# 🧠 Agentic Workflow

Unlike a traditional chatbot that relies on a single prompt, Wayfarer follows a multi-stage agentic pipeline.

```
User Prompt
      │
      ▼
Extractor Agent
      │
      ▼
Clarifier Agent
      │
      ▼
Planner Agent
      │
      ▼
Recommendation Agent
      │
      ▼
Validator Agent
      │
      ▼
Interactive Dashboard
```

### 1️⃣ Extractor Agent

Extracts structured trip information from natural language while remembering previous conversation history.

Examples:

- Destination
- Budget
- Duration
- Number of travellers
- Interests
- Food preferences
- Hotel preferences
- Travel pace

---

### 2️⃣ Clarifier Agent

If any important information is missing, the assistant asks only the next most relevant question instead of overwhelming the user.

Example:

> User: Plan a trip to Japan.

Assistant:

- When are you planning to travel?
- What's your approximate budget?

---

### 3️⃣ Planner Agent

Creates a high-level travel plan before generating detailed recommendations.

---

### 4️⃣ Recommendation Agent

Generates the complete itinerary including:

- Day-wise schedule
- Hotels
- Transportation
- Food recommendations
- Budget allocation
- Packing checklist
- Travel tips

---

### 5️⃣ Validator Agent

Performs a validation pass before returning the itinerary to ensure:

- Budget consistency
- Day count correctness
- Required sections exist
- Overall response quality

---

# 📂 Project Structure

```
Wayfarer
│
├── backend
│   ├── app
│   │   ├── core
│   │   ├── llm
│   │   ├── models
│   │   ├── prompts
│   │   ├── routes
│   │   ├── schemas
│   │   ├── services
│   │   └── utils
│   ├── requirements.txt
│   └── server.py
│
├── frontend
│   ├── app
│   ├── components
│   ├── hooks
│   ├── lib
│   └── package.json
│
├── images
│   ├── home.png
│   └── itinerary.png
│
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+

---

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

Create `.env`

```env
LLM_PROVIDER=groq

GROQ_API_KEY=YOUR_API_KEY

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/travel_itinerary

CORS_ORIGINS=http://localhost:3000
```

Start the backend

```bash
uvicorn server:app --reload --port 8001
```

---

## Frontend Setup

```bash
cd frontend

npm install
```

Create `.env.local`

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
```

Run

```bash
npm run dev
```

Open

```
http://localhost:3000
```

---

# 🔄 Switching LLM Providers

Simply change the provider inside `.env`.

### Gemini

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR_KEY
```

### Groq

```env
LLM_PROVIDER=groq
GROQ_API_KEY=YOUR_KEY
```

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=YOUR_KEY
```

No code changes are required.

---

# 🌐 API Endpoints

| Method | Endpoint | Description |
|----------|----------------------------|--------------------------------|
| POST | `/api/chat/stream` | Conversational chat endpoint |
| GET | `/api/chat/{session_id}/history` | Conversation history |
| GET | `/api/itinerary/{session_id}` | Latest itinerary |
| GET | `/api/health` | Health check |

---

# 💬 Example Conversation

### User

> Plan a 7-day trip to Japan.

### Assistant

- When are you planning to travel?
- What's your budget?
- How many travellers?

---

### User

October, ₹2 lakh, 2 people.

---

### Assistant

Generates a complete itinerary dashboard with:

- Day-wise schedule
- Hotel recommendations
- Budget breakdown
- Transportation
- Food suggestions
- Packing checklist
- Travel tips

---

# 🚀 Future Improvements

- Flight booking integration
- Google Maps integration
- Hotel booking APIs
- Weather forecasting
- PDF itinerary export
- Expense tracker
- Multi-language support
- Calendar synchronization

---

# 👨‍💻 Author

**Vrushabh Jain**

If you found this project useful, consider giving it a ⭐ on GitHub.