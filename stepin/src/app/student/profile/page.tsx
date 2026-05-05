"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";

interface StrengthMap {
  [key: string]: number;
}

interface CareerRanking {
  career: string;
  score: number;
}

interface StudentProfile {
  strength_map: StrengthMap;
  career_rankings: CareerRanking[];
  total_worlds_explored: number;
  total_sessions: number;
}

export default function StudentProfilePage() {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load student profile from local storage or API
    async function loadProfile() {
      try {
        // For now, use stored data or fetch from API
        const storedProfile = localStorage.getItem('studentProfile');
        if (storedProfile) {
          setProfile(JSON.parse(storedProfile));
        } else {
          // Mock profile for demo
          setProfile({
            strength_map: {
              analytical: 0.6,
              empathetic: 0.8,
              leadership: 0.5,
              creative: 0.7,
              technical: 0.6,
              communication: 0.7,
            },
            career_rankings: [
              { career: "Medicine", score: 0.85 },
              { career: "Technology", score: 0.75 },
              { career: "Education", score: 0.65 },
            ],
            total_worlds_explored: 3,
            total_sessions: 5,
          });
        }
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  // Calculate strength bar color based on score
  const getStrengthColor = (score: number) => {
    if (score >= 0.8) return "bg-green-500";
    if (score >= 0.6) return "bg-blue-500";
    if (score >= 0.4) return "bg-yellow-500";
    return "bg-gray-500";
  };

  // Format strength name for display
  const formatStrengthName = (key: string) => {
    return key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " ");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="text-gray-500">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900 py-12 px-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link
            href="/"
            className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
          >
            ← Back to Home
          </Link>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-3xl font-light text-white mb-2"
        >
          Your Profile
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-gray-500 mb-8"
        >
          Explore your strength map and career interests
        </motion.p>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-2 gap-4 mb-8"
        >
          <div className="p-4 bg-dark-800/50 border border-dark-700 rounded-sm">
            <p className="text-2xl text-white font-medium">
              {profile?.total_worlds_explored || 0}
            </p>
            <p className="text-sm text-gray-500">Worlds Explored</p>
          </div>
          <div className="p-4 bg-dark-800/50 border border-dark-700 rounded-sm">
            <p className="text-2xl text-white font-medium">
              {profile?.total_sessions || 0}
            </p>
            <p className="text-sm text-gray-500">Sessions Completed</p>
          </div>
        </motion.div>

        {/* Strength Map */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <h2 className="text-xl text-white mb-4">Your Strength Map</h2>
          <div className="space-y-4">
            {profile?.strength_map && Object.entries(profile.strength_map).map(([key, value]) => (
              <div key={key}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-300">
                    {formatStrengthName(key)}
                  </span>
                  <span className="text-sm text-gray-500">
                    {Math.round(value * 100)}%
                  </span>
                </div>
                <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value * 100}%` }}
                    transition={{ duration: 0.5, delay: 0.5 }}
                    className={`h-full ${getStrengthColor(value)}`}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Career Rankings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h2 className="text-xl text-white mb-4">Career Interests</h2>
          <div className="space-y-3">
            {profile?.career_rankings?.map((ranking, idx) => (
              <Link
                key={ranking.career}
                href={`/careers?category=${ranking.career.toLowerCase()}`}
                className="block p-4 bg-dark-800/50 border border-dark-700 hover:border-dark-500 rounded-sm transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-medium text-gray-600">
                      {idx + 1}
                    </span>
                    <span className="text-white">{ranking.career}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-dark-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-500"
                        style={{ width: `${ranking.score * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-500">
                      {Math.round(ranking.score * 100)}%
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Explore More */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 text-center"
        >
          <Link
            href="/careers"
            className="inline-block px-6 py-3 text-sm font-medium text-dark-900 bg-gray-200 hover:bg-white transition-colors rounded-sm"
          >
            Explore More Worlds
          </Link>
        </motion.div>
      </div>
    </div>
  );
}