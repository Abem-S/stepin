/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

// Types
interface CareerWorld {
  id: string;
  title: string;
  category: string;
  professional_name: string;
  years_experience: number;
}

// Mock seeded worlds - with years revealed only during Rewind!
const SEEDED_WORLDS: Record<string, CareerWorld> = {
  "medicine-1": {
    id: "medicine-1",
    title: "Surgical Resident",
    category: "medicine",
    professional_name: "Dr. Sarah Chen",
    years_experience: 7,
  },
  "technology-1": {
    id: "technology-1",
    title: "Startup Engineer",
    category: "technology",
    professional_name: "Marcus Rivera",
    years_experience: 5,
  },
};

interface AlternativeWorld {
  id: string;
  title: string;
  reason: string;
}

const ALTERNATIVE_WORLDS: Record<string, AlternativeWorld> = {
  "medicine-1": {
    id: "technology-1",
    title: "Startup Engineer",
    reason: "Based on your comfort with fast-paced problem solving",
  },
  "technology-1": {
    id: "medicine-1",
    title: "Surgical Resident",
    reason: "Based on your careful decision-making approach",
  },
};

function RewindContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const worldId = searchParams.get("world") || "medicine-1";
  
  const [phase, setPhase] = useState<"reveal" | "rewind" | "choice" | "alt">("reveal");
  const [world, setWorld] = useState<CareerWorld | null>(null);
  const [alternativeWorld, setAlternativeWorld] = useState<AlternativeWorld | null>(null);
  const [decisionPoints, setDecisionPoints] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load world data from sessionStorage (actual career name from shadow-day)
    const careerName = sessionStorage.getItem('careerName');
    const storedWorldId = sessionStorage.getItem('lastWorldId') || worldId;
    
    if (careerName) {
      setWorld({
        id: storedWorldId,
        title: careerName,
        category: "career",
        professional_name: "Professional",
        years_experience: 0,
      });
    } else {
      const currentWorld = SEEDED_WORLDS[worldId] || SEEDED_WORLDS["medicine-1"];
      setWorld(currentWorld);
    }
    setAlternativeWorld(null); // Disable alternative for now

    // Use real decisions from session storage or fallback
    try {
      const savedChoices = sessionStorage.getItem('recentChoices');
      if (savedChoices) {
        setDecisionPoints(JSON.parse(savedChoices));
      } else {
        setDecisionPoints([
          "You chose to take action",
          "You decided to reflect",
        ]);
      }
    } catch (_e) {
      setDecisionPoints(["You made your choices"]);
    }

    setLoading(false);

    // Phase transitions
    // After reveal, go to rewind
    const rewindTimer = setTimeout(() => {
      setPhase("rewind");
    }, 3000);

    // After rewind, go to choice
    const choiceTimer = setTimeout(() => {
      setPhase("choice");
    }, 6000);

    return () => {
      clearTimeout(rewindTimer);
      clearTimeout(choiceTimer);
    };
  }, [worldId]);

  // Handle "Yes" choice
  const handleYes = () => {
    router.push("/shadow-day/dna-card?world=" + worldId + "&choice=yes");
  };

  // Handle "Not For Me" choice
  const handleNotForMe = () => {
    if (alternativeWorld) {
      setPhase("alt");
    } else {
      router.push("/careers");
    }
  };

  // Go to alternative world
  const goToAlternativeWorld = () => {
    if (alternativeWorld) {
      router.push(`/shadow-day/the-drop?world=${alternativeWorld.id}`);
    }
  };

  // Go back to careers
  const goToCareers = () => {
    router.push("/careers");
  };

  if (loading || !world) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-6">
      <AnimatePresence mode="wait">
        {/* Phase 1: Reveal years */}
        {phase === "reveal" && (
          <motion.div
            key="reveal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center"
          >
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 1 }}
              className="text-3xl md:text-5xl font-light text-white"
            >
              You just lived
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.5, duration: 1 }}
              className="text-4xl md:text-6xl font-bold text-white mt-4"
            >
              a day in the life
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 2.5, duration: 1 }}
              className="text-3xl md:text-5xl font-light text-white mt-4"
            >
              of a {world.title}.
            </motion.p>
          </motion.div>
        )}

        {/* Phase 2: Rewind - fast forward through decisions */}
        {phase === "rewind" && (
          <motion.div
            key="rewind"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center max-w-lg"
          >
            <div className="text-gray-500 text-sm mb-8">Rewinding...</div>
            <div className="space-y-4">
              {decisionPoints.map((point, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 0.6, x: 0 }}
                  transition={{ delay: idx * 0.5, duration: 0.3 }}
                  className="text-gray-400 text-lg"
                >
                  {point}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Phase 3: Choice */}
        {phase === "choice" && (
          <motion.div
            key="choice"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="text-center max-w-lg"
          >
            <h2 className="text-2xl md:text-3xl font-light text-white mb-8">
              Knowing everything you just felt —<br />would you choose this path?
            </h2>
            
            <div className="flex flex-col gap-4">
              <button
                onClick={handleYes}
                className="px-8 py-4 text-lg font-medium text-black bg-white hover:bg-gray-200 transition-colors rounded-sm"
              >
                Yes
              </button>
              <button
                onClick={handleNotForMe}
                className="px-8 py-4 text-lg font-medium text-white border border-gray-700 hover:border-gray-500 transition-colors rounded-sm"
              >
                Not For Me
              </button>
            </div>
          </motion.div>
        )}

        {/* Phase 4: Alternative world suggestion */}
        {phase === "alt" && alternativeWorld && (
          <motion.div
            key="alt"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="text-center max-w-lg"
          >
            <p className="text-xl text-gray-300 mb-4">
              That world wasn&apos;t yours — but your reactions tell us something.
            </p>
            <p className="text-lg text-gray-400 mb-8">
              Here&apos;s a world that might fit better.
            </p>
            
            <div className="p-6 bg-dark-800/50 border border-dark-700 rounded-sm mb-8">
              <h3 className="text-xl font-medium text-white mb-2">
                {alternativeWorld.title}
              </h3>
              <p className="text-sm text-gray-400">
                {alternativeWorld.reason}
              </p>
            </div>
            
            <div className="flex flex-col gap-4">
              <button
                onClick={goToAlternativeWorld}
                className="px-8 py-4 text-lg font-medium text-black bg-white hover:bg-gray-200 transition-colors rounded-sm"
              >
                Enter This World
              </button>
              <button
                onClick={goToCareers}
                className="px-8 py-4 text-lg font-medium text-gray-400 hover:text-white transition-colors"
              >
                Choose Something Else
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function RewindPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    }>
      <RewindContent />
    </Suspense>
  );
}