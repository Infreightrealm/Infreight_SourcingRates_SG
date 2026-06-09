"use client";
import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import RateSearchForm from "@/components/RateSearchForm";
import ResultsTable from "@/components/ResultsTable";
import LoadingState from "@/components/LoadingState";
import StatusBadge from "@/components/StatusBadge";
import VncViewer from "@/components/VncViewer";
import ChatWidget from "@/components/ChatWidget";
import SelfHealingAlerts from "@/components/SelfHealingAlerts";
import { ThemeToggle } from "@/components/ThemeToggle";
import { createRateSearch, pollRateSearch, healthCheck, getRateSearchResults } from "@/lib/api";
import type { RateSearchRequest, RateSearchResultResponse } from "@/lib/types";
import { toast } from "sonner";

function HomeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [searchResult, setSearchResult] = useState<RateSearchResultResponse | null>(null);
  const [mockMode, setMockMode] = useState<boolean | null>(null);
  const [searchId, setSearchId] = useState<string | null>(searchParams.get("id"));

  let backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  if (backendUrl && !backendUrl.startsWith("http://") && !backendUrl.startsWith("https://")) {
    backendUrl = `https://${backendUrl}`;
  }

  // Check backend health on mount
  useEffect(() => {
    healthCheck()
      .then((h) => setMockMode(h.mock_mode))
      .catch(() => setMockMode(null));
  }, []);

  // Resume polling if searchId is in URL on mount
  useEffect(() => {
    const id = searchParams.get("id");
    if (id && !searchResult && !isLoading) {
      setIsLoading(true);
      // Fetch initial data then start polling
      getRateSearchResults(id)
        .then(data => {
          setSearchResult(data);
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
  }, []);

  const handleSearch = async (request: RateSearchRequest) => {
    setIsLoading(true);
    setSearchResult(null);
    toast.info("Starting rate search...");
    
    try {
      const { search_id } = await createRateSearch(request);
      setSearchId(search_id);
      
      // Update URL without refreshing
      router.push(`/?id=${search_id}`, { scroll: false });

      // Poll for results
      await pollRateSearch(search_id, (data) => {
        setSearchResult(data);
      });
      toast.success("Rate search finished!");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "An error occurred";
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative z-10 min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-200 dark:border-white/10 bg-white/70 dark:bg-white/[0.02] backdrop-blur-xl sticky top-0 z-30 transition-colors">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-blue-500/20">
              IF
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                Infreight Ocean Carrier Rate Search
              </h1>
              <p className="text-xs text-slate-500 dark:text-white/40">Automated freight quotation comparison</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {searchId && (
              <button
                onClick={() => {
                  setSearchId(null);
                  setSearchResult(null);
                  router.push("/");
                }}
                className="px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-white font-medium text-xs transition-all duration-200"
              >
                🔄 New Search
              </button>
            )}
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
            {searchId && <StatusBadge status={searchResult?.status || "QUEUED"} size="md" />}
            
            <div className="w-px h-6 bg-slate-200 dark:bg-white/10 mx-1"></div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8 flex-1 w-full">
        {/* Self-Healing alerts / approvals */}
        <SelfHealingAlerts backendUrl={backendUrl} isSearching={isLoading} />

        {/* Search Form Card */}
        <section className="bg-white/60 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 rounded-2xl p-6 backdrop-blur-sm transition-colors shadow-sm">
          <div className="flex items-center gap-2 mb-5">
            <svg className="w-5 h-5 text-blue-500 dark:text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <h2 className="text-base font-semibold text-slate-900 dark:text-white">Search Parameters</h2>
          </div>
          <RateSearchForm key={searchId || "new"} onSubmit={handleSearch} isLoading={isLoading} />
        </section>

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
        <div className="max-w-7xl mx-auto px-6 text-center text-xs text-slate-500 dark:text-white/30">
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
