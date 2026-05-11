"use client";
import { useState, useEffect } from "react";
import RateSearchForm from "@/components/RateSearchForm";
import ResultsTable from "@/components/ResultsTable";
import LoadingState from "@/components/LoadingState";
import StatusBadge from "@/components/StatusBadge";
import { createRateSearch, pollRateSearch, healthCheck } from "@/lib/api";
import type { RateSearchRequest, RateSearchResultResponse } from "@/lib/types";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [searchResult, setSearchResult] = useState<RateSearchResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mockMode, setMockMode] = useState<boolean | null>(null);
  const [searchId, setSearchId] = useState<string | null>(null);

  // Check backend health on mount
  useEffect(() => {
    healthCheck()
      .then((h) => setMockMode(h.mock_mode))
      .catch(() => setMockMode(null));
  }, []);

  const handleSearch = async (request: RateSearchRequest) => {
    setIsLoading(true);
    setError(null);
    setSearchResult(null);
    setSearchId(null);

    try {
      const { search_id } = await createRateSearch(request);
      setSearchId(search_id);

      // Poll for results
      await pollRateSearch(search_id, (data) => {
        setSearchResult(data);
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative z-10 min-h-screen">
      {/* Header */}
      <header className="border-b border-white/10 bg-white/[0.02] backdrop-blur-xl sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-blue-500/20">
              IF
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">
                Infreight Ocean Carrier Rate Search
              </h1>
              <p className="text-xs text-white/40">Automated freight quotation comparison</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {mockMode !== null && (
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                mockMode
                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${mockMode ? "bg-amber-400" : "bg-emerald-400"}`} />
                {mockMode ? "Mock Mode" : "Live Mode"}
              </span>
            )}
            {searchId && <StatusBadge status={searchResult?.status || "QUEUED"} size="md" />}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Search Form Card */}
        <section className="bg-white/[0.03] border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
          <div className="flex items-center gap-2 mb-5">
            <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <h2 className="text-base font-semibold text-white">Search Parameters</h2>
          </div>
          <RateSearchForm onSubmit={handleSearch} isLoading={isLoading} />
        </section>

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 text-red-300 text-sm">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Loading */}
        {isLoading && !searchResult && <LoadingState />}

        {/* Results */}
        {searchResult && (
          <section className="animate-in">
            <ResultsTable data={searchResult} />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-xs text-white/30">
          Infreight Logistics — Ocean Carrier Rate Automation System
        </div>
      </footer>
    </div>
  );
}
