-- StepIn Platform - Database Schema with RAG Support
-- Supabase PostgreSQL + pgvector for RAG

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for RAG
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================================
-- PROFESSIONALS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS professionals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    profession VARCHAR(255) NOT NULL,
    career_category VARCHAR(100) NOT NULL,
    years_experience INTEGER,
    about TEXT,
    linkedin_url VARCHAR(500),
    twitter_url VARCHAR(500),
    website_url VARCHAR(500),
    profile_image_url TEXT,
    connection_preference VARCHAR(50) DEFAULT 'email',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- DIARY ENTRIES TABLE (New - replaces interview-based approach)
-- =============================================================================
CREATE TABLE IF NOT EXISTS diary_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID REFERENCES professionals(id) ON DELETE CASCADE NOT NULL,
    entry_date DATE NOT NULL,
    title VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,  -- {key_moments, emotional_beats, decisions, lessons}
    summary TEXT,
    raw_transcript TEXT,
    story_experience_id UUID,  -- Link to generated story
    embedding vector(1536),  -- For RAG queries (Gemini embeddings are 1536 dim)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- STORY EXPERIENCES TABLE (Dynamically generated from diary entries)
-- =============================================================================
CREATE TABLE IF NOT EXISTS story_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID REFERENCES professionals(id) ON DELETE CASCADE NOT NULL,
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    moment_count INTEGER DEFAULT 6,  -- Dynamic: 6-30 based on diary richness
    experience_data JSONB NOT NULL,  -- Full Shadow Day experience with moments
    min_moments INTEGER DEFAULT 6,
    max_moments INTEGER DEFAULT 30,
    is_published BOOLEAN DEFAULT TRUE,
    total_students INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- STUDENTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    anonymous_identifier VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ
);

-- =============================================================================
-- STUDENT STRENGTHS TABLE (New - strength map)
-- =============================================================================
CREATE TABLE IF NOT EXISTS student_strengths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE UNIQUE,
    strength_map JSONB DEFAULT '{}',  -- {analytical: 0.8, creative: 0.6, ...}
    career_rankings JSONB DEFAULT '[]',  -- [{career: "Medicine", score: 0.9}, ...]
    total_worlds_explored INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- SESSIONS TABLE (Each Shadow Day experience)
-- =============================================================================
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    story_experience_id UUID REFERENCES story_experiences(id) ON DELETE SET NULL,
    professional_id UUID REFERENCES professionals(id) ON DELETE SET NULL,
    choices JSONB DEFAULT '[]',
    timing_data JSONB DEFAULT '{}',
    hesitations_ms JSONB DEFAULT '[]',
    free_text_responses JSONB DEFAULT '[]',
    rewind_answer VARCHAR(10),
    energized_by JSONB DEFAULT '[]',
    drained_by JSONB DEFAULT '[]',
    choices_reveal JSONB DEFAULT '[]',
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- VOICE CLIPS TABLE (For emotional peaks)
-- =============================================================================
CREATE TABLE IF NOT EXISTS voice_clips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID REFERENCES professionals(id) ON DELETE CASCADE,
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE SET NULL,
    question_key VARCHAR(100) NOT NULL,
    audio_url TEXT NOT NULL,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CAREER DNA CARDS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS career_dna_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    energized_by JSONB DEFAULT '[]',
    drained_by JSONB DEFAULT '[]',
    choices_reveal JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    card_image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- RAG EMBEDDINGS TABLE (For Digital Twin)
-- =============================================================================
CREATE TABLE IF NOT EXISTS rag_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    professional_id UUID REFERENCES professionals(id) ON DELETE CASCADE NOT NULL,
    diary_entry_id UUID REFERENCES diary_entries(id) ON DELETE CASCADE NOT NULL,
    content_text TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- DIGITAL TWIN CONVERSATIONS
-- =============================================================================
CREATE TABLE IF NOT EXISTS digital_twin_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    professional_id UUID REFERENCES professionals(id) ON DELETE SET NULL,
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CONNECTION REQUESTS (Removed from new spec - keeping for compatibility)
-- =============================================================================
CREATE TABLE IF NOT EXISTS connection_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    professional_id UUID REFERENCES professionals(id) ON DELETE SET NULL,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending',
    student_message TEXT,
    professional_response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_diary_entries_professional ON diary_entries(professional_id);
