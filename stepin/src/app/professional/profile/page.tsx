"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";

interface Professional {
  id: string;
  name: string;
  profession: string;
  career_category: string;
  years_experience: number;
  about: string;
  linkedin_url?: string;
  twitter_url?: string;
  website_url?: string;
}

interface DiaryEntry {
  id: string;
  entry_date: string;
  title: string;
  summary: string;
  content: {
    key_moments?: Array<{ time: string; event: string }>;
    emotional_beats?: string[];
    lessons?: string[];
  };
  story_experience_id?: string;
}

export default function ProfessionalProfilePage() {
  const [professional, setProfessional] = useState<Professional | null>(null);
  const [diaryEntries, setDiaryEntries] = useState<DiaryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEntry, setSelectedEntry] = useState<DiaryEntry | null>(null);

  useEffect(() => {
    async function loadProfile() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
        
        // Fetch professional data
        const profResponse = await fetch(`${apiUrl}/api/professionals/11111111-1111-1111-1111-111111111111`);
        if (profResponse.ok) {
          const profData = await profResponse.json();
          setProfessional(profData);
        } else {
          // Fallback to demo data
          setProfessional({
            id: "11111111-1111-1111-1111-111111111111",
            name: "Dr. Sarah Chen",
            profession: "Surgical Resident",
            career_category: "Medicine",
            years_experience: 4,
            about: "Surgical resident passionate about trauma surgery and mentoring the next generation of surgeons.",
          });
        }
        
        // Fetch diary entries
        const entriesResponse = await fetch(`${apiUrl}/api/professionals/11111111-1111-1111-1111-111111111111/diary-entries`);
        if (entriesResponse.ok) {
          const entriesData = await entriesResponse.json();
          setDiaryEntries(entriesData.entries || []);
        } else {
          // Fallback demo entries
          setDiaryEntries([
            {
              id: "22222222-2222-2222-2222-222222222222",
              entry_date: "2024-01-15",
              title: "Emergency Tuesday",
              summary: "A challenging Tuesday with a trauma case that tested my skills and my heart.",
              content: {
                key_moments: [
                  { time: "6:47 AM", event: "Trauma alert called - 67-year-old male, car accident" },
                  { time: "7:15 AM", event: "Difficult conversation with patient's daughter" },
                  { time: "10:30 AM", event: "Surgery complete - patient stabilized unexpectedly" },
                ],
                emotional_beats: ["fear", "empathy", "unexpected_joy"],
                lessons: ["Medicine is about showing up when it matters most"],
              },
            },
            {
              id: "33333333-3333-3333-3333-333333333333",
              entry_date: "2024-01-18",
              title: "Thursday Challenges",
              summary: "A tough day with an attending conflict, but a small win that reminded me why I do this.",
              content: {
                key_moments: [
                  { time: "2:00 PM", event: "Conflict with attending over surgical approach" },
                  { time: "6:00 PM", event: "Exhaustion after 12-hour shift" },
                  { time: "8:00 PM", event: "Small victory - resident who I mentored nailed a procedure" },
                ],
                emotional_beats: ["frustration", "exhaustion", "pride"],
                lessons: ["The hazing in medicine is real, but so is what you learn from it"],
              },
            },
          ]);
        }
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
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
        {/* Back link */}
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

        {/* Profile Header */}
        {professional && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-12"
          >
            <h1 className="text-3xl font-light text-white mb-2">
              {professional.name}
            </h1>
            <p className="text-xl text-gray-400 mb-4">
              {professional.profession} • {professional.years_experience} years
            </p>
            <p className="text-gray-500 max-w-2xl">
              {professional.about}
            </p>
            
            {/* Social Links */}
            <div className="flex gap-4 mt-6">
              {professional.linkedin_url && (
                <a
                  href={professional.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-500 hover:text-white transition-colors"
                >
                  LinkedIn
                </a>
              )}
              {professional.twitter_url && (
                <a
                  href={professional.twitter_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-500 hover:text-white transition-colors"
                >
                  Twitter
                </a>
              )}
              {professional.website_url && (
                <a
                  href={professional.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-500 hover:text-white transition-colors"
                >
                  Website
                </a>
              )}
            </div>
          </motion.div>
        )}

        {/* Voice Diary Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12"
        >
          <Link
            href="/professional/voice-chat"
            className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-sm transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            Start Voice Diary
          </Link>
        </motion.div>

        {/* Diary Entries Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-xl text-white mb-6">Voice Diary Entries</h2>
          
          {diaryEntries.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              No diary entries yet. Start a voice diary to create your first entry.
            </div>
          ) : (
            <div className="space-y-4">
              {diaryEntries.map((entry, idx) => (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * idx }}
                  className="p-6 bg-dark-800/50 border border-dark-700 rounded-sm cursor-pointer hover:border-dark-500 transition-all"
                  onClick={() => setSelectedEntry(selectedEntry?.id === entry.id ? null : entry)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">
                        {formatDate(entry.entry_date)}
                      </p>
                      <h3 className="text-lg text-white font-medium">{entry.title}</h3>
                      <p className="text-gray-400 mt-2">{entry.summary}</p>
                    </div>
                    {entry.story_experience_id && (
                      <span className="px-3 py-1 text-xs bg-purple-500/20 text-purple-400 rounded-full">
                        Story Generated
                      </span>
                    )}
                  </div>

                  {/* Expanded Content */}
                  {selectedEntry?.id === entry.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="mt-4 pt-4 border-t border-dark-700"
                    >
                      {/* Key Moments */}
                      {entry.content.key_moments && (
                        <div className="mb-4">
                          <h4 className="text-sm text-gray-500 mb-2">Key Moments</h4>
                          <div className="space-y-2">
                            {entry.content.key_moments.map((moment, i) => (
                              <div key={i} className="flex gap-3 text-sm">
                                <span className="text-gray-600">{moment.time}</span>
                                <span className="text-gray-300">{moment.event}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Emotional Beats */}
                      {entry.content.emotional_beats && (
                        <div className="mb-4">
                          <h4 className="text-sm text-gray-500 mb-2">Emotional Journey</h4>
                          <div className="flex gap-2 flex-wrap">
                            {entry.content.emotional_beats.map((emotion, i) => (
                              <span
                                key={i}
                                className="px-2 py-1 text-xs bg-dark-700 text-gray-300 rounded"
                              >
                                {emotion}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* View Story Link */}
                      {entry.story_experience_id && (
                        <Link
                          href={`/shadow-day/the-drop?world=${entry.story_experience_id}`}
                          className="inline-block mt-4 px-4 py-2 text-sm text-dark-900 bg-gray-200 hover:bg-white rounded-sm transition-colors"
                        >
                          View Generated Story →
                        </Link>
                      )}
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}