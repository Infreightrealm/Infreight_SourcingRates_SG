import { useState, useEffect } from "react";
import { X, CheckCircle } from "lucide-react";
import { API_URL } from "../lib/api";
import { Overlay, Panel } from "@/components/ui/surfaces";

interface SearchCompletionModalProps {
  searchId: string;
  isCompleted: boolean;
}

export function SearchCompletionModal({ searchId, isCompleted }: SearchCompletionModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [released, setReleased] = useState(false);

  useEffect(() => {
    // If the search just completed, set a 2-minute timer to show the modal
    if (isCompleted && !released) {
      const timer = setTimeout(() => {
        setIsOpen(true);
      }, 2 * 60 * 1000); // 2 minutes

      return () => clearTimeout(timer);
    }
  }, [isCompleted, released]);

  const handleRelease = async () => {
    try {
      await fetch(`${API_URL}/api/rate-search/${searchId}/release`, {
        method: "POST",
      });
      setReleased(true);
      setIsOpen(false);
    } catch (err) {
      console.error("Failed to release lock:", err);
    }
  };

  const handleWait = () => {
    setIsOpen(false);
    // Restart the 2-minute timer when "No" is clicked
    setTimeout(() => {
      if (!released) {
        setIsOpen(true);
      }
    }, 2 * 60 * 1000);
  };

  if (!isOpen) return null;

  return (
    <Overlay>
      <Panel className="max-w-md p-6">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="animate-float-gentle inline-flex size-9 items-center justify-center rounded-xl border border-success/25 bg-success/12 text-success-foreground">
              <CheckCircle className="size-5" />
            </span>
            <h3 className="animate-fade-in-up stagger-2 text-lg font-semibold tracking-tight text-foreground">Search Completed</h3>
          </div>
          <button
            onClick={handleWait}
            aria-label="Close"
            className="flex size-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            <X className="size-4" />
          </button>
        </div>

        <p className="animate-fade-in-up stagger-3 mb-8 text-sm leading-relaxed text-muted-foreground">
          Your rate search results have finished loading. Are you done analyzing these results so the next user in the queue can start their search?
        </p>

        <div className="flex justify-end space-x-4">
          <button 
            onClick={handleWait}
            className="btn-interactive rounded-lg px-5 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground"
          >
            No, I need more time
          </button>
          <button 
            onClick={handleRelease}
            className="btn-interactive rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white shadow-panel hover:bg-emerald-500"
          >
            Yes, I'm done
          </button>
        </div>
      </Panel>
    </Overlay>
  );
}