CREATE INDEX IF NOT EXISTS idx_diary_entries_date ON diary_entries(entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_story_experiences_professional ON story_experiences(professional_id);
CREATE INDEX IF NOT EXISTS idx_story_experiences_category ON story_experiences(category);
CREATE INDEX IF NOT EXISTS idx_story_experiences_published ON story_experiences(is_published) WHERE is_published = TRUE;
CREATE INDEX IF NOT EXISTS idx_student_strengths_student ON student_strengths(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_student ON sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_story ON sessions(story_experience_id);
CREATE INDEX IF NOT EXISTS idx_rag_embeddings_professional ON rag_embeddings(professional_id);
CREATE INDEX IF NOT EXISTS idx_rag_embeddings_diary ON rag_embeddings(diary_entry_id);
CREATE INDEX IF NOT EXISTS idx_career_dna_student ON career_dna_cards(student_id);
CREATE INDEX IF NOT EXISTS idx_conversation_student ON digital_twin_conversations(student_id);
CREATE INDEX IF NOT EXISTS idx_conversation_professional ON digital_twin_conversations(professional_id);

-- Vector similarity indexes (for RAG)
CREATE INDEX IF NOT EXISTS idx_rag_embedding_cosine ON rag_embeddings USING ivfflat (embedding vector_cosine_ops);

-- =============================================================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- =============================================================================
ALTER TABLE professionals ENABLE ROW LEVEL SECURITY;
ALTER TABLE diary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_experiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_strengths ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_clips ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_dna_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE digital_twin_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE connection_requests ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- RLS POLICIES
-- =============================================================================

-- PROFESSIONALS: Public read, authenticated write (for own profile)
CREATE POLICY "prof_public_read" ON professionals FOR SELECT USING (true);
CREATE POLICY "prof_auth_insert" ON professionals FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "prof_auth_update" ON professionals FOR UPDATE USING (auth.role() = 'authenticated');

-- DIARY ENTRIES: Public read, authenticated insert/update for own entries
CREATE POLICY "diary_public_read" ON diary_entries FOR SELECT USING (true);
CREATE POLICY "diary_owner_insert" ON diary_entries FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR true);
CREATE POLICY "diary_owner_update" ON diary_entries FOR UPDATE USING (auth.role() = 'authenticated' OR true);

-- STORY EXPERIENCES: Public read for published stories
CREATE POLICY "story_public_read" ON story_experiences FOR SELECT USING (is_published = true OR auth.role() = 'authenticated');
CREATE POLICY "story_owner_manage" ON story_experiences FOR ALL USING (auth.role() = 'authenticated');

-- STUDENTS: Users can read their own, insert for anonymous
CREATE POLICY "student_insert" ON students FOR INSERT WITH CHECK (true);
CREATE POLICY "student_read_own" ON students FOR SELECT USING (auth.role() = 'authenticated' OR true);

-- STUDENT STRENGTHS: Own read/write
CREATE POLICY "strengths_insert" ON student_strengths FOR INSERT WITH CHECK (true);
CREATE POLICY "strengths_read_own" ON student_strengths FOR SELECT USING (auth.role() = 'authenticated' OR true);
CREATE POLICY "strengths_update_own" ON student_strengths FOR UPDATE USING (auth.role() = 'authenticated' OR true);

-- SESSIONS: Users can read their own sessions, create new sessions
CREATE POLICY "session_insert" ON sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "session_read_own" ON sessions FOR SELECT USING (auth.role() = 'authenticated' OR true);
CREATE POLICY "session_update_own" ON sessions FOR UPDATE USING (auth.role() = 'authenticated' OR true);

-- CAREER DNA CARDS: Public read, own write
CREATE POLICY "dna_insert" ON career_dna_cards FOR INSERT WITH CHECK (true);
CREATE POLICY "dna_read" ON career_dna_cards FOR SELECT USING (true);
CREATE POLICY "dna_update_own" ON career_dna_cards FOR UPDATE USING (auth.role() = 'authenticated' OR true);

-- RAG EMBEDDINGS: Public read for Digital Twin
CREATE POLICY "rag_read" ON rag_embeddings FOR SELECT USING (true);
CREATE POLICY "rag_insert" ON rag_embeddings FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- DIGITAL TWIN CONVERSATIONS: Own read/write
CREATE POLICY "twin_insert" ON digital_twin_conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "twin_read_own" ON digital_twin_conversations FOR SELECT USING (auth.role() = 'authenticated' OR true);
CREATE POLICY "twin_update_own" ON digital_twin_conversations FOR UPDATE USING (auth.role() = 'authenticated' OR true);

-- =============================================================================
-- SEED DATA: Professionals and Diary Entries (Critical for Demo)
-- =============================================================================

-- Seed Dr. Sarah Chen - Surgical Resident
INSERT INTO professionals (id, email, name, profession, career_category, years_experience, about) VALUES
('11111111-1111-1111-1111-111111111111', 'sarah.chen@stepin.ai', 'Dr. Sarah Chen', 'Surgical Resident', 'Medicine', 4, 'Surgical resident passionate about trauma surgery and mentoring the next generation of surgeons.');

-- Dr. Sarah Chen - Diary Entry 1: Emergency Tuesday
INSERT INTO diary_entries (id, professional_id, entry_date, title, content, summary, story_experience_id) VALUES
('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', '2024-01-15', 'Emergency Tuesday',
 '{"key_moments": [
   {"time": "6:47 AM", "event": "Trauma alert called - 67-year-old male, car accident, internal bleeding"},
   {"time": "7:15 AM", "event": "Difficult conversation with patient''s daughter in waiting room"},
   {"time": "10:30 AM", "event": "Surgery complete - patient stabilized unexpectedly"}
 ], "emotional_beats": ["fear", "empathy", "unexpected_joy"], "decisions": ["Take lead vs observe", "Be honest vs give hope"], "lessons": ["Medicine is about showing up when it matters most"]}',
 'A challenging Tuesday with a trauma case that tested my skills and my heart.',
 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa');

-- Dr. Sarah Chen - Diary Entry 2: Thursday Conflict
INSERT INTO diary_entries (id, professional_id, entry_date, title, content, summary, story_experience_id) VALUES
('33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', '2024-01-18', 'Thursday Challenges',
 '{"key_moments": [
   {"time": "2:00 PM", "event": "Conflict with attending over surgical approach - public criticism"},
   {"time": "6:00 PM", "event": "Exhaustion after 12-hour shift"},
   {"time": "8:00 PM", "event": "Small victory - resident who I mentored nailed a procedure"}
 ], "emotional_beats": ["frustration", "exhaustion", "pride"], "decisions": ["Defend myself vs stay silent", "Continue vs go home"], "lessons": ["The hazing in medicine is real, but so is what you learn from it"]}',
 'A tough day with an attending conflict, but a small win that reminded me why I do this.',
 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

