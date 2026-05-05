"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { motion } from "framer-motion";
import { Suspense } from "react";

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const role = searchParams.get("role") || "student";
  const redirectTo = searchParams.get("redirectTo") || (role === "professional" ? "/professional" : "/careers");

  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [profession, setProfession] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const supabase = createClient();

  // Check if already logged in
  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) router.push(redirectTo);
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "signup") {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { name, role, profession: isProf ? profession : undefined },
          },
        });
        if (error) throw error;
        setMessage("Account created! You can log in now.");
        setMode("login");
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;

        // Enforce role — redirect to the portal that matches the account's role
        const storedRole = data.user?.user_metadata?.role || "student";
        if (storedRole !== role) {
          // Sign them out and show a helpful message
          await supabase.auth.signOut();
          setError(
            `This account is registered as a ${storedRole}. Please use the ${storedRole} login instead.`
          );
          setLoading(false);
          return;
        }

        const destination =
          redirectTo && redirectTo.startsWith("/") ? redirectTo
          : storedRole === "professional" ? "/professional"
          : "/student";
        router.push(destination);
        router.refresh();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const isProf = role === "professional";

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-light text-white mb-2">
            {isProf ? "Professional Portal" : "StepIn"}
          </h1>
          <p className="text-gray-500 text-sm">
            {isProf
              ? "Share your journey. Inspire the next generation."
              : "Explore careers. Discover yourself."}
          </p>
        </div>

        {/* Role badge */}
        <div className="flex justify-center mb-6">
          <span
            className={`px-3 py-1 text-xs rounded-full border ${
              isProf
                ? "border-purple-600 text-purple-400"
                : "border-blue-600 text-blue-400"
            }`}
          >
            {isProf ? "Professional Account" : "Student Account"}
          </span>
        </div>

        {/* Card */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-8">
          {/* Mode tabs */}
          <div className="flex mb-6 border border-white/10 rounded-lg overflow-hidden">
            <button
              onClick={() => setMode("login")}
              className={`flex-1 py-2 text-sm transition-colors ${
                mode === "login" ? "bg-white/10 text-white" : "text-gray-500 hover:text-gray-300"
              }`}
            >
              Log In
            </button>
            <button
              onClick={() => setMode("signup")}
              className={`flex-1 py-2 text-sm transition-colors ${
                mode === "signup" ? "bg-white/10 text-white" : "text-gray-500 hover:text-gray-300"
              }`}
            >
              Sign Up
            </button>
          </div>

          {message && (
            <div className="mb-4 p-3 bg-green-900/30 border border-green-700 rounded-lg text-green-400 text-sm">
              {message}
            </div>
          )}
          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "signup" && isProf && (
              <div>
                <label className="block text-xs text-gray-500 mb-1">Your Profession / Career</label>
                <input
                  type="text"
                  value={profession}
                  onChange={(e) => setProfession(e.target.value)}
                  placeholder="e.g. Mechanical Engineer, Doctor, Software Engineer"
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:border-white/30 focus:outline-none"
                />
              </div>
            )}
            {mode === "signup" && (
              <div>
                <label className="block text-xs text-gray-500 mb-1">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:border-white/30 focus:outline-none"
                />
              </div>
            )}
            <div>
              <label className="block text-xs text-gray-500 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:border-white/30 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:border-white/30 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-lg font-medium transition-all ${
                isProf
                  ? "bg-purple-600 hover:bg-purple-700"
                  : "bg-white text-black hover:bg-gray-200"
              } disabled:opacity-50`}
            >
              {loading ? "Please wait..." : mode === "login" ? "Log In" : "Create Account"}
            </button>
          </form>
        </div>

        {/* Switch portal link — stays inside auth */}
        <div className="text-center mt-4">
          {isProf ? (
            <button
              onClick={() => router.push("/auth/login?role=student")}
              className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
            >
              Student account? → Sign in here
            </button>
          ) : (
            <button
              onClick={() => router.push("/auth/login?role=professional")}
              className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
            >
              Professional account? → Sign in here
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-black" />}>
      <LoginContent />
    </Suspense>
  );
}
