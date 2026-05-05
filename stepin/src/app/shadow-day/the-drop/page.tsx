"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

function TheDropContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const worldId = searchParams.get("world");
  
  const [showFirstLine, setShowFirstLine] = useState(false);
  const [showSecondLine, setShowSecondLine] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    // Start the sequence when component mounts
    // First line fades in immediately
    const firstLineTimer = setTimeout(() => {
      setShowFirstLine(true);
    }, 500); // Small delay for dramatic effect

    // Second line fades in after 800ms delay
    const secondLineTimer = setTimeout(() => {
      setShowSecondLine(true);
    }, 2500); // 500 + ~2000ms (first line display time + 800ms delay)

    // Transition to Shadow Day after second line
    const transitionTimer = setTimeout(() => {
      setIsComplete(true);
      
      // Navigate to Shadow Day with world_id
      if (worldId) {
        router.push(`/shadow-day?world=${worldId}`);
      } else {
        router.push("/shadow-day");
      }
    }, 4500); // Give time for second line to be fully visible

    return () => {
      clearTimeout(firstLineTimer);
      clearTimeout(secondLineTimer);
      clearTimeout(transitionTimer);
    };
  }, [router, worldId]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center overflow-hidden">
      <AnimatePresence mode="wait">
        {!isComplete ? (
          <motion.div
            key="the-drop"
            className="text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Line 1: "It's Tuesday." */}
            <AnimatePresence>
              {showFirstLine && (
                <motion.p
                  key="line-1"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ 
                    duration: 1.2, 
                    ease: "easeOut" 
                  }}
                  className="text-2xl md:text-4xl lg:text-5xl font-light text-white tracking-wide mb-8"
                  style={{ 
                    fontFamily: 'Geist, system-ui, sans-serif',
                    letterSpacing: '0.05em'
                  }}
                >
                  Your journey is about to begin.
                </motion.p>
              )}
            </AnimatePresence>

            {/* Line 2: "Every choice matters." */}
            <AnimatePresence>
              {showSecondLine && (
                <motion.p
                  key="line-2"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ 
                    duration: 1.2, 
                    ease: "easeOut" 
                  }}
                  className="text-xl md:text-3xl lg:text-4xl font-light text-white/90 tracking-wide"
                  style={{ 
                    fontFamily: 'Geist, system-ui, sans-serif',
                    letterSpacing: '0.05em'
                  }}
                >
                  Every choice matters.
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        ) : (
          <motion.div
            key="transitioning"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-black"
          >
            {/* Empty black screen during transition */}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function TheDropPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    }>
      <TheDropContent />
    </Suspense>
  );
}