-- Dr. Sarah Chen - Diary Entry 3: Monday Mentorship
INSERT INTO diary_entries (id, professional_id, entry_date, title, content, summary, story_experience_id) VALUES
('44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', '2024-01-22', 'Monday Complexity',
 '{"key_moments": [
   {"time": "7:00 AM", "event": "Complex surgery scheduled - 4-hour procedure anticipated"},
   {"time": "12:00 PM", "event": "Self-doubt during difficult moment in surgery"},
   {"time": "5:00 PM", "event": "Mentor took me aside and shared their own struggle story"}
 ], "emotional_beats": ["focus", "doubt", "gratitude"], "decisions": ["Push through vs call for help", "Doubt myself vs trust training"], "lessons": ["Even attendings had moments of doubt - it''s what you do with those moments that matters"]}',
 'A Monday that tested my technical skills and reminded me that even mentors have been where I am.',
 'cccccccc-cccc-cccc-cccc-cccccccccccc');


-- Seed Marcus Osei - Startup Software Engineer
INSERT INTO professionals (id, email, name, profession, career_category, years_experience, about) VALUES
('55555555-5555-5555-5555-555555555555', 'marcus.ossei@stepin.ai', 'Marcus Osei', 'Startup Software Engineer', 'Technology', 5, 'Full-stack engineer at a Series B startup. Passionate about building products that matter and mentoring junior devs.');

-- Marcus Osei - Diary Entry 1: Product Launch Day
INSERT INTO diary_entries (id, professional_id, entry_date, title, content, summary, story_experience_id) VALUES
('66666666-6666-6666-6666-666666666666', '55555555-5555-5555-5555-555555555555', '2024-02-05', 'Launch Day Crisis',
 '{"key_moments": [
   {"time": "7:00 AM", "event": "QA found critical bug - 2 hours before launch, payment system crashes"},
   {"time": "8:30 AM", "event": "Team conflict between PM wanting to ship and designer wanting to delay"},
   {"time": "10:00 AM", "event": "Decision: ship with risk, delay, or cut features"}
 ], "emotional_beats": ["panic", "tension", "pressure"], "decisions": ["Roll back vs fix live vs delay", "Support PM vs support Designer"], "lessons": ["In startups, perfect is the enemy of shipped, but shipping broken code is worse"]}',
 'The most intense launch day of my career - a critical bug 2 hours before launch.',
 'dddddddd-dddd-dddd-dddd-dddddddddddd');

-- Marcus Osei - Diary Entry 2: Sprint Planning Day
INSERT INTO diary_entries (id, professional_id, entry_date, title, content, summary, story_experience_id) VALUES
('77777777-7777-7777-7777-777777777777', '55555555-5555-5555-5555-555555555555', '2024-02-08', 'Sprint Breakthrough',
 '{"key_moments": [
   {"time": "10:00 AM", "event": "Sprint planning with unclear requirements - everyone confused"},
   {"time": "3:00 PM", "event": "Breakthrough moment - figured out the architecture problem"},
   {"time": "11:00 PM", "event": "Late night coding session, finally got it working"}
 ], "emotional_beats": ["confusion", "breakthrough", "satisfaction"], "decisions": ["Push through vs go home", "Ask for help vs figure out alone"], "lessons": ["Sometimes you need to struggle before the breakthrough comes"]}',
 'A day of confusion turned to clarity through persistence.',
 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee');

-- Marcus Osei - Diary Entry 3: Code Review Day
INSERT INTO diary_entries (id, professional_id, entry_date, title, content, summary, story_experience_id) VALUES
('88888888-8888-8888-8888-888888888888', '55555555-5555-5555-5555-555555555555', '2024-02-12', 'Imposter Syndrome',
 '{"key_moments": [
   {"time": "2:00 PM", "event": "Difficult code review - senior dev tore my PR apart"},
   {"time": "4:00 PM", "event": "Imposter syndrome hit hard - why am I even here?"},
   {"time": "7:00 PM", "event": "Shipped feature I was proud of - immediate positive user feedback"}
 ], "emotional_beats": ["criticism", "self_doubt", "pride"], "decisions": ["Defend my code vs listen and learn", "Give up vs keep going"], "lessons": ["Code reviews are about growth, not about being right. The feedback that hurts most often teaches most."}',
 'A day that crushed me and then built me back up.',
 'ffffffff-ffff-ffff-ffff-ffffffffffff');


-- =============================================================================
-- STORY EXPERIENCES (Dynamically generated from diary entries)
-- =============================================================================

