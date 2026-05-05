"use client";

import { Suspense, useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import html2canvas from "html2canvas";

// Types
interface CareerWorld {
  id: string;
  title: string;
  category: string;
  professional_name: string;
  years_experience: number;
}

interface CareerDNACard {
  energizedBy: string[];
  drainedBy: string[];
  choicesReveal: string[];
  recommendations: Array<{
    career_name: string;
    reason: string;
  }>;
}

// Mock seeded worlds
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

// Mock DNA card data (would come from Reflection Agent)
const MOCK_DNA_DATA: Record<string, CareerDNACard> = {
  "medicine-1": {
    energizedBy: [
      "Making split-second decisions that save lives",
      "The team camaraderie in high-pressure moments",
      "The tangible impact of helping families in crisis",
    ],
    drainedBy: [
      "The hierarchical nature of medical training",
      "Lack of sleep and personal time",
      "Emotional weight of patient outcomes",
    ],
    choicesReveal: [
      "You prioritize direct patient communication",
      "You value celebration of small wins",
      "You process internally before acting",
    ],
    recommendations: [
      {
        career_name: "Emergency Medicine",
        reason: "Your comfort with urgency and quick decisions fits well",
      },
      {
        career_name: "Pediatrics",
        reason: "Your care for families shows strong interpersonal skills",
      },
      {
        career_name: "Medical Research",
        reason: "Your analytical approach could thrive in research",
      },
    ],
  },
  "technology-1": {
    energizedBy: [
      "Building products that users actually need",
      "Solving complex technical problems",
      "Working with a tight-knit team",
    ],
    drainedBy: [
      "Constant firefighting culture",
      "Unpredictable work hours",
      "Pressure from investors and users",
    ],
    choicesReveal: [
      "You take ownership of problems",
      "You value transparent communication",
      "You balance speed with quality",
    ],
    recommendations: [
      {
        career_name: "Product Management",
        reason: "Your technical skills + communication style fits PM well",
      },
      {
        career_name: "DevOps Engineering",
        reason: "Your crisis management skills would excel here",
      },
      {
        career_name: "Technical Lead",
        reason: "Your team-first approach shows leadership potential",
      },
    ],
  },
};

function DNACardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const worldId = searchParams.get("world") || "medicine-1";
  
  const cardRef = useRef<HTMLDivElement>(null);
  const [world, setWorld] = useState<CareerWorld | null>(null);
  const [dnaCard, setDNACard] = useState<CareerDNACard | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    const storedDNAString = sessionStorage.getItem('careerDna');
    const careerName = sessionStorage.getItem('careerName');
    
    // First try session storage
    if (storedDNAString) {
      try {
        const storedDNA = JSON.parse(storedDNAString);
        setDNACard({
          energizedBy: storedDNA.energized_by || storedDNA.energizedBy || [],
          drainedBy: storedDNA.drained_by || storedDNA.drainedBy || [],
          choicesReveal: storedDNA.choices_reveal || storedDNA.choicesReveal || [],
          recommendations: storedDNA.recommendations || [],
        });
        setWorld({
          id: worldId,
          title: careerName || "Professional",
          category: "Career",
          professional_name: storedDNA.professional_name || "Unknown",
          years_experience: storedDNA.years_experience || 0,
        });
      } catch (e) {
        console.error("Failed to parse stored DNA:", e);
        setWorld(SEEDED_WORLDS[worldId] || SEEDED_WORLDS["medicine-1"]);
        setDNACard(MOCK_DNA_DATA[worldId] || MOCK_DNA_DATA["medicine-1"]);
      }
    } else {
      setWorld(SEEDED_WORLDS[worldId] || SEEDED_WORLDS["medicine-1"]);
      setDNACard(MOCK_DNA_DATA[worldId] || MOCK_DNA_DATA["medicine-1"]);
    }
    
    setLoading(false);
  }, [worldId]);

  // Export card as PNG
  const exportCard = async () => {
    if (!cardRef.current) return;
    
    setExporting(true);
    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: "#0a0a0a",
        scale: 2,
      });
      
      const link = document.createElement("a");
      link.download = "career-dna-card.png";
      link.href = canvas.toDataURL("image/png");
      link.click();
    } catch (err) {
      console.error("Failed to export card:", err);
    } finally {
      setExporting(false);
    }
  };

  // Share to X (Twitter)
  const shareToX = () => {
    const text = encodeURIComponent(
      `I just explored what it's like to be a ${world?.title}. Here's my Career DNA:`
    );
    const url = encodeURIComponent("https://stepin.app");
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank");
  };

  // Share to LinkedIn
  const shareToLinkedIn = () => {
    const url = encodeURIComponent("https://stepin.app");
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, "_blank");
  };

  if (loading || !world || !dnaCard) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading your DNA Card...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black flex flex-col items-center py-12 px-4">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-3xl font-light text-white mb-2">Your Career DNA</h1>
        <p className="text-gray-500">
          Based on your experience as a {world.title}
        </p>
      </motion.div>

      {/* DNA Card */}
      <motion.div
        ref={cardRef}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="w-full max-w-4xl bg-dark-900 border border-dark-800 rounded-sm overflow-hidden"
        style={{ width: "600px", minHeight: "315px" }}
      >
        <div className="h-full flex flex-col p-6">
          {/* Card Header */}
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-medium text-white">Career DNA</h2>
              <p className="text-sm text-gray-500">Your exploration of {world.title}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-600">STEPIN</p>
            </div>
          </div>

          {/* Card Content - Three Columns */}
          <div className="flex-1 grid grid-cols-3 gap-4">
            {/* What Energized You */}
            <div className="border-r border-dark-800 pr-4">
              <h3 className="text-xs font-medium text-green-400 uppercase tracking-wider mb-2">
                Energized By
              </h3>
              <ul className="space-y-1">
                {dnaCard.energizedBy.slice(0, 2).map((item, idx) => (
                  <li key={idx} className="text-xs text-gray-300">
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* What Drained You */}
            <div className="border-r border-dark-800 px-4">
              <h3 className="text-xs font-medium text-red-400 uppercase tracking-wider mb-2">
                Drained By
              </h3>
              <ul className="space-y-1">
                {dnaCard.drainedBy.slice(0, 2).map((item, idx) => (
                  <li key={idx} className="text-xs text-gray-300">
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* What Choices Reveal */}
            <div className="pl-4">
              <h3 className="text-xs font-medium text-blue-400 uppercase tracking-wider mb-2">
                Choices Reveal
              </h3>
              <ul className="space-y-1">
                {dnaCard.choicesReveal.slice(0, 2).map((item, idx) => (
                  <li key={idx} className="text-xs text-gray-300">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recommendations */}
          <div className="mt-4 pt-4 border-t border-dark-800">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
              Recommended Next Steps
            </h3>
            <div className="flex gap-4">
              {dnaCard.recommendations.slice(0, 2).map((rec, idx) => (
                <div key={idx} className="flex-1">
                  <p className="text-sm text-white font-medium">{rec.career_name}</p>
                  <p className="text-xs text-gray-500">{rec.reason}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="flex flex-col gap-4 mt-8"
      >
        <div className="flex gap-4">
          <button
            onClick={exportCard}
            disabled={exporting}
            className="px-6 py-3 text-sm font-medium text-black bg-white hover:bg-gray-200 transition-colors rounded-sm disabled:opacity-50"
          >
            {exporting ? "Exporting..." : "Download Card"}
          </button>
          <button
            onClick={shareToX}
            className="px-6 py-3 text-sm font-medium text-white border border-dark-700 hover:border-dark-500 transition-colors rounded-sm"
          >
            Share on X
          </button>
          <button
            onClick={shareToLinkedIn}
            className="px-6 py-3 text-sm font-medium text-white border border-dark-700 hover:border-dark-500 transition-colors rounded-sm"
          >
            Share on LinkedIn
          </button>
        </div>

        <div className="flex flex-col gap-2 mt-4">
          <button
            onClick={() => router.push("/careers")}
            className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
          >
            Explore Another World
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default function DNACardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading your DNA Card...</div>
      </div>
    }>
      <DNACardContent />
    </Suspense>
  );
}