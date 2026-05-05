"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createClient } from "@/lib/supabase";


interface Message {
  role: "user" | "ai";
  content: string;
  timestamp: Date;
}

export default function VoiceChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  const [professionalId, setProfessionalId] = useState("11111111-1111-1111-1111-111111111111");
  const [professionalName, setProfessionalName] = useState("Professional");
  const [profession, setProfession] = useState<string | null>(null);

  useEffect(() => {
    createClient().auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setProfessionalId(user.id);
        setProfessionalName(user.user_metadata?.name || user.email?.split('@')[0] || 'Professional');
        setProfession(user.user_metadata?.profession || null);
      }
    });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    setMessages([
      {
        role: "ai",
        content: `Hi! Welcome to your daily journal. Let's reflect on your day together.

Tell me about what happened today - the highs, the lows, the moments that stood out. I'll listen and ask questions to help you reflect.

When you're done, just say "I'm finished" to close this entry.`,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const saveJournal = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/professional/journal/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          professional_id: professionalId,
          professional_name: professionalName,
          profession: profession,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
        }),
      });
      return response.ok;
    } catch (err) {
      console.error("Error saving journal:", err);
      return false;
    }
  };

  const handleSaveAndFinish = async () => {
    if (isLoading || isFinished) return;
    setIsLoading(true);
    setMessages((prev) => [...prev, {
      role: "ai",
      content: "Thanks for sharing! Saving your journal entry now — this will be turned into an experience students can explore.",
      timestamp: new Date(),
    }]);
    await saveJournal();
    setIsFinished(true);
    setIsLoading(false);
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = inputText.trim();
    setInputText("");
    setIsLoading(true);

    const userMsg: Message = {
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await fetch(`${apiUrl}/api/professional/journal/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          professional_id: professionalId,
          professional_name: professionalName,
          message: userMessage,
          conversation: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (!response.ok) throw new Error("Failed to get response");

      const data = await response.json();

      setMessages((prev) => [...prev, {
        role: "ai",
        content: data.response || "Tell me more about that.",
        timestamp: new Date(),
      }]);
    } catch (err) {
      console.error("Error sending message:", err);
      setMessages((prev) => [...prev, {
        role: "ai",
        content: "Thanks for sharing! What else happened today?",
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewEntry = () => {
    setIsFinished(false);
    setMessages([{
      role: "ai",
      content: "Let's reflect on today. What's been happening?",
      timestamp: new Date(),
    }]);
  };

  if (isFinished) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-lg text-center"
        >
          <div className="text-6xl mb-6">✅</div>
          <h1 className="text-3xl font-bold mb-4">Journal Entry Saved!</h1>
          <p className="text-gray-400 mb-6">
            Your reflection has been saved. It will be processed into a story that students can experience through Shadow Day.
          </p>
          
          <div className="space-y-3">
            <button
              onClick={startNewEntry}
              className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-colors"
            >
              Start New Entry
            </button>
            
            <button
              onClick={() => window.location.href = '/professional'}
              className="w-full py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      <header className="border-b border-white/10 p-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-light">📓 Daily Journal</h1>
            <p className="text-gray-400 text-sm">Reflect and share your day</p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto space-y-4">
          <AnimatePresence>
            {messages.map((message, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-xl ${
                    message.role === "user"
                      ? "bg-purple-600 text-white"
                      : "bg-white/10 text-gray-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="bg-white/10 p-4 rounded-xl text-gray-400">
                <span className="animate-pulse">Thinking...</span>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="border-t border-white/10 p-4">
        <div className="max-w-3xl mx-auto space-y-2">
          <div className="flex gap-2">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Share your day..."
              disabled={isLoading}
              className="flex-1 p-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none resize-none"
              rows={2}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputText.trim()}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-white/10 text-white rounded-xl self-end"
            >
              Send
            </button>
          </div>
          {/* Save button — always visible so professional can finish whenever they want */}
          <button
            onClick={handleSaveAndFinish}
            disabled={isLoading || messages.length < 3}
            className="w-full py-2 text-sm text-gray-400 hover:text-white border border-white/10 hover:border-white/30 rounded-xl transition-all disabled:opacity-30"
          >
            ✅ Save &amp; Turn Into a Student Experience
          </button>
        </div>
      </footer>
    </div>
  );
}