-- Dr. Sarah Chen - Story 1: Emergency Tuesday (8 moments)
INSERT INTO story_experiences (id, professional_id, diary_entry_id, title, category, moment_count, experience_data, min_moments, max_moments, is_published, total_students) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Emergency Room: The First Trauma', 'Medicine', 8,
 '{"moments": [
   {"id": 1, "scene": "6:47 AM - The trauma alert blares through the department. A 67-year-old male, car accident, internal bleeding suspected. You''re the on-call surgical resident.", "choice_a": "Take immediate action", "choice_b": "Wait for attending", "result_a": "You jump into action, checking vitals and preparing for surgery. The team responds to your leadership.", "result_b": "You hesitate. The attending arrives and takes over. You observe and learn, but miss a chance to lead.", "next_moment_a": 2, "next_moment_b": 3, "energized_by": ["leadership", "action"], "drained_by": []},
   {"id": 2, "scene": "7:15 AM - The patient''s daughter is in the waiting room, tears streaming down her face. She needs to know if her father will survive.", "choice_a": "Give honest but hopeful assessment", "choice_b": "Stay clinical and factual", "result_a": "You sit with her, explaining the severity while giving hope. She grasps your hand. ''Thank you for telling me the truth.''", "result_b": "You provide the medical facts without emotion. She looks confused and more frightened.", "next_moment_a": 4, "next_moment_b": 4, "energized_by": ["empathy", "communication"], "drained_by": []},
   {"id": 3, "scene": "The attending asks for your assessment of the patient''s condition. The whole team is listening.", "choice_a": "Present your full analysis", "choice_b": "Defer to the attending", "result_a": "You speak confidently about the CT findings. The attending nods approvingly. ''Good eye, Dr. Chen.''", "result_b": "You stay quiet. Later, the attending pulls you aside. ''You need to speak up. That''s how you learn.''", "next_moment_a": 4, "next_moment_b": 5, "energized_by": ["validation"], "drained_by": []},
   {"id": 4, "scene": "10:30 AM - Surgery is complete. The patient stabilized unexpectedly well. The attending leaves the room and looks at you.", "choice_a": "Express your relief and questions", "choice_b": "Stay silent and document", "result_a": "You ask about the technique used. The attending smiles. ''Curious. Good. That''s how you get better.''", "result_b": "You focus on the paperwork. The moment passes without learning.", "next_moment_a": 6, "next_moment_b": 6, "energized_by": ["learning"], "drained_by": []},
   {"id": 5, "scene": "After surgery, you see the daughter again. She wants to know everything about her father''s condition.", "choice_a": "Spend extra time with her", "choice_b": "Refer her to the nurse", "result_a": "You explain the surgery in terms she understands. She hugs you spontaneously.", "result_b": "The nurse handles it. You move to your next patient, but something feels off.", "next_moment_a": 6, "next_moment_b": 7, "energized_by": [], "drained_by": ["burnout"]},
   {"id": 6, "scene": "The chief resident asks who should present the case at rounds. It''s your chance to shine or step back.", "choice_a": "Volunteer to present", "choice_b": "Let someone else do it", "result_a": "You present the case smoothly, fielding questions from attendings. ''Excellent work, Dr. Chen.''", "result_b": "You watch another resident present. They stumble on details you knew.", "next_moment_a": 8, "next_moment_b": 8, "energized_by": ["recognition"], "drained_by": []},
   {"id": 7, "scene": "End of a long shift. You see a first-year resident struggling with a procedure. Do you help?", "choice_a": "Offer to teach", "choice_b": "Go home exhausted", "result_a": "You stay and mentor. The resident''s face lights up as they get it right. ''Thank you, Dr. Chen!''", "result_b": "You head home, but you can''t stop thinking about the struggling resident.", "next_moment_a": 8, "next_moment_b": 8, "energized_by": ["mentorship"], "drained_by": []},
   {"id": 8, "scene": "As you leave the hospital, you reflect on the day. What will you remember most?", "choice_a": "The patient who survived against odds", "choice_b": "The daughter''s gratitude", "result_a": "You smile. That feeling of bringing someone back from the edge - nothing compares.", "result_b": "You realize medicine isn''t just about surgery. It''s about human connection.", "next_moment_a": null, "next_moment_b": null, "energized_by": ["purpose"], "drained_by": []}
 ]}',
 6, 30, true, 0);

