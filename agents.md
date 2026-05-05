# StepIn Agent Architecture — Updated May 2026

## Overview

StepIn uses a multi-agent pipeline to turn a professional's journal entry into an interactive career world for students, then personalize the experience based on the student's choices.

---

## Agent Pipeline

### 1. Journal Chat Agent (Conversational)
**Endpoint:** `POST /api/professional/journal/chat`
**Purpose:** Conversational AI companion that guides a professional through journaling about their workday.
- Maintains full conversation history (passed from frontend as `messages` array)
- Asks follow-up questions about emotions, challenges, and key decisions
- Professional ends the session manually via the **"Save & Turn Into a Student Experience"** button (no auto-detect)
- Model: `gemini-2.0-flash`

### 2. Story Generation Agent
**Endpoint:** `POST /api/professional/journal/save`
**Purpose:** Takes the journal conversation and generates a structured interactive story in JSON.
- Input: Full message history, professional name, profession
- Output: A JSON `experience_data` object with **6–10 interactive moments**
- Each moment contains: `text_lines`, `choices` (2–3 options), `emotional_intensity`, `pull_quote`
- Saves to `story_experiences` table with `professional_name` and `profession/category` columns
- Model: `gemini-2.5-pro`

### 3. Profile Agent
**Endpoint:** `POST /api/agents/profile`
**Purpose:** Analyzes a student's choices, hesitation times, and free-text responses to build a psychological profile.
- Input: `student_id`, `choices[]`, `hesitations_ms[]`, `free_text_responses[]`
- Output: `energized_by`, `drained_by`, `choices_reveal` arrays
- Saves result to `student_strengths` table (best-effort) and in-memory via `save_student_dna()`
- Model: `gemini-2.5-pro`

### 4. Reflection Agent (Career DNA Generator)
**Endpoint:** `POST /api/agents/reflection`
**Purpose:** Generates a student's Career DNA based on their accumulated choices across career worlds.
- Input: `student_id`, `profile_data` (includes `career_name`, `energized_by`, `drained_by`), available careers list
- Output: Rich DNA object with insights, patterns, and 2–3 career recommendations
- Recommendations are **restricted to careers that exist in `story_experiences`** (no hallucination)
- Automatically saves to in-memory DNA store via `save_student_dna()` after generation
- Model: `gemini-2.5-pro`

### 5. Recommender Agent
**Endpoint:** `POST /api/agents/recommender`
**Purpose:** Recommends career worlds to a student based on their saved profile.
- Input: `student_id`, `profile_data`
- Fetches student's saved profile from `student_strengths` (DB) or passes the given profile data
- Fetches available career worlds from `story_experiences` (published only)
- Returns ranked career recommendations with reasons
- Model: `gemini-2.5-pro`

---

## Student DNA Store

Because `student_strengths` has a FK constraint on a legacy `students` table (not Supabase Auth), DNA is stored in-memory on the backend:

**Module:** `backend/app/routes/student.py`
- `save_student_dna(student_id, dna)` — merges new DNA into existing (accumulates over multiple sessions)
- `GET /api/student/dna/{student_id}` — returns merged DNA; tries DB fallback if not in memory
- `POST /api/student/dna/{student_id}` — manual upsert

DNA is **additive**: each Shadow Day session adds to (not replaces) `energized_by`, `drained_by`, and `choices_reveal`.

---

## Authentication (Supabase Auth)

Both students and professionals authenticate via Supabase Auth with role-based routing:

| Role | Dashboard | Login URL |
|------|-----------|-----------|
| `student` | `/student` | `/auth/login?role=student` |
| `professional` | `/professional` | `/auth/login?role=professional` |

- Role is stored in `user_metadata.role` at signup
- Login enforces role — a student account cannot log in via the professional portal
- Next.js middleware (`src/middleware.ts`) protects `/professional/*` and `/student/*`
- Profession stored in `user_metadata.profession` for professionals

---

## Story Display (Careers Page)

- `GET /api/careers` — returns all categories with world counts
- `GET /api/careers/{category}/worlds?search=` — returns worlds sorted latest-first, filtered by search (title or professional name)
- Each world card shows: **title**, **professional name** (`by <name>`), **category**
- `professional_name` is stored directly in `story_experiences` (no extra lookup needed)

---

## Key Design Decisions

1. **No auto-finish in journal** — Removed keyword detection (`"finish"`, `"done"`) that was cutting sessions short. Professional uses a dedicated **Save button**.
2. **DNA accumulation** — Student profiles grow over time as they explore more careers. Arrays deduplicate to avoid noise.
3. **In-memory + best-effort DB** — Avoids breaking FK constraints; backend memory is source of truth for live sessions.
4. **Profession as category** — Professional's registered profession becomes the story category, enabling career-based browsing/filtering.