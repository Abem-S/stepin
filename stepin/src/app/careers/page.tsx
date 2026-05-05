"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

// Types
interface CareerCategory {
  id: string;
  name: string;
  world_count: number;
}

interface CareerWorld {
  id: string;
  title: string;
  category: string;
  professional_name: string;
  total_students: number;
}

interface CareersResponse {
  categories: CareerCategory[];
}

interface WorldsResponse {
  category: string;
  worlds: CareerWorld[];
}

// API functions
async function fetchCareers(): Promise<CareersResponse> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
  const response = await fetch(`${apiUrl}/api/careers`);
  if (!response.ok) {
    throw new Error("Failed to fetch careers");
  }
  return response.json();
}

async function fetchWorlds(category: string, search?: string): Promise<WorldsResponse> {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/careers/${category}/worlds${search ? '?' + params : ''}`
  );
  if (!response.ok) throw new Error("Failed to fetch worlds");
  return response.json();
}

// Category card component
function CategoryCard({
  category,
  onClick,
}: {
  category: CareerCategory;
  onClick: () => void;
}) {
  return (
    <motion.button
      whileHover={{ scale: 1.02, backgroundColor: "rgba(255,255,255,0.05)" }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full p-6 bg-dark-800/50 border border-dark-700 rounded-sm text-left transition-all duration-200 hover:border-dark-600"
    >
      <h3 className="text-xl font-medium text-gray-200 mb-2">
        {category.name}
      </h3>
      <p className="text-sm text-gray-500">
        {category.world_count}{" "}
        {category.world_count === 1 ? "world" : "worlds"} available
      </p>
    </motion.button>
  );
}

// World card component
function WorldCard({ world }: { world: CareerWorld }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 bg-dark-800/50 border border-dark-700 rounded-sm hover:border-dark-500 transition-all"
    >
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{world.category}</p>
      <h4 className="text-lg font-medium text-gray-200 mb-1">{world.title}</h4>
      <p className="text-sm text-gray-500 mb-4">by {world.professional_name}</p>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-600">
          {world.total_students > 0 ? `${world.total_students} explored` : 'Be the first'}
        </span>
        <Link
          href={`/shadow-day/the-drop?world=${world.id}`}
          className="px-4 py-2 text-sm font-medium text-dark-900 bg-gray-200 hover:bg-white transition-colors duration-200 rounded-sm"
        >
          Enter →
        </Link>
      </div>
    </motion.div>
  );
}

// Empty state component
function EmptyState({ categoryName }: { categoryName: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="text-center py-12"
    >
      <p className="text-gray-400 mb-2">{categoryName}</p>
      <p className="text-gray-600 text-sm">New worlds coming soon</p>
    </motion.div>
  );
}

export default function CareersPage() {
  const [careers, setCareers] = useState<CareerCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [worlds, setWorlds] = useState<CareerWorld[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingWorlds, setLoadingWorlds] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  // Fetch careers on mount
  useEffect(() => {
    async function loadCareers() {
      try {
        const data = await fetchCareers();
        setCareers(data.categories);
      } catch (err) {
        setError("Failed to load careers. Please try again.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadCareers();
  }, []);

  // Fetch worlds when category is selected or search changes
  useEffect(() => {
    const category: string = selectedCategory ?? "";
    if (!category) return;

    let cancelled = false;

    async function loadWorlds() {
      setLoadingWorlds(true);
      try {
        const data = await fetchWorlds(category, search || undefined);
        if (!cancelled) setWorlds(data.worlds);
      } catch (err) {
        console.error("Failed to load worlds:", err);
      } finally {
        if (!cancelled) setLoadingWorlds(false);
      }
    }
    loadWorlds();

    return () => { cancelled = true; };
  }, [selectedCategory, search]);

  const selectedCategoryData = careers.find((c) => c.id === selectedCategory);

  return (
    <div className="min-h-screen flex flex-col bg-dark-900">
      {/* Header */}
      <header className="px-6 py-8 border-b border-dark-800">
        <div className="max-w-4xl mx-auto">
          <Link
            href="/"
            className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
          >
            ← Back to Home
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xl md:text-3xl font-light text-gray-200 mb-2"
          >
            Choose Your Path
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-gray-500 mb-8"
          >
            Select a career category to explore
          </motion.p>

          {/* Error State */}
          {error && (
            <div className="text-red-400 text-center py-8">{error}</div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-gray-500 text-center py-8">
              Loading careers...
            </div>
          )}

          {/* Categories Grid */}
          {!loading && !error && (
            <AnimatePresence mode="wait">
              {selectedCategory ? (
                <motion.div
                  key="worlds"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  {/* Back to categories */}
                  <button
                    onClick={() => setSelectedCategory(null)}
                    className="mb-6 text-sm text-gray-500 hover:text-gray-300 transition-colors"
                  >
                    ← Back to all categories
                  </button>

                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl text-gray-200">
                      {selectedCategoryData?.name}
                    </h2>
                    {/* Search box */}
                    <input
                      type="text"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder="Search by name or professional..."
                      className="px-4 py-2 text-sm bg-dark-800/80 border border-dark-700 rounded-sm text-gray-300 placeholder-gray-600 focus:border-dark-500 focus:outline-none w-64"
                    />
                  </div>

                  {/* Loading Worlds */}
                  {loadingWorlds && (
                    <div className="text-gray-500 text-center py-8">
                      Loading worlds...
                    </div>
                  )}

                  {/* World List */}
                  {!loadingWorlds && (
                    <>
                      {worlds.length > 0 ? (
                        <div className="grid gap-4 md:grid-cols-2">
                          {worlds.map((world) => (
                            <WorldCard key={world.id} world={world} />
                          ))}
                        </div>
                      ) : (
                        <EmptyState
                          categoryName={selectedCategoryData?.name || ""}
                        />
                      )}
                    </>
                  )}
                </motion.div>
              ) : (
                <motion.div
                  key="categories"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {careers.map((category, index) => (
                      <motion.div
                        key={category.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <CategoryCard
                          category={category}
                          onClick={() => setSelectedCategory(category.id)}
                        />
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          )}
        </div>
      </main>

      {/* Minimal Footer */}
      <footer className="flex items-center justify-center gap-8 py-8 border-t border-dark-800">
        <Link
          href="/about"
          className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
        >
          About
        </Link>
        <Link
          href="/privacy"
          className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
        >
          Privacy
        </Link>
      </footer>
    </div>
  );
}