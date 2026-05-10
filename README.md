# StepIn — Career Exploration Platform

StepIn is an AI-powered career exploration platform that connects professionals with students through immersive Shadow Day experiences. Professionals share their career journeys via interactive journaling, and students explore these worlds to discover their Career DNA.

---

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (React 18)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Animations:** Framer Motion
- **Database/Auth:** Supabase (PostgreSQL + Auth)
- **Audio:** Howler.js for ambient sounds

### Backend
- **Framework:** FastAPI (Python)
- **AI:** Google Gemini (google-genai)
- **Agent Orchestration:** LangGraph
- **Database:** Supabase (PostgreSQL)
- **Caching:** Redis

---

## Project Structure

```
stepin/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # AI agents (LangGraph-based)
│   │   │   ├── base.py
│   │   │   ├── profile_agent.py
│   │   │   ├── reflection_agent.py
│   │   │   ├── recommender_agent.py
│   │   │   └── scenario_agent.py
│   │   ├── models/         # Pydantic models
│   │   ├── routes/         # API endpoints
│   │   │   ├── journal.py      # Professional journaling
│   │   │   ├── careers.py      # Career worlds
│   │   │   ├── student.py      # Student DNA
│   │   │   └── agents.py       # Agent endpoints
│   │   ├── services/       # Business logic
│   │   │   ├── gemini_service.py
│   │   │   ├── rag_service.py
│   │   │   └── world_builder_service.py
│   │   ├── database.py
│   │   └── main.py
│   ├── migrations/
│   └── requirements.txt
│
└── stepin/                 # Next.js frontend
    └── src/
        └── app/
            ├── auth/login/     # Authentication
            ├── student/        # Student dashboard
            ├── professional/   # Professional dashboard
            └── shadow-day/     # Career exploration experience
                ├── page.tsx        # World selection
                ├── rewind/         # Interactive story player
                ├── the-drop/       # First moment experience
                └── dna-card/       # Career DNA display
```

---

## How It Works

### For Professionals

1. **Sign up** at `/auth/login?role=professional`
2. **Journal** about your workday using the AI companion
3. **Save** your journal to transform it into an interactive career world
4. Students can now explore your career journey

### For Students

1. **Sign up** at `/auth/login?role=student`
2. **Explore** career worlds across different categories (Medicine, Technology, etc.)
3. **Experience** interactive stories with choices that reveal your interests
4. **Discover** your Career DNA — what energizes you and what drains you
5. **Get recommendations** for careers that match your DNA

---

## AI Agents

| Agent | Purpose |
|-------|---------|
| **Journal Chat Agent** | Conversational AI that guides professionals through journaling |
| **Story Generation Agent** | Converts journal entries into interactive JSON stories |
| **Profile Agent** | Analyzes student choices to build psychological profile |
| **Reflection Agent** | Generates Career DNA from accumulated choices |
| **Recommender Agent** | Recommends career worlds based on student profile |

---

## API Endpoints

### Authentication
- `POST /api/professional/register` — Register professional
- `POST /api/student/register` — Register student

### Journaling
- `POST /api/professional/journal/chat` — Chat with AI companion
- `POST /api/professional/journal/save` — Save journal as story

### Career Worlds
- `GET /api/careers` — List all categories
- `GET /api/careers/{category}/worlds` — Get worlds by category

### Student DNA
- `GET /api/student/dna/{student_id}` — Get student's Career DNA
- `POST /api/student/dna/{student_id}` — Save/update DNA

### Agents
- `POST /api/agents/profile` — Generate student profile
- `POST /api/agents/reflection` — Generate Career DNA
- `POST /api/agents/recommender` — Get recommendations

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.12+
- Supabase account
- Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run server
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend Setup

```bash
cd stepin
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

---

## Environment Variables

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_key
REDIS_URL=your_redis_url
```

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8001
```

