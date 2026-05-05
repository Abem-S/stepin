"use client";

import { useEffect, useRef, useCallback } from "react";
import { Howl } from "howler";

interface AmbientAudioProps {
  /** Current mood: "tense", "calm", "urgent", "gentle", "neutral" */
  mood?: "tense" | "calm" | "urgent" | "gentle" | "neutral";
  /** Volume level 0-1 */
  volume?: number;
  /** Whether audio should be playing */
  isPlaying?: boolean;
}

/**
 * Ambient Audio Component
 * 
 * Provides mood-based ambient audio that shifts based on the student's
 * choices and the emotional state of the Shadow Day experience.
 * 
 * Mood transitions:
 * - tense → urgent (high tension moments)
 * - calm → gentle (reflective moments)
 * - Default: neutral atmospheric
 */
export default function AmbientAudio({ 
  mood = "neutral", 
  volume = 0.3,
  isPlaying = true 
}: AmbientAudioProps) {
  const howlRef = useRef<Howl | null>(null);
  const currentMoodRef = useRef<string>("neutral");

  // Audio URLs by mood - using royalty-free atmospheric sounds
  const audioSources: Record<string, string> = {
    tense: "https://assets.mixkit.co/active_storage/sfx/2515/2515-preview.mp3",
    calm: "https://assets.mixkit.co/active_storage/sfx/2538/2538-preview.mp3",
    urgent: "https://assets.mixkit.co/active_storage/sfx/2515/2515-preview.mp3",
    gentle: "https://assets.mixkit.co/active_storage/sfx/2538/2538-preview.mp3",
    neutral: "https://assets.mixkit.co/active_storage/sfx/2538/2538-preview.mp3",
  };

  // Initialize audio
  useEffect(() => {
    // Create Howl instance
    howlRef.current = new Howl({
      src: [audioSources.neutral],
      loop: true,
      volume: volume,
      html5: true, // Use HTML5 Audio for streaming
      onloaderror: (_id, error) => {
        console.error("Failed to load ambient audio:", error);
      },
    });

    // Start playing if enabled
    if (isPlaying) {
      howlRef.current.play();
    }

    // Cleanup
    return () => {
      if (howlRef.current) {
        howlRef.current.stop();
        howlRef.current.unload();
      }
    };
  }, []);

  // Handle mood changes with smooth transitions
  useEffect(() => {
    if (!howlRef.current || currentMoodRef.current === mood) return;

    const newSrc = audioSources[mood];
    
    setTimeout(() => {
      if (howlRef.current) {
        const shouldPlay = howlRef.current.playing();
        howlRef.current.stop();
        howlRef.current.unload();
        howlRef.current = new Howl({
          src: [newSrc],
          loop: true,
          volume,
          html5: true,
          onloaderror: (_id, error) => {
            console.error("Failed to load ambient audio:", error);
          },
        });

        if (shouldPlay && isPlaying) {
          howlRef.current.play();
        }
      }
    }, 500);

    currentMoodRef.current = mood;
  }, [mood, volume]);

  // Handle play/pause
  useEffect(() => {
    if (!howlRef.current) return;
    
    if (isPlaying) {
      if (!howlRef.current.playing()) {
        howlRef.current.play();
      }
    } else {
      if (howlRef.current.playing()) {
        howlRef.current.pause();
      }
    }
  }, [isPlaying]);

  // Update volume
  useEffect(() => {
    if (howlRef.current) {
      howlRef.current.volume(volume);
    }
  }, [volume]);

  // This component doesn't render anything visible
  return null;
}

/**
 * Hook for managing ambient audio programmatically
 */
export function useAmbientAudio() {
  const moodRef = useRef<string>("neutral");
  const isPlayingRef = useRef<boolean>(true);

  const setMood = useCallback((mood: string) => {
    moodRef.current = mood;
    // Trigger custom event for the component to respond to
    window.dispatchEvent(new CustomEvent('ambient-audio-mood', { detail: { mood } }));
  }, []);

  const play = useCallback(() => {
    isPlayingRef.current = true;
    window.dispatchEvent(new CustomEvent('ambient-audio-play', { detail: { play: true } }));
  }, []);

  const pause = useCallback(() => {
    isPlayingRef.current = false;
    window.dispatchEvent(new CustomEvent('ambient-audio-play', { detail: { play: false } }));
  }, []);

  return { setMood, play, pause, mood: moodRef.current, isPlaying: isPlayingRef.current };
}