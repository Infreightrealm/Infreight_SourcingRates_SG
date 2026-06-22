"use client";
import { useState, useEffect } from "react";
import type { CarrierResultSchema } from "@/lib/types";

interface VncViewerProps {
  backendUrl: string;
  isSearching: boolean;
  results?: CarrierResultSchema[];
}

interface CarrierVnc {
  name: string;
  code: string;
  path: string;
  ws_path: string;
}

export default function VncViewer({ backendUrl, isSearching, results = [] }: VncViewerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isAvailable, setIsAvailable] = useState(false);
  const [carriers, setCarriers] = useState<CarrierVnc[]>([]);
  const [fallbackVncPath, setFallbackVncPath] = useState("");
  const [activeTab, setActiveTab] = useState<string>("maersk");
  const [dismissedOverlays, setDismissedOverlays] = useState<Record<string, boolean>>({});

  // Reset dismissed overlays when a new search starts
  useEffect(() => {
    if (isSearching) {
      setDismissedOverlays({});
    }
  }, [isSearching]);

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
      const timer = setTimeout(() => {
        setIsOpen(true);
      }, 0);
      return () => clearTimeout(timer);
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
      case "greenx":
        return isActive 
          ? "border-[#112A62] text-[#112A62] dark:text-[#3a7fff] dark:border-[#3a7fff] bg-[#112A62]/10" 
          : "hover:text-[#112A62] dark:hover:text-[#3a7fff] hover:bg-[#112A62]/5 border-transparent";
      case "msc":
        return isActive 
          ? "border-black text-black dark:text-white dark:border-white bg-black/10 dark:bg-white/10" 
          : "hover:text-black dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 border-transparent";
      case "oocl":
        return isActive 
          ? "border-[#E31837] text-[#E31837] dark:text-[#ff4d6a] dark:border-[#ff4d6a] bg-[#E31837]/10" 
          : "hover:text-[#E31837] dark:hover:text-[#ff4d6a] hover:bg-[#E31837]/5 border-transparent";
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
      case "greenx": return "bg-[#112A62] dark:bg-[#3a7fff]";
      case "msc": return "bg-black dark:bg-white";
      case "oocl": return "bg-[#E31837] dark:bg-[#ff4d6a]";
      default: return "bg-emerald-500";
    }
  };

  const getBackendCarrierKey = (vncCode: string): string => {
    const code = vncCode.toLowerCase();
    if (code.includes("maersk")) return "MAERSK";
    if (code.includes("cma")) return "CMA_CGM";
    if (code.includes("one")) return "ONE";
    if (code.includes("hapag")) return "HAPAG_LLOYD";
    if (code.includes("oocl")) return "OOCL";
    if (code.includes("greenx")) return "GREENX";
    if (code.includes("msc")) return "MSC";
    return vncCode.toUpperCase();
  };

  const getIndicatorStyle = (carrierCode: string) => {
    const backendKey = getBackendCarrierKey(carrierCode);
    const result = results?.find((r) => r.carrier === backendKey);

    if (result) {
      let status = result.status;
      if (backendKey === "MSC" && status === "TIMEOUT") {
        status = "NO_QUOTES_AVAILABLE";
      }
      if (
        status === "MANUAL_ACTION_REQUIRED" ||
        status === "WAITING_FOR_HUMAN_VERIFICATION" ||
        status === "BOT_CHALLENGE_DETECTED" ||
        status === "CAPTCHA_OR_MANUAL_REVIEW_REQUIRED"
      ) {
        return "bg-amber-500 dark:bg-amber-400 animate-ping";
      }
      if (status === "RUNNING" || status === "QUEUED") {
        return "bg-emerald-500 dark:bg-emerald-400 animate-pulse";
      } else if (
        status === "COMPLETED" ||
        status === "AVAILABLE_QUOTES_FOUND" ||
        status === "NO_QUOTES_AVAILABLE"
      ) {
        return "bg-emerald-500 dark:bg-emerald-400";
      } else {
        // Any other status is an issue / failure / partial result
        return "bg-red-500 dark:bg-red-400";
      }
    }

    // Fallback if global search is active and we have no results yet
    if (isSearching && (!results || results.length === 0)) {
      return "bg-emerald-500 dark:bg-emerald-400 animate-pulse";
    }

    // Default neutral/idle state: Brand color with opacity
    return `${getPulseColor(carrierCode)} opacity-80`;
  };

  // Find which carriers require manual action/verification
  const manualActionCarriers = carriers.filter((carrier) => {
    const backendKey = getBackendCarrierKey(carrier.code);
    const result = results?.find((r) => r.carrier === backendKey);
    if (!result) return false;
    const status = result.status;
    return (
      status === "MANUAL_ACTION_REQUIRED" ||
      status === "WAITING_FOR_HUMAN_VERIFICATION" ||
      status === "BOT_CHALLENGE_DETECTED" ||
      status === "CAPTCHA_OR_MANUAL_REVIEW_REQUIRED"
    );
  });

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
              : manualActionCarriers.length > 0
                ? "bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold border border-amber-600 border-b-0 animate-bounce"
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
            {manualActionCarriers.length > 0 ? (
              <svg className="w-3.5 h-3.5 animate-pulse" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            ) : (
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a9 9 0 11-18 0V5.25" />
              </svg>
            )}
            {manualActionCarriers.length > 0
              ? `⚠️ Solve CAPTCHA (${manualActionCarriers.map((c) => c.name).join(", ")})`
              : isSearching
                ? "🔴 Live Browser Tabs"
                : "Live Browser Tabs"}
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
            animate-slide-up
          "
        >
          {/* Panel Header & Tabs */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-slate-300 dark:border-white/10 bg-slate-200 dark:bg-white/[0.03]">
            {carriers.length > 0 ? (
              /* Multi-Tab Layout */
              <div className="flex items-center gap-1">
                {carriers.map((carrier) => {
                  const isActive = activeTab === carrier.code;
                  const needsAction = manualActionCarriers.some((c) => c.code === carrier.code);
                  return (
                    <button
                      key={carrier.code}
                      onClick={() => setActiveTab(carrier.code)}
                      className={`
                        px-3 py-1.5 rounded-lg text-xs font-semibold
                        transition-all duration-200 flex items-center gap-2 border-b-2 btn-interactive
                        ${
                          needsAction
                            ? "border-amber-500 bg-amber-500/10 text-amber-600 dark:text-amber-400 animate-pulse font-bold"
                            : getBrandColorStyles(carrier.code, isActive)
                        }
                      `}
                    >
                      <span className={`w-2 h-2 rounded-full ${needsAction ? "bg-amber-500 dark:bg-amber-400 animate-ping" : getIndicatorStyle(carrier.code)}`} />
                      {needsAction ? `⚠️ ${carrier.name}` : carrier.name}
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

          {/* Action Required Banner */}
          {manualActionCarriers.length > 0 && (
            <div className="bg-amber-500/15 dark:bg-amber-500/10 border-b border-amber-500/30 px-4 py-2.5 flex items-center gap-2 text-xs text-amber-800 dark:text-amber-400 animate-shake">
              <svg className="w-4 h-4 flex-shrink-0 animate-bounce text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>
                <strong>CAPTCHA / Verification Required:</strong> Human intervention is needed on{" "}
                <span className="font-bold underline">
                  {manualActionCarriers.map((c) => c.name).join(", ")}
                </span>
                . Select the active tab(s) below and solve the challenge inside the display.
              </span>
            </div>
          )}

          {/* VNC iframes (mounted concurrently to maintain state, but toggled via css visibility) */}
          <div className="flex-1 relative bg-white dark:bg-black">
            {carriers.length > 0 ? (
              carriers.map((carrier) => {
                const isActive = activeTab === carrier.code;
                const backendKey = getBackendCarrierKey(carrier.code);
                const result = results?.find((r) => r.carrier === backendKey);
                const status = result?.status;
                const isDismissed = dismissedOverlays[carrier.code];

                // Determine overlay content
                let overlayContent = null;
                if (!isSearching) {
                  overlayContent = {
                    title: "System Idle",
                    desc: "Start a new rate search to watch the live carrier portal browser automation.",
                    icon: (
                      <svg className="w-10 h-10 text-slate-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
                      </svg>
                    ),
                    spinner: false
                  };
                } else if (results && results.length > 0 && !result) {
                  overlayContent = {
                    title: "Not Selected",
                    desc: `${carrier.name} was not selected for this rate search.`,
                    icon: (
                      <svg className="w-10 h-10 text-slate-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                      </svg>
                    ),
                    spinner: false
                  };
                } else if (status === "QUEUED") {
                  overlayContent = {
                    title: "Sourcing is Queued",
                    desc: "We limit concurrent carrier browsers to prevent resource overload. Sourcing for this carrier will start automatically once a slot becomes available.",
                    icon: null,
                    spinner: true
                  };
                } else if (status && ["COMPLETED", "AVAILABLE_QUOTES_FOUND", "NO_QUOTES_AVAILABLE", "FAILED", "LOGIN_FAILED", "CONNECTOR_NOT_AVAILABLE", "TIMEOUT", "UNKNOWN_ERROR", "EXTRACTION_FAILED", "INVALID_SEARCH_INPUT", "CARRIER_SITE_CHANGED"].includes(status)) {
                  overlayContent = {
                    title: "Sourcing Finished",
                    desc: `Search completed with status: ${status.replace(/_/g, " ")}.`,
                    icon: (
                      <svg className="w-10 h-10 text-emerald-500/80 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ),
                    spinner: false
                  };
                }

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
                    {!isDismissed && overlayContent && (
                      <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/95 text-white z-10 p-6 text-center animate-fade-in">
                        {overlayContent.spinner ? (
                          <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-emerald-500 animate-spin mb-4" />
                        ) : (
                          overlayContent.icon
                        )}
                        <h4 className="text-sm font-semibold mb-1">
                          {overlayContent.title}
                        </h4>
                        <p className="text-xs text-slate-400 max-w-sm mb-4 leading-relaxed">
                          {overlayContent.desc}
                        </p>
                        <button
                          onClick={() => setDismissedOverlays(prev => ({ ...prev, [carrier.code]: true }))}
                          className="px-3 py-1.5 bg-white/10 hover:bg-white/20 active:bg-white/30 rounded-lg text-[10px] font-medium transition-colors border border-white/5"
                        >
                          Dismiss Overlay
                        </button>
                      </div>
                    )}
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
