"use client";
import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import RateSearchForm from "@/components/RateSearchForm";
import RfqInputSection from "@/components/RfqInputSection";
import ResultsTable from "@/components/ResultsTable";
import LoadingState from "@/components/LoadingState";
import StatusBadge from "@/components/StatusBadge";
import VncViewer from "@/components/VncViewer";
import ChatWidget from "@/components/ChatWidget";
import SelfHealingAlerts from "@/components/SelfHealingAlerts";
import { ThemeToggle } from "@/components/ThemeToggle";
import { SearchCompletionModal } from "@/components/SearchCompletionModal";
import LoginModal from "@/components/LoginModal";
import { createRateSearch, createBatchRateSearch, pollRateSearch, pollBatchSearchStatus, healthCheck, getRateSearchResults, getApiUrl, getPrimaryApiUrl, registerUrlSwitchCallback, releaseRateSearch, forceRestorePrimary } from "@/lib/api";
import type { RateSearchRequest, RateSearchResultResponse } from "@/lib/types";
import { exportMultiRouteResultsToExcel, exportTariffMatrixToExcel, type BatchRouteResult } from "@/lib/excelExport";
import SearchHistoryModal from "@/components/SearchHistoryModal";
import BackendConfigModal from "@/components/BackendConfigModal";
import { toast } from "sonner";

function HomeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [searchResult, setSearchResult] = useState<RateSearchResultResponse | null>(null);
  const [mockMode, setMockMode] = useState<boolean | null>(null);
  const [searchId, setSearchId] = useState<string | null>(searchParams.get("id"));
  const [userName, setUserName] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);
  const [backendUrl, setBackendUrl] = useState(getApiUrl());
  const [isBackendModalOpen, setIsBackendModalOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [parsedRfqFields, setParsedRfqFields] = useState<RateSearchRequest | undefined>(undefined);

  // Continuous Batch Multi-Route Execution State
  const [batchResults, setBatchResults] = useState<BatchRouteResult[]>([]);
  const [isBatchRunning, setIsBatchRunning] = useState(false);
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0 });
  const [selectedCarriers, setSelectedCarriers] = useState<string[]>(["ALL"]);



  // Check backend health and sync user session on mount
  useEffect(() => {
    setIsClient(true);
    const savedName = localStorage.getItem("userName");
    if (savedName) {
      setUserName(savedName);
      import("@/lib/api").then(({ validateSession }) => {
        validateSession(savedName).catch((err: any) => {
          console.warn("Failed to validate user session:", err);
          localStorage.removeItem("userName");
          setUserName("");
          toast.info("User sessions were reset by admin. Please enter your name to log in.");
        });
      });
    }

    let lastToastedUrl: string | null = null;
    registerUrlSwitchCallback((newUrl, isRestored, reason) => {
      setBackendUrl(newUrl);
      if (lastToastedUrl === newUrl) return;
      lastToastedUrl = newUrl;
      if (isRestored) {
        toast.success(`Primary Local Backend is BACK ONLINE! Restored connection: ${newUrl}`, {
          duration: 6000,
        });
      } else {
        toast.warning(`Primary backend unreachable. Auto-switched to Cloud Backup: ${newUrl}`, {
          duration: 6000,
          description: reason ? `Reason: ${reason}` : undefined,
        });
      }
    });

    healthCheck()
      .then((h) => setMockMode(h.mock_mode))
      .catch(() => setMockMode(null));
  }, []);

  // Resume polling or restore batch results if search_ids or id is in URL on mount
  useEffect(() => {
    const rawSearchIds = searchParams.get("search_ids");
    if (rawSearchIds && !isBatchRunning && batchResults.length === 0) {
      const searchIds = rawSearchIds.split(",").map(s => s.trim()).filter(Boolean);
      if (searchIds.length > 0) {
        setIsBatchRunning(true);
        setIsLoading(true);

        Promise.all(searchIds.map(sId => getRateSearchResults(sId).catch(() => null)))
          .then(results => {
            const initialResults: BatchRouteResult[] = results.map((res, idx) => {
              const orig = res?.origin || `Route #${idx + 1}`;
              const dest = res?.destination || `Destination #${idx + 1}`;
              const hasFinishedCarrier = res?.results?.some(r => ["AVAILABLE_QUOTES_FOUND", "NO_QUOTES_AVAILABLE", "COMPLETED", "FAILED"].includes(r.status));
              const isTerminal = res ? (["COMPLETED", "PARTIAL_COMPLETED", "FAILED"].includes(res.status) || hasFinishedCarrier) : false;
              return {
                origin: orig,
                destination: dest,
                status: isTerminal ? "completed" : "running",
                searchResult: res
              };
            });

            setBatchResults(initialResults);
            const initialCompleted = initialResults.filter(r => r.status === "completed").length;
            setBatchProgress({ current: initialCompleted, total: searchIds.length });

            // Resume with ONE batch-status poll per tick (not one poller per route);
            // full results are re-fetched once per route when it turns terminal.
            const indexOf = new Map(searchIds.map((id, i) => [id, i]));
            return pollBatchSearchStatus(
              searchIds,
              (items) => {
                setBatchResults(prev => {
                  const next = prev.map((item, idx) => {
                    const st = items.find(i => indexOf.get(i.search_id) === idx);
                    if (!st || item.status === "completed") return item;
                    return { ...item, status: st.is_terminal ? "completed" as const : "running" as const };
                  });
                  setBatchProgress({ current: next.filter(r => r.status === "completed").length, total: searchIds.length });
                  return next;
                });
              },
              async (searchId) => {
                const idx = indexOf.get(searchId);
                if (idx === undefined) return;
                const data = await getRateSearchResults(searchId).catch(() => null);
                setBatchResults(prev => {
                  const next = prev.map((item, i) =>
                    i === idx ? { ...item, status: "completed" as const, searchResult: data ?? item.searchResult } : item
                  );
                  setBatchProgress({ current: next.filter(r => r.status === "completed").length, total: searchIds.length });
                  return next;
                });
              },
            );
          })
          .then(() => {
            setBatchResults(prev => {
              setBatchProgress({ current: prev.filter(r => r.status === "completed").length, total: prev.length });
              return prev;
            });
          })
          .catch(err => {
            console.warn("Failed to restore batch search:", err);
          })
          .finally(() => {
            setIsLoading(false);
            setIsBatchRunning(false);
          });
      }
    }

    const id = searchParams.get("id");
    if (id && !searchResult && !isLoading && !rawSearchIds) {
      setIsLoading(true);
      getRateSearchResults(id)
        .then(data => {
          setSearchResult(data);
          if (data.origin && data.destination) {
            setParsedRfqFields((prev) => ({
              carriers: prev?.carriers || ["ALL"],
              origin: data.origin!,
              destination: data.destination!,
              container_types: data.container_types || (data.container_type ? [data.container_type] : ["DRY 40H"]),
              container_quantity: 1,
              weight_per_container_kg: prev?.weight_per_container_kg || 20000,
              commodity: "Furniture",
              departure_date: "tomorrow",
              search_window_days: 14,
              service_term: "CY/CY"
            }));
          }
          if (!["COMPLETED", "PARTIAL_COMPLETED", "FAILED"].includes(data.status)) {
            pollRateSearch(id, (updatedData) => {
              setSearchResult(updatedData);
            }).finally(() => setIsLoading(false));
          } else {
            setIsLoading(false);
          }
        })
        .catch(err => {
          toast.error("Could not recover search results: " + err.message);
          setIsLoading(false);
        });
    }
  }, [searchParams]);

  const handleSearch = async (request: RateSearchRequest) => {
    setIsLoading(true);
    setSearchResult(null);
    setParsedRfqFields(request); // Retain searched origin & destination in form
    
    // Check if it's an "All Carrier" search or many carriers
    if (request.carriers.includes("ALL") || request.carriers.length > 3) {
      toast.info("Concurrency Limit Active", {
        description: "To prevent server crashes and anti-bot blocks, we are processing carriers in batches of 3. Hapag-Lloyd and ONE are prioritized first!",
        duration: 8000,
      });
    } else {
      toast.info("Starting rate search...");
    }
    
    try {
      const payload = { ...request, user_name: userName || undefined };
      const { search_id } = await createRateSearch(payload);
      setSearchId(search_id);
      
      // Update URL without refreshing
      router.push(`/?id=${search_id}`, { scroll: false });

      // Poll for results
      await pollRateSearch(search_id, (data) => {
        setSearchResult(data);
        if (data.origin && data.destination) {
          setParsedRfqFields((prev) => ({
            carriers: prev?.carriers || request.carriers,
            origin: data.origin!,
            destination: data.destination!,
            container_types: data.container_types || (data.container_type ? [data.container_type] : ["DRY 40H"]),
            container_quantity: 1,
            weight_per_container_kg: prev?.weight_per_container_kg || request.weight_per_container_kg,
            commodity: "Furniture",
            departure_date: "tomorrow",
            search_window_days: 14,
            service_term: "CY/CY"
          }));
        }
      });
      toast.success("Rate search finished!");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "An error occurred";
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBatchRunAll = async (
    allPairs: Array<{ origin: string; destination: string; container_types?: string[]; weight_per_container_kg?: number }>,
    searchMode: 'quick' | 'detailed' = 'quick'
  ) => {
    if (!allPairs || allPairs.length === 0) return;

    // Clear previous search_ids query parameter from URL and clear previous search result state
    if (typeof window !== "undefined") {
      window.history.pushState(null, "", window.location.pathname);
    }
    setSearchResult(null);

    // Deduplicate pairs by origin + destination
    const uniquePairs: Array<{ origin: string; destination: string; container_types?: string[]; weight_per_container_kg?: number }> = [];
    const seenKeys = new Set<string>();
    for (const p of allPairs) {
      const key = `${(p.origin || "").trim().toLowerCase()}___${(p.destination || "").trim().toLowerCase()}`;
      if (!seenKeys.has(key)) {
        seenKeys.add(key);
        uniquePairs.push(p);
      }
    }

    // Support up to 200 unique route pairs per inquiry batch (comfortably covers 168 port pairs)
    const cappedPairs = uniquePairs.slice(0, 200);

    if (uniquePairs.length > 200) {
      toast.warning(`🛡️ Anti-Bot Safety Cap: Processing first 200 routes (out of ${uniquePairs.length} total) to maintain carrier compliance.`);
    }

    setIsBatchRunning(true);
    setBatchProgress({ current: 0, total: cappedPairs.length });

    const initialBatch: BatchRouteResult[] = cappedPairs.map(p => ({
      origin: p.origin,
      destination: p.destination,
      status: "running"
    }));
    setBatchResults(initialBatch);

    const activeCarriers = selectedCarriers.length > 0 ? selectedCarriers : ["ALL"];
    const carrierLabel = activeCarriers.includes("ALL") ? "All 7 Carriers" : activeCarriers.join(", ");
    const modeLabel = searchMode === 'quick' ? '⚡ Quick Cheapest-in-14d Mode' : '🔍 Detailed All-Quotes Mode';

    toast.info(`⚡ PERSISTENT BATCH ENGINE ACTIVATED (${modeLabel}): Sourcing ${cappedPairs.length} routes for [${carrierLabel}]...`);

    try {
      const batchRes = await createBatchRateSearch({
        routes: cappedPairs,
        carriers: activeCarriers,
        user_name: userName || undefined,
        search_mode: searchMode,
        commodity: "Furniture"
      });

      const searchIds = batchRes.search_ids;

      // Update browser URL query params so batch results persist across page refresh!
      if (typeof window !== "undefined" && searchIds.length > 0) {
        const newUrl = `${window.location.pathname}?search_ids=${searchIds.join(",")}`;
        window.history.pushState({ path: newUrl }, "", newUrl);
      }

      if (batchRes.deduplicated_routes) {
        toast.info(`Collapsed ${batchRes.deduplicated_routes} duplicate route(s) that resolved to the same port pair.`);
      }
      for (const w of batchRes.warnings || []) {
        toast.warning(w);
      }

      // ONE batch-status poll per tick (not one poller per route), bounded by wall
      // clock, not attempt count. Full results are fetched once per route, the first
      // time that route is seen terminal.
      // Rows must follow the BACKEND's search order: it de-duplicates routes by
      // LOCODE pair, so search_ids can be fewer than cappedPairs and index-aligning
      // the two would mislabel rows. Seed one row per search_id and fill names from
      // the status feed.
      const indexOf = new Map(searchIds.map((id, i) => [id, i]));
      setBatchResults(searchIds.map((_, i) => ({
        origin: cappedPairs[i]?.origin ?? `Route #${i + 1}`,
        destination: cappedPairs[i]?.destination ?? `Destination #${i + 1}`,
        status: "running" as const,
      })));
      setBatchProgress({ current: 0, total: searchIds.length });
      await pollBatchSearchStatus(
        searchIds,
        (items) => {
          setBatchResults(prev => {
            const next = prev.map((item, idx) => {
              const st = items.find(i => indexOf.get(i.search_id) === idx);
              if (!st) return item;
              const named = { ...item, origin: st.origin || item.origin, destination: st.destination || item.destination };
              if (item.status === "completed") return named;
              return { ...named, status: st.is_terminal ? "completed" as const : "running" as const };
            });
            setBatchProgress({ current: next.filter(r => r.status === "completed").length, total: searchIds.length });
            return next;
          });
        },
        async (searchId) => {
          const idx = indexOf.get(searchId);
          if (idx === undefined) return;
          const data = await getRateSearchResults(searchId).catch(() => null);
          setBatchResults(prev => {
            const next = prev.map((item, i) =>
              i === idx ? { ...item, status: "completed" as const, searchResult: data ?? item.searchResult } : item
            );
            setBatchProgress({ current: next.filter(r => r.status === "completed").length, total: searchIds.length });
            return next;
          });
        },
      );
      toast.success(`🎉 Vertical Persistent Batch complete! Successfully processed ${searchIds.length} routes.`);

    } catch (err: any) {
      console.error("Vertical Batch search error:", err);
      toast.error(`Vertical Batch search error: ${err.message || err}`);
    } finally {
      setIsBatchRunning(false);
    }
  };



  return (
    <div className="relative z-10 min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-200 dark:border-white/10 bg-white/70 dark:bg-white/[0.02] backdrop-blur-xl sticky top-0 z-30 transition-colors">
        <div className="max-w-[98%] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-white/80 dark:bg-white/10 p-1 flex items-center justify-center border border-slate-200/80 dark:border-white/15 shadow-sm flex-shrink-0">
              <img
                src="/infreight_logo.png"
                alt="Infreight Logistics"
                className="w-full h-full object-contain"
              />
            </div>


            <div>
              <h1 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                Infreight Ocean & Air Rate Automation
              </h1>
              <p className="text-xs text-slate-500 dark:text-white/40">Automated ocean rate searches & airfreight partner routing</p>

            </div>
          </div>
          <div className="flex items-center gap-3">
            {searchId && (
              <button
                onClick={async () => {
                  try {
                    await releaseRateSearch(searchId);
                  } catch (e) {
                    console.error("Failed to release lock on new search", e);
                  }
                  setSearchId(null);
                  setSearchResult(null);
                  router.push("/");
                }}
                className="px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-white font-medium text-xs transition-all duration-200"
              >
                🔄 New Search
              </button>
            )}
            <button
              onClick={async () => {
                try {
                  const { forceStopSearches } = await import("@/lib/api");
                  await forceStopSearches();
                  toast.success("Searches & Browser Workers forcefully stopped");
                  setSearchId(null);
                  setSearchResult(null);
                  setIsLoading(false);
                  setIsBatchRunning(false);
                  setBatchResults([]);
                  setBatchProgress({ current: 0, total: 0 });
                } catch (e) {
                  toast.error("Failed to stop searches");
                }
              }}
              className="px-3.5 py-1.5 rounded-xl border border-red-200 dark:border-red-900/50 bg-red-50 hover:bg-red-100 dark:bg-red-500/10 dark:hover:bg-red-500/20 text-red-700 dark:text-red-400 font-medium text-xs transition-all duration-200 flex items-center gap-1.5"
              title="Force stop all queued and active searches"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18" />
              </svg>
              Force Stop
            </button>
            {mockMode !== null && (
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                mockMode
                  ? "bg-amber-100 text-amber-700 border border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20"
                  : "bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20"
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${mockMode ? "bg-amber-400" : "bg-emerald-400"}`} />
                {mockMode ? "Mock Mode" : "Live Mode"}
              </span>
            )}
            
            {(() => {
              const isPrimaryActive = backendUrl.toLowerCase().trim() === getPrimaryApiUrl().toLowerCase().trim();
              return (
                <button
                  onClick={() => setIsBackendModalOpen(true)}
                  className={`px-3 py-1 rounded-full border text-xs font-medium transition-all duration-200 flex items-center gap-1.5 cursor-pointer shadow-sm ${
                    isPrimaryActive
                      ? "border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300"
                      : "border-amber-200 dark:border-amber-500/30 bg-amber-50 hover:bg-amber-100 dark:bg-amber-500/10 dark:hover:bg-amber-500/20 text-amber-700 dark:text-amber-300"
                  }`}
                  title="Click to configure backend URL or reconnect to Local/Tunnel Backend"
                >
                  <span className={`w-2 h-2 rounded-full ${isPrimaryActive ? "bg-emerald-500" : "bg-amber-500 animate-pulse"}`} />
                  {isPrimaryActive
                    ? (backendUrl.includes("localhost") || backendUrl.includes("127.0.0.1") ? "Local Backend" : "Local Tunnel Relay")
                    : "Cloud Backup (Configure Server)"
                  }
                </button>
              );
            })()}
            {searchId && <StatusBadge status={searchResult?.status || "QUEUED"} size="md" />}
            
            <button
              onClick={() => setIsHistoryModalOpen(true)}
              className="px-3.5 py-1.5 rounded-xl border border-blue-200 dark:border-blue-500/30 bg-blue-50 hover:bg-blue-100 dark:bg-blue-500/10 dark:hover:bg-blue-500/20 text-blue-700 dark:text-blue-300 font-semibold text-xs transition-all duration-200 flex items-center gap-1.5 shadow-sm cursor-pointer"
              title="View Search History & Export Past Quotes"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>My Searches & History</span>
            </button>
            <div className="w-px h-6 bg-slate-200 dark:bg-white/10 mx-1"></div>
            {userName && (
              <button
                onClick={() => {
                  localStorage.removeItem("userName");
                  setUserName(null);
                }}
                className="group px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-white font-medium text-xs transition-all duration-200 flex items-center gap-1.5 relative overflow-hidden"
                title="Change User / Logout"
              >
                <div className="flex items-center gap-1.5 transition-transform duration-200 group-hover:-translate-y-6">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                  </svg>
                  {userName}
                </div>
                <div className="absolute inset-0 flex items-center justify-center gap-1.5 text-red-500 translate-y-6 transition-transform duration-200 group-hover:translate-y-0">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                  </svg>
                  Logout
                </div>
              </button>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="max-w-[98%] mx-auto px-6 py-8 space-y-8 flex-1 w-full">
        {/* Self-Healing alerts / approvals */}
        <SelfHealingAlerts backendUrl={backendUrl} isSearching={isLoading} />

        {/* AI RFQ Front Door */}
        <RfqInputSection onParsedSuccess={(fields) => setParsedRfqFields(fields)} onBatchRunAll={handleBatchRunAll} selectedCarriers={selectedCarriers} />

        {/* Batch Progress & Excel Export Panel */}
        {batchResults.length > 0 && (
          <section className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-6 backdrop-blur-md animate-fade-in-up space-y-4 shadow-sm">
            <div className="flex items-center justify-between flex-wrap gap-3 border-b border-emerald-500/20 pb-3">
              <div>
                <h3 className="text-base font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-2">
                  <span>⚡ Batch Continuous Search Execution</span>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30">
                    {batchProgress.current} / {batchProgress.total} Routes Processed
                  </span>
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-1">
                  Running sequential searches across all {batchResults.length} port-to-port routes for all ocean carriers.
                </p>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                <button
                  type="button"
                  onClick={() => exportTariffMatrixToExcel(batchResults, "PASIR GUDANG / TG PELEPAS", "Pasir_Gudang_168_Tariff_Rates.xlsx")}
                  className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-bold rounded-xl text-xs shadow-lg shadow-amber-500/25 transition-all flex items-center gap-1.5 btn-interactive cursor-pointer border border-amber-400/50"
                  title="Export rate matrix in the exact EX PASIR GUDANG 1st Half / 2nd Half 20' & 40' layout"
                >
                  <span>📊</span> Export Tariff Rate Sheet (.xlsx)
                </button>

                <button
                  type="button"
                  onClick={() => exportMultiRouteResultsToExcel(batchResults)}
                  className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl text-xs shadow-lg shadow-emerald-500/25 transition-all flex items-center gap-1.5 btn-interactive cursor-pointer"
                >
                  <span>📥</span> Full Multi-Sheet (.xlsx)
                </button>
              </div>
            </div>

            {/* Batch Progress Bar */}
            <div className="w-full bg-slate-200 dark:bg-black/30 rounded-full h-3 overflow-hidden border border-emerald-500/20">
              <div
                className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-300 rounded-full"
                style={{ width: `${batchProgress.total > 0 ? (batchProgress.current / batchProgress.total) * 100 : 0}%` }}
              />
            </div>

            {/* Batch Item Status Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-56 overflow-y-auto pr-1">
              {batchResults.map((item, idx) => {
                let badgeStyle = "bg-slate-100 dark:bg-white/5 border-slate-200 dark:border-white/10 text-slate-500 cursor-pointer hover:scale-[1.02]";
                if (item.status === "running") badgeStyle = "bg-blue-500/20 border-blue-500/40 text-blue-600 dark:text-blue-300 font-bold animate-pulse cursor-pointer hover:scale-[1.02]";
                if (item.status === "completed") badgeStyle = "bg-emerald-500/20 border-emerald-500/40 text-emerald-700 dark:text-emerald-300 font-semibold cursor-pointer hover:scale-[1.02] shadow-sm";
                if (item.status === "failed") badgeStyle = "bg-rose-500/20 border-rose-500/40 text-rose-600 dark:text-rose-400 cursor-pointer hover:scale-[1.02]";

                const isSelected = searchResult && searchResult.destination === item.destination;

                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      if (item.searchResult) {
                        setSearchResult(item.searchResult);
                        toast.info(`Viewing live results for Route #${idx + 1}: ${item.origin} ➔ ${item.destination}`);
                      } else {
                        toast.info(`Route #${idx + 1} (${item.destination}) is currently ${item.status}.`);
                      }
                    }}
                    className={`p-2 rounded-xl border text-[11px] font-mono flex flex-col gap-0.5 text-left transition-all duration-200 ${badgeStyle} ${
                      isSelected ? "ring-2 ring-emerald-500 ring-offset-1 dark:ring-offset-slate-900 scale-[1.02]" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] opacity-70">
                      <span>#{idx + 1}</span>
                      <span>{item.status.toUpperCase()}</span>
                    </div>
                    <div className="truncate font-semibold text-slate-900 dark:text-white">{item.destination}</div>
                    {item.searchResult && item.searchResult.results && (
                      <div className="text-[9px] text-emerald-600 dark:text-emerald-400 font-sans font-medium mt-0.5">
                        {item.searchResult.results.reduce((acc, r) => acc + (r.quotes?.length || 0), 0)} quotes found ➔
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </section>
        )}


        {/* Search Form Card */}
        <section className="bg-white/60 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 rounded-2xl p-6 backdrop-blur-sm transition-colors shadow-sm">
          <div className="flex items-center gap-2 mb-5">
            <svg className="w-5 h-5 text-blue-500 dark:text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <h2 className="text-base font-semibold text-slate-900 dark:text-white">Search Parameters</h2>
          </div>
          <RateSearchForm key={searchId || JSON.stringify(parsedRfqFields) || "new"} onSubmit={handleSearch} isLoading={isLoading} initialValues={parsedRfqFields} selectedCarriers={selectedCarriers} onCarrierChange={setSelectedCarriers} />
        </section>


        {/* Queue Status Overlay */}
        {searchResult && searchResult.status === "QUEUED" && searchResult.queue_position !== undefined && (
          <section className="bg-blue-500/10 border border-blue-500/20 rounded-2xl p-6 backdrop-blur-sm text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="text-xl font-bold text-blue-400 mb-2">
              {searchResult.queue_position > 0 ? `You are #${searchResult.queue_position} in line` : "Your search is starting..."}
            </h3>
            {searchResult.queue_position > 0 && searchResult.active_search_info && (
              <p className="text-slate-400">
                Currently processing: <span className="text-slate-300 font-medium">{searchResult.active_search_info}</span>
              </p>
            )}
            <p className="text-sm text-blue-500/60 mt-4">Please leave this window open. Your search will automatically begin when it's your turn.</p>
          </section>
        )}

        {/* Loading */}
        {isLoading && !searchResult && <LoadingState />}

        {/* Results */}
        {searchResult && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ResultsTable data={searchResult} />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-white/5 py-6 mt-auto transition-colors">
        <div className="max-w-[98%] mx-auto px-6 text-center text-xs text-slate-500 dark:text-white/30">
          Infreight Logistics — Ocean Carrier Rate Automation System
        </div>
      </footer>

      {/* VNC Live Browser Viewer (HITL for 2FA/CAPTCHA) */}
      <VncViewer
        backendUrl={backendUrl}
        isSearching={isLoading}
        results={searchResult?.results || []}
      />
      <ChatWidget backendUrl={backendUrl} />

      {searchId && searchResult && (
        <SearchCompletionModal 
          searchId={searchId} 
          isCompleted={["COMPLETED", "PARTIAL_COMPLETED", "FAILED"].includes(searchResult.status)} 
        />
      )}
      
      {isClient && !userName && (
        <LoginModal 
          onLogin={(name) => {
            localStorage.setItem("userName", name);
            setUserName(name);
          }} 
        />
      )}

      <BackendConfigModal
        isOpen={isBackendModalOpen}
        onClose={() => setIsBackendModalOpen(false)}
        onUrlChanged={(newUrl) => {
          setBackendUrl(newUrl);
          healthCheck().then((h) => setMockMode(h.mock_mode)).catch(() => {});
        }}
      />

      <SearchHistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        userName={userName}
        onSelectSearch={(res) => {
          setSearchResult(res);
          if (res?.search_id) {
            setSearchId(res.search_id);
          }
          const el = document.getElementById("results-section");
          if (el) {
            el.scrollIntoView({ behavior: "smooth" });
          }
        }}
      />
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<LoadingState />}>
      <HomeContent />
    </Suspense>
  );
}
