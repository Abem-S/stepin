"use client";

import { Suspense, useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Howl } from "howler";

// Types for career world data
interface Moment {
  id: string;
  text_lines: string[];
  image_url: string | null;
  image_data?: string | null; // Base64 from AI generation (optional, filled at runtime)
  audio_url: string | null;
  choices: string[];
  is_emotional_peak: boolean;
  voice_clip_url: string | null;
  pull_quote: string | null;
}

interface CareerWorld {
  id: string;
  title: string;
  category: string;
  professional_name: string;
  years_experience: number; // Protected - only revealed during Rewind!
  moments: Moment[];
}

// Mock seeded data for demo
const SEEDED_WORLDS: Record<string, CareerWorld> = {
  "medicine-1": {
    id: "medicine-1",
    title: "Surgical Resident's Tuesday",
    category: "medicine",
    professional_name: "Dr. Sarah Chen",
    years_experience: 7, // Protected during The Drop and Shadow Day!
    moments: [
      {
        id: "m1",
        text_lines: [
          "Your pager goes off at 6:47 AM.",
          "Code Blue in the ER. Trauma alert.",
        ],
        image_url: "/images/hospital-emergency.jpg",
        audio_url: "/audio/hospital-morning.mp3",
        choices: [
          "Run toward the ER immediately",
          "Grab your coffee first – you'll need the energy",
          "Call the attending on call first",
        ],
        is_emotional_peak: false,
        voice_clip_url: null,
        pull_quote: null,
      },
      {
        id: "m2",
        text_lines: [
          "The patient is a 34-year-old father of two.",
          "Car accident. Internal bleeding.",
          "His wife is in the waiting room.",
        ],
        image_url: "/images/family-conversation.jpg",
        audio_url: "/audio/hospital-ambient.mp3",
        choices: [
          "Go to the family yourself – they need a doctor who cares",
          "Focus on saving the patient – the team needs you in the OR",
          "Have the nurse inform the family while you operate",
        ],
        is_emotional_peak: true,
        voice_clip_url: null,
        pull_quote: "The hardest part isn't the surgery. It's looking a father in the eye and not knowing if he'll see his kids grow up.",
      },
      {
        id: "m3",
        text_lines: [
          "You find the source of bleeding. A torn artery.",
          "Your hands are steady. Years of training kick in.",
          "Clamp. Suture. The bleeding stops.",
        ],
        image_url: "/images/surgery-success.jpg",
        audio_url: "/audio/surgery-room.mp3",
        choices: [
          "Let out a breath – you saved him",
          "Stay focused – there could be more damage",
          "Momentarily celebrate – this win matters",
        ],
        is_emotional_peak: true,
        voice_clip_url: null,
        pull_quote: "That feeling when the heart rate stabilizes – there's nothing like it. It's why we do this.",
      },
      {
        id: "m4",
        text_lines: [
          "Post-op, the attending reviews your work.",
          "'Good, but you lost too much blood. Next time, faster.'",
          "No praise. Just critique.",
        ],
        image_url: "/images/attending-critique.jpg",
        audio_url: "/audio/hospital-ambient.mp3",
        choices: [
          "Defend your decisions – you saved the patient",
          "Stay silent and learn – that's how the game works",
          "Ask clarifying questions – turn it into a teaching moment",
        ],
        is_emotional_peak: false,
        voice_clip_url: null,
        pull_quote: null,
      },
      {
        id: "m5",
        text_lines: [
          "14 hours later. The shift is over.",
          "You check on your patient. Stable.",
          "You sit in the doctor’s lounge, alone.",
        ],
        image_url: "/images/end-of-shift.jpg",
        audio_url: "/audio/hospital-quiet.mp3",
        choices: [
          "Call your family – they've been waiting",
          "Chart everything meticulously – details matter",
          "Sit in silence – process the day",
        ],
        is_emotional_peak: true,
        voice_clip_url: null,
        pull_quote: "At 2 AM, when the hospital is quiet, that's when it hits you. Every life you touch changes you. Forever.",
      },
    ],
  },
  "technology-1": {
    id: "technology-1",
    title: "Startup Engineer's Launch Day",
    category: "technology",
    professional_name: "Marcus Rivera",
    years_experience: 5, // Protected during The Drop and Shadow Day!
    moments: [
      {
        id: "m1",
        text_lines: [
          "It's 7 AM. You roll into the office.",
          "Slack is already exploding. PagerDuty too.",
          "Critical bug found. 2 hours before launch.",
        ],
        image_url: "/images/startup-morning.jpg",
        audio_url: "/audio/office-morning.mp3",
        choices: [
          "Start debugging immediately – no time for coffee",
          "Call an emergency standup – this affects everyone",
          "Assess the severity first – maybe it's fixable",
        ],
        is_emotional_peak: false,
        voice_clip_url: null,
        pull_quote: null,
      },
      {
        id: "m2",
        text_lines: [
          "The bug is in the payment system.",
          "User data might be exposed. GDPR violation.",
          "Your teammate who wrote the code is on vacation.",
        ],
        image_url: "/images/team-conflict.jpg",
        audio_url: "/audio/office-busy.mp3",
        choices: [
          "Fix it yourself – take ownership",
          "Roll back the release – ship without this feature",
          "Call the CEO – this is a company-level decision",
        ],
        is_emotional_peak: true,
        voice_clip_url: null,
        pull_quote: "The hardest code you'll ever write is the kind that runs at 2 AM when everything is on fire.",
      },
      {
        id: "m3",
        text_lines: [
          "It's decision time: ship broken or delay launch?",
          "Investors are watching. Customer expectations are set.",
          "Your team is exhausted but capable.",
        ],
        image_url: "/images/ship-vs-delay.jpg",
        audio_url: "/audio/office-tension.mp3",
        choices: [
          "Ship it – iterate fast, fix in production",
          "Delay – quality over speed, always",
          "Partial launch – ship stable features only",
        ],
        is_emotional_peak: true,
        voice_clip_url: null,
        pull_quote: "Every engineer knows this moment. The choice between done and right.",
      },
      {
        id: "m4",
        text_lines: [
          "You shipped. Then the reports started coming in.",
          "Users can't log in. Password reset is broken.",
          "Social media is trending with complaints.",
        ],
        image_url: "/images/crisis-mode.jpg",
        audio_url: "/audio/office-alarm.mp3",
        choices: [
          "Work through the night – fix it before morning",
          "Communicate transparently – issue a public status",
          "Rally the team – distributed fixes are faster",
        ],
        is_emotional_peak: false,
        voice_clip_url: null,
        pull_quote: null,
      },
      {
        id: "m5",
        text_lines: [
          "4 AM. The crisis is over. Sort of.",
          "You and the team sit in the conference room.",
          "Pizza boxes. Empty energy drink cans. Honest conversation.",
        ],
        image_url: "/images/retrospective.jpg",
        audio_url: "/audio/office-quiet.mp3",
        choices: [
          "Schedule a proper retro – learn from this",
          "Go home – sleep is non-negotiable",
          "Write the post-mortem now – details are fresh",
        ],
        is_emotional_peak: true,
        voice_clip_url: null,
        pull_quote: "Startup life isn't for everyone. But those of us who love it – we love the chaos. We love the team. We love building something that matters.",
      },
    ],
  },
};

