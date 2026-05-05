"use client";

import { Suspense, useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
  role: "user" | "professional";
  content: string;
}

interface Professional {
  id: string;
  name: string;
  profession: string;
}

function DigitalTwinContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const professionalId = searchParams.get("professional") || "11111111-1111-1111-1111-111111111111";
  
  const [professional, setProfessional] = useState<Professional | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  // Load professional data
  useEffect(() => {
    async function loadProfessional() {
      try {
        const response = await fetch(`${apiUrl}/api/professionals/${professionalId}`);
        if (response.ok) {
          const data = await response.json();
          setProfessional(data);
          
          // Add welcome message
          setMessages([
            {
              role: "professional",
              content: `Hi! I'm ${data.name}. Ask me anything about what it's really like to work as a ${data.profession}.`,
            },
          ]);
        }
      } catch (err) {
        console.error("Failed to load professional:", err);
        // Fallback
        setProfessional({
          id: professionalId,
          name: "Dr. Sarah Chen",
          profession: "Surgical Resident",
        });
        setMessages([
          {
            role: "professional",
            content: "Hi! I'm Dr. Sarah Chen. Ask me anything about what it's really like to work as a Surgical Resident.",
          },
        ]);
      }
    }
    loadProfessional();
  }, [professionalId, apiUrl]);

  // Auto-scroll to messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Send text message to Digital Twin
  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;
    
    const userMessage = inputText.trim();
    setInputText("");
    setIsLoading(true);
    
    // Add user message immediately
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    
    try {
      const response = await fetch(`${apiUrl}/api/digital-twin/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          professional_id: professionalId,
          professional_name: professional?.name || "Professional",
          message: userMessage,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [
          ...prev,
          { role: "professional", content: data.response },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "professional", content: "I'm having trouble responding right now. Can you try again?" },
        ]);
      }
    } catch (err) {
      console.error("Error sending message:", err);
      setMessages((prev) => [
        ...prev,
        { role: "professional", content: "Something went wrong. Please try again." },
      ]);
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

  if (!professional) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900 flex flex-col">
      {/* Header */}
      <header className="border-b border-dark-800 p-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="text-gray-500 hover:text-gray-300 transition-colors"
            >
              ← Back
            </button>
            <div>
              <h1 className="text-lg text-white font-medium">
                Chat with {professional.name}
              </h1>
              <p className="text-sm text-gray-500">
                Digital Twin • {professional.profession}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
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
                  className={`max-w-[80%] p-4 rounded-sm ${
                    message.role === "user"
                      ? "bg-purple-500/20 text-white"
                      : "bg-dark-800 text-gray-200"
                  }`}
                >
                  {message.content}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-dark-800 p-4 rounded-sm text-gray-400">
                <span className="animate-pulse">Thinking...</span>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="border-t border-dark-800 p-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-2">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about their career journey..."
              disabled={isLoading}
              className="flex-1 p-4 bg-dark-800 border border-dark-700 rounded-sm text-white placeholder-gray-600 focus:border-purple-500 focus:outline-none resize-none"
              rows={2}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputText.trim()}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-dark-700 disabled:text-gray-500 text-white rounded-sm transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function DigitalTwinPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-black flex items-center justify-center">
          <div className="text-gray-500">Loading...</div>
        </div>
      }
    >
      <DigitalTwinContent />
    </Suspense>
  );
}