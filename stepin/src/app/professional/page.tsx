"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";


interface ProfessionalData {
  id: string;
  name: string;
  career_title: string;
  years_experience: number;
  students_count: number;
  connection_requests: number;
  voice_clips_recorded: number;
}

function ProfessionalDashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const professionalId = searchParams.get("id");
  
  const [professional, setProfessional] = useState<ProfessionalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "interview" | "students" | "connections" | "stories">("overview");
  const [userEmail, setUserEmail] = useState<string | null>(null);
  
  useEffect(() => {
    const supabase = createClient();
    // Load Supabase user
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUserEmail(user.email || null);
        const displayName = user.user_metadata?.name || user.email?.split('@')[0] || 'Professional';
        setProfessional({
          id: user.id,
          name: displayName,
          career_title: user.user_metadata?.career_title || 'Professional',
          years_experience: user.user_metadata?.years_experience || 0,
          students_count: 0,
          connection_requests: 0,
          voice_clips_recorded: 0,
        });
      } else {
        // Fallback demo data
        setProfessional({
          id: professionalId || "demo-professional",
          name: "Professional",
          career_title: "Career Professional",
          years_experience: 0,
          students_count: 0,
          connection_requests: 0,
          voice_clips_recorded: 0,
        });
      }
      setLoading(false);
    });
  }, [professionalId]);
  
  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }
  
  if (!professional) {
    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center">
        <p className="text-red-400 mb-4">Professional not found</p>
        <button
          onClick={() => router.push("/")}
          className="text-gray-400 hover:text-white"
        >
          Return home
        </button>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/10 p-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-light">{professional.name}</h1>
            <p className="text-gray-400">{professional.career_title}{professional.years_experience > 0 ? ` • ${professional.years_experience} years` : ''}</p>
            {userEmail && <p className="text-gray-600 text-xs mt-0.5">{userEmail}</p>}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={async () => {
                const supabase = createClient();
                await supabase.auth.signOut();
                router.push('/auth/login?role=professional');
              }}
              className="text-gray-500 hover:text-red-400 text-sm transition-colors"
            >
              Log Out
            </button>
            <button
              onClick={() => router.push('/')}
              className="text-gray-400 hover:text-white"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </header>
      
      {/* Navigation Tabs */}
      <nav className="border-b border-white/10">
        <div className="max-w-6xl mx-auto flex gap-8 px-6 overflow-x-auto">
          {[
            { key: "overview", label: "Overview" },
            { key: "voice-chat", label: "📓 Journal", href: "/professional/voice-chat" },
            { key: "stories", label: "📖 Stories" },
          ].map((tab) => (
            tab.href ? (
              <a
                key={tab.key}
                href={tab.href}
                className="py-4 border-b-2 border-transparent text-gray-500 hover:text-gray-300 transition-colors whitespace-nowrap"
              >
                {tab.label}
              </a>
            ) : (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as typeof activeTab)}
                className={`py-4 border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? "border-white text-white"
                    : "border-transparent text-gray-500 hover:text-gray-300"
                }`}
              >
                {tab.label}
              </button>
            )
          ))}
        </div>
      </nav>
      
      {/* Content */}
      <main className="max-w-6xl mx-auto p-6">
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <StatCard
              title="Stories Published"
              value={professional.students_count}
              description="Interactive career worlds you've created"
            />
            <div className="bg-white/5 border border-white/10 rounded-lg p-6 flex flex-col justify-between">
              <div>
                <h3 className="text-gray-400 text-sm uppercase tracking-wide">Your Journal</h3>
                <p className="text-gray-300 mt-2 text-sm">Share a new day from your career and turn it into an experience for students.</p>
              </div>
              <a href="/professional/voice-chat" className="mt-4 inline-block px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition-colors">
                Write Todays Entry →
              </a>
            </div>
          </div>
        )}
        
        {activeTab === "interview" && (
          <InterviewRecorder />
        )}
        
        {activeTab === "students" && (
          <StudentsList />
        )}
        
        {activeTab === "connections" && (
          <ConnectionRequests />
        )}

        {activeTab === "stories" && (
          <StoriesList professionalId={professional.id} />
        )}
      </main>
    </div>
  );
}

function StatCard({ title, value, description }: { title: string; value: number; description: string }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6">
      <h3 className="text-gray-400 text-sm uppercase tracking-wide">{title}</h3>
      <p className="text-4xl font-light mt-2">{value}</p>
      <p className="text-gray-500 text-sm mt-2">{description}</p>
    </div>
  );
}

function InterviewRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  const professionalId = "demo-professional"; // In production, get from auth
  
  const questions = [
    { key: "worst_monday", question: "Tell me about the worst Monday morning you've had in your career." },
    { key: "advice_at_20", question: "If you could give advice to your 20-year-old self, what would it be?" },
    { key: "almost_quit", question: "What's a moment that almost made you quit?" },
    { key: "best_day", question: "Describe the best day in your career." },
    { key: "unspoken_truth", question: "What's an unspoken truth about your career?" },
  ];
  
  // Start interview on mount
  useEffect(() => {
    async function startInterview() {
      try {
        const response = await fetch(`${apiUrl}/api/interview/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            professional_id: professionalId,
            professional_name: "Dr. Sarah Chen",
            career_title: "Chief Medical Officer",
            years_experience: 12,
            category: "Medicine",
          }),
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log("Interview started:", data);
        }
      } catch (err) {
        console.error("Error starting interview:", err);
        setError("Could not start interview. Please check if backend is running.");
      }
    }
    
    startInterview();
  }, [apiUrl, professionalId]);
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error starting recording:", err);
    }
  };
  
  const stopRecording = () => {
    setIsRecording(false);
  };
  
  const saveAnswer = async () => {
    if (!audioBlob) return;
    
    setIsSubmitting(true);
    const question = questions[currentQuestion];
    
    // For now, we'll use text input as fallback since we need to transcribe
    // In production, use Whisper API or Gemini to transcribe the audio
    const textAnswer = prompt("Please type your answer (audio transcription coming soon):") || "";
    
    try {
      const response = await fetch(`${apiUrl}/api/interview/submit-answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          professional_id: professionalId,
          answer_text: textAnswer,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnswers({ ...answers, [question.key]: textAnswer });
        console.log("Answer submitted:", data);
      }
    } catch (err) {
      console.error("Error submitting answer:", err);
    }
    
    setIsSubmitting(false);
  };
  
  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setAudioBlob(null);
    }
  };
  
  const buildWorld = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/interview/build-world`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          professional_id: professionalId,
          professional_name: "Dr. Sarah Chen",
          career_title: "Chief Medical Officer",
          years_experience: 12,
          category: "Medicine",
          interview_responses: answers,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log("Career world built:", data);
        alert("Career World created successfully! Students can now experience your journey.");
      }
    } catch (err) {
      console.error("Error building world:", err);
    }
  };
  
  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-xl font-light mb-6">Record Your Interview</h2>
      
      <div className="bg-white/5 border border-white/10 rounded-lg p-8">
        <div className="flex items-center justify-between mb-6">
          <span className="text-gray-400">
            Question {currentQuestion + 1} of {questions.length}
          </span>
          <span className={`px-3 py-1 rounded-full text-sm ${
            audioBlob ? "bg-green-500/20 text-green-400" : 
            isRecording ? "bg-red-500/20 text-red-400" :
            "bg-gray-500/20 text-gray-400"
          }`}>
            {audioBlob ? "Recorded" : isRecording ? "Recording..." : "Not recorded"}
          </span>
        </div>
        
        <p className="text-lg mb-8">{questions[currentQuestion].question}</p>
        
        <div className="flex items-center justify-center gap-4">
          {!isRecording && !audioBlob && (
            <button
              onClick={startRecording}
              className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-colors"
            >
              <span className="sr-only">Start recording</span>
              <div className="w-4 h-4 bg-white rounded-full" />
            </button>
          )}
          
          {isRecording && (
            <button
              onClick={stopRecording}
              className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-colors animate-pulse"
            >
              <span className="sr-only">Stop recording</span>
              <div className="w-6 h-6 bg-white rounded-sm" />
            </button>
          )}
          
          {audioBlob && (
            <div className="flex gap-4">
              <button
                onClick={startRecording}
                className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                disabled={isSubmitting}
              >
                Re-record
              </button>
              <button
                onClick={saveAnswer}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Saving..." : "Save Answer"}
              </button>
              {currentQuestion < questions.length - 1 && (
                <button
                  onClick={nextQuestion}
                  className="px-6 py-3 bg-white text-black hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Next Question →
                </button>
              )}
              {currentQuestion === questions.length - 1 && answers[questions[currentQuestion].key] && (
                <button
                  onClick={buildWorld}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  Build My World →
                </button>
              )}
            </div>
          )}
        </div>
        
        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
        
        {Object.keys(answers).length > 0 && (
          <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <p className="text-green-400 text-sm">
              ✓ {Object.keys(answers).length} of {questions.length} questions answered
            </p>
          </div>
        )}
        
        {audioBlob && (
          <div className="mt-4 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <p className="text-green-400 text-sm">
              ✓ Recording saved! Your voice clip has been recorded for this question.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function StudentsList() {
  const students = [
    { id: "1", name: "Alex M.", date: "2024-01-15", choices: ["Empathetic", "Direct"], feedback: "Great experience" },
    { id: "2", name: "Jordan K.", date: "2024-01-14", choices: ["Analytical", "Thoughtful"], feedback: "Very insightful" },
    { id: "3", name: "Casey L.", date: "2024-01-13", choices: ["Action-oriented", "Quick"], feedback: "Loved it" },
  ];
  
  return (
    <div>
      <h2 className="text-xl font-light mb-6">Students Who Lived Your Career</h2>
      
      <div className="space-y-4">
        {students.map((student) => (
          <div
            key={student.id}
            className="bg-white/5 border border-white/10 rounded-lg p-4 flex items-center justify-between"
          >
            <div>
              <p className="font-medium">{student.name}</p>
              <p className="text-gray-400 text-sm">{student.date}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Choices showed:</p>
              <p className="text-sm">{student.choices.join(", ")}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ConnectionRequests() {
  const requests = [
    { id: "1", student: "Alex M.", message: "I'd love to chat about your path to CMO!", status: "pending" },
    { id: "2", student: "Jordan K.", message: "Would you have 15 min for a call?", status: "pending" },
  ];
  
  return (
    <div>
      <h2 className="text-xl font-light mb-6">Connection Requests</h2>
      
      <div className="space-y-4">
        {requests.map((req) => (
          <div
            key={req.id}
            className="bg-white/5 border border-white/10 rounded-lg p-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium">{req.student}</p>
                <p className="text-gray-400 text-sm mt-1">{req.message}</p>
              </div>
              <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm">
                {req.status}
              </span>
            </div>
            <div className="flex gap-3 mt-4">
              <button className="px-4 py-2 bg-white text-black rounded-lg hover:bg-gray-200 transition-colors">
                Accept
              </button>
              <button className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                Decline
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StoriesList({ professionalId }: { professionalId: string }) {
  const [stories, setStories] = useState<Array<{id: string; created_at: string; status: string; story_title: string | null}>>([]);
  const [loading, setLoading] = useState(true);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  
  useEffect(() => {
    if (!professionalId) return;
    async function fetchStories() {
      try {
        const response = await fetch(`${apiUrl}/api/professional/journal/entries/${professionalId}`);
        const data = await response.json();
        setStories(data.entries || []);
      } catch (err) {
        console.error("Error fetching stories:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStories();
  }, [apiUrl, professionalId]);
  
  const processStory = async (journalId: string) => {
    try {
      await fetch(`${apiUrl}/api/professional/journal/process/${journalId}`, { method: "POST" });
      // Refresh the list
      const response = await fetch(`${apiUrl}/api/professional/journal/entries/${professionalId}`);
      const data = await response.json();
      setStories(data.entries || []);
    } catch (err) {
      console.error("Error processing story:", err);
    }
  };
  
  if (loading) {
    return <div className="text-gray-500">Loading stories...</div>;
  }
  
  return (
    <div>
      <h2 className="text-xl font-light mb-6">📖 Your Stories</h2>
      
      {stories.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No stories yet. Start a journal entry to create one!</p>
          <a
            href="/professional/voice-chat"
            className="inline-block px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl"
          >
            Start Journal Entry →
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {stories.map((story) => (
            <div
              key={story.id}
              className="bg-white/5 border border-white/10 rounded-lg p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">
                    {story.story_title || "Untitled Story"}
                  </p>
                  <p className="text-gray-500 text-sm">
                    {new Date(story.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm ${
                  story.status === "completed" 
                    ? "bg-green-500/20 text-green-400"
                    : story.status === "processing"
                    ? "bg-yellow-500/20 text-yellow-400"
                    : "bg-gray-500/20 text-gray-400"
                }`}>
                  {story.status}
                </span>
              </div>
              
              {story.status === "pending" && (
                <button
                  onClick={() => processStory(story.id)}
                  className="mt-3 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm"
                >
                  Generate Story →
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ProfessionalPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    }>
      <ProfessionalDashboardContent />
    </Suspense>
  );
}