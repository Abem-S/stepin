/* eslint-disable @typescript-eslint/no-unused-vars, react-hooks/exhaustive-deps */
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { motion } from "framer-motion";
import Link from "next/link";

interface LivedExperience {
  world_id: string;
  world_title: string;
  category: string;
  completed_at: string;
  choices_summary: string[];
}

interface DNAProfile {
  energized_by: string[];
  drained_by: string[];
  choices_reveal: string[];
}

interface Recommendation {
  id: string;
  career_name: string;
  category: string;
  reason: string;
}

export default function StudentDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<{ id: string; email: string; name: string } | null>(null);
  const [livedExperiences, setLivedExperiences] = useState<LivedExperience[]>([]);
  const [dna, setDna] = useState<DNAProfile | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  const supabase = createClient();

  useEffect(() => {
    async function load() {
      const { data: { user: authUser } } = await supabase.auth.getUser();
      if (!authUser) { router.push("/auth/login?role=student"); return; }

      const name = authUser.user_metadata?.name || authUser.email?.split("@")[0] || "Student";
      setUser({ id: authUser.id, email: authUser.email || "", name });

      // Load student DNA from backend API (bypasses broken FK constraint in student_strengths)
      try {
        const resp = await fetch(`${apiUrl}/api/student/dna/${authUser.id}`);
        if (resp.ok) {
          const data = await resp.json();
          if (data.found && data.dna) {
            setDna({
              energized_by: data.dna.energized_by || [],
              drained_by: data.dna.drained_by || [],
              choices_reveal: data.dna.choices_reveal || [],
            });

            // Get AI recommendations based on saved profile
            try {
              const recResp = await fetch(`${apiUrl}/api/agents/recommender`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  student_id: authUser.id,
                  profile_data: data.dna,
                }),
              });
              if (recResp.ok) {
                const recData = await recResp.json();
                setRecommendations(recData.recommendations || []);
              }
            } catch (e) { console.error("Recommendations failed", e); }
          }
        }
      } catch (e) { console.error("DNA fetch failed", e); }

      setLoading(false);
    }
    load();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading your dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/10 p-6">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-light">{user?.name}</h1>
            <p className="text-gray-500 text-sm">{user?.email}</p>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/careers" className="text-sm text-gray-400 hover:text-white transition-colors">
              Explore Careers →
            </Link>
            <button onClick={handleLogout} className="text-sm text-gray-500 hover:text-red-400 transition-colors">
              Log Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto p-6 space-y-10">

        {/* Career DNA Section */}
        {dna && (dna.energized_by.length > 0 || dna.drained_by.length > 0) ? (
          <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <h2 className="text-lg font-light text-white mb-4">🧬 Your Career DNA</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {dna.energized_by.length > 0 && (
                <div className="bg-green-900/20 border border-green-700/40 rounded-xl p-5">
                  <h3 className="text-xs text-green-400 uppercase tracking-wider mb-3">Energized By</h3>
                  <ul className="space-y-1">
                    {dna.energized_by.map((item, i) => (
                      <li key={i} className="text-sm text-gray-300">{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              {dna.drained_by.length > 0 && (
                <div className="bg-red-900/20 border border-red-700/40 rounded-xl p-5">
                  <h3 className="text-xs text-red-400 uppercase tracking-wider mb-3">Drained By</h3>
                  <ul className="space-y-1">
                    {dna.drained_by.map((item, i) => (
                      <li key={i} className="text-sm text-gray-300">{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              {dna.choices_reveal.length > 0 && (
                <div className="bg-blue-900/20 border border-blue-700/40 rounded-xl p-5">
                  <h3 className="text-xs text-blue-400 uppercase tracking-wider mb-3">Your Choices Reveal</h3>
                  <ul className="space-y-1">
                    {dna.choices_reveal.map((item, i) => (
                      <li key={i} className="text-sm text-gray-300">{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.section>
        ) : (
          <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className="bg-white/5 border border-white/10 rounded-xl p-8 text-center">
            <h2 className="text-lg font-light mb-2">No Career DNA yet</h2>
            <p className="text-gray-500 text-sm mb-4">
              Live a Shadow Day experience to discover what energizes and drains you.
            </p>
            <Link href="/careers"
              className="inline-block px-6 py-3 bg-white text-black rounded-lg font-medium hover:bg-gray-200 transition-colors">
              Explore Career Worlds →
            </Link>
          </motion.section>
        )}

        {/* AI Recommendations */}
        {recommendations.length > 0 && (
          <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <h2 className="text-lg font-light text-white mb-4">✨ Recommended for You</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.slice(0, 4).map((rec, i) => (
                <Link key={i} href={`/careers`}
                  className="block bg-white/5 border border-white/10 hover:border-white/30 rounded-xl p-5 transition-all">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-white">{rec.career_name}</h3>
                      <p className="text-xs text-gray-500 mt-0.5">{rec.category}</p>
                    </div>
                    <span className="text-xs text-purple-400 border border-purple-700/50 px-2 py-0.5 rounded-full">Match</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-3">{rec.reason}</p>
                </Link>
              ))}
            </div>
          </motion.section>
        )}

        {/* Explore More CTA */}
        <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          className="border border-white/10 rounded-xl p-6 text-center">
          <h2 className="text-lg font-light mb-2">Keep Exploring</h2>
          <p className="text-gray-500 text-sm mb-4">
            Every world you live updates your Career DNA and refines your recommendations.
          </p>
          <Link href="/careers"
            className="inline-block px-8 py-3 bg-white text-black rounded-lg font-medium hover:bg-gray-200 transition-colors">
            Browse All Career Worlds
          </Link>
        </motion.section>
      </main>
    </div>
  );
}
