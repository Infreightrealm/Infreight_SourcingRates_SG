"use client";
import { useState, useEffect } from "react";

interface VncViewerProps {
  backendUrl: string;
  isSearching: boolean;
}

export default function VncViewer({ backendUrl, isSearching }: VncViewerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isAvailable, setIsAvailable] = useState(false);
  const [vncPath, setVncPath] = useState("");

  useEffect(() => {
    // Check if VNC is available on mount
    fetch(`${backendUrl}/api/vnc-status`)
      .then((res) => res.json())
      .then((data) => {
        setIsAvailable(data.available);
        if (data.available) {
          setVncPath(data.vnc_path);
        }
      })
      .catch(() => setIsAvailable(false));
  }, [backendUrl]);

  // Auto-open when searching starts
  useEffect(() => {
    if (isSearching && isAvailable) {
      setIsOpen(true);
    }
  }, [isSearching, isAvailable]);

  if (!isAvailable) return null;

  // Build the full VNC URL from the backend origin
  const vncUrl = (() => {
    try {
      const url = new URL(backendUrl);
      return `${url.protocol}//${url.host}${vncPath}`;
    } catch {
      return `${backendUrl}${vncPath}`;
    }
  })();

  return (
    <div className="fixed bottom-0 right-0 z-50 flex flex-col items-end">
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          mr-4 mb-0 px-4 py-2 rounded-t-xl text-xs font-semibold
          transition-all duration-300 shadow-lg
          flex items-center gap-2
          ${
            isOpen
              ? "bg-red-100 text-red-700 border border-red-200 border-b-0 hover:bg-red-200 dark:bg-red-500/20 dark:text-red-300 dark:border-red-500/30 dark:hover:bg-red-500/30"
              : isSearching
                ? "bg-emerald-100 text-emerald-700 border border-emerald-200 border-b-0 hover:bg-emerald-200 animate-pulse dark:bg-emerald-500/20 dark:text-emerald-300 dark:border-emerald-500/30 dark:hover:bg-emerald-500/30"
                : "bg-slate-200 text-slate-700 border border-slate-300 border-b-0 hover:bg-slate-300 dark:bg-white/10 dark:text-white/60 dark:border-white/10 dark:hover:bg-white/20"
          }
        `}
      >
        {isOpen ? (
          <>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Close Browser View
          </>
        ) : (
          <>
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a9 9 0 11-18 0V5.25" />
            </svg>
            {isSearching ? "🔴 Live Browser View" : "Live Browser View"}
          </>
        )}
      </button>

      {/* VNC Panel */}
      {isOpen && (
        <div
          className="
            w-[820px] h-[520px]
            bg-slate-50/95 dark:bg-[#0a0a0f]/95 backdrop-blur-xl
            border border-slate-300 dark:border-white/10 rounded-tl-2xl
            shadow-2xl shadow-black/20 dark:shadow-black/50
            flex flex-col overflow-hidden
          "
        >
          {/* Panel Header */}
          <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-300 dark:border-white/10 bg-slate-200 dark:bg-white/[0.03]">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse" />
              <span className="text-xs font-medium text-slate-800 dark:text-white/70">
                Live Browser — Carrier Portal View
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-500 dark:text-white/30 font-mono">
                VNC
              </span>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-300 dark:hover:bg-white/10 text-slate-500 hover:text-slate-900 dark:text-white/40 dark:hover:text-white/80 transition-colors"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </button>
            </div>
          </div>

          {/* noVNC iframe */}
          <div className="flex-1 relative bg-white dark:bg-black">
            <iframe
              src={vncUrl}
              className="w-full h-full border-0"
              allow="clipboard-read; clipboard-write"
              title="Live Browser View — noVNC"
            />
          </div>
        </div>
      )}
    </div>
  );
}
