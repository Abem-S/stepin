"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { createClient } from "@/lib/supabase";

export default function Home() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  // If already logged in, redirect to correct dashboard
  useEffect(() => {
    createClient().auth.getUser().then(({ data: { user } }) => {
      if (user) {
        const role = user.user_metadata?.role;
        router.replace(role === "professional" ? "/professional" : "/student");
      } else {
        setChecking(false);
      }
    });
  }, []);

  if (checking) {
    return <div className="min-h-screen bg-black" />;
  }

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center px-6">
      {/* Headline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="text-center max-w-2xl mb-16"
      >
        <h1 className="text-4xl md:text-6xl font-light leading-tight mb-4 text-gray-100">
          Before you choose your future —<br />
          <span className="text-white font-normal">live someone else&apos;s first.</span>
        </h1>
        <p className="text-gray-500 text-lg">
          StepIn lets students experience real careers through the eyes of the people who live them.
        </p>
      </motion.div>

      {/* Two Role Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl"
      >
        {/* Student Card */}
        <button
          onClick={() => router.push("/auth/login?role=student")}
          className="group relative bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/30 rounded-2xl p-8 text-left transition-all duration-300"
        >
          <div className="text-3xl mb-4">🎓</div>
          <h2 className="text-xl font-medium text-white mb-2">I&apos;m a Student</h2>
          <p className="text-gray-400 text-sm leading-relaxed">
            Step into real careers. Live the decisions. Discover what actually fits you.
          </p>
          <div className="mt-6 text-sm text-gray-500 group-hover:text-gray-300 transition-colors">
            Sign in to explore →
          </div>
        </button>

        {/* Professional Card */}
        <button
          onClick={() => router.push("/auth/login?role=professional")}
          className="group relative bg-purple-950/30 hover:bg-purple-900/30 border border-purple-800/30 hover:border-purple-600/50 rounded-2xl p-8 text-left transition-all duration-300"
        >
          <div className="text-3xl mb-4">💼</div>
          <h2 className="text-xl font-medium text-white mb-2">I&apos;m a Professional</h2>
          <p className="text-gray-400 text-sm leading-relaxed">
            Share your journey. Turn your daily work into an experience that inspires the next generation.
          </p>
          <div className="mt-6 text-sm text-purple-400 group-hover:text-purple-300 transition-colors">
            Sign in to share →
          </div>
        </button>
      </motion.div>

      {/* Subtle footer tagline */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-12 text-gray-700 text-xs"
      >
        No career exploration platform captures reality like this.
      </motion.p>
    </div>
  );
}