"use client";

import { useState, useEffect } from "react";
import { 
  User, Trash2, ShieldCheck, Search, Users, Activity, LogOut, Plus, Globe, 
  Building2, Save, Sliders, RefreshCw, Clock, MapPin, BarChart3, TrendingUp, 
  Award, AlertTriangle, CheckCircle2, DollarSign, Filter, ArrowUpRight, 
  ArrowDownRight, Sparkles, Layers 
} from "lucide-react";
import { API_URL } from "@/lib/api";
import PortAutocomplete from "@/components/PortAutocomplete";
import { toast } from "sonner";

interface UserRecord {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export default function AdminDashboard() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Tabs
  const [activeTab, setActiveTab] = useState<"analytics" | "users" | "ports" | "overrides" | "history" | "route_health" | "exchange_rates">("analytics");

  // Consolidated Analytics state
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [analyticsTimeRange, setAnalyticsTimeRange] = useState<"all" | "30d" | "14d" | "7d" | "today">("all");
  const [analyticsUserFilter, setAnalyticsUserFilter] = useState<string>("all");
  const [analyticsCarrierFilter, setAnalyticsCarrierFilter] = useState<string>("all");
  const [hoveredDay, setHoveredDay] = useState<number | null>(null);
  const [laneSearchQuery, setLaneSearchQuery] = useState<string>("");

  // Ports config state
  const [popularPorts, setPopularPorts] = useState<string[]>([]);
  const [boostedCountries, setBoostedCountries] = useState<string[]>([]);
  const [countriesMap, setCountriesMap] = useState<Record<string, string>>({});

  // Route health matrix state
  const [routeHealth, setRouteHealth] = useState<{ carriers: string[]; routes: any[] } | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(false);

  // Carrier Overrides state
  const [carrierOverrides, setCarrierOverrides] = useState<Record<string, Record<string, string>>>({});
  const [loadingOverrides, setLoadingOverrides] = useState(false);
  const [selectedCarrier, setSelectedCarrier] = useState("maersk");
  const [overrideKey, setOverrideKey] = useState("");
  const [overrideText, setOverrideText] = useState("");
  const [carrierFilter, setCarrierFilter] = useState("all");
  const [overrideSearch, setOverrideSearch] = useState("");

  const [savingConfig, setSavingConfig] = useState(false);
  const [newPortInput, setNewPortInput] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("");

  // User Search History state
  const [searchHistory, setSearchHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyUserFilter, setHistoryUserFilter] = useState("all");
  const [historyQuery, setHistoryQuery] = useState("");

  // Exchange Rates state
  const [exchangeRates, setExchangeRates] = useState<Record<string, { code: string; name: string; rate_per_usd: number; usd_per_unit: number; symbol: string }>>({});
  const [loadingRates, setLoadingRates] = useState(false);
  const [rateInputs, setRateInputs] = useState<Record<string, string>>({});
  const [rateSearch, setRateSearch] = useState("");

  const fetchExchangeRates = async () => {
    setLoadingRates(true);
    try {
      const { getExchangeRates } = await import("@/lib/api");
      const data = await getExchangeRates(password);
      setExchangeRates(data || {});
      const inputs: Record<string, string> = {};
      Object.entries(data || {}).forEach(([code, info]) => {
        inputs[code] = String(info.rate_per_usd);
      });
      setRateInputs(inputs);
    } catch (e) {
      console.error("Failed to fetch exchange rates", e);
      toast.error("Failed to load exchange rates");
    } finally {
      setLoadingRates(false);
    }
  };

  const handleSaveRate = async (code: string) => {
    const valStr = rateInputs[code];
    const numVal = parseFloat(valStr);
    if (isNaN(numVal) || numVal <= 0) {
      toast.error("Please enter a valid rate greater than 0.");
      return;
    }
    try {
      const { updateExchangeRate } = await import("@/lib/api");
      await updateExchangeRate(code, numVal, password);
      toast.success(`Updated ${code} rate: 1 USD = ${numVal} ${code}`);
      fetchExchangeRates();
    } catch (err: any) {
      toast.error(err.message || `Failed to update rate for ${code}`);
    }
  };

  const fetchSearchHistory = async (userFilter?: string) => {
    setLoadingHistory(true);
    try {
      const { getSearchHistory } = await import("@/lib/api");
      const targetUser = (userFilter || historyUserFilter) === "all" ? undefined : (userFilter || historyUserFilter);
      const data = await getSearchHistory(targetUser);
      setSearchHistory(data || []);
    } catch (e) {
      console.error("Failed to fetch search history", e);
    } finally {
      setLoadingHistory(false);
    }
  };

  const fetchRouteHealth = async () => {
    setLoadingHealth(true);
    try {
      const { getRouteHealth } = await import("@/lib/api");
      const data = await getRouteHealth();
      setRouteHealth(data || { carriers: [], routes: [] });
    } catch (e) {
      console.error("Failed to fetch route health matrix", e);
    } finally {
      setLoadingHealth(false);
    }
  };

  const fetchOverrides = async () => {
    setLoadingOverrides(true);
    try {
      const { getCarrierOverrides } = await import("@/lib/api");
      const data = await getCarrierOverrides(password);
      setCarrierOverrides(data || {});
    } catch (e) {
      console.error("Failed to fetch carrier overrides", e);
    } finally {
      setLoadingOverrides(false);
    }
  };

  const fetchAnalytics = async (
    timeRange = analyticsTimeRange,
    userFilter = analyticsUserFilter,
    carrierFilter = analyticsCarrierFilter
  ) => {
    setLoadingAnalytics(true);
    try {
      const { getAdminAnalytics } = await import("@/lib/api");
      const data = await getAdminAnalytics({
        timeRange,
        userName: userFilter,
        carrier: carrierFilter,
      });
      setAnalyticsData(data);
    } catch (e) {
      console.error("Failed to fetch analytics data", e);
      toast.error("Failed to load consolidated analytics");
    } finally {
      setLoadingAnalytics(false);
    }
  };

  useEffect(() => {
    if (authenticated) {
      if (activeTab === "analytics") {
        fetchAnalytics();
      } else if (activeTab === "users") {
        fetchUsers();
      } else if (activeTab === "route_health") {
        fetchRouteHealth();
      } else if (activeTab === "overrides") {
        fetchOverrides();
      } else if (activeTab === "history") {
        fetchSearchHistory();
      } else if (activeTab === "exchange_rates") {
        fetchExchangeRates();
      }
    }
  }, [authenticated, activeTab]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/admin/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      if (!res.ok) throw new Error("Invalid password");
      setAuthenticated(true);
      fetchAnalytics();
      fetchUsers();
      fetchPortsConfig();
      fetchOverrides();
    } catch (err) {
      setError("Incorrect admin password.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetAllUsers = async () => {
    if (!confirm("Are you sure you want to kick all users and reset the database list to 0 for a fresh start? All active browser sessions will be logged out.")) {
      return;
    }
    try {
      const { resetAllUsers } = await import("@/lib/api");
      await resetAllUsers(password);
      toast.success("All user sessions and database records have been reset to 0!");
      fetchUsers();
    } catch (e: any) {
      toast.error(e?.message || "Failed to reset user sessions");
    }
  };

  const fetchUsers = async () => {
    try {
      const { getUsers } = await import("@/lib/api");
      const data = await getUsers(password);
      setUsers(data || []);
    } catch (e) {
      console.error("Failed to fetch users", e);
    }
  };

  // Custom Ports state
  const [customPorts, setCustomPorts] = useState<any[]>([]);
  const [customCode, setCustomCode] = useState("");
  const [customName, setCustomName] = useState("");
  const [customCountry, setCustomCountry] = useState("");
  const [customAliases, setCustomAliases] = useState("");
  const [addingCustomPort, setAddingCustomPort] = useState(false);

  const fetchCustomPorts = async () => {
    try {
      const { getCustomPorts } = await import("@/lib/api");
      const data = await getCustomPorts(password);
      setCustomPorts(data || []);
    } catch (e) {
      console.error("Failed to fetch custom ports", e);
    }
  };

  const fetchPortsConfig = async () => {
    try {
      const { getPortsConfig, getCountriesMap } = await import("@/lib/api");
      const config = await getPortsConfig(password);
      setPopularPorts(config.popular_ports || []);
      setBoostedCountries(config.boosted_countries || []);
      
      const countries = await getCountriesMap();
      setCountriesMap(countries);
      fetchCustomPorts();
    } catch (e) {
      console.error("Failed to fetch ports config/countries:", e);
    }
  };

  const handleCreateCustomPort = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanCode = customCode.trim().toUpperCase();
    if (cleanCode.length !== 5 || !/^[A-Z]+$/.test(cleanCode)) {
      toast.error("LOCODE must be a 5-letter uppercase string (e.g. INKCH).");
      return;
    }
    if (!customName.trim() || !customCountry) {
      toast.error("City/Port name and country are required.");
      return;
    }

    setAddingCustomPort(true);
    try {
      const { addCustomPort } = await import("@/lib/api");
      const aliasesList = customAliases.split(",").map((a) => a.trim()).filter(Boolean);
      await addCustomPort(
        {
          code: cleanCode,
          name: customName.trim(),
          country: customCountry,
          aliases: aliasesList,
        },
        password
      );

      toast.success(`Port ${cleanCode} (${customName}) registered/amended successfully!`);
      setCustomCode("");
      setCustomName("");
      setCustomCountry("");
      setCustomAliases("");
      fetchCustomPorts();
      fetchPortsConfig();
    } catch (err: any) {
      toast.error(err.message || "Failed to register custom port.");
    } finally {
      setAddingCustomPort(false);
    }
  };

