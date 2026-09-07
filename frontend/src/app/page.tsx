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
import WorkspacePanel from "@/components/WorkspacePanel";
import LaunchIntro from "@/components/LaunchIntro";
import { usePreferences, type SavedLane } from "@/lib/preferences";
import { Card } from "@/components/ui/card";
import { Badge, Dot } from "@/components/ui/badge";
import { Separator, SectionHeading } from "@/components/ui/surfaces";
import {
  Download,
  History,
  LogOut,
  SlidersHorizontal,
  OctagonX,
  RotateCcw,
  Search,
  Table2,
  UserRound,
  Zap,
} from "lucide-react";
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
  const [isWorkspaceOpen, setIsWorkspaceOpen] = useState(false);
  const [introReplayKey, setIntroReplayKey] = useState(0);
  const [formRoute, setFormRoute] = useState<{ origin: string; destination: string; containerTypes: string[]; weightKg: number } | null>(null);
  const { prefs } = usePreferences();
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

  // Stamp workspace appearance on <html> so the token overrides in globals.css
  // apply to every surface, including portalled overlays.
  useEffect(() => {
    const root = document.documentElement;
    root.dataset.accent = prefs.accent;
    root.dataset.density = prefs.density;
  }, [prefs.accent, prefs.density]);

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

  /** Load a pinned lane into the search form. Same shape the RFQ parser emits. */
  const handleSelectLane = (lane: SavedLane) => {
    setParsedRfqFields({
      carriers: selectedCarriers.length ? selectedCarriers : ["ALL"],
      origin: lane.origin,
      destination: lane.destination,
      container_types: lane.containerTypes,
      container_quantity: 1,
      weight_per_container_kg: lane.weightKg,
      commodity: "Furniture",
      departure_date: "tomorrow",
      search_window_days: 14,
      service_term: "CY/CY",
    });
  };

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
      <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur-xl transition-colors supports-[backdrop-filter]:bg-background/65">
        <div className="mx-auto flex max-w-[98%] items-center justify-between gap-4 px-6 py-3.5">
          <div className="flex items-center gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-border bg-card p-1 shadow-panel sm:size-11">
              <img
                src="/infreight_logo.png"
                alt="Infreight Logistics"
                className="h-full w-full object-contain"
              />
            </div>


            <div>
              <h1 className="text-base font-semibold tracking-tight text-foreground sm:text-lg">
                Infreight <span className="text-gradient-brand">Ocean &amp; Air</span> Rate Automation
              </h1>
              <p className="text-xs text-muted-foreground">Automated ocean rate searches &amp; airfreight partner routing</p>

            </div>
          </div>
          <div className="flex flex-wrap items-center justify-end gap-2">
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
                className="btn-interactive inline-flex h-8 items-center gap-1.5 rounded-lg border border-border bg-secondary px-3 text-xs font-medium text-secondary-foreground hover:bg-accent"
              >
                <RotateCcw className="size-3.5" />
                New Search
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
              className="btn-interactive inline-flex h-8 items-center gap-1.5 rounded-lg border border-destructive/25 bg-destructive/10 px-3 text-xs font-medium text-destructive-foreground hover:bg-destructive/16"
              title="Force stop all queued and active searches"
            >
              <OctagonX className="size-3.5" />
              Force Stop
            </button>
            {mockMode !== null && (
              <Badge variant={mockMode ? "warning" : "success"} className="h-8 px-3">
                <Dot pulse={!mockMode} />
                {mockMode ? "Mock Mode" : "Live Mode"}
              </Badge>
            )}
            
            {(() => {
              const isPrimaryActive = backendUrl.toLowerCase().trim() === getPrimaryApiUrl().toLowerCase().trim();
              return (
                <button
                  onClick={() => setIsBackendModalOpen(true)}
                  className={`btn-interactive inline-flex h-8 cursor-pointer items-center gap-1.5 rounded-full border px-3 text-xs font-medium ${
                    isPrimaryActive
                      ? "border-success/25 bg-success/12 text-success-foreground hover:bg-success/20"
                      : "border-warning/30 bg-warning/12 text-warning-foreground hover:bg-warning/20"
                  }`}
                  title="Click to configure backend URL or reconnect to Local/Tunnel Backend"
                >
                  <Dot pulse={!isPrimaryActive} />
                  {isPrimaryActive
                    ? (backendUrl.includes("localhost") || backendUrl.includes("127.0.0.1") ? "Local Backend" : "Local Tunnel Relay")
                    : "Cloud Backup (Configure Server)"
                  }
                </button>
              );
            })()}
            {searchId && <StatusBadge status={searchResult?.status || "QUEUED"} size="md" />}
            
            <button
              onClick={() => setIsWorkspaceOpen(true)}
              className="btn-interactive inline-flex h-8 cursor-pointer items-center gap-1.5 rounded-lg border border-border bg-secondary px-3 text-xs font-medium text-secondary-foreground hover:bg-accent"
              title="Workspace — activity, saved lanes, appearance and panels"
            >
              <SlidersHorizontal className="size-3.5" />
              <span className="hidden sm:inline">Workspace</span>
            </button>
            <button
              onClick={() => setIsHistoryModalOpen(true)}
              className="btn-interactive inline-flex h-8 cursor-pointer items-center gap-1.5 rounded-lg border border-primary/25 bg-primary/10 px-3 text-xs font-semibold text-primary hover:bg-primary/16"
              title="View Search History & Export Past Quotes"
            >
              <History className="size-3.5" />
              <span>My Searches &amp; History</span>
            </button>
            <Separator orientation="vertical" className="mx-1" />
            {userName && (
              <button
                onClick={() => {
                  localStorage.removeItem("userName");
                  setUserName(null);
                }}
                className="group relative inline-flex h-8 items-center gap-1.5 overflow-hidden rounded-lg border border-border bg-secondary px-3 text-xs font-medium text-secondary-foreground transition-colors hover:bg-accent"
                title="Change User / Logout"
              >
                <span className="flex items-center gap-1.5 transition-transform duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:-translate-y-6">
                  <UserRound className="size-3.5" />
                  {userName}
                </span>
                <span className="absolute inset-0 flex translate-y-6 items-center justify-center gap-1.5 text-destructive-foreground transition-transform duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:translate-y-0">
                  <LogOut className="size-3.5" />
                  Logout
                </span>
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
        {prefs.panels.rfq && (
          <RfqInputSection onParsedSuccess={(fields) => setParsedRfqFields(fields)} onBatchRunAll={handleBatchRunAll} selectedCarriers={selectedCarriers} />
        )}

        {/* Batch Progress & Excel Export Panel */}
        {batchResults.length > 0 && (
          <Card variant="success" className="animate-fade-in-up space-y-4 p-6 backdrop-blur-md">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-success/20 pb-3">
              <div>
                <h3 className="flex flex-wrap items-center gap-2 text-sm font-semibold text-foreground">
                  <Zap className="size-4 text-success" />
                  <span>Batch Continuous Search Execution</span>
                  <Badge variant="success" size="sm" className="font-mono">
                    {batchProgress.current} / {batchProgress.total} Routes Processed
                  </Badge>
                </h3>
                <p className="mt-1 text-xs text-muted-foreground">
                  Running sequential searches across all {batchResults.length} port-to-port routes for all ocean carriers.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => exportTariffMatrixToExcel(batchResults, "PASIR GUDANG / TG PELEPAS", "Pasir_Gudang_168_Tariff_Rates.xlsx")}
                  className="btn-interactive inline-flex h-9 cursor-pointer items-center gap-1.5 rounded-lg border border-warning/40 bg-warning/15 px-4 text-xs font-semibold text-warning-foreground hover:bg-warning/25"
                  title="Export rate matrix in the exact EX PASIR GUDANG 1st Half / 2nd Half 20' & 40' layout"
                >
                  <Table2 className="size-3.5" /> Export Tariff Rate Sheet (.xlsx)
                </button>

                <button
                  type="button"
                  onClick={() => exportMultiRouteResultsToExcel(batchResults)}
                  className="btn-interactive shine-on-hover inline-flex h-9 cursor-pointer items-center gap-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 px-4 text-xs font-semibold text-white shadow-lg shadow-emerald-500/25 hover:brightness-110"
                >
                  <Download className="size-3.5" /> Full Multi-Sheet (.xlsx)
                </button>
              </div>
            </div>

            {/* Batch Progress Bar */}
            <div
              className="h-2.5 w-full overflow-hidden rounded-full border border-success/20 bg-muted"
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={batchProgress.total}
              aria-valuenow={batchProgress.current}
              aria-label="Batch search progress"
            >
              <div
                className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
                style={{ width: `${batchProgress.total > 0 ? (batchProgress.current / batchProgress.total) * 100 : 0}%` }}
              />
            </div>

            {/* Batch Item Status Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-56 overflow-y-auto pr-1">
              {batchResults.map((item, idx) => {
                let badgeStyle = "border-border bg-card text-muted-foreground";
                if (item.status === "running") badgeStyle = "border-info/40 bg-info/12 text-info-foreground font-bold animate-pulse";
                if (item.status === "completed") badgeStyle = "border-success/40 bg-success/12 text-success-foreground font-semibold shadow-panel";
                if (item.status === "failed") badgeStyle = "border-destructive/40 bg-destructive/12 text-destructive-foreground";

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
                    className={`card-hover flex cursor-pointer flex-col gap-0.5 rounded-xl border p-2 text-left font-mono text-[11px] ${badgeStyle} ${
                      isSelected ? "ring-2 ring-success ring-offset-1 ring-offset-background" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] opacity-70">
                      <span>#{idx + 1}</span>
                      <span>{item.status.toUpperCase()}</span>
                    </div>
                    <div className="truncate font-semibold text-foreground">{item.destination}</div>
                    {item.searchResult && item.searchResult.results && (
                      <div className="mt-0.5 font-sans text-[9px] font-medium text-success-foreground">
                        {item.searchResult.results.reduce((acc, r) => acc + (r.quotes?.length || 0), 0)} quotes found ➔
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </Card>
        )}


        {/* Search Form Card */}
        <Card variant="glass" className="animate-fade-in-up stagger-1 p-6">
          <SectionHeading
            className="mb-5"
            icon={<Search />}
            title="Search Parameters"
            description="Pick carriers, route and equipment, then run the search."
          />
          <RateSearchForm key={searchId || JSON.stringify(parsedRfqFields) || "new"} onSubmit={handleSearch} isLoading={isLoading} initialValues={parsedRfqFields} selectedCarriers={selectedCarriers} onCarrierChange={setSelectedCarriers} onRouteChange={setFormRoute} />
        </Card>


        {/* Queue Status Overlay */}
        {searchResult && searchResult.status === "QUEUED" && searchResult.queue_position !== undefined && (
          <Card variant="info" className="p-6 text-center backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="mb-2 text-xl font-semibold text-info-foreground">
              {searchResult.queue_position > 0 ? `You are #${searchResult.queue_position} in line` : "Your search is starting…"}
            </h3>
            {searchResult.queue_position > 0 && searchResult.active_search_info && (
              <p className="text-sm text-muted-foreground">
                Currently processing: <span className="font-medium text-foreground">{searchResult.active_search_info}</span>
              </p>
            )}
            <p className="mt-4 text-xs text-muted-foreground">Please leave this window open. Your search will automatically begin when it&apos;s your turn.</p>
          </Card>
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
      <footer className="mt-auto border-t border-border py-6 transition-colors">
        <div className="mx-auto flex max-w-[98%] flex-wrap items-center justify-center gap-x-2 gap-y-1 px-6 text-center text-xs text-muted-foreground">
          <span className="font-medium text-foreground/70">Infreight Logistics</span>
          <span aria-hidden className="text-border">•</span>
          <span>Ocean Carrier Rate Automation System</span>
        </div>
      </footer>

      {/* VNC Live Browser Viewer (HITL for 2FA/CAPTCHA) */}
      {prefs.panels.liveViewer && (
        <VncViewer
          backendUrl={backendUrl}
          isSearching={isLoading}
          results={searchResult?.results || []}
        />
      )}
      {prefs.panels.assistant && <ChatWidget backendUrl={backendUrl} />}

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

      <WorkspacePanel
        isOpen={isWorkspaceOpen}
        onClose={() => setIsWorkspaceOpen(false)}
        userName={userName}
        currentLane={
          formRoute?.origin?.trim() && formRoute?.destination?.trim() ? formRoute : undefined
        }
        onSelectLane={handleSelectLane}
        onReplayIntro={() => setIntroReplayKey((k) => k + 1)}
      />

      {isClient && (
        <LaunchIntro
          key={introReplayKey}
          seen={prefs.introSeen}
          force={introReplayKey > 0}
        />
      )}

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