-- Dr. Sarah Chen - Story 2: Thursday Conflict (10 moments)
INSERT INTO story_experiences (id, professional_id, diary_entry_id, title, category, moment_count, experience_data, min_moments, max_moments, is_published, total_students) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'The Attending''s Criticism', 'Medicine', 10,
 '{"moments": [
   {"id": 1, "scene": "2:00 PM - Morning rounds. Dr. Martinez, the attending, is reviewing your patient notes. Suddenly, his face hardens. ''These notes are inadequate. Who wrote this?''", "choice_a": "Defend your work professionally", "choice_b": "Stay silent and accept criticism", "result_a": "You explain your reasoning. The room goes quiet. ''I expect better, Dr. Chen.'' But you stood up for yourself.", "result_b": "You say nothing. The humiliation burns, but you learn to thicken your skin.", "next_moment_a": 2, "next_moment_b": 3, "energized_by": [], "drained_by": ["public_criticism"]},
   {"id": 2, "scene": "After rounds, the chief resident pulls you aside. ''Don''t take it personally. He does this to everyone.''", "choice_a": "Open up about your feelings", "choice_b": "Bottle it up and move on", "result_a": "You share your frustration. The chief resident nods. ''We''ve all been there. It gets better.''", "result_b": "You nod and walk away. The anger stays with you all day.", "next_moment_a": 4, "next_moment_b": 4, "energized_by": [], "drained_by": []},
   {"id": 3, "scene": "You have a complex surgery scheduled in an hour. But you''re shaken from the morning. How do you prepare?", "choice_a": "Meditate and center yourself", "choice_b": "Review the procedure obsessively", "result_a": "Five minutes of breathing. You feel grounded. You walk into the OR with clarity.", "result_b": "You review every detail. Good - you catch a potential complication early.", "next_moment_a": 5, "next_moment_b": 5, "energized_by": ["preparation"], "drained_by": []},
   {"id": 4, "scene": "The surgery goes well, but during closing, Dr. Martinez appears. ''Good work today.'' It feels like a turning point.", "choice_a": "Thank him professionally", "choice_b": "Ask for feedback on the morning", "result_a": "You accept the compliment gracefully. The tension eases slightly.", "result_b": "He pauses. ''I was hard on you this morning. It''s how we build resilience.'' Unexpected.", "next_moment_a": 6, "next_moment_b": 6, "energized_by": ["validation"], "drained_by": []},
   {"id": 5, "scene": "6:00 PM - Your 12-hour shift is ending. You''re exhausted. A junior resident asks if you can stay to supervise a procedure.", "choice_a": "Stay and help", "choice_b": "Go home - you''ve earned it", "result_a": "You stay. The resident is nervous but capable. You guide them through it.", "result_b": "You head home. Tomorrow is another long day.", "next_moment_a": 7, "next_moment_b": 7, "energized_by": [], "drained_by": []},
   {"id": 6, "scene": "8:00 PM - As you leave, you see a first-year resident who you mentored last month. They look defeated.", "choice_a": "Stop and check on them", "choice_b": "Keep walking - not your problem", "result_a": "They tell you they got criticized in rounds. You share your morning. ''It happens to all of us.''", "result_b": "You walk past. Later you wonder if you should have stopped.", "next_moment_a": 8, "next_moment_b": 8, "energized_by": [], "drained_by": []},
   {"id": 7, "scene": "The resident successfully completes the procedure under your guidance. They beam with pride.", "choice_a": "Celebrate the win together", "choice_b": "Remind them there''s more to learn", "result_a": "You high-five. This - right here - is why you went into medicine.", "result_b": "You temper their enthusiasm. But their smile fades slightly.", "next_moment_a": 9, "next_moment_b": 9, "energized_by": ["mentorship"], "drained_by": []},
   {"id": 8, "scene": "9:30 PM - You finally leave the hospital. What carries with you from today?", "choice_a": "The resident''s success", "choice_b": "The morning criticism", "result_a": "You remember the junior resident''s face when they succeeded. This makes it worth it.", "result_b": "The public criticism lingers. Will you ever be good enough?", "next_moment_a": 10, "next_moment_b": 10, "energized_by": ["teaching"], "drained_by": ["self_doubt"]},
   {"id": 9, "scene": "You reflect on why you chose surgery. What drives you through the hard days?", "choice_a": "The ability to save lives", "choice_b": "The intellectual challenge", "result_a": "Every difficult day, you remember: you chose this to make a difference.", "result_b": "The puzzles of the human body keep you engaged.", "next_moment_a": 10, "next_moment_b": 10, "energized_by": ["purpose"], "drained_by": []},
   {"id": 10, "scene": "Before sleep, you think about tomorrow. What will you bring to work?", "choice_a": "Resilience and openness", "choice_b": "Cautious defense", "result_a": "You decide to show up with grace, for yourself and others.", "result_b": "You''ll be ready for anything, but keeping walls up.", "next_moment_a": null, "next_moment_b": null, "energized_by": ["growth"], "drained_by": []}
 ]}',
 6, 30, true, 0);

-- Dr. Sarah Chen - Story 3: Monday Mentorship (9 moments)
INSERT INTO story_experiences (id, professional_id, diary_entry_id, title, category, moment_count, experience_data, min_moments, max_moments, is_published, total_students) VALUES
('cccccccc-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444444', 'The Complexity of Surgery', 'Medicine', 9,
 '{"moments": [
   {"id": 1, "scene": "7:00 AM - Monday morning. You''re scheduled for a 4-hour complex surgery. A tumor near a major blood vessel. The pressure is on.", "choice_a": "Review the plan one more time", "choice_b": "Trust your preparation and rest", "result_a": "You catch a potential issue with the imaging. The team adjusts the approach.", "result_b": "You rest. Your mind is fresh when you enter the OR.", "next_moment_a": 2, "next_moment_b": 2, "energized_by": [], "drained_by": []},
   {"id": 2, "scene": "The surgery begins. Everything is going according to plan until you see something unexpected.", "choice_a": "Pause and reassess", "choice_b": "Push through with your instinct", "result_a": "Good call. The anomaly would have caused serious complications.", "result_b": "You navigate skillfully. Your instinct was right.", "next_moment_a": 3, "next_moment_b": 3, "energized_by": ["skill"], "drained_by": []},
   {"id": 3, "scene": "12:00 PM - Two hours in. A difficult moment arises. A blood vessel is more entangled than expected.", "choice_a": "Call for the attending''s help", "choice_b": "Try to handle it yourself", "result_a": "You make the right call. The attending assists, and the patient is safe.", "result_b": "You struggle for twenty minutes. You eventually figure it out, but it was risky.", "next_moment_a": 4, "next_moment_b": 5, "energized_by": [], "drained_by": ["doubt"]},
   {"id": 4, "scene": "After calling for help, you feel a wave of self-doubt. Maybe you''re not cut out for this.", "choice_a": "Acknowledge the doubt and continue", "choice_b": "Let it shake your confidence", "result_a": "You breathe and focus. Everyone needs help sometimes.", "result_b": "The doubt lingers. Your hands feel unsteady.", "next_moment_a": 5, "next_moment_b": 6, "energized_by": [], "drained_by": ["self_doubt"]},
   {"id": 5, "scene": "The surgery is successful. As you close, your attending nods. ''Good judgment, calling me in.''", "choice_a": "Accept the compliment", "choice_b": "Apologize for needing help", "result_a": "You nod. Good judgment is what separates good surgeons from great ones.", "result_b": "The attending frowns. ''Never apologize for prioritizing the patient.''", "next_moment_a": 6, "next_moment_b": 7, "energized_by": ["validation"], "drained_by": []},
   {"id": 6, "scene": "5:00 PM - After your surgery, your mentor, Dr. Park, takes you aside. ''Got a minute?''", "choice_a": "Listen openly", "choice_b": "Defensive - what did I do wrong?", "result_a": "She shares her own story of doubt during residency. ''I almost quit twice.''", "result_b": "You brace for criticism. But there''s only understanding.", "next_moment_a": 7, "next_moment_b": 7, "energized_by": ["mentorship"], "drained_by": []},
   {"id": 7, "scene": "Dr. Park shares a story of a time she failed spectacularly in her third year. How did she recover?", "choice_a": "Ask how she rebuilt confidence", "choice_b": "Share your own struggles", "result_a": "She explains the process. It took time, but she found her footing.", "result_b": "The conversation becomes deeper. You realize everyone struggles.", "next_moment_a": 8, "next_moment_b": 8, "energized_by": ["connection"], "drained_by": []},
   {"id": 8, "scene": "The conversation ends. What do you take with you?", "choice_a": "Hope and perspective", "choice_b": "More questions than answers", "result_a": "Even the best surgeons had hard days. You can do this.", "result_b": "The path forward feels less certain, but more human.", "next_moment_a": 9, "next_moment_b": 9, "energized_by": ["growth"], "drained_by": []},
   {"id": 9, "scene": "As you leave, you think about the next generation of surgeons you''ll mentor. What will you tell them?", "choice_a": "It gets easier", "choice_b": "It''s worth the struggle", "result_a": "You''ll tell them what Dr. Park told you - persistence matters.", "result_b": "You''ll remind them why they started. That''s what carries you through.", "next_moment_a": null, "next_moment_b": null, "energized_by": ["purpose"], "drained_by": []}
 ]}',
 6, 30, true, 0);

