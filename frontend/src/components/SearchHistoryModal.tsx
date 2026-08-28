"use client";
import { useState, useEffect } from "react";
import { 
  History, 
  Search, 
  Download, 
  ExternalLink, 
  X, 
  RefreshCw, 
  Ship, 
  Calendar, 
  Box, 
  CheckCircle2, 
  AlertCircle, 
  User as UserIcon,
  CheckSquare,
  Square
} from "lucide-react";
import { getSearchHistory, getRateSearchResults } from "@/lib/api";
import { exportMultiRouteResultsToExcel, type BatchRouteResult } from "@/lib/excelExport";
import type { RateSearchResultResponse } from "@/lib/types";
import { toast } from "sonner";

interface SearchHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  userName: string | null;
  onSelectSearch: (result: RateSearchResultResponse) => void;
}

export interface SearchHistoryItem {
  id: string;
  user_name: string;
  created_at: string;
  origin: string;
  destination: string;
  container_type: string;
  container_quantity: number;
  weight_per_container_kg: number;
  commodity: string;
  departure_date: string;
  selected_carriers: string[];
  status: string;
  total_quotes: number;
  carrier_results: Array<{
    carrier: string;
    status: string;
    error_message?: string;
    quotes_count: number;
  }>;
}

export default function SearchHistoryModal({
  isOpen,
  onClose,
  userName,
  onSelectSearch,
}: SearchHistoryModalProps) {
  const [historyItems, setHistoryItems] = useState<SearchHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [showOnlyMySearches, setShowOnlyMySearches] = useState(true);
  const [exportingId, setExportingId] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [batchExporting, setBatchExporting] = useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const filterUser = showOnlyMySearches && userName ? userName : undefined;
      const data = await getSearchHistory(filterUser);
      setHistoryItems(data || []);
    } catch (err: any) {
      console.error("Failed to load search history:", err);
      toast.error(err.message || "Failed to load search history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen, showOnlyMySearches]);

  if (!isOpen) return null;

  const filteredItems = historyItems.filter((item) => {
    if (!searchFilter.trim()) return true;
    const query = searchFilter.toLowerCase();
    return (
      item.origin.toLowerCase().includes(query) ||
      item.destination.toLowerCase().includes(query) ||
      item.commodity.toLowerCase().includes(query) ||
      item.container_type.toLowerCase().includes(query) ||
      item.user_name.toLowerCase().includes(query) ||
      (item.selected_carriers && item.selected_carriers.some(c => c.toLowerCase().includes(query)))
    );
  });

  const handleRetrieveSearch = async (item: SearchHistoryItem) => {
    try {
      toast.loading(`Retrieving search results for ${item.origin} ➔ ${item.destination}...`, { id: "retrieve-search" });
      const fullResult = await getRateSearchResults(item.id);
      toast.success(`Loaded rates for ${item.origin} ➔ ${item.destination}`, { id: "retrieve-search" });
      onSelectSearch(fullResult);
      onClose();
    } catch (err: any) {
      toast.error(`Failed to load search details: ${err.message}`, { id: "retrieve-search" });
    }
  };

  const handleExportSingle = async (e: React.MouseEvent, item: SearchHistoryItem) => {
    e.stopPropagation();
    setExportingId(item.id);
    try {
      toast.loading(`Fetching rates for Excel export (${item.origin} ➔ ${item.destination})...`, { id: "export-single" });
      const fullResult = await getRateSearchResults(item.id);
      const safeOrig = (item.origin || "Origin").replace(/[^a-zA-Z0-9]/g, "_");
      const safeDest = (item.destination || "Destination").replace(/[^a-zA-Z0-9]/g, "_");
      await exportMultiRouteResultsToExcel([
        {
          origin: fullResult.origin || item.origin,
          destination: fullResult.destination || item.destination,
          status: "completed",
          searchResult: fullResult,
        }
      ], `Infreight_${safeOrig}_to_${safeDest}_Rates.xlsx`);
      toast.success(`Excel export downloaded for ${item.origin} ➔ ${item.destination}!`, { id: "export-single" });
    } catch (err: any) {
      toast.error(`Failed to export to Excel: ${err.message}`, { id: "export-single" });
    } finally {
      setExportingId(null);
    }
  };

  const toggleSelectId = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredItems.length && filteredItems.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredItems.map((i) => i.id)));
    }
  };

  const handleBatchExportSelected = async () => {
    if (selectedIds.size === 0) return;
    setBatchExporting(true);
    try {
      toast.loading(`Preparing batch Excel export for ${selectedIds.size} searches...`, { id: "batch-export" });
      const selectedList = filteredItems.filter((item) => selectedIds.has(item.id));
      
      const batchRouteResults: BatchRouteResult[] = await Promise.all(
        selectedList.map(async (item) => {
          try {
            const fullRes = await getRateSearchResults(item.id);
            return {
              origin: item.origin,
              destination: item.destination,
              status: "completed" as const,
              searchResult: fullRes,
            };
          } catch {
            return {
              origin: item.origin,
              destination: item.destination,
              status: "failed" as const,
              searchResult: null,
            };
          }
        })
      );

      exportMultiRouteResultsToExcel(batchRouteResults);
      toast.success(`Batch Excel workbook exported successfully for ${selectedIds.size} routes!`, { id: "batch-export" });
    } catch (err: any) {
      toast.error(`Batch export failed: ${err.message}`, { id: "batch-export" });
    } finally {
      setBatchExporting(false);
    }
  };

  const formatDate = (isoStr: string) => {
    if (!isoStr) return "N/A";
    try {
      const d = new Date(isoStr);
      return d.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/60 backdrop-blur-md animate-blur-in p-4 overflow-y-auto">
      <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl w-full max-w-5xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] my-auto animate-scale-in-spring">
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-200 dark:border-gray-800 flex items-center justify-between flex-wrap gap-4 bg-slate-50/50 dark:bg-white/[0.02]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-blue-500/10 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center border border-blue-500/20">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                Rate Search History
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                  {filteredItems.length} Searches
                </span>
              </h2>
              <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">
                Access your past ocean freight rate queries, retrieve live breakdown tables, and export to Excel (.xlsx).
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchHistory}
              disabled={loading}
              className="p-2.5 rounded-xl border border-slate-200 dark:border-white/10 text-slate-600 dark:text-gray-300 hover:bg-slate-100 dark:hover:bg-white/5 transition-all text-xs font-medium flex items-center gap-1.5 cursor-pointer"
              title="Refresh Search History"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              <span>Refresh</span>
            </button>
            <button
              onClick={onClose}
              className="p-2.5 rounded-xl border border-slate-200 dark:border-white/10 text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Toolbar & Filter Controls */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-gray-800 bg-white dark:bg-[#121212] flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3 flex-1 min-w-[280px]">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                placeholder="Filter by origin, destination, commodity, container type, carrier..."
                className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              />
              {searchFilter && (
                <button
                  onClick={() => setSearchFilter("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-white text-xs"
                >
                  Clear
                </button>
              )}
            </div>

            {userName && (
              <div className="flex items-center bg-slate-100 dark:bg-white/5 p-1 rounded-xl border border-slate-200 dark:border-white/10">
                <button
                  onClick={() => setShowOnlyMySearches(true)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    showOnlyMySearches
                      ? "bg-white dark:bg-blue-600 text-slate-900 dark:text-white shadow-sm font-semibold"
                      : "text-slate-500 dark:text-gray-400 hover:text-slate-800 dark:hover:text-white"
                  }`}
                >
                  My Searches ({userName})
                </button>
                <button
                  onClick={() => setShowOnlyMySearches(false)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    !showOnlyMySearches
                      ? "bg-white dark:bg-blue-600 text-slate-900 dark:text-white shadow-sm font-semibold"
                      : "text-slate-500 dark:text-gray-400 hover:text-slate-800 dark:hover:text-white"
                  }`}
                >
                  All Team Searches
                </button>
              </div>
            )}
          </div>

          {/* Selection Actions & Batch Export */}
          <div className="flex items-center gap-3">
            <button
              onClick={toggleSelectAll}
              className="text-xs text-slate-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium flex items-center gap-1.5 cursor-pointer"
            >
              {selectedIds.size === filteredItems.length && filteredItems.length > 0 ? (
                <CheckSquare className="w-4 h-4 text-blue-500" />
              ) : (
                <Square className="w-4 h-4 text-slate-400" />
              )}
              <span>
                {selectedIds.size === filteredItems.length && filteredItems.length > 0
                  ? "Deselect All"
                  : `Select All (${filteredItems.length})`}
              </span>
            </button>

            {selectedIds.size > 0 && (
              <button
                onClick={handleBatchExportSelected}
                disabled={batchExporting}
                className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl text-xs shadow-md transition-all flex items-center gap-2 cursor-pointer btn-interactive"
              >
                <Download className="w-4 h-4" />
                <span>
                  {batchExporting ? "Exporting Batch..." : `Export Selected (${selectedIds.size}) to Excel`}
                </span>
              </button>
            )}
          </div>
        </div>

        {/* History Item List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {loading ? (
            <div className="py-16 text-center text-slate-400 dark:text-gray-500 space-y-3">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500" />
              <p className="text-sm font-medium">Loading search history...</p>
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="py-16 text-center text-slate-400 dark:text-gray-500 space-y-3">
              <Ship className="w-12 h-12 mx-auto text-slate-300 dark:text-gray-600" />
              <p className="text-base font-semibold text-slate-700 dark:text-gray-300">No Rate Searches Found</p>
              <p className="text-xs max-w-sm mx-auto text-slate-500 dark:text-gray-400">
                {searchFilter
                  ? `No search history matching "${searchFilter}". Try clearing filters.`
                  : "You haven't run any rate searches yet. Start a search on the home page!"}
              </p>
            </div>
          ) : (
            filteredItems.map((item) => {
              const isSelected = selectedIds.has(item.id);
              const isExportingThis = exportingId === item.id;
              const hasQuotes = item.total_quotes > 0;

              return (
                <div
                  key={item.id}
                  onClick={() => handleRetrieveSearch(item)}
                  className={`group relative bg-white dark:bg-white/[0.02] border rounded-2xl p-4 transition-all duration-200 hover:shadow-lg cursor-pointer flex flex-col gap-3 ${
                    isSelected
                      ? "border-blue-500 ring-2 ring-blue-500/20 bg-blue-50/20 dark:bg-blue-500/[0.04]"
                      : "border-slate-200 dark:border-gray-800/80 hover:border-blue-400/50 dark:hover:border-blue-500/40"
                  }`}
                >
                  {/* Top Line: User, Date, Status */}
                  <div className="flex items-center justify-between flex-wrap gap-2 text-xs">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => toggleSelectId(e, item.id)}
                        className="text-slate-400 hover:text-blue-500 transition-colors p-0.5"
                      >
                        {isSelected ? (
                          <CheckSquare className="w-4 h-4 text-blue-500" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-300 dark:text-gray-600" />
                        )}
                      </button>
                      <div className="flex items-center gap-1.5 text-slate-600 dark:text-gray-300 font-medium">
                        <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                        <span>{item.user_name}</span>
                      </div>
                      <span className="text-slate-300 dark:text-gray-700">•</span>
                      <div className="flex items-center gap-1 text-slate-400 font-mono">
                        <Calendar className="w-3.5 h-3.5" />
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold font-mono border ${
                          item.status === "COMPLETED"
                            ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                            : item.status === "RUNNING"
                            ? "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20 animate-pulse"
                            : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"
                        }`}
                      >
                        {item.status} ({item.total_quotes} Quotes Found)
                      </span>
                    </div>
                  </div>

                  {/* Route & Cargo Specs */}
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                        <Ship className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                          <span>{item.origin}</span>
                          <span className="text-blue-500 font-mono text-sm">➔</span>
                          <span>{item.destination}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-500 dark:text-gray-400 font-mono flex-wrap">
                          <span className="flex items-center gap-1 font-semibold text-slate-700 dark:text-gray-300">
                            <Box className="w-3.5 h-3.5 text-blue-500" />
                            {item.container_type || "20GP, 40HQ"}
                          </span>
                          <span>•</span>
                          <span>{item.weight_per_container_kg ? `${item.weight_per_container_kg.toLocaleString()} kg` : "20,000 kg"}</span>
                          <span>•</span>
                          <span className="truncate max-w-[200px]">{item.commodity || "FAK"}</span>
                        </div>
                      </div>
                    </div>

                    {/* Quick Action Buttons */}
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => handleExportSingle(e, item)}
                        disabled={isExportingThis}
                        className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-emerald-500/10 hover:text-emerald-600 dark:hover:text-emerald-400 border border-slate-200 dark:border-white/10 hover:border-emerald-500/30 text-slate-700 dark:text-gray-200 text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer"
                        title="Export this search result to Excel (.xlsx)"
                      >
                        <Download className={`w-3.5 h-3.5 ${isExportingThis ? "animate-bounce" : ""}`} />
                        <span>{isExportingThis ? "Exporting..." : "Export to Excel"}</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleRetrieveSearch(item)}
                        className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md transition-all flex items-center gap-1.5 cursor-pointer btn-interactive"
                      >
                        <span>View Results</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Carrier Results Breakdown Badges */}
                  {item.carrier_results && item.carrier_results.length > 0 && (
                    <div className="pt-2 border-t border-slate-100 dark:border-white/5 flex items-center gap-1.5 flex-wrap text-[11px]">
                      <span className="text-slate-400 font-mono mr-1">Carriers:</span>
                      {item.carrier_results.map((cr, idx) => {
                        const isSucc = cr.quotes_count > 0 || cr.status === "AVAILABLE_QUOTES_FOUND";
                        return (
                          <span
                            key={idx}
                            className={`px-2 py-0.5 rounded-lg border font-mono flex items-center gap-1 ${
                              isSucc
                                ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-medium"
                                : "bg-slate-100 dark:bg-white/5 border-slate-200 dark:border-white/10 text-slate-500"
                            }`}
                          >
                            <span>{cr.carrier}</span>
                            <span className="font-bold">({cr.quotes_count})</span>
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 dark:border-gray-800 bg-slate-50/50 dark:bg-white/[0.02] flex items-center justify-between flex-wrap gap-4 text-xs text-slate-500 dark:text-gray-400">
          <div>
            Showing <strong className="text-slate-900 dark:text-white">{filteredItems.length}</strong> rate search queries from database.
          </div>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-200 dark:bg-white/10 hover:bg-slate-300 dark:hover:bg-white/20 text-slate-700 dark:text-white font-semibold transition-all cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