  const handleDeleteCustomPort = async (code: string, name: string) => {
    if (!confirm(`Are you sure you want to delete custom port '${code}' (${name})?`)) return;
    try {
      const { deleteCustomPort } = await import("@/lib/api");
      await deleteCustomPort(code, password);
      toast.success(`Custom port ${code} deleted.`);
      fetchCustomPorts();
      fetchPortsConfig();
    } catch (e: any) {
      toast.error("Failed to delete custom port.");
    }
  };

  const deleteUser = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete user '${name}'?`)) return;
    try {
      const res = await fetch(`${API_URL}/api/users/${id}`, {
        method: "DELETE",
        headers: { "x-admin-password": password },
      });
      if (res.ok) {
        toast.success(`User ${name} deleted.`);
        fetchUsers();
      } else {
        toast.error("Failed to delete user.");
      }
    } catch (e) {
      toast.error("Error deleting user.");
    }
  };

  const handleAddPort = () => {
    let code = "";
    // Match [INKCH] or (INKCH)
    const bracketMatch = newPortInput.match(/[\[\(]\s*([A-Za-z]{5})\s*[\]\)]/);
    if (bracketMatch) {
      code = bracketMatch[1].toUpperCase();
    } else {
      // Find 5-letter UN/LOCODE word
      const words = newPortInput.trim().split(/[\s,]+/);
      for (const w of words) {
        const cleanW = w.replace(/[^A-Za-z]/g, "").toUpperCase();
        if (cleanW.length === 5) {
          code = cleanW;
          break;
        }
      }
    }

    if (!code) {
      toast.error("Please select a valid port from the autocomplete or enter a 5-letter UN/LOCODE (e.g. INKCH).");
      return;
    }

    if (popularPorts.includes(code)) {
      toast.error(`Port ${code} is already in the boosted ports list.`);
      return;
    }

    setPopularPorts([...popularPorts, code]);
    setNewPortInput("");
    toast.success(`Added port ${code} to boosted list.`);
  };

  const handleRemovePort = (code: string) => {
    setPopularPorts(popularPorts.filter((p) => p !== code));
    toast.success(`Removed port ${code}.`);
  };

  const handleAddCountry = () => {
    if (!selectedCountry) {
      toast.error("Please select a country to add.");
      return;
    }

    const clean = selectedCountry.trim().toUpperCase();
    if (boostedCountries.includes(clean)) {
      toast.error(`Country ${clean} is already in the boosted list.`);
      return;
    }

    setBoostedCountries([...boostedCountries, clean]);
    setSelectedCountry("");
    toast.success(`Added country ${countriesMap[clean] || clean} to boosted list.`);
  };

  const handleRemoveCountry = (code: string) => {
    setBoostedCountries(boostedCountries.filter((c) => c !== code));
    toast.success(`Removed country ${code}.`);
  };

  const handleSaveConfig = async () => {
    setSavingConfig(true);
    try {
      const { savePortsConfig } = await import("@/lib/api");
      await savePortsConfig({ popular_ports: popularPorts, boosted_countries: boostedCountries }, password);
      toast.success("Ports & Countries configuration saved successfully!");
    } catch (err: any) {
      toast.error(err.message || "Failed to save configuration.");
    } finally {
      setSavingConfig(false);
    }
  };

  const handleAddOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideKey.trim() || !overrideText.trim()) {
      toast.error("Please enter both a trigger keyword/code and target search text.");
      return;
    }
    try {
      const { addCarrierOverride } = await import("@/lib/api");
      await addCarrierOverride(selectedCarrier, overrideKey.trim(), overrideText.trim(), password);
      toast.success(`Override saved for ${selectedCarrier.toUpperCase()}!`);
      setOverrideKey("");
      setOverrideText("");
      fetchOverrides();
    } catch (err: any) {
      toast.error(err.message || "Failed to save carrier override.");
    }
  };

  const handleDeleteOverride = async (carrier: string, key: string) => {
    if (!confirm(`Remove override for ${carrier.toUpperCase()}: '${key}'?`)) return;
    try {
      const { deleteCarrierOverride } = await import("@/lib/api");
      await deleteCarrierOverride(carrier, key, password);
      toast.success(`Removed override '${key}' from ${carrier.toUpperCase()}`);
      fetchOverrides();
    } catch (err: any) {
      toast.error(err.message || "Failed to delete carrier override.");
    }
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="w-full max-w-md border border-border bg-card rounded-3xl p-8 shadow-xl">
          <div className="flex flex-col items-center text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4 border border-indigo-100 dark:border-indigo-500/20">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-bold text-foreground">Admin Dashboard</h1>
            <p className="text-muted-foreground text-sm mt-1">Enter password to access registry management</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <input
                type="password"
                placeholder="Admin Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-muted/40 dark:bg-black/50 border border-border rounded-xl px-4 py-3 text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus-visible:ring-ring transition-all text-sm"
              />
            </div>
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl px-4 py-3 font-medium transition-colors disabled:opacity-50"
            >
              {loading ? "Verifying..." : "Access Dashboard"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Flatten carrier overrides for search & filtering
  const allOverrideList: { carrier: string; key: string; text: string }[] = [];
  Object.entries(carrierOverrides).forEach(([carrier, kvMap]) => {
    if (carrierFilter === "all" || carrierFilter === carrier) {
      Object.entries(kvMap || {}).forEach(([key, text]) => {
        if (!overrideSearch || key.toLowerCase().includes(overrideSearch.toLowerCase()) || text.toLowerCase().includes(overrideSearch.toLowerCase())) {
          allOverrideList.push({ carrier, key, text });
        }
      });
    }
  });

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
              <ShieldCheck className="w-8 h-8 text-indigo-500" />
              Admin Registry
            </h1>
            <p className="text-muted-foreground mt-1">Manage platform user access, port ranking, and live carrier search overrides.</p>
          </div>
          <button 
            onClick={() => { setAuthenticated(false); setPassword(""); }}
            className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-accent text-foreground dark:text-white rounded-xl transition-colors font-medium text-sm"
          >
            <LogOut className="w-4 h-4" />
            Lock Dashboard
          </button>
        </header>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="border border-border bg-card rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-500/10 flex items-center justify-center text-blue-600 dark:text-blue-400">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                <p className="text-2xl font-bold text-foreground">{users.length}</p>
              </div>
            </div>
          </div>
          <div className="border border-border bg-card rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold text-foreground">{users.filter(u => u.is_active).length}</p>
              </div>
            </div>
          </div>
          <div className="border border-border bg-card rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-500/10 flex items-center justify-center text-purple-600 dark:text-purple-400">
                <Sliders className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Carrier Port Overrides</p>
                <p className="text-2xl font-bold text-foreground">
                  {Object.values(carrierOverrides).reduce((acc, obj) => acc + Object.keys(obj || {}).length, 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-4 border-b border-border pb-px flex-wrap">
          <button
            onClick={() => setActiveTab("analytics")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative flex items-center gap-2 ${
              activeTab === "analytics"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Consolidated Analytics
            {activeTab === "analytics" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative ${
              activeTab === "users"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            User Registry
            {activeTab === "users" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("ports")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative ${
              activeTab === "ports"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Port Ranking Config
            {activeTab === "ports" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("overrides")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative flex items-center gap-2 ${
              activeTab === "overrides"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Carrier Port Overrides
            {activeTab === "overrides" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative flex items-center gap-2 ${
              activeTab === "history"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            User Search History
            {activeTab === "history" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("exchange_rates")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative flex items-center gap-2 ${
              activeTab === "exchange_rates"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <span>💱 Currency Conversion Rates</span>
            {activeTab === "exchange_rates" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("route_health")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative ${
              activeTab === "route_health"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Route Reliability Matrix
            {activeTab === "route_health" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
        </div>

        {/* TAB 0: CONSOLIDATED GLOBAL ANALYTICS */}
        {activeTab === "analytics" && (
          <div className="space-y-6">
            {/* Controls & Filter Bar */}
            <div className="border border-border bg-card rounded-2xl p-5 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2.5">
                  <BarChart3 className="w-6 h-6 text-indigo-500" />
                  Global Sourcing Intelligence
                </h2>
                <p className="text-muted-foreground text-xs mt-1">
                  Cross-account sourcing activity, trade lane popularity rankings, carrier accuracy diagnostics, and freight pricing spectrum.
                </p>
              </div>

              <div className="flex items-center gap-3 flex-wrap">
                {/* Time Range Filter Pills */}
                <div className="flex items-center bg-muted/60 dark:bg-black/40 border border-border p-1 rounded-xl gap-1">
                  {[
                    { id: "all", label: "All Time" },
                    { id: "30d", label: "Last 30 Days" },
                    { id: "14d", label: "Last 14 Days" },
                    { id: "7d", label: "Last 7 Days" },
                    { id: "today", label: "Today" },
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        setAnalyticsTimeRange(item.id as any);
                        fetchAnalytics(item.id as any, analyticsUserFilter, analyticsCarrierFilter);
                      }}
                      className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                        analyticsTimeRange === item.id
                          ? "bg-indigo-600 text-white shadow-xs"
                          : "text-muted-foreground hover:text-foreground hover:bg-muted"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>

                {/* User Filter Dropdown */}
                <select
                  value={analyticsUserFilter}
                  onChange={(e) => {
                    const val = e.target.value;
                    setAnalyticsUserFilter(val);
                    fetchAnalytics(analyticsTimeRange, val, analyticsCarrierFilter);
                  }}
                  className="bg-muted/40 dark:bg-black/50 border border-border rounded-xl px-3 py-1.5 text-xs text-foreground font-medium outline-none focus:ring-2 focus-visible:ring-ring cursor-pointer"
                >
                  <option value="all">All Accounts (Global)</option>
                  {(analyticsData?.all_users || []).map((u: string) => (
                    <option key={u} value={u}>{u}</option>
                  ))}
                </select>

                {/* Refresh Button */}
                <button
                  onClick={() => fetchAnalytics(analyticsTimeRange, analyticsUserFilter, analyticsCarrierFilter)}
                  disabled={loadingAnalytics}
                  className="p-2 border border-border bg-card hover:bg-accent text-foreground rounded-xl transition-colors disabled:opacity-50"
                  title="Refresh Analytics"
                >
                  <RefreshCw className={`w-4 h-4 ${loadingAnalytics ? "animate-spin text-indigo-500" : ""}`} />
                </button>
              </div>
            </div>

            {loadingAnalytics && !analyticsData ? (
              <div className="text-center py-20 text-muted-foreground font-mono text-sm animate-pulse border border-border bg-card rounded-3xl">
                Crunching global sourcing intelligence and carrier metrics...
              </div>
            ) : (
              <>
                {/* Global KPI Hero Grid (Matching workspace reference style) */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  <div className="rounded-xl border border-border bg-card px-4 py-3.5 shadow-sm">
                    <div className="font-mono text-2xl font-bold tabular-nums text-indigo-600 dark:text-indigo-400">
                      {analyticsData?.summary?.total_searches?.toLocaleString() || "0"}
                    </div>
                    <div className="mt-1 text-xs font-medium text-muted-foreground">Searches run</div>
                    <div className="text-[10px] text-muted-foreground/70 font-mono mt-0.5">
                      Across {analyticsData?.summary?.active_users_count || 0} active accounts
                    </div>
                  </div>

                  <div className="rounded-xl border border-border bg-card px-4 py-3.5 shadow-sm">
                    <div className="font-mono text-2xl font-bold tabular-nums text-emerald-600 dark:text-emerald-400">
                      {analyticsData?.summary?.total_quotes?.toLocaleString() || "0"}
                    </div>
                    <div className="mt-1 text-xs font-medium text-muted-foreground">Quotes returned</div>
                    <div className="text-[10px] text-muted-foreground/70 font-mono mt-0.5">
                      Live freight rates
                    </div>
                  </div>

                  <div className="rounded-xl border border-border bg-card px-4 py-3.5 shadow-sm">
                    <div className="font-mono text-2xl font-bold tabular-nums text-foreground">
                      {analyticsData?.summary?.hit_rate_percent || 0}%
                    </div>
                    <div className="mt-1 text-xs font-medium text-muted-foreground">Returned ≥1 quote</div>
                    <div className="text-[10px] text-muted-foreground/70 font-mono mt-0.5">
                      {analyticsData?.summary?.searches_with_quotes?.toLocaleString() || 0} successful hits
                    </div>
                  </div>

                  <div className="rounded-xl border border-border bg-card px-4 py-3.5 shadow-sm">
                    <div className="font-mono text-2xl font-bold tabular-nums text-purple-600 dark:text-purple-400">
                      {analyticsData?.summary?.distinct_lanes?.toLocaleString() || "0"}
                    </div>
                    <div className="mt-1 text-xs font-medium text-muted-foreground">Distinct lanes</div>
                    <div className="text-[10px] text-muted-foreground/70 font-mono mt-0.5">
                      Unique port pairings
                    </div>
                  </div>

                  <div className="rounded-xl border border-border bg-card px-4 py-3.5 shadow-sm">
                    <div className="font-mono text-sm font-bold truncate text-foreground" title={analyticsData?.summary?.most_active_lane?.display_lane || "N/A"}>
                      {analyticsData?.summary?.most_active_lane?.display_lane || "None"}
                    </div>
                    <div className="mt-1 text-xs font-medium text-muted-foreground">Most active lane</div>
                    <div className="text-[10px] text-muted-foreground/70 font-mono mt-0.5">
                      {analyticsData?.summary?.most_active_lane?.search_count || 0} searches ({analyticsData?.summary?.most_active_lane?.volume_percentage || 0}%)
                    </div>
                  </div>

                  <div className="rounded-xl border border-border bg-card px-4 py-3.5 shadow-sm">
                    <div className="font-mono text-base font-bold truncate text-amber-600 dark:text-amber-400" title={analyticsData?.summary?.top_user?.user_name || "N/A"}>
                      {analyticsData?.summary?.top_user?.user_name || "None"}
                    </div>
                    <div className="mt-1 text-xs font-medium text-muted-foreground">Top sourcing user</div>
                    <div className="text-[10px] text-muted-foreground/70 font-mono mt-0.5">
                      {analyticsData?.summary?.top_user?.search_count || 0} searches ({analyticsData?.summary?.top_user?.volume_percentage || 0}%)
                    </div>
                  </div>
                </div>

                {/* Global Activity Timeline (Searches Per Day) */}
                <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
                  <div className="mb-3 flex items-baseline justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                        <Activity className="w-4 h-4 text-indigo-500" />
                        Searches per day (Global volume)
                      </h3>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Timeline of company sourcing requests and extracted live quotes
                      </p>
                    </div>
                    <span className="font-mono text-xs text-muted-foreground">
                      last {analyticsData?.timeline?.days_count || 14} days
                    </span>
                  </div>

                  <div className="relative mt-4">
                    <div className="flex h-24 items-end gap-[3px]" onMouseLeave={() => setHoveredDay(null)}>
                      {(analyticsData?.timeline?.per_day || []).map((day: any, i: number) => {
                        const busiest = analyticsData?.timeline?.busiest_day || 1;
                        const pct = Math.min(100, Math.max(3, (day.searches / busiest) * 100));
                        return (
                          <div
                            key={day.iso}
                            className="group relative flex h-full flex-1 cursor-default items-end"
                            onMouseEnter={() => setHoveredDay(i)}
                          >
                            <div
                              className="mx-auto w-full max-w-[22px] rounded-t-[4px] transition-all"
                              style={{
                                height: day.searches ? `${pct}%` : "2px",
                                background: day.searches
                                  ? hoveredDay === i
                                    ? "rgb(99 102 241)"
                                    : "rgba(99, 102, 241, 0.65)"
                                  : "var(--border)",
                              }}
                            />
                          </div>
                        );
                      })}
                    </div>

                    {/* Baseline */}
                    <div className="mt-1 h-px w-full bg-border" />

                    <div className="mt-2 flex justify-between font-mono text-xs text-muted-foreground">
                      <span>{analyticsData?.timeline?.per_day?.[0]?.label}</span>
                      <span className="text-indigo-600 dark:text-indigo-400 font-medium">
                        {hoveredDay !== null && analyticsData?.timeline?.per_day?.[hoveredDay]
                          ? `${analyticsData.timeline.per_day[hoveredDay].label} · ${analyticsData.timeline.per_day[hoveredDay].searches} searches · ${analyticsData.timeline.per_day[hoveredDay].quotes} quotes`
                          : `peak ${analyticsData?.timeline?.busiest_day || 0}/day`}
                      </span>
                      <span>{analyticsData?.timeline?.per_day?.[analyticsData?.timeline?.per_day?.length - 1]?.label}</span>
                    </div>
                  </div>
                </div>

                {/* Carrier Accuracy & Reliability Section */}
                <div className="border border-border bg-card rounded-2xl p-6 shadow-sm space-y-5">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-border pb-4">
                    <div>
                      <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                        <Award className="w-5 h-5 text-indigo-500" />
                        Carrier Extraction Accuracy & Failure Analysis
                      </h3>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Performance benchmarks: identifying our most reliable vs most inaccurate/fragile carrier connections.
                      </p>
                    </div>
                  </div>

                  {/* Highlights: Most Accurate vs Most Inaccurate */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Most Accurate */}
                    <div className="border border-emerald-500/30 bg-emerald-500/5 dark:bg-emerald-500/10 rounded-xl p-4 flex items-start gap-3.5">
                      <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
                        <CheckCircle2 className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                            🏆 Most Accurate Carrier
                          </span>
                          <span className="font-mono text-sm font-bold text-emerald-600 dark:text-emerald-400">
                            {analyticsData?.summary?.most_accurate_carrier?.accuracy_percent || 0}% Accuracy
                          </span>
                        </div>
                        <h4 className="text-base font-bold text-foreground mt-0.5">
                          {analyticsData?.summary?.most_accurate_carrier?.carrier_name || analyticsData?.summary?.most_accurate_carrier?.carrier || "None"}
                        </h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          Successfully extracted quotes on {analyticsData?.summary?.most_accurate_carrier?.quotes_found_count || 0} searches ({analyticsData?.summary?.most_accurate_carrier?.total_queries || 0} total queries).
                        </p>
                      </div>
                    </div>

                    {/* Most Inaccurate */}
                    <div className="border border-rose-500/30 bg-rose-500/5 dark:bg-rose-500/10 rounded-xl p-4 flex items-start gap-3.5">
                      <div className="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
                        <AlertTriangle className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400">
                            ⚠️ Most Inaccurate / Problematic
                          </span>
                          <span className="font-mono text-sm font-bold text-rose-600 dark:text-rose-400">
                            {analyticsData?.summary?.most_inaccurate_carrier?.failure_percent || 0}% Failure Rate
                          </span>
                        </div>
                        <h4 className="text-base font-bold text-foreground mt-0.5">
                          {analyticsData?.summary?.most_inaccurate_carrier?.carrier_name || analyticsData?.summary?.most_inaccurate_carrier?.carrier || "None"}
                        </h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          Encountered {analyticsData?.summary?.most_inaccurate_carrier?.failure_count || 0} portal errors, timeouts, or empty extractions across {analyticsData?.summary?.most_inaccurate_carrier?.total_queries || 0} queries.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Carrier Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground font-semibold">
                          <th className="py-2.5 px-3">Carrier Line</th>
                          <th className="py-2.5 px-3">Total Requests</th>
                          <th className="py-2.5 px-3 w-56">Extraction Reliability</th>
                          <th className="py-2.5 px-3 text-right">Accuracy Rate</th>
                          <th className="py-2.5 px-3 text-right">No Quotes Found</th>
                          <th className="py-2.5 px-3 text-right">Failures & Errors</th>
                          <th className="py-2.5 px-3 text-right">Port Mismatches</th>
                          <th className="py-2.5 px-3 text-center">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/60">
                        {(analyticsData?.carrier_ranking || []).map((c: any) => (
                          <tr key={c.carrier} className="hover:bg-muted/40 transition-colors font-medium">
                            <td className="py-3 px-3">
                              <span className="font-bold text-foreground">{c.carrier_name}</span>
                              <span className="ml-1.5 text-[10px] text-muted-foreground font-mono">({c.carrier})</span>
                            </td>
                            <td className="py-3 px-3 font-mono tabular-nums text-foreground">
                              {c.total_queries.toLocaleString()}
                            </td>
                            <td className="py-3 px-3 w-56">
                              <div className="h-2 w-full bg-muted rounded-full overflow-hidden flex">
                                <div
                                  className="bg-emerald-500 h-full"
                                  style={{ width: `${c.accuracy_percent}%` }}
                                  title={`Quotes found: ${c.quotes_found_count} (${c.accuracy_percent}%)`}
                                />
                                <div
                                  className="bg-amber-400 h-full"
                                  style={{ width: `${c.no_quotes_percent}%` }}
                                  title={`No quotes: ${c.no_quotes_count} (${c.no_quotes_percent}%)`}
                                />
                                <div
                                  className="bg-rose-500 h-full"
                                  style={{ width: `${c.failure_percent}%` }}
                                  title={`Failures: ${c.failure_count} (${c.failure_percent}%)`}
                                />
                              </div>
                              <div className="flex justify-between text-[9px] text-muted-foreground mt-1 font-mono">
                                <span className="text-emerald-500">{c.accuracy_percent}% succ</span>
                                <span className="text-amber-500">{c.no_quotes_percent}% empty</span>
                                <span className="text-rose-500">{c.failure_percent}% err</span>
                              </div>
                            </td>
                            <td className="py-3 px-3 text-right font-mono font-bold text-foreground">
                              {c.accuracy_percent}%
                            </td>
                            <td className="py-3 px-3 text-right font-mono tabular-nums text-muted-foreground">
                              {c.no_quotes_count}
                            </td>
                            <td className="py-3 px-3 text-right font-mono tabular-nums text-rose-500 font-semibold">
                              {c.failure_count}
                            </td>
                            <td className="py-3 px-3 text-right font-mono tabular-nums">
                              {c.port_mismatch_count > 0 ? (
                                <span className="text-amber-500 font-bold bg-amber-500/10 px-1.5 py-0.5 rounded">
                                  {c.port_mismatch_count}
                                </span>
                              ) : (
                                <span className="text-muted-foreground">0</span>
                              )}
                            </td>
                            <td className="py-3 px-3 text-center">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                                c.reliability_tier === "High"
                                  ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                                  : c.reliability_tier === "Moderate"
                                  ? "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
                                  : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20"
                              }`}>
                                {c.reliability_tier}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Most-Searched Port-to-Port Pairings (Trade Lanes) */}
                <div className="border border-border bg-card rounded-2xl p-6 shadow-sm space-y-4">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border pb-4">
                    <div>
                      <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-indigo-500" />
                        Most-Searched Port-to-Port Pairings (Trade Lanes)
                      </h3>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Ranked trade lanes by employee search volume, platform volume share, and live quote hit rates.
                      </p>
                    </div>

                    <div className="relative">
                      <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                      <input
                        type="text"
                        placeholder="Filter port or trade lane..."
                        value={laneSearchQuery}
                        onChange={(e) => setLaneSearchQuery(e.target.value)}
                        className="pl-8 pr-3 py-1.5 text-xs bg-muted/40 dark:bg-black/40 border border-border rounded-xl text-foreground placeholder-muted-foreground outline-none focus:ring-2 focus-visible:ring-ring w-64"
                      />
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground font-semibold">
                          <th className="py-2.5 px-3">#</th>
                          <th className="py-2.5 px-3">Trade Lane</th>
                          <th className="py-2.5 px-3 w-48">Sourcing Requests</th>
                          <th className="py-2.5 px-3 text-right">Hit Rate</th>
                          <th className="py-2.5 px-3 text-right">Freight Rate Spread</th>
                          <th className="py-2.5 px-3">Top Value Carrier</th>
                          <th className="py-2.5 px-3 text-right">Active Users</th>
                          <th className="py-2.5 px-3 text-right">Last Searched</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/60">
                        {(analyticsData?.top_lanes || [])
                          .filter((lane: any) =>
                            !laneSearchQuery ||
                            lane.display_lane.toLowerCase().includes(laneSearchQuery.toLowerCase()) ||
                            lane.origin.toLowerCase().includes(laneSearchQuery.toLowerCase()) ||
                            lane.destination.toLowerCase().includes(laneSearchQuery.toLowerCase())
                          )
                          .slice(0, 30)
                          .map((lane: any, index: number) => {
                            const maxVol = analyticsData?.top_lanes?.[0]?.search_count || 1;
                            const barPct = Math.max(3, (lane.search_count / maxVol) * 100);
                            return (
                              <tr key={lane.display_lane} className="hover:bg-muted/40 transition-colors font-medium">
                                <td className="py-3 px-3 font-mono text-muted-foreground font-bold">
                                  {index + 1}
                                </td>
                                <td className="py-3 px-3">
                                  <div className="font-mono text-xs font-bold text-foreground">
                                    {lane.origin} → {lane.destination}
                                  </div>
                                  <div className="text-[10px] text-muted-foreground">
                                    {lane.quotes_count} quotes returned
                                  </div>
                                </td>
                                <td className="py-3 px-3">
                                  <div className="flex items-center justify-between text-xs font-mono mb-1">
                                    <span className="font-bold text-foreground">{lane.search_count}</span>
                                    <span className="text-muted-foreground text-[10px]">{lane.volume_percentage}% share</span>
                                  </div>
                                  <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-indigo-500 rounded-full"
                                      style={{ width: `${barPct}%` }}
                                    />
                                  </div>
                                </td>
                                <td className="py-3 px-3 text-right font-mono">
                                  <span className={`font-bold ${lane.hit_rate_percent >= 50 ? "text-emerald-500" : lane.hit_rate_percent > 0 ? "text-amber-500" : "text-muted-foreground"}`}>
                                    {lane.hit_rate_percent}%
                                  </span>
                                </td>
                                <td className="py-3 px-3 text-right font-mono">
                                  {lane.min_price ? (
                                    <div>
                                      <span className="font-bold text-foreground">${lane.min_price?.toLocaleString()}</span>
                                      {lane.max_price && lane.max_price > lane.min_price && (
                                        <span className="text-muted-foreground text-[10px] block">
                                          up to ${lane.max_price?.toLocaleString()}
                                        </span>
                                      )}
                                    </div>
                                  ) : (
                                    <span className="text-muted-foreground italic text-[10px]">No quotes</span>
                                  )}
                                </td>
                                <td className="py-3 px-3">
                                  {lane.cheapest_carrier ? (
                                    <span className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-mono text-[10px] font-bold border border-indigo-500/20">
                                      {lane.cheapest_carrier}
                                    </span>
                                  ) : (
                                    <span className="text-muted-foreground text-[10px]">-</span>
                                  )}
                                </td>
                                <td className="py-3 px-3 text-right font-mono text-muted-foreground">
                                  {lane.unique_users_count}
                                </td>
                                <td className="py-3 px-3 text-right font-mono text-[10px] text-muted-foreground">
                                  {lane.last_searched_at ? new Date(lane.last_searched_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }) : "-"}
                                </td>
                              </tr>
                            );
                          })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Freight Rate Pricing Spectrum (Cheapest vs Most Expensive) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Top Economical Lanes */}
                  <div className="border border-border bg-card rounded-2xl p-5 shadow-sm space-y-3">
                    <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                      <ArrowDownRight className="w-4 h-4 text-emerald-500" />
                      Top Economical Trade Lanes (Cheapest Rates)
                    </h3>
                    <div className="space-y-2.5">
                      {(analyticsData?.pricing_spectrum?.cheapest_lanes || []).map((lane: any) => (
                        <div key={lane.display_lane} className="flex items-center justify-between p-3 rounded-xl bg-muted/30 border border-border">
                          <div>
                            <div className="font-mono text-xs font-bold text-foreground">
                              {lane.origin} → {lane.destination}
                            </div>
                            <div className="text-[10px] text-muted-foreground font-mono mt-0.5">
                              Lowest with <span className="font-bold text-indigo-500">{lane.cheapest_carrier || "Carrier"}</span> · avg ${lane.avg_price?.toLocaleString()}
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="font-mono text-sm font-bold text-emerald-600 dark:text-emerald-400">
                              ${lane.min_price?.toLocaleString()}
                            </span>
                            <span className="block text-[10px] text-muted-foreground">lowest quote</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Top Premium Lanes */}
                  <div className="border border-border bg-card rounded-2xl p-5 shadow-sm space-y-3">
                    <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                      <ArrowUpRight className="w-4 h-4 text-rose-500" />
                      Top Premium Trade Lanes (Highest Rates)
                    </h3>
                    <div className="space-y-2.5">
                      {(analyticsData?.pricing_spectrum?.expensive_lanes || []).map((lane: any) => (
                        <div key={lane.display_lane} className="flex items-center justify-between p-3 rounded-xl bg-muted/30 border border-border">
                          <div>
                            <div className="font-mono text-xs font-bold text-foreground">
                              {lane.origin} → {lane.destination}
                            </div>
                            <div className="text-[10px] text-muted-foreground font-mono mt-0.5">
                              avg ${lane.avg_price?.toLocaleString()} across {lane.quotes_count} quotes
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="font-mono text-sm font-bold text-rose-600 dark:text-rose-400">
                              ${lane.max_price?.toLocaleString()}
                            </span>
                            <span className="block text-[10px] text-muted-foreground">peak quote</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* User Sourcing Activity Leaderboard */}
                <div className="border border-border bg-card rounded-2xl p-6 shadow-sm space-y-4">
                  <div className="border-b border-border pb-4">
                    <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                      <Users className="w-5 h-5 text-indigo-500" />
                      User Sourcing Activity Leaderboard (Who Is Searching The Most)
                    </h3>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Search request frequency and live quotes generated across all employee user accounts.
                    </p>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground font-semibold">
                          <th className="py-2.5 px-3">Rank</th>
                          <th className="py-2.5 px-3">User Account</th>
                          <th className="py-2.5 px-3 w-64">Sourcing Frequency</th>
                          <th className="py-2.5 px-3 text-right">Quotes Generated</th>
                          <th className="py-2.5 px-3 text-right">Distinct Lanes</th>
                          <th className="py-2.5 px-3 text-right">Last Active</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/60">
                        {(analyticsData?.user_leaderboard || []).map((u: any, idx: number) => {
                          const maxSearch = analyticsData?.user_leaderboard?.[0]?.search_count || 1;
                          const barPct = Math.max(3, (u.search_count / maxSearch) * 100);
                          return (
                            <tr key={u.user_name} className="hover:bg-muted/40 transition-colors font-medium">
                              <td className="py-3 px-3 font-mono font-bold text-muted-foreground">
                                #{idx + 1}
                              </td>
                              <td className="py-3 px-3">
                                <div className="flex items-center gap-2.5">
                                  <div className="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xs">
                                    {u.user_name.charAt(0).toUpperCase()}
                                  </div>
                                  <span className="font-bold text-foreground text-sm">{u.user_name}</span>
                                </div>
                              </td>
                              <td className="py-3 px-3">
                                <div className="flex items-center justify-between text-xs font-mono mb-1">
                                  <span className="font-bold text-foreground">{u.search_count.toLocaleString()} searches</span>
                                  <span className="text-muted-foreground text-[10px]">{u.volume_percentage}% share</span>
                                </div>
                                <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-indigo-500 rounded-full"
                                    style={{ width: `${barPct}%` }}
                                  />
                                </div>
                              </td>
                              <td className="py-3 px-3 text-right font-mono tabular-nums font-bold text-foreground">
                                {u.quotes_generated.toLocaleString()}
                              </td>
                              <td className="py-3 px-3 text-right font-mono tabular-nums text-muted-foreground">
                                {u.distinct_lanes}
                              </td>
                              <td className="py-3 px-3 text-right font-mono text-[10px] text-muted-foreground">
                                {u.last_active ? new Date(u.last_active).toLocaleString(undefined, { dateStyle: "short", timeStyle: "short" }) : "-"}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB 1: USER REGISTRY */}
        {activeTab === "users" && (
          <div className="border border-border bg-card rounded-3xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <h2 className="text-lg font-bold text-foreground">Registered Users</h2>
              <div className="flex items-center gap-3">
                <button
                  onClick={fetchUsers}
                  className="px-3 py-1.5 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-semibold rounded-lg hover:bg-indigo-100 transition-colors flex items-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Refresh Users
                </button>
                <button
                  onClick={handleResetAllUsers}
                  className="px-3 py-1.5 bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400 text-xs font-semibold rounded-lg hover:bg-rose-100 transition-colors flex items-center gap-1.5"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Reset All Sessions (Fresh Start)
                </button>
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input 
                    type="text" 
                    placeholder="Search users..." 
                    className="pl-9 pr-4 py-2 bg-muted/40 dark:bg-black/50 border border-border rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus-visible:ring-ring w-64"
                  />
                </div>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-muted/40 dark:bg-black/40 text-muted-foreground">
                  <tr>
                    <th className="px-6 py-4 font-medium">User Name</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium">Joined Date</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-muted-foreground">
                        No users registered yet.
                      </td>
                    </tr>
                  ) : (
                    users.map((user) => (
                      <tr key={user.id} className="hover:bg-accent/60 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs">
                              {user.name.charAt(0).toUpperCase()}
                            </div>
                            <span className="font-medium text-foreground">{user.name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                            user.is_active 
                              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400" 
                              : "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400"
                          }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${user.is_active ? "bg-emerald-400" : "bg-red-400"}`} />
                            {user.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-muted-foreground">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button 
                            onClick={() => deleteUser(user.id, user.name)}
                            className="p-2 text-muted-foreground hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors"
                            title="Delete User"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 2: PORT RANKING CONFIG */}
        {activeTab === "ports" && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* Column 1: Boosted Ports */}
            <div className="border border-border bg-card rounded-3xl p-6 shadow-sm space-y-6 flex flex-col justify-between min-h-[500px]">
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-indigo-500" />
                    Boosted Ports (Cities)
                  </h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Configure specific port codes (UN/LOCODEs) to rank higher in searches.
                  </p>
                </div>

                {/* Add Port Form */}
                <div className="flex items-end gap-3 rounded-2xl border border-border bg-muted/40 p-4">
                  <div className="flex-1">
                    <PortAutocomplete
                      label="Search Port to Add"
                      value={newPortInput}
                      onChange={(val) => setNewPortInput(val)}
                      placeholder="Type to search..."
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleAddPort}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium text-sm transition-colors flex items-center gap-1.5 h-[42px]"
                  >
                    <Plus className="w-4 h-4" />
                    Add
                  </button>
                </div>

                {/* List of Ports */}
                <div className="max-h-[350px] overflow-y-auto space-y-2 pr-1">
                  {popularPorts.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      No custom ports boosted yet.
                    </p>
                  ) : (
                    popularPorts.map((code) => (
                      <div
                        key={code}
                        className="flex items-center justify-between px-4 py-3 bg-muted/40 hover:bg-muted dark:hover:bg-white/[0.04] border border-line rounded-xl transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-mono font-bold bg-blue-100 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 px-2 py-1 rounded">
                            {code}
                          </span>
                          <span className="text-sm font-medium text-foreground">
                            {code.substring(0, 2) in countriesMap
                              ? `${countriesMap[code.substring(0, 2)]}`
                              : code.substring(0, 2)}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemovePort(code)}
                          className="p-1.5 text-muted-foreground hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Column 2: Boosted Countries */}
            <div className="border border-border bg-card rounded-3xl p-6 shadow-sm space-y-6 flex flex-col justify-between min-h-[500px]">
              <div className="space-y-6 w-full">
                <div>
                  <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
                    <Globe className="w-5 h-5 text-indigo-500" />
                    Boosted Countries
                  </h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Prioritize all ports from these countries when matching keywords.
                  </p>
                </div>

                {/* Add Country Form */}
                <div className="flex items-end gap-3 rounded-2xl border border-border bg-muted/40 p-4">
                  <div className="flex-1 space-y-1.5">
                    <label className="block text-xs font-semibold text-foreground">
                      Select Country to Add
                    </label>
                    <select
                      value={selectedCountry}
                      onChange={(e) => setSelectedCountry(e.target.value)}
                      className="w-full border border-input bg-card dark:bg-white/[0.04] rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus-visible:ring-ring h-[42px]"
                    >
                      <option value="">-- Select Country --</option>
                      {Object.entries(countriesMap)
                        .sort((a, b) => a[1].localeCompare(b[1]))
                        .map(([code, name]) => (
                          <option key={code} value={code}>
                            {name} ({code})
                          </option>
                        ))}
                    </select>
                  </div>
                  <button
                    type="button"
                    onClick={handleAddCountry}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium text-sm transition-colors flex items-center gap-1.5 h-[42px]"
                  >
                    <Plus className="w-4 h-4" />
                    Add
                  </button>
                </div>

                {/* List of Boosted Countries */}
                <div className="max-h-[350px] overflow-y-auto space-y-2 pr-1">
                  {boostedCountries.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      No custom countries boosted yet.
                    </p>
                  ) : (
                    boostedCountries.map((code) => (
                      <div
                        key={code}
                        className="flex items-center justify-between px-4 py-3 bg-muted/40 hover:bg-muted dark:hover:bg-white/[0.04] border border-line rounded-xl transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-mono font-bold bg-purple-100 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400 px-2 py-1 rounded">
                            {code}
                          </span>
                          <span className="text-sm font-medium text-foreground">
                            {countriesMap[code] || code}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveCountry(code)}
                          className="p-1.5 text-muted-foreground hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Save Button */}
              <div className="mt-4 w-full border-t border-line pt-4">
                <button
                  type="button"
                  disabled={savingConfig}
                  onClick={handleSaveConfig}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl px-4 py-3 font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/15"
                >
                  <Save className="w-5 h-5" />
                  {savingConfig ? "Saving Configuration..." : "Save Config Settings"}
                </button>
              </div>
            </div>
          </div>

          {/* Bottom Card: Register / Amend Custom City & Port Code */}
          <div className="border border-border bg-card rounded-3xl p-6 shadow-sm space-y-6">
            <div>
              <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
                <MapPin className="w-5 h-5 text-indigo-500" />
                Register / Amend Custom City & Port Code
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                Add a brand new city with its 5-letter UN/LOCODE, or amend the display city name attached to an existing port code. Applied live immediately across all searches!
              </p>
            </div>

            <form onSubmit={handleCreateCustomPort} className="space-y-4 rounded-2xl border border-border bg-muted/40 p-5">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1">
                    UN/LOCODE (5-letter)
                  </label>
                  <input
                    type="text"
                    maxLength={5}
                    value={customCode}
                    onChange={(e) => setCustomCode(e.target.value.toUpperCase())}
                    placeholder="e.g. INKCH"
                    className="w-full border border-input bg-card dark:bg-white/[0.04] rounded-xl px-3 py-2 text-sm font-mono text-foreground uppercase focus:outline-none focus:ring-2 focus-visible:ring-ring h-[42px]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1">
                    City / Port Display Name
                  </label>
                  <input
                    type="text"
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    placeholder="e.g. Cochin (KERALA)"
                    className="w-full border border-input bg-card dark:bg-white/[0.04] rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus-visible:ring-ring h-[42px]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1">
                    Country
                  </label>
                  <select
                    value={customCountry}
                    onChange={(e) => setCustomCountry(e.target.value)}
                    className="w-full border border-input bg-card dark:bg-white/[0.04] rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus-visible:ring-ring h-[42px]"
                    required
                  >
                    <option value="">-- Select Country --</option>
                    {Object.entries(countriesMap)
                      .sort((a, b) => a[1].localeCompare(b[1]))
                      .map(([code, name]) => (
                        <option key={code} value={code}>
                          {name} ({code})
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <div className="flex-1 mr-4">
                  <input
                    type="text"
                    value={customAliases}
                    onChange={(e) => setCustomAliases(e.target.value)}
                    placeholder="Optional Aliases (comma-separated, e.g. kochi sz, cochin freezone)"
                    className="w-full border border-input bg-card dark:bg-white/[0.04] rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-2 focus-visible:ring-ring h-[38px]"
                  />
                </div>
                <button
                  type="submit"
                  disabled={addingCustomPort}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium text-sm transition-colors flex items-center gap-1.5 h-[38px] whitespace-nowrap shadow-md shadow-indigo-600/20"
                >
                  <Plus className="w-4 h-4" />
                  {addingCustomPort ? "Registering..." : "Save / Amend Port Code"}
                </button>
              </div>
            </form>

            {/* Registered Custom Ports Table */}
            {customPorts.length > 0 && (
              <div className="space-y-3 border-t border-line pt-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Registered Custom & Amended City Port Codes ({customPorts.length})
                </h3>
                <div className="space-y-2 max-h-[250px] overflow-y-auto pr-1">
                  {customPorts.map((cp) => (
                    <div
                      key={cp.code}
                      className="flex items-center justify-between px-4 py-3 bg-muted/40 hover:bg-muted dark:hover:bg-white/[0.04] border border-line rounded-xl transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono font-bold bg-indigo-100 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 px-2 py-1 rounded">
                          {cp.code}
                        </span>
                        <span className="text-sm font-semibold text-foreground">
                          {cp.name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          ({countriesMap[cp.country] || cp.country})
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleDeleteCustomPort(cp.code, cp.name)}
                        className="p-1.5 text-muted-foreground hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

        {/* TAB 3: CARRIER PORT OVERRIDES (NEW!) */}
        {activeTab === "overrides" && (
          <div className="border border-border bg-card rounded-3xl p-6 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-indigo-500" />
                  Carrier Port Overrides
                </h2>
                <p className="text-xs text-muted-foreground mt-1">
                  Dynamically map city keywords and LOCODEs to exact carrier autocomplete search strings (e.g. Maersk: &apos;El Dekheila&apos; &rarr; &apos;Alexandria Dekheila, Egypt&apos;). Applied live without code redeployment!
                </p>
              </div>
              <button
                onClick={fetchOverrides}
                disabled={loadingOverrides}
                className="px-3.5 py-2 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-semibold rounded-xl hover:bg-indigo-100 dark:hover:bg-indigo-500/20 transition-colors flex items-center gap-2"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingOverrides ? "animate-spin" : ""}`} />
                {loadingOverrides ? "Refreshing..." : "Refresh Overrides"}
              </button>
            </div>

            {/* Add New Override Form */}
            <form onSubmit={handleAddOverride} className="bg-muted/40 dark:bg-black/40 p-5 rounded-2xl border border-border space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
                <Plus className="w-4 h-4 text-indigo-500" />
                Add / Update Carrier Port Override
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1">
                    Select Target Carrier
                  </label>
                  <select
                    value={selectedCarrier}
                    onChange={(e) => setSelectedCarrier(e.target.value)}
                    className="w-full rounded-lg border border-input bg-card px-3 py-2.5 text-sm text-foreground shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/22 dark:bg-white/[0.04]"
                  >
                    <option value="maersk">Maersk</option>
                    <option value="one">ONE (Ocean Network Express)</option>
                    <option value="cma">CMA CGM</option>
                    <option value="hapag">Hapag-Lloyd</option>
                    <option value="msc">MSC</option>
                    <option value="greenx">GreenX</option>
                    <option value="oocl">OOCL</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1">
                    Trigger Keyword / LOCODE
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. El Dekheila or EGEDK"
                    value={overrideKey}
                    onChange={(e) => setOverrideKey(e.target.value)}
                    className="w-full rounded-lg border border-input bg-card px-3 py-2.5 text-sm text-foreground shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/22 dark:bg-white/[0.04]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1">
                    Target Autocomplete Search Text
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Alexandria Dekheila, Egypt"
                    value={overrideText}
                    onChange={(e) => setOverrideText(e.target.value)}
                    className="w-full rounded-lg border border-input bg-card px-3 py-2.5 text-sm text-foreground shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/22 dark:bg-white/[0.04]"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-1">
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-all shadow-md flex items-center gap-1.5"
                >
                  <Plus className="w-4 h-4" />
                  Save Override
                </button>
              </div>
            </form>

            {/* Filter and Search Bar */}
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between pt-2">
              <div className="flex flex-wrap gap-2">
                {["all", "maersk", "one", "cma", "hapag", "msc", "greenx", "oocl"].map((c) => (
                  <button
                    key={c}
                    onClick={() => setCarrierFilter(c)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                      carrierFilter === c
                        ? "bg-indigo-600 text-white shadow-sm"
                        : "bg-muted text-muted-foreground hover:bg-accent"
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>

              <div className="relative w-full md:w-64">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search overrides..."
                  value={overrideSearch}
                  onChange={(e) => setOverrideSearch(e.target.value)}
                  className="pl-9 pr-4 py-2 bg-muted/40 dark:bg-black/50 border border-border rounded-xl text-sm text-white focus:outline-none focus:ring-1 focus-visible:ring-ring w-full"
                />
              </div>
            </div>

            {/* Overrides Table */}
            <div className="overflow-x-auto border border-border rounded-2xl">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="border-b border-border bg-muted/40 dark:bg-black/40 text-muted-foreground text-xs font-semibold">
                    <th className="px-4 py-3">Carrier</th>
                    <th className="px-4 py-3">Trigger Keyword / Code</th>
                    <th className="px-4 py-3">Target Autocomplete Search Text</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {allOverrideList.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-muted-foreground text-sm">
                        No carrier port overrides match your current filter.
                      </td>
                    </tr>
                  ) : (
                    allOverrideList.map(({ carrier, key, text }) => (
                      <tr key={`${carrier}-${key}`} className="hover:bg-muted/40/70 dark:hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold font-mono uppercase bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
                            {carrier}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-semibold text-foreground font-mono">
                          {key}
                        </td>
                        <td className="px-4 py-3 text-foreground font-medium">
                          {text}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => handleDeleteOverride(carrier, key)}
                            className="p-1.5 text-muted-foreground hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors"
                            title="Delete Override"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB: USER SEARCH HISTORY */}
        {activeTab === "history" && (
          <div className="border border-border bg-card rounded-3xl shadow-sm overflow-hidden p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-5">
              <div>
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                  <Clock className="w-5 h-5 text-indigo-500" />
                  User Search History Log
                </h2>
                <p className="text-sm text-muted-foreground">
                  Track what each individual team member searched, on what day, and at what exact time.
                </p>
              </div>
              <button
                onClick={() => fetchSearchHistory()}
                disabled={loadingHistory}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/20 flex items-center gap-2 self-start sm:self-auto"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingHistory ? "animate-spin" : ""}`} />
                Refresh History
              </button>
            </div>

            {/* Filter Pills & Search */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider mr-1">Filter User:</span>
                <button
                  onClick={() => { setHistoryUserFilter("all"); fetchSearchHistory("all"); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    historyUserFilter === "all"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                      : "bg-muted dark:bg-gray-800 text-muted-foreground hover:bg-secondary"
                  }`}
                >
                  All Users
                </button>
                {users.map((u) => (
                  <button
                    key={u.id}
                    onClick={() => { setHistoryUserFilter(u.name); fetchSearchHistory(u.name); }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      historyUserFilter === u.name
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                        : "bg-muted dark:bg-gray-800 text-muted-foreground hover:bg-secondary"
                    }`}
                  >
                    {u.name}
                  </button>
                ))}
              </div>

              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Filter by route, port, commodity..."
                  value={historyQuery}
                  onChange={(e) => setHistoryQuery(e.target.value)}
                  className="pl-9 pr-4 py-2 bg-muted/40 dark:bg-black/50 border border-border rounded-xl text-sm text-foreground focus:outline-none focus:ring-1 focus-visible:ring-ring w-full sm:w-64"
                />
              </div>
            </div>

            {/* History Table */}
            {loadingHistory ? (
              <div className="py-16 text-center text-muted-foreground flex flex-col items-center gap-3">
                <RefreshCw className="w-8 h-8 animate-spin text-indigo-500" />
                <p className="text-sm font-medium">Loading search history logs...</p>
              </div>
            ) : searchHistory.length === 0 ? (
              <div className="py-16 text-center text-muted-foreground bg-muted/40 dark:bg-black/20 rounded-2xl border border-dashed border-border">
                <Clock className="w-10 h-10 mx-auto mb-2 text-muted-foreground/60" />
                <p className="text-base font-semibold text-foreground">No search logs found</p>
                <p className="text-xs text-muted-foreground max-w-md mx-auto mt-1">
                  When team members run rate searches on the main platform, their exact queries, timestamps, and carrier results will be logged here.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-border">
                <table className="w-full text-left text-sm text-muted-foreground">
                  <thead className="bg-muted/60 text-xs font-semibold uppercase text-muted-foreground">
                    <tr>
                      <th className="px-5 py-3.5">User</th>
                      <th className="px-5 py-3.5">Date & Time</th>
                      <th className="px-5 py-3.5">Route</th>
                      <th className="px-5 py-3.5">Cargo Specs</th>
                      <th className="px-5 py-3.5">Carriers Searched</th>
                      <th className="px-5 py-3.5">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {searchHistory
                      .filter((item) => {
                        if (!historyQuery.trim()) return true;
                        const q = historyQuery.toLowerCase();
                        return (
                          item.user_name.toLowerCase().includes(q) ||
                          item.origin.toLowerCase().includes(q) ||
                          item.destination.toLowerCase().includes(q) ||
                          (item.commodity && item.commodity.toLowerCase().includes(q))
                        );
                      })
                      .map((item) => {
                        const dateStr = item.created_at ? (item.created_at.endsWith("Z") || item.created_at.includes("+") ? item.created_at : item.created_at + "Z") : null;
                        const dateObj = dateStr ? new Date(dateStr) : null;
                        const formattedDate = dateObj
                          ? dateObj.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })
                          : "N/A";
                        const formattedTime = dateObj
                          ? dateObj.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true })
                          : "";

                        return (
                          <tr key={item.id} className="hover:bg-muted/40/50 dark:hover:bg-gray-800/40 transition-colors">
                            <td className="px-5 py-4 font-semibold text-foreground whitespace-nowrap">
                              <span className="inline-flex items-center gap-2 px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 text-xs font-bold">
                                <Users className="w-3.5 h-3.5" />
                                {item.user_name}
                              </span>
                            </td>
                            <td className="px-5 py-4 whitespace-nowrap">
                              <div className="text-xs font-semibold text-foreground">{formattedDate}</div>
                              <div className="text-[11px] text-muted-foreground font-mono">{formattedTime}</div>
                            </td>
                            <td className="px-5 py-4">
                              <div className="font-semibold text-foreground flex items-center gap-1.5 text-xs">
                                <span className="truncate max-w-[120px]">{item.origin}</span>
                                <span className="text-indigo-500 font-bold">➔</span>
                                <span className="truncate max-w-[120px]">{item.destination}</span>
                              </div>
                            </td>
                            <td className="px-5 py-4 whitespace-nowrap">
                              <div className="text-xs font-medium text-foreground">
                                {item.container_quantity}x {item.container_type}
                              </div>
                              <div className="text-[11px] text-muted-foreground">
                                {item.weight_per_container_kg ? item.weight_per_container_kg.toLocaleString() : "0"} KG • {item.commodity}
                              </div>
                            </td>
                            <td className="px-5 py-4">
                              <div className="flex flex-wrap gap-1">
                                {(item.selected_carriers || []).map((c: string) => (
                                  <span key={c} className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-muted dark:bg-gray-800 text-foreground">
                                    {c}
                                  </span>
                                ))}
                              </div>
                            </td>
                            <td className="px-5 py-4 whitespace-nowrap">
                              <span
                                className={`px-2.5 py-1 rounded-full text-[11px] font-bold uppercase ${
                                  item.status === "COMPLETED"
                                    ? "bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                                    : item.status === "FAILED"
                                    ? "bg-rose-100 dark:bg-rose-500/10 text-rose-700 dark:text-rose-400"
                                    : "bg-amber-100 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400"
                                }`}
                              >
                                {item.status} ({item.total_quotes} {item.total_quotes === 1 ? "quote" : "quotes"})
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: ROUTE RELIABILITY MATRIX */}
        {activeTab === "route_health" && (
          <div className="border border-border bg-card rounded-3xl shadow-sm overflow-hidden p-6">

            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
                  <Activity className="w-5 h-5 text-indigo-500" />
                  Route Reliability &amp; Port Match Matrix
                </h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Historical search outcomes and port resolution health per carrier.
                </p>
              </div>
              <button
                onClick={fetchRouteHealth}
                disabled={loadingHealth}
                className="px-3.5 py-2 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-semibold rounded-xl hover:bg-indigo-100 transition-colors"
              >
                {loadingHealth ? "Refreshing..." : "Refresh Matrix"}
              </button>
            </div>

            {loadingHealth && !routeHealth ? (
              <div className="py-12 text-center text-muted-foreground text-sm">
                Loading route reliability matrix...
              </div>
            ) : !routeHealth || routeHealth.routes.length === 0 ? (
              <div className="py-12 text-center text-muted-foreground text-sm">
                No route health logs recorded yet. Run carrier searches to populate route health metrics.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-border bg-muted/40 dark:bg-black/40 text-muted-foreground">
                      <th className="px-4 py-3 font-semibold">Origin -&gt; Destination Route</th>

                      {routeHealth.carriers.map((carrier) => (
                        <th key={carrier} className="px-3 py-3 font-semibold text-center">
                          {carrier}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line">
                    {routeHealth.routes.map((row, idx) => (
                      <tr key={idx} className="hover:bg-muted/40/50 dark:hover:bg-white/5 transition-colors">

                        <td className="px-4 py-3 font-medium text-foreground whitespace-nowrap">
                          {row.route_key}
                        </td>
                        {routeHealth.carriers.map((carrier) => {
                          const health = row.carrier_health[carrier];
                          if (!health) {
                            return (
                              <td key={carrier} className="px-3 py-3 text-center text-muted-foreground/60">
                                -
                              </td>
                            );
                          }
                          const isSuccess = health.status === "SUCCESS" || health.status === "COMPLETED" || (health.quotes_count && health.quotes_count > 0);
                          const isNoQuotes = health.status === "NO_QUOTES_AVAILABLE" || health.status === "NO_QUOTES";
                          const isMismatch = health.has_port_mismatch === true;
                          const isUnknownMismatch = health.has_port_mismatch === null;

                          return (
                            <td key={carrier} className="px-3 py-3 text-center">
                              <div className="flex flex-col items-center gap-1">
                                {isMismatch ? (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300 border border-amber-300 dark:border-amber-500/30 flex items-center gap-1" title={health.mismatch_warning || "Port Mismatch"}>
                                    {"⚠️ Mismatch"}
                                  </span>
                                ) : isSuccess ? (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300 whitespace-nowrap">
                                    {health.quotes_count && health.quotes_count > 0 ? `SUCCESS (${health.quotes_count} quotes)` : "SUCCESS"}
                                  </span>
                                ) : isNoQuotes ? (
                                  <span className="rounded border border-border bg-muted px-2 py-0.5 text-[10px] font-bold text-foreground">
                                    NO QUOTES
                                  </span>
                                ) : (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300" title={health.error_message || health.status}>
                                    FAILED
                                  </span>
                                )}

                                {isUnknownMismatch && !isMismatch && (
                                  <span className="text-[9px] text-muted-foreground" title="Carrier port string not returned">
                                    (Unverified)
                                  </span>
                                )}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Exchange Rates Tab */}
        {activeTab === "exchange_rates" && (
          <div className="border border-border bg-card rounded-3xl p-8 shadow-sm space-y-6">
            <div className="flex items-center justify-between flex-wrap gap-4 border-b border-border pb-4">
              <div>
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                  <span>💱 Currency Exchange Rates Management</span>
                </h2>
                <p className="text-muted-foreground text-sm mt-1">
                  View and manually update currency exchange rates relative to USD. Rates are automatically saved for currency conversions.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="text"
                  placeholder="Search currency (USD, INR, EUR)..."
                  value={rateSearch}
                  onChange={(e) => setRateSearch(e.target.value)}
                  className="bg-muted/40 dark:bg-black/50 border border-border rounded-xl px-4 py-2 text-sm text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus-visible:ring-ring w-64"
                />
                <button
                  onClick={fetchExchangeRates}
                  className="p-2.5 bg-muted hover:bg-accent text-foreground dark:text-white rounded-xl transition-colors"
                  title="Refresh rates"
                >
                  <RefreshCw className={`w-4 h-4 ${loadingRates ? "animate-spin" : ""}`} />
                </button>
              </div>
            </div>

            {loadingRates ? (
              <div className="text-center py-12 text-muted-foreground font-mono text-sm animate-pulse">
                Loading live exchange rates...
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(exchangeRates)
                  .filter(([code, info]) => !rateSearch || code.toLowerCase().includes(rateSearch.toLowerCase()) || info.name.toLowerCase().includes(rateSearch.toLowerCase()))
                  .map(([code, info]) => {
                    const isUsd = code === "USD";
                    return (
                      <div key={code} className="bg-muted/40 dark:bg-black/30 border border-border rounded-2xl p-5 space-y-3 flex flex-col justify-between hover:border-indigo-500/40 transition-colors">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-lg font-bold text-foreground font-mono">{code}</span>
                            <span className="text-xs text-muted-foreground ml-2">({info.symbol})</span>
                          </div>
                          <span className="text-xs px-2 py-0.5 rounded font-medium bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
                            {info.name}
                          </span>
                        </div>

                        <div className="space-y-1.5">
                          <label className="text-xs font-medium text-muted-foreground">
                            1 USD = X {code}
                          </label>
                          <div className="flex items-center gap-2">
                            <input
                              type="number"
                              step="any"
                              disabled={isUsd}
                              value={rateInputs[code] ?? info.rate_per_usd}
                              onChange={(e) => setRateInputs({ ...rateInputs, [code]: e.target.value })}
                              className="w-full rounded-lg border border-input bg-card px-3 py-2 font-mono text-sm font-bold text-foreground shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/22 disabled:opacity-50 dark:bg-white/[0.04]"
                            />
                            {!isUsd && (
                              <button
                                onClick={() => handleSaveRate(code)}
                                className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1 shadow-sm whitespace-nowrap"
                              >
                                <Save className="w-3.5 h-3.5" /> Save
                              </button>
                            )}
                          </div>
                        </div>

                        <div className="text-[11px] text-muted-foreground font-mono pt-1 border-t border-border flex justify-between">
                          <span>Inverse: 1 {code} = ${(info.usd_per_unit).toFixed(6)} USD</span>
                        </div>
                      </div>
                    );
                  })}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