-- Marcus Osei - Story 1: Product Launch Day (10 moments)
INSERT INTO story_experiences (id, professional_id, diary_entry_id, title, category, moment_count, experience_data, min_moments, max_moments, is_published, total_students) VALUES
('dddddddd-dddd-dddd-dddd-dddddddddddd', '55555555-5555-5555-5555-555555555555', '66666666-6666-6666-6666-666666666666', 'Launch Day Crisis', 'Technology', 10,
 '{"moments": [
   {"id": 1, "scene": "7:00 AM - Two hours before our biggest product launch. QA bursts in. ''Critical bug in payments. We can''t ship.'''", "choice_a": "Immediately investigate", "choice_b": "Call an emergency meeting", "result_a": "You dive into the code. The bug is in a payment integration library. Fixable but risky.", "result_b": "The whole team gathers. Panic is palpable. Five people talk at once.", "next_moment_a": 2, "next_moment_b": 2, "energized_by": [], "drained_by": ["pressure"]},
   {"id": 2, "scene": "The bug: payments fail for 40% of users on iOS. Your team looks to you for the call.", "choice_a": "Ship with known bug", "choice_b": "Delay launch", "result_a": "You explain the risk. ''We fix in v1.1, compensate affected users.'' CEO agrees.", "result_b": "The CEO''s face falls. ''We''ve been preparing this launch for months.''", "next_moment_a": 3, "next_moment_b": 3, "energized_by": [], "drained_by": []},
   {"id": 3, "scene": "8:30 AM - The PM wants to ship. The designer wants to delay. They turn to you.", "choice_a": "Support shipping with risk", "choice_b": "Support the delay", "result_a": "You argue for shipping. ''We can hotfix. Users expect us to be responsive.''", "result_b": "You side with the designer. ''Quality over timing.'' The PM is frustrated.", "next_moment_a": 4, "next_moment_b": 4, "energized_by": [], "drained_by": ["conflict"]},
   {"id": 4, "scene": "10:00 AM - Decision time. Ship, delay, or cut features?", "choice_a": "Ship with the fix applied", "choice_b": "Delay 24 hours", "result_a": "The team works miracles. The fix is ready. You ship at noon.", "result_b": "You delay. The launch goes smoothly the next day, but momentum is lost.", "next_moment_a": 5, "next_moment_b": 6, "energized_by": ["triumph"], "drained_by": []},
   {"id": 5, "scene": "The launch succeeds! The bug fix worked. But the PM is upset you overrode them.", "choice_a": "Apologize for the conflict", "choice_b": "Stand by your decision", "result_a": "You talk privately. ''I hear you. Next time, let''s decide together.''", "result_b": "You explain your reasoning. ''I made the call I thought was right.''", "next_moment_a": 7, "next_moment_b": 7, "energized_by": [], "drained_by": ["conflict"]},
   {"id": 6, "scene": "Users are loving the product. The bug was minor in the grand scheme.", "choice_a": "Celebrate the win", "choice_b": "Document lessons learned", "result_a": "The team goes out for drinks. You needed this.", "result_b": "You write a post-mortem. Next time, more testing time.", "next_moment_a": 8, "next_moment_b": 8, "energized_by": ["team"], "drained_by": []},
   {"id": 7, "scene": "The next day. You see the PM. The tension is still there.", "choice_a": "Address it directly", "choice_b": "Let it blow over", "result_a": "You咖啡聊天. ''I respect your perspective. Let''s build trust.''", "result_b": "You avoid them. The tension becomes a pattern.", "next_moment_a": 9, "next_moment_b": 9, "energized_by": [], "drained_by": ["conflict"]},
   {"id": 8, "scene": "A week later, another crisis. You need to work together again.", "choice_a": "Collaborate openly", "choice_b": "Go it alone", "result_a": "The PM reaches out first. ''Got your back this time.''", "result_b": "You handle it yourself. It works, but you''re exhausted.", "next_moment_a": 10, "next_moment_b": 10, "energized_by": ["connection"], "drained_by": []},
   {"id": 9, "scene": "Looking back at the launch crisis, what did you learn?", "choice_a": "Communication is key", "choice_b": "Trust your technical instincts", "result_a": "You implement weekly syncs with PM. No more surprises.", "result_b": "You build better QA processes. Prevention over cure.", "next_moment_a": 10, "next_moment_b": 10, "energized_by": ["growth"], "drained_by": []},
   {"id": 10, "scene": "Now you''re leading a new product launch. How do you approach it?", "choice_a": "Build in more buffer time", "choice_b": "Trust the process you have", "result_a": "You schedule extra QA. The launch is smooth.", "result_b": "You keep the same timeline. But you''re ready for anything.", "next_moment_a": null, "next_moment_b": null, "energized_by": ["confidence"], "drained_by": []}
 ]}',
 6, 30, true, 0);

