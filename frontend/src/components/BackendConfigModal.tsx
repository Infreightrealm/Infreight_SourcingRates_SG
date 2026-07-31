"use client";
import { useState } from "react";
import { getPrimaryApiUrl, setCustomPrimaryApiUrl, forceRestorePrimary, getApiUrl } from "@/lib/api";
import { toast } from "sonner";

interface BackendConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUrlChanged: (newUrl: string) => void;
}

export default function BackendConfigModal({ isOpen, onClose, onUrlChanged }: BackendConfigModalProps) {
  const [urlInput, setUrlInput] = useState(() => getPrimaryApiUrl());
  const [isTesting, setIsTesting] = useState(false);

  if (!isOpen) return null;

  const handleSaveAndTest = async () => {
    setIsTesting(true);
    const cleaned = urlInput.trim();
    setCustomPrimaryApiUrl(cleaned);
    
    toast.info("Testing connection to " + (cleaned || "Primary Backend") + "...");
    const res = await forceRestorePrimary();
    setIsTesting(false);
    
    if (res.success) {
      toast.success(`Connected to Primary Backend (${res.url})!`);
      onUrlChanged(res.url);
      onClose();
    } else {
      toast.error("Could not connect to Primary Backend", {
        description: res.error,
        duration: 8000,
      });
    }
  };

  const handleReset = () => {
    setCustomPrimaryApiUrl("");
    const defaultUrl = getPrimaryApiUrl();
    setUrlInput(defaultUrl);
    toast.info("Reset primary URL to default.");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-slate-900 border border-slate-700/60 text-white rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-5 animate-scale-in">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">🔌</span>
            <h3 className="font-semibold text-lg">Backend Server Settings</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            ✕
          </button>
        </div>

        <div className="space-y-4 text-sm">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Primary Backend URL (Local Machine / ngrok Tunnel)
            </label>
            <input
              type="text"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="e.g. https://your-tunnel.ngrok-free.app or http://localhost:8000"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 font-mono text-xs"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              If your ngrok tunnel URL changes when you restart ngrok on your computer, paste your new ngrok URL here!
            </p>
          </div>

          <div className="bg-slate-800/50 p-3 rounded-xl border border-slate-700/40 text-xs space-y-1">
            <div className="flex justify-between text-slate-400">
              <span>Active Backend:</span>
              <span className="font-mono text-emerald-400 font-medium truncate max-w-[220px]">{getApiUrl()}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <button
            onClick={handleReset}
            className="text-xs text-slate-400 hover:text-slate-200 underline"
          >
            Reset Default
          </button>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveAndTest}
              disabled={isTesting}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50"
            >
              {isTesting ? "Testing..." : "Save & Connect"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
