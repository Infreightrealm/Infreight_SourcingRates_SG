import { useState, useEffect } from "react";
import { X, CheckCircle } from "lucide-react";
import { API_URL } from "../lib/api";

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
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-blur-in">
      <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-2xl w-full max-w-md p-6 shadow-2xl animate-scale-in-spring">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3 text-emerald-400">
            <div className="animate-float-gentle">
              <CheckCircle className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-medium text-slate-900 dark:text-white animate-fade-in-up stagger-2">Search Completed</h3>
          </div>
          <button onClick={handleWait} className="p-1 hover:bg-slate-200 dark:hover:bg-gray-800 rounded-full text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <p className="text-slate-500 dark:text-gray-400 mb-8 leading-relaxed animate-fade-in-up stagger-3">
          Your rate search results have finished loading. Are you done analyzing these results so the next user in the queue can start their search?
        </p>

        <div className="flex justify-end space-x-4">
          <button 
            onClick={handleWait}
            className="px-5 py-2.5 rounded-lg text-sm font-medium text-slate-500 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-gray-800 transition-colors btn-interactive"
          >
            No, I need more time
          </button>
          <button 
            onClick={handleRelease}
            className="px-5 py-2.5 rounded-lg text-sm font-medium bg-emerald-500 hover:bg-emerald-400 text-black transition-colors btn-interactive"
          >
            Yes, I'm done
          </button>
        </div>
      </div>
    </div>
  );
}