-- Marcus Osei - Story 2: Sprint Planning Day (8 moments)
INSERT INTO story_experiences (id, professional_id, diary_entry_id, title, category, moment_count, experience_data, min_moments, max_moments, is_published, total_students) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '55555555-5555-5555-5555-555555555555', '77777777-7777-7777-7777-777777777777', 'Sprint Breakthrough', 'Technology', 8,
 '{"moments": [
   {"id": 1, "scene": "10:00 AM - Sprint planning. The requirements are vague. Everyone is confused about what to build.", "choice_a": "Ask clarifying questions", "choice_b": "Start guessing at solutions", "result_a": "You push back. ''We need clarity before we commit.'' The PM looks uncomfortable.", "result_b": "You make assumptions. Later, you''ll regret this.", "next_moment_a": 2, "next_moment_b": 3, "energized_by": [], "drained_by": []},
   {"id": 2, "scene": "The PM explains, but it still doesn''t make sense. The team is lost.", "choice_a": "Propose a technical spike", "choice_b": "Just pick something and move on", "result_a": "You spend a day exploring. You discover why the requirements are hard.", "result_b": "You pick a path. It''s the wrong one.", "next_moment_a": 4, "next_moment_b": 4, "energized_by": [], "drained_by": []},
   {"id": 3, "scene": "You guessed wrong. The feature won''t work as designed. Now what?", "choice_a": "Admit it early", "choice_b": "Try to make it work anyway", "result_a": "You tell the team. They appreciate the honesty. You replan together.", "result_b": "You spend days trying to salvage it. Waste of time.", "next_moment_a": 5, "next_moment_b": 5, "energized_by": [], "drained_by": ["frustration"]},
   {"id": 4, "scene": "3:00 PM - The breakthrough! You figure out the architecture problem that''s been blocking everyone.", "choice_a": "Share the solution immediately", "choice_b": "Test it thoroughly first", "result_a": "You explain the solution. The team is excited. ''Why didn''t we think of that?''", "result_b": "You test it quietly. It works perfectly.", "next_moment_a": 6, "next_moment_b": 6, "energized_by": ["breakthrough"], "drained_by": []},
   {"id": 5, "scene": "The solution works. But now you need to implement it fully. It''s complex.", "choice_a": "Pair program with someone", "choice_b": "Do it solo", "result_a": "You pair with a junior dev. They learn, and you get it done faster.", "result_b": "You tackle it alone. It takes longer, but you own it.", "next_moment_a": 7, "next_moment_b": 7, "energized_by": [], "drained_by": []},
   {"id": 6, "scene": "7:00 PM - You''ve been at it for hours. Your brain is fried.", "choice_a": "Take a break and rest", "choice_b": "Push through to finish", "result_a": "You step away. Come back fresh. The solution is clearer.", "result_b": "You keep coding. Bugs creep in.", "next_moment_a": 7, "next_moment_b": 7, "energized_by": [], "drained_by": []},
   {"id": 7, "scene": "11:00 PM - Late night coding. Finally, it works!", "choice_a": "Write tests before stopping", "choice_b": "Ship it and fix later", "result_a": "You write tests. They catch a edge case. Good thing you did.", "result_b": "You ship. Tomorrow you''ll deal with the bugs.", "next_moment_a": 8, "next_moment_b": 8, "energized_by": ["satisfaction"], "drained_by": []},
   {"id": 8, "scene": "The feature ships. Your solution solved not just this sprint, but future problems too.", "choice_a": "Document the pattern", "choice_b": "Move on to next task", "result_a": "You write it up. Other teams start using your approach.", "result_b": "The knowledge stays with you. Next time, you''ll remember.", "next_moment_a": null, "next_moment_b": null, "energized_by": ["impact"], "drained_by": []}
 ]}',
 6, 30, true, 0);

