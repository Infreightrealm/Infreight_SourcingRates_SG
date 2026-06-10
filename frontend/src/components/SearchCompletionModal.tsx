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
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#121212] border border-gray-800 rounded-2xl w-full max-w-md p-6 shadow-2xl animate-in fade-in zoom-in duration-300">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3 text-emerald-400">
            <CheckCircle className="w-6 h-6" />
            <h3 className="text-xl font-medium text-white">Search Completed</h3>
          </div>
          <button onClick={handleWait} className="p-1 hover:bg-gray-800 rounded-full text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <p className="text-gray-400 mb-8 leading-relaxed">
          Your rate search results have finished loading. Are you done analyzing these results so the next user in the queue can start their search?
        </p>

        <div className="flex justify-end space-x-4">
          <button 
            onClick={handleWait}
            className="px-5 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
          >
            No, I need more time
          </button>
          <button 
            onClick={handleRelease}
            className="px-5 py-2.5 rounded-lg text-sm font-medium bg-emerald-500 hover:bg-emerald-400 text-black transition-colors"
          >
            Yes, I'm done
          </button>
        </div>
      </div>
    </div>
  );
}
