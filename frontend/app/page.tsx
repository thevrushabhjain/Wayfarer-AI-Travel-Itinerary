"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect } from "react";
import { toast } from "sonner";

import { ChatPanel } from "@/components/chat/ChatPanel";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { ItineraryDashboard } from "@/components/dashboard/ItineraryDashboard";
import { RefineBar } from "@/components/dashboard/RefineBar";
import { GridBackground } from "@/components/layout/GridBackground";
import { useChat } from "@/hooks/use-chat";
import { clearSession } from "@/lib/session";

export default function Home() {
  const { messages, itinerary, progressStage, isSending, error, initialized, sendMessage } = useChat();

  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  const handleReset = () => {
    clearSession();
    window.location.reload();
  };

  if (!initialized) {
    return <main className="min-h-screen bg-black" />;
  }

  return (
    <main data-testid="app-root" className="relative min-h-screen bg-black">
      <GridBackground />
      <AnimatePresence mode="wait">
        {itinerary ? (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="relative z-10"
          >
            <DashboardHeader onReset={handleReset} />
            <ItineraryDashboard itinerary={itinerary} />
            <RefineBar onSend={sendMessage} isSending={isSending} progressStage={progressStage} />
          </motion.div>
        ) : (
          <motion.div
            key="chat"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ChatPanel messages={messages} onSend={sendMessage} isSending={isSending} progressStage={progressStage} />
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