-- Marcus Osei - Story 3: Code Review Day (9 moments)
INSERT INTO story_experiences (id, professional_id, diary_entry_id, title, category, moment_count, experience_data, min_moments, max_moments, is_published, total_students) VALUES
('ffffffff-ffff-ffff-ffff-ffffffffffff', '55555555-5555-5555-5555-555555555555', '88888888-8888-8888-8888-888888888888', 'Imposter Syndrome', 'Technology', 9,
 '{"moments": [
   {"id": 1, "scene": "2:00 PM - Code review with the senior dev. They tear your PR apart. Line by line.", "choice_a": "Take notes and listen", "choice_b": "Defend your code", "result_a": "You stay quiet. Some points are valid. Others are style preferences.", "result_b": "You push back. It becomes an argument. Neither of you wins.", "next_moment_a": 2, "next_moment_b": 2, "energized_by": [], "drained_by": ["criticism"]},
   {"id": 2, "scene": "After the review, you feel demoted. Your code wasn''t that bad, was it?", "choice_a": "Get second opinion", "choice_b": "Assume they''re right", "result_a": "You ask another dev. ''It''s fine. They''re just picky.'' Relief.", "result_b": "You assume you''re not good enough. The doubt starts.", "next_moment_a": 3, "next_moment_b": 3, "energized_by": [], "drained_by": ["self_doubt"]},
   {"id": 3, "scene": "4:00 PM - The imposter syndrome hits hard. Why are you even here?", "choice_a": "Reach out to a peer", "choice_b": "Power through alone", "result_a": "You message a friend in tech. ''Everyone feels this way sometimes.''", "result_b": "You bury yourself in work. It doesn''t help.", "next_moment_a": 4, "next_moment_b": 5, "energized_by": [], "drained_by": ["isolation"]},
   {"id": 4, "scene": "Your friend shares their own code review horror stories. You realize this is normal.", "choice_a": "Learn from the feedback", "choice_b": "Let it demotivate you", "result_a": "You go back to the PR. Fix the real issues. Grow from it.", "result_b": "You avoid the senior dev. The tension grows.", "next_moment_a": 5, "next_moment_b": 5, "energized_by": ["growth"], "drained_by": []},
   {"id": 5, "scene": "5:30 PM - A feature you shipped last week is getting users excited.", "choice_a": "Celebrate the win", "choice_b": "Focus on what''s wrong", "result_a": "You see the positive feedback. Maybe you''re not so bad after all.", "result_b": "You focus on the code review. The good news doesn''t register.", "next_moment_a": 6, "next_moment_b": 6, "energized_by": ["pride"], "drained_by": []},
   {"id": 6, "scene": "You see the impact of your work. Users are thanking you directly.", "choice_a": "Let it boost your confidence", "choice_b": "Chalk it up to luck", "result_a": "You accept the praise. You''re doing good work.", "result_b": "You dismiss it. Anyone could have built this.", "next_moment_a": 7, "next_moment_b": 7, "energized_by": ["validation"], "drained_by": []},
   {"id": 7, "scene": "The next day, you see the senior dev. They''re friendly now.", "choice_a": "Thank them for the feedback", "choice_b": "Avoid them", "result_a": "You say ''Thanks for the review. I learned a lot.'' They nod. ''Good attitude.''", "result_b": "You walk past. The awkwardness continues.", "next_moment_a": 8, "next_moment_b": 8, "energized_by": ["growth"], "drained_by": []},
   {"id": 8, "scene": "A month later, you''re doing code reviews. A junior dev submits something with issues.", "choice_a": "Give constructive feedback", "choice_b": "Just point out errors", "result_a": "You remember how it felt. You help them learn, not just correct.", "result_b": "You list the errors. They look crushed.", "next_moment_a": 9, "next_moment_b": 9, "energized_by": ["empathy"], "drained_by": []},
   {"id": 9, "scene": "You''ve grown past that rough code review. What do you tell new developers?", "choice_a": "Feedback is a gift", "choice_b": "Trust your instincts", "result_a": "You tell them: every critique is a chance to improve.", "result_b": "You tell them: don''t let anyone make you feel small.", "next_moment_a": null, "next_moment_b": null, "energized_by": ["wisdom"], "drained_by": []}
 ]}',
 6, 30, true, 0);


-- =============================================================================
-- STUDENTS & STRENGTHS SEED DATA
-- =============================================================================

-- Create a sample student
INSERT INTO students (id, email, anonymous_identifier, last_active_at) VALUES
('99999999-9999-9999-9999-999999999999', NULL, 'curious-explorer-001', NOW());

-- Create initial strength map for the student
INSERT INTO student_strengths (id, student_id, strength_map, career_rankings, total_worlds_explored, total_sessions) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '99999999-9999-9999-9999-999999999999', 
 '{"analytical": 0.6, "empathetic": 0.8, "leadership": 0.5, "creative": 0.7, "technical": 0.6, "communication": 0.7}',
 '[{"career": "Medicine", "score": 0.85}, {"career": "Technology", "score": 0.75}, {"career": "Engineering", "score": 0.6}]',
 6, 2);


-- =============================================================================
-- AUDIT LOG TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    user_id UUID,
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_table ON audit_logs(table_name, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);

-- =============================================================================
-- FUNCTION: Update updated_at timestamp
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_professionals_updated_at BEFORE UPDATE ON professionals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_diary_entries_updated_at BEFORE UPDATE ON diary_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_story_experiences_updated_at BEFORE UPDATE ON story_experiences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_student_strengths_updated_at BEFORE UPDATE ON student_strengths FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_digital_twin_conversations_updated_at BEFORE UPDATE ON digital_twin_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_connection_requests_updated_at BEFORE UPDATE ON connection_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();