// Session state
interface SessionState {
  worldId: string;
  currentMomentIndex: number;
  choices: Array<{ momentIndex: number; choice: string; freeText?: string; hesitationMs: number }>;
  startTime: number;
}

function ShadowDayContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const worldId = searchParams.get("world");
  
  const [world, setWorld] = useState<CareerWorld | null>(null);
  const [session, setSession] = useState<SessionState | null>(null);
  const [currentMoment, setCurrentMoment] = useState<Moment | null>(null);
  const [displayedLines, setDisplayedLines] = useState<string[]>([]);
  const [showChoices, setShowChoices] = useState(false);
  const [selectedChoice, setSelectedChoice] = useState<number | null>(null);
  const [freeText, setFreeText] = useState("");
  const [hesitationStartTime, setHesitationStartTime] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [studentProfile, setStudentProfile] = useState<{energized_by: string[]; drained_by: string[]; choices_reveal?: string[]} | null>(null);
  const [studentId, setStudentId] = useState<string>("anonymous-" + Math.random().toString(36).slice(2));
  const audioRef = useRef<Howl | null>(null);
  const voiceClipRef = useRef<Howl | null>(null);

  // Load auth user ID on mount
  useEffect(() => {
    import("@/lib/supabase").then(({ createClient }) => {
      createClient().auth.getUser().then(({ data: { user } }) => {
        if (user) setStudentId(user.id);
      });
    });
  }, []);

  // Load career world on mount - with AI pre-generated images
  const loadedRef = useRef(false);
  
  useEffect(() => {
    if (loadedRef.current) return;
    loadedRef.current = true;
    
    async function loadWorld() {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      
      const worldIdKey = worldId || "medicine-1";
      let selectedWorld: CareerWorld;
      
      if (SEEDED_WORLDS[worldIdKey]) {
        selectedWorld = JSON.parse(JSON.stringify(SEEDED_WORLDS[worldIdKey]));
      } else {
        try {
          const response = await fetch(`${apiUrl}/api/careers/world/${worldId}`);
          if (!response.ok) throw new Error("World not found");
          const data = await response.json();
          
          selectedWorld = {
            id: data.id,
            title: data.title,
            category: data.category,
            professional_name: data.professional_name,
            years_experience: data.years_experience || 0,
            moments: data.experience_data?.moments || [
              {
                id: "m1",
                text_lines: data.experience_data?.story ? [data.experience_data.story] : ["Welcome to my journey."],
                image_url: null,
                audio_url: null,
                choices: ["Reflect on this", "Continue the journey"],
                is_emotional_peak: true,
                voice_clip_url: null,
                pull_quote: data.title,
              }
            ]
          };
        } catch (err) {
          console.error(err);
          selectedWorld = JSON.parse(JSON.stringify(SEEDED_WORLDS["medicine-1"]));
        }
      }
      
      // Removed AI image generation entirely as requested
      console.log('Using world data without image generation');
      
      // Immediately set world and session (no waiting for images)
      setWorld(selectedWorld);
      await new Promise(resolve => setTimeout(resolve, 50));
      
      setSession({
        worldId: selectedWorld.id,
        currentMomentIndex: 0,
        choices: [],
        startTime: Date.now(),
      });
      setLoading(false);
    }
    loadWorld();
  }, [worldId]);

  // Display text lines with animation
  useEffect(() => {
    if (!currentMoment || !world) return;

    let lineIndex = 0;
    const lines = currentMoment.text_lines;

    const displayNextLine = () => {
      if (lineIndex < lines.length) {
        setDisplayedLines((prev) => [...prev, lines[lineIndex]]);
        lineIndex++;
        setTimeout(displayNextLine, 800);
      } else {
        // All lines displayed, show choices
        setTimeout(() => {
          setShowChoices(true);
          setHesitationStartTime(Date.now());
        }, 500);
      }
    };

    // Start displaying lines
    const initialDelay = setTimeout(() => {
      displayNextLine();
    }, 500);

    return () => clearTimeout(initialDelay);
  }, [currentMoment, world]);

  // Set current moment when session changes
  useEffect(() => {
    if (!session || !world) return;
    const newMoment = world.moments[session.currentMomentIndex];
    setCurrentMoment(newMoment);
    setDisplayedLines([]);
    setShowChoices(false);
    setSelectedChoice(null);
    setFreeText("");
  }, [session, world]);
  
  // Update current moment when world is updated with new images
  useEffect(() => {
    if (!session || !world || !currentMoment) return;
    const updatedMoment = world.moments[session.currentMomentIndex];
    // Only update if the moment has an image now that it didn't have before
    if (updatedMoment.image_data && !currentMoment.image_data) {
      console.log('Updating current moment with new image');
      setCurrentMoment(updatedMoment);
    }
  }, [world, session, currentMoment]);

  // TASK 22: Ambient audio playback - disabled (no audio files available)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const playAmbientAudio = useCallback((_audioUrl: string | null) => {
    // Audio playback disabled - no audio files available
  }, []);

  // TASK 23: Voice clip playback for emotional peaks
  const playVoiceClip = useCallback((voiceClipUrl: string | null) => {
    // Stop ambient audio when playing voice clip
    if (audioRef.current) {
      audioRef.current.fade(0.3, 0, 1000);
      setTimeout(() => audioRef.current?.stop(), 1000);
    }
    
    if (!voiceClipUrl) return;
    
    const voiceSound = new Howl({
      src: [voiceClipUrl],
      volume: 1.0,
      html5: true,
      onend: () => {
        // Resume ambient audio after voice clip ends
        if (audioRef.current) {
          audioRef.current.play();
          audioRef.current.fade(0, 0.3, 1000);
        }
      },
    });
    
    voiceClipRef.current = voiceSound;
    voiceSound.play();
  }, []);

  // Effect: Handle audio and image when moment changes
  useEffect(() => {
    if (!currentMoment || !world || !session) return;
    
    // Play ambient audio for this moment (Task 22)
    playAmbientAudio(currentMoment.audio_url);
    
    // Skip AI image generation - using seeded images for instant loading
    
    // Handle voice clip for emotional peaks (Task 23)
    if (currentMoment.is_emotional_peak && currentMoment.voice_clip_url) {
      playVoiceClip(currentMoment.voice_clip_url);
    } else if (currentMoment.is_emotional_peak && currentMoment.pull_quote && !currentMoment.voice_clip_url) {
      // Fallback: Pull quote is displayed cinematically (handled in JSX)
    }
    
    // Cleanup on unmount
    return () => {
      if (audioRef.current) {
        audioRef.current.stop();
      }
      if (voiceClipRef.current) {
        voiceClipRef.current.stop();
      }
    };
  }, [currentMoment, world, session, playAmbientAudio, playVoiceClip]);

  // Handle choice selection - with Profile Agent tracking
  const handleChoice = async (choiceIndex: number, text: string) => {
    if (!session || hesitationStartTime === 0) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    const hesitationMs = Date.now() - hesitationStartTime;
    
    const newChoice = {
      momentIndex: session.currentMomentIndex,
      choice: text,
      freeText: undefined,
      hesitationMs,
    };

    setSelectedChoice(choiceIndex);

    // Call Profile Agent to track this choice (AI-powered) - fire and forget, don't wait
    const allChoices = [...session.choices, newChoice];
    const freeTexts = allChoices.filter(c => c.freeText).map(c => c.freeText);
    const hesitations = allChoices.map(c => c.hesitationMs);
    
    // Fire and forget - don't await the response
    fetch(`${apiUrl}/api/agents/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        session_id: studentId,
        choices: allChoices,
        free_text_responses: freeTexts,
        hesitations_ms: hesitations,
      }),
    }).then(response => response.json()).then(profileData => {
      setStudentProfile(profileData);
    }).catch(() => {
      // Silent fail - don't interrupt the experience
    });

    // Move to next moment immediately (no waiting for AI)
    setTimeout(() => {
      const nextIndex = session.currentMomentIndex + 1;
      
      if (nextIndex >= world!.moments.length) {
        // Completed all moments - call Reflection Agent for Career DNA
        generateCareerDna(studentId, allChoices, world!.title);
      } else {
        // Go to next moment
        setSession({
          ...session,
          currentMomentIndex: nextIndex,
          choices: allChoices,
        });
      }
    }, 500);
  };

  // Generate Career DNA using Reflection Agent - non-blocking
  const generateCareerDna = async (studentId: string, choices: Array<{ momentIndex: number; choice: string; freeText?: string; hesitationMs: number }>, careerName: string) => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    
    // Store basic data immediately
    sessionStorage.setItem('careerName', careerName);
    
    // Prepare the profile data
    const profileData = {
      ...(studentProfile || {}),
      career_name: careerName,
      energized_by: studentProfile?.energized_by || choices.map(() => "decision making"),
      drained_by: studentProfile?.drained_by || choices.map(() => "challenges"),
    };
    
    // Fire and forget the AI call - store result when it comes
    fetch(`${apiUrl}/api/agents/reflection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        session_id: studentId,
        profile_data: profileData,
      }),
    }).then(response => response.json())
    .then(dnaData => {
      // Save to sessionStorage for display
      sessionStorage.setItem('careerDna', JSON.stringify(dnaData));
      
      // CRITICAL: Also save to backend for permanent storage
      fetch(`${apiUrl}/api/student/dna/${studentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          energized_by: dnaData.energized_by || profileData.energized_by,
          drained_by: dnaData.drained_by || profileData.drained_by,
          choices_reveal: dnaData.choices_reveal || [],
        }),
      }).catch(err => console.error("Failed to save DNA to backend:", err));
    })
    .catch(() => {});
    
    const choiceTexts = choices.map(c => `You chose: ${c.freeText || c.choice}`);
    sessionStorage.setItem('recentChoices', JSON.stringify(choiceTexts));
    
    // Navigate to Rewind immediately - no waiting
    router.push(`/shadow-day/rewind?world=${session?.worldId}`);
  };

  // Handle free text submission
  const handleFreeTextSubmit = async () => {
    if (!session || !freeText.trim() || hesitationStartTime === 0) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    const hesitationMs = Date.now() - hesitationStartTime;
    
    const newChoice = {
      momentIndex: session.currentMomentIndex,
      choice: "Free text response",
      freeText: freeText.trim(),
      hesitationMs,
    };

    // Call Profile Agent for free text - fire and forget
    const allChoices = [...session.choices, newChoice];
    const freeTexts = allChoices.filter(c => c.freeText).map(c => c.freeText);
    const hesitations = allChoices.map(c => c.hesitationMs);
    
    fetch(`${apiUrl}/api/agents/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        session_id: studentId,
        choices: allChoices,
        free_text_responses: freeTexts,
        hesitations_ms: hesitations,
      }),
    }).catch(() => {});

    setTimeout(() => {
      const nextIndex = session.currentMomentIndex + 1;
      
      if (nextIndex >= world!.moments.length) {
        generateCareerDna(studentId, allChoices, world!.title);
      } else {
        setSession({
          ...session,
          currentMomentIndex: nextIndex,
          choices: allChoices,
        });
      }
    }, 500);
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading experience...</div>
      </div>
    );
  }

  // Error state
  if (!world || !currentMoment) {
    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center">
        <p className="text-red-400 mb-4">Something went wrong</p>
        <button
          onClick={() => router.push("/careers")}
          className="text-gray-400 hover:text-white transition-colors"
        >
          Return to Career Selection
        </button>
      </div>
    );
  }

  // Determine background image - prefer AI-generated, fall back to gradient
  const backgroundImageSrc = currentMoment.image_data || null;
  console.log('Current moment:', currentMoment.id, 'has image_data:', !!currentMoment.image_data);
  
  // Create atmospheric gradient fallback based on moment
  const momentIndex = world.moments.findIndex(m => m.id === currentMoment.id);
  const gradientColors = [
    ['#1a1a2e', '#16213e', '#0f3460'],  // m1: Dark blue
    ['#2d132c', '#801336', '#c72c41'],  // m2: Deep red
    ['#0d1b2a', '#1b263b', '#415a77'],  // m3: Steel blue
    ['#1b1b1b', '#2d2d2d', '#404040'],  // m4: Dark gray
    ['#0a0a0a', '#1a1a1a', '#2d2d2d'],  // m5: Near black
  ];
  const colors = gradientColors[momentIndex] || gradientColors[0];
  const gradientStyle = `linear-gradient(135deg, ${colors[0]} 0%, ${colors[1]} 50%, ${colors[2]} 100%)`;
  
  const backgroundStyle = backgroundImageSrc
    ? { backgroundImage: `url(${backgroundImageSrc})`, backgroundSize: 'cover', backgroundPosition: 'center' }
    : { background: gradientStyle };

  return (
    <div 
      className="min-h-screen flex flex-col relative"
      style={backgroundStyle}
    >
      {/* Dark overlay for readability */}
      <div className="absolute inset-0 bg-black/60 z-0" />

      {/* Content */}
      <div className="relative z-10 flex-1 flex flex-col">
        {/* Progress indicator */}
        <div className="p-4 flex items-center justify-between border-b border-white/10">
          <div className="text-sm text-gray-400">
            {world.title}
          </div>
          <div className="flex gap-1">
            {world.moments.map((_, idx) => (
              <div
                key={idx}
                className={`w-2 h-2 rounded-full transition-colors ${
                  session && idx < session.currentMomentIndex
                    ? 'bg-gray-400'
                    : session && idx === session.currentMomentIndex
                    ? 'bg-white'
                    : 'bg-gray-700'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Main content area */}
        <div className="flex-1 flex flex-col justify-center px-6 py-12 max-w-2xl mx-auto w-full">
          {/* Text lines */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentMoment.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6 mb-12"
            >
              {displayedLines.map((line, idx) => (
                <motion.p
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="text-xl md:text-2xl font-light text-white leading-relaxed"
                >
                  {line}
                </motion.p>
              ))}
            </motion.div>
          </AnimatePresence>

          {/* Pull quote (if emotional peak) */}
          <AnimatePresence>
            {currentMoment.is_emotional_peak && currentMoment.pull_quote && displayedLines.length === currentMoment.text_lines.length && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5, duration: 1 }}
                className="mb-12"
              >
                <blockquote className="border-l-2 border-white/30 pl-6 py-2">
                  <p className="text-lg text-gray-300 italic">
                    &ldquo;{currentMoment.pull_quote}&rdquo;
                  </p>
                  <cite className="text-sm text-gray-500 mt-2 block">
                    — {world.professional_name}
                  </cite>
                </blockquote>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Choices */}
          <AnimatePresence>
            {showChoices && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                {currentMoment.choices.map((choice, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChoice(idx, choice)}
                    disabled={selectedChoice !== null}
                    className={`w-full p-4 text-left border rounded-sm transition-all duration-200 ${
                      selectedChoice === idx
                        ? 'border-white bg-white/10'
                        : 'border-gray-700 hover:border-gray-500 bg-black/40 hover:bg-black/60'
                    } text-gray-200`}
                  >
                    {choice}
                  </button>
                ))}

                {/* Free text option */}
                <div className="mt-6 pt-6 border-t border-gray-800">
                  <textarea
                    value={freeText}
                    onChange={(e) => setFreeText(e.target.value)}
                    placeholder="Or write your own response..."
                    className="w-full p-4 bg-black/40 border border-gray-700 rounded-sm text-gray-200 placeholder-gray-600 focus:border-gray-500 focus:outline-none resize-none"
                    rows={3}
                  />
                  {freeText.trim() && (
                    <button
                      onClick={handleFreeTextSubmit}
                      disabled={selectedChoice !== null}
                      className="mt-3 px-6 py-2 bg-white text-black font-medium rounded-sm hover:bg-gray-200 transition-colors"
                    >
                      Submit
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="p-4 text-center text-xs text-gray-600 border-t border-white/5">
          Forward only – no going back
        </div>
      </div>
    </div>
  );
}

export default function ShadowDayPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading experience...</div>
      </div>
    }>
      <ShadowDayContent />
    </Suspense>
  );
}