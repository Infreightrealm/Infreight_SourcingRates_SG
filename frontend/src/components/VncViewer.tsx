"use client";
import { useState, useEffect } from "react";

interface VncViewerProps {
  backendUrl: string;
  isSearching: boolean;
}

interface CarrierVnc {
  name: string;
  code: string;
  path: string;
  ws_path: string;
}

export default function VncViewer({ backendUrl, isSearching }: VncViewerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isAvailable, setIsAvailable] = useState(false);
  const [carriers, setCarriers] = useState<CarrierVnc[]>([]);
  const [fallbackVncPath, setFallbackVncPath] = useState("");
  const [activeTab, setActiveTab] = useState<string>("maersk");

  useEffect(() => {
    // Check if VNC is available on mount
    fetch(`${backendUrl}/api/vnc-status`)
      .then((res) => res.json())
      .then((data) => {
        setIsAvailable(data.available);
        if (data.available) {
          if (data.carriers && data.carriers.length > 0) {
            setCarriers(data.carriers);
            // Default to first carrier
            setActiveTab(data.carriers[0].code);
          } else {
            setFallbackVncPath(data.vnc_path || "");
          }
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

  // Build full VNC URL helper
  const getFullVncUrl = (path: string) => {
    try {
      const url = new URL(backendUrl);
      return `${url.protocol}//${url.host}${path}`;
    } catch {
      return `${backendUrl}${path}`;
    }
  };

  // Brand colors mapping
  const getBrandColorStyles = (code: string, isActive: boolean) => {
    switch (code) {
      case "maersk":
        return isActive 
          ? "border-[#004B8C] text-[#004B8C] dark:text-[#3a9fff] dark:border-[#3a9fff] bg-[#004B8C]/10" 
          : "hover:text-[#004B8C] dark:hover:text-[#3a9fff] hover:bg-[#004B8C]/5 border-transparent";
      case "cma":
        return isActive 
          ? "border-[#ED1C24] text-[#ED1C24] dark:text-[#ff4d5a] dark:border-[#ff4d5a] bg-[#ED1C24]/10" 
          : "hover:text-[#ED1C24] dark:hover:text-[#ff4d5a] hover:bg-[#ED1C24]/5 border-transparent";
      case "one":
        return isActive 
          ? "border-[#E4007F] text-[#E4007F] dark:text-[#ff52b9] dark:border-[#ff52b9] bg-[#E4007F]/10" 
          : "hover:text-[#E4007F] dark:hover:text-[#ff52b9] hover:bg-[#E4007F]/5 border-transparent";
      case "hapag":
        return isActive 
          ? "border-[#FF5F00] text-[#FF5F00] dark:text-[#ff8137] dark:border-[#ff8137] bg-[#FF5F00]/10" 
          : "hover:text-[#FF5F00] dark:hover:text-[#ff8137] hover:bg-[#FF5F00]/5 border-transparent";
      default:
        return isActive 
          ? "border-emerald-500 text-emerald-500 bg-emerald-500/10" 
          : "hover:text-emerald-500 hover:bg-emerald-500/5 border-transparent";
    }
  };

  const getPulseColor = (code: string) => {
    switch (code) {
      case "maersk": return "bg-[#004B8C] dark:bg-[#3a9fff]";
      case "cma": return "bg-[#ED1C24] dark:bg-[#ff4d5a]";
      case "one": return "bg-[#E4007F] dark:bg-[#ff52b9]";
      case "hapag": return "bg-[#FF5F00] dark:bg-[#ff8137]";
      default: return "bg-emerald-500";
    }
  };

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
            {isSearching ? "🔴 Live Browser Tabs" : "Live Browser Tabs"}
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
          {/* Panel Header & Tabs */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-slate-300 dark:border-white/10 bg-slate-200 dark:bg-white/[0.03]">
            {carriers.length > 0 ? (
              /* Multi-Tab Layout */
              <div className="flex items-center gap-1">
                {carriers.map((carrier) => {
                  const isActive = activeTab === carrier.code;
                  return (
                    <button
                      key={carrier.code}
                      onClick={() => setActiveTab(carrier.code)}
                      className={`
                        px-3 py-1.5 rounded-lg text-xs font-semibold
                        transition-all duration-200 flex items-center gap-2 border-b-2
                        ${getBrandColorStyles(carrier.code, isActive)}
                      `}
                    >
                      <span className={`w-2 h-2 rounded-full ${getPulseColor(carrier.code)} ${isSearching ? "animate-ping" : "opacity-80"}`} />
                      {carrier.name}
                    </button>
                  );
                })}
              </div>
            ) : (
              /* Legacy Single Tab Fallback */
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse" />
                <span className="text-xs font-medium text-slate-800 dark:text-white/70">
                  Live Browser — Carrier Portal View
                </span>
              </div>
            )}
            
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-500 dark:text-white/30 font-mono">
                MULTI-DISPLAY VNC
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

          {/* VNC iframes (mounted concurrently to maintain state, but toggled via css visibility) */}
          <div className="flex-1 relative bg-white dark:bg-black">
            {carriers.length > 0 ? (
              carriers.map((carrier) => {
                const isActive = activeTab === carrier.code;
                return (
                  <div
                    key={carrier.code}
                    className="w-full h-full absolute inset-0"
                    style={{ display: isActive ? "block" : "none" }}
                  >
                    <iframe
                      src={getFullVncUrl(carrier.path)}
                      className="w-full h-full border-0"
                      allow="clipboard-read; clipboard-write"
                      title={`Live Browser View — ${carrier.name}`}
                    />
                  </div>
                );
              })
            ) : (
              /* Legacy Fallback Single View */
              <iframe
                src={getFullVncUrl(fallbackVncPath)}
                className="w-full h-full border-0"
                allow="clipboard-read; clipboard-write"
                title="Live Browser View — noVNC"
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
