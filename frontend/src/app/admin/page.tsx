"use client";

import { useState, useEffect } from "react";
import { User, Trash2, ShieldCheck, Search, Users, Activity, LogOut, Plus, Globe, Building2, Save, Sliders, RefreshCw, Clock } from "lucide-react";
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
  const [activeTab, setActiveTab] = useState<"users" | "ports" | "overrides" | "history" | "route_health">("users");

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

  useEffect(() => {
    if (authenticated) {
      if (activeTab === "users") {
        fetchUsers();
      } else if (activeTab === "route_health") {
        fetchRouteHealth();
      } else if (activeTab === "overrides") {
        fetchOverrides();
      } else if (activeTab === "history") {
        fetchSearchHistory();
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

  const fetchPortsConfig = async () => {
    try {
      const { getPortsConfig, getCountriesMap } = await import("@/lib/api");
      const config = await getPortsConfig(password);
      setPopularPorts(config.popular_ports || []);
      setBoostedCountries(config.boosted_countries || []);
      
      const countries = await getCountriesMap();
      setCountriesMap(countries);
    } catch (e) {
      console.error("Failed to fetch ports config/countries:", e);
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
    const match = newPortInput.match(/\(\s*([A-Za-z]{5})\s*\)/);
    let code = "";
    if (match) {
      code = match[1].toUpperCase();
    } else {
      const clean = newPortInput.trim().toUpperCase();
      if (clean.length === 5 && /^[A-Z]+$/.test(clean)) {
        code = clean;
      }
    }

    if (!code) {
      toast.error("Please select a valid port from the autocomplete or enter a 5-letter UN/LOCODE.");
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
      <div className="min-h-screen bg-slate-50 dark:bg-[#0A0A0A] flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl p-8 shadow-xl">
          <div className="flex flex-col items-center text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4 border border-indigo-100 dark:border-indigo-500/20">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admin Dashboard</h1>
            <p className="text-slate-500 dark:text-gray-400 text-sm mt-1">Enter password to access registry management</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <input
                type="password"
                placeholder="Admin Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-gray-800 rounded-xl px-4 py-3 text-slate-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm"
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
    <div className="min-h-screen bg-slate-50 dark:bg-[#0A0A0A] p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
              <ShieldCheck className="w-8 h-8 text-indigo-500" />
              Admin Registry
            </h1>
            <p className="text-slate-500 dark:text-gray-400 mt-1">Manage platform user access, port ranking, and live carrier search overrides.</p>
          </div>
          <button 
            onClick={() => { setAuthenticated(false); setPassword(""); }}
            className="flex items-center gap-2 px-4 py-2 bg-slate-200 dark:bg-white/10 hover:bg-slate-300 dark:hover:bg-white/20 text-slate-700 dark:text-white rounded-xl transition-colors font-medium text-sm"
          >
            <LogOut className="w-4 h-4" />
            Lock Dashboard
          </button>
        </header>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-500/10 flex items-center justify-center text-blue-600 dark:text-blue-400">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-gray-400">Total Users</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{users.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-gray-400">Active Users</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{users.filter(u => u.is_active).length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-500/10 flex items-center justify-center text-purple-600 dark:text-purple-400">
                <Sliders className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-gray-400">Carrier Port Overrides</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {Object.values(carrierOverrides).reduce((acc, obj) => acc + Object.keys(obj || {}).length, 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-4 border-b border-slate-200 dark:border-gray-800 pb-px flex-wrap">
          <button
            onClick={() => setActiveTab("users")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative ${
              activeTab === "users"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white"
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
                : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white"
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
                : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white"
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
                : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white"
            }`}
          >
            User Search History
            {activeTab === "history" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("route_health")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative ${
              activeTab === "route_health"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white"
            }`}
          >
            Route Reliability Matrix
            {activeTab === "route_health" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
            )}
          </button>
        </div>

        {/* TAB 1: USER REGISTRY */}
        {activeTab === "users" && (
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-200 dark:border-gray-800 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Registered Users</h2>
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
                    className="pl-9 pr-4 py-2 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-gray-800 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-64"
                  />
                </div>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 dark:bg-black/40 text-slate-500 dark:text-gray-400">
                  <tr>
                    <th className="px-6 py-4 font-medium">User Name</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium">Joined Date</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-gray-800">
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-slate-500 dark:text-gray-400">
                        No users registered yet.
                      </td>
                    </tr>
                  ) : (
                    users.map((user) => (
                      <tr key={user.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs">
                              {user.name.charAt(0).toUpperCase()}
                            </div>
                            <span className="font-medium text-slate-900 dark:text-white">{user.name}</span>
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
                        <td className="px-6 py-4 text-slate-500 dark:text-gray-400">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button 
                            onClick={() => deleteUser(user.id, user.name)}
                            className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors"
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* Column 1: Boosted Ports */}
            <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl p-6 shadow-sm space-y-6 flex flex-col justify-between min-h-[500px]">
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-indigo-500" />
                    Boosted Ports (Cities)
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">
                    Configure specific port codes (UN/LOCODEs) to rank higher in searches.
                  </p>
                </div>

                {/* Add Port Form */}
                <div className="flex items-end gap-3 bg-slate-50 dark:bg-black/40 p-4 rounded-2xl border border-slate-100 dark:border-gray-800">
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
                    <p className="text-sm text-slate-500 dark:text-gray-400 text-center py-8">
                      No custom ports boosted yet.
                    </p>
                  ) : (
                    popularPorts.map((code) => (
                      <div
                        key={code}
                        className="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-white/[0.02] hover:bg-slate-100 dark:hover:bg-white/[0.04] border border-slate-100 dark:border-white/5 rounded-xl transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-mono font-bold bg-blue-100 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 px-2 py-1 rounded">
                            {code}
                          </span>
                          <span className="text-sm font-medium text-slate-850 dark:text-gray-200">
                            {code.substring(0, 2) in countriesMap
                              ? `${countriesMap[code.substring(0, 2)]}`
                              : code.substring(0, 2)}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemovePort(code)}
                          className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
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
            <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl p-6 shadow-sm space-y-6 flex flex-col justify-between min-h-[500px]">
              <div className="space-y-6 w-full">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Globe className="w-5 h-5 text-indigo-500" />
                    Boosted Countries
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">
                    Prioritize all ports from these countries when matching keywords.
                  </p>
                </div>

                {/* Add Country Form */}
                <div className="flex items-end gap-3 bg-slate-50 dark:bg-black/40 p-4 rounded-2xl border border-slate-100 dark:border-gray-800">
                  <div className="flex-1 space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300">
                      Select Country to Add
                    </label>
                    <select
                      value={selectedCountry}
                      onChange={(e) => setSelectedCountry(e.target.value)}
                      className="w-full bg-white dark:bg-[#18181b] border border-slate-200 dark:border-gray-800 rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 h-[42px]"
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
                    <p className="text-sm text-slate-500 dark:text-gray-400 text-center py-8">
                      No custom countries boosted yet.
                    </p>
                  ) : (
                    boostedCountries.map((code) => (
                      <div
                        key={code}
                        className="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-white/[0.02] hover:bg-slate-100 dark:hover:bg-white/[0.04] border border-slate-100 dark:border-white/5 rounded-xl transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-mono font-bold bg-purple-100 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400 px-2 py-1 rounded">
                            {code}
                          </span>
                          <span className="text-sm font-medium text-slate-850 dark:text-gray-200">
                            {countriesMap[code] || code}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveCountry(code)}
                          className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Save Button */}
              <div className="pt-4 border-t border-slate-100 dark:border-gray-800 mt-4 w-full">
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
        )}

        {/* TAB 3: CARRIER PORT OVERRIDES (NEW!) */}
        {activeTab === "overrides" && (
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl p-6 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-gray-800 pb-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-indigo-500" />
                  Carrier Port Overrides
                </h2>
                <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">
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
            <form onSubmit={handleAddOverride} className="bg-slate-50 dark:bg-black/40 p-5 rounded-2xl border border-slate-200 dark:border-gray-800 space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-gray-300 flex items-center gap-1.5">
                <Plus className="w-4 h-4 text-indigo-500" />
                Add / Update Carrier Port Override
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 mb-1">
                    Select Target Carrier
                  </label>
                  <select
                    value={selectedCarrier}
                    onChange={(e) => setSelectedCarrier(e.target.value)}
                    className="w-full bg-white dark:bg-black/60 border border-slate-300 dark:border-gray-700 rounded-xl px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none"
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
                  <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 mb-1">
                    Trigger Keyword / LOCODE
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. El Dekheila or EGEDK"
                    value={overrideKey}
                    onChange={(e) => setOverrideKey(e.target.value)}
                    className="w-full bg-white dark:bg-black/60 border border-slate-300 dark:border-gray-700 rounded-xl px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 mb-1">
                    Target Autocomplete Search Text
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Alexandria Dekheila, Egypt"
                    value={overrideText}
                    onChange={(e) => setOverrideText(e.target.value)}
                    className="w-full bg-white dark:bg-black/60 border border-slate-300 dark:border-gray-700 rounded-xl px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none"
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
                        : "bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-gray-400 hover:bg-slate-200 dark:hover:bg-white/10"
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
                  className="pl-9 pr-4 py-2 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-gray-800 rounded-xl text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-full"
                />
              </div>
            </div>

            {/* Overrides Table */}
            <div className="overflow-x-auto border border-slate-200 dark:border-gray-800 rounded-2xl">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-gray-800 bg-slate-50 dark:bg-black/40 text-slate-500 dark:text-gray-400 text-xs font-semibold">
                    <th className="px-4 py-3">Carrier</th>
                    <th className="px-4 py-3">Trigger Keyword / Code</th>
                    <th className="px-4 py-3">Target Autocomplete Search Text</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-gray-800/80">
                  {allOverrideList.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-slate-500 dark:text-gray-400 text-sm">
                        No carrier port overrides match your current filter.
                      </td>
                    </tr>
                  ) : (
                    allOverrideList.map(({ carrier, key, text }) => (
                      <tr key={`${carrier}-${key}`} className="hover:bg-slate-50/70 dark:hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold font-mono uppercase bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
                            {carrier}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-semibold text-slate-900 dark:text-white font-mono">
                          {key}
                        </td>
                        <td className="px-4 py-3 text-slate-700 dark:text-gray-200 font-medium">
                          {text}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => handleDeleteOverride(carrier, key)}
                            className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors"
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
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl shadow-sm overflow-hidden p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-gray-800 pb-5">
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Clock className="w-5 h-5 text-indigo-500" />
                  User Search History Log
                </h2>
                <p className="text-sm text-slate-500 dark:text-gray-400">
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
                <span className="text-xs font-bold text-slate-500 dark:text-gray-400 uppercase tracking-wider mr-1">Filter User:</span>
                <button
                  onClick={() => { setHistoryUserFilter("all"); fetchSearchHistory("all"); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    historyUserFilter === "all"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                      : "bg-slate-100 dark:bg-gray-800 text-slate-600 dark:text-gray-300 hover:bg-slate-200"
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
                        : "bg-slate-100 dark:bg-gray-800 text-slate-600 dark:text-gray-300 hover:bg-slate-200"
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
                  className="pl-9 pr-4 py-2 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-gray-800 rounded-xl text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-full sm:w-64"
                />
              </div>
            </div>

            {/* History Table */}
            {loadingHistory ? (
              <div className="py-16 text-center text-slate-400 dark:text-gray-500 flex flex-col items-center gap-3">
                <RefreshCw className="w-8 h-8 animate-spin text-indigo-500" />
                <p className="text-sm font-medium">Loading search history logs...</p>
              </div>
            ) : searchHistory.length === 0 ? (
              <div className="py-16 text-center text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-black/20 rounded-2xl border border-dashed border-slate-200 dark:border-gray-800">
                <Clock className="w-10 h-10 mx-auto text-slate-300 dark:text-gray-600 mb-2" />
                <p className="text-base font-semibold text-slate-700 dark:text-gray-300">No search logs found</p>
                <p className="text-xs text-slate-400 dark:text-gray-500 max-w-md mx-auto mt-1">
                  When team members run rate searches on the main platform, their exact queries, timestamps, and carrier results will be logged here.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-gray-800">
                <table className="w-full text-left text-sm text-slate-600 dark:text-gray-300">
                  <thead className="bg-slate-50 dark:bg-[#18181b] text-xs uppercase text-slate-500 dark:text-gray-400 font-semibold">
                    <tr>
                      <th className="px-5 py-3.5">User</th>
                      <th className="px-5 py-3.5">Date & Time</th>
                      <th className="px-5 py-3.5">Route</th>
                      <th className="px-5 py-3.5">Cargo Specs</th>
                      <th className="px-5 py-3.5">Carriers Searched</th>
                      <th className="px-5 py-3.5">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-gray-800">
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
                          <tr key={item.id} className="hover:bg-slate-50/50 dark:hover:bg-gray-800/40 transition-colors">
                            <td className="px-5 py-4 font-semibold text-slate-900 dark:text-white whitespace-nowrap">
                              <span className="inline-flex items-center gap-2 px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 text-xs font-bold">
                                <Users className="w-3.5 h-3.5" />
                                {item.user_name}
                              </span>
                            </td>
                            <td className="px-5 py-4 whitespace-nowrap">
                              <div className="text-xs font-semibold text-slate-900 dark:text-gray-200">{formattedDate}</div>
                              <div className="text-[11px] text-slate-400 dark:text-gray-500 font-mono">{formattedTime}</div>
                            </td>
                            <td className="px-5 py-4">
                              <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-1.5 text-xs">
                                <span className="truncate max-w-[120px]">{item.origin}</span>
                                <span className="text-indigo-500 font-bold">➔</span>
                                <span className="truncate max-w-[120px]">{item.destination}</span>
                              </div>
                            </td>
                            <td className="px-5 py-4 whitespace-nowrap">
                              <div className="text-xs font-medium text-slate-800 dark:text-gray-300">
                                {item.container_quantity}x {item.container_type}
                              </div>
                              <div className="text-[11px] text-slate-400 dark:text-gray-500">
                                {item.weight_per_container_kg ? item.weight_per_container_kg.toLocaleString() : "0"} KG • {item.commodity}
                              </div>
                            </td>
                            <td className="px-5 py-4">
                              <div className="flex flex-wrap gap-1">
                                {(item.selected_carriers || []).map((c: string) => (
                                  <span key={c} className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 dark:bg-gray-800 text-slate-700 dark:text-gray-300">
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
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl shadow-sm overflow-hidden p-6">

            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-indigo-500" />
                  Route Reliability &amp; Port Match Matrix
                </h2>
                <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">
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
              <div className="py-12 text-center text-slate-500 dark:text-gray-400 text-sm">
                Loading route reliability matrix...
              </div>
            ) : !routeHealth || routeHealth.routes.length === 0 ? (
              <div className="py-12 text-center text-slate-500 dark:text-gray-400 text-sm">
                No route health logs recorded yet. Run carrier searches to populate route health metrics.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-gray-800 bg-slate-50 dark:bg-black/40 text-slate-500 dark:text-gray-400">
                      <th className="px-4 py-3 font-semibold">Origin -&gt; Destination Route</th>

                      {routeHealth.carriers.map((carrier) => (
                        <th key={carrier} className="px-3 py-3 font-semibold text-center">
                          {carrier}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-gray-800/60">
                    {routeHealth.routes.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-white/5 transition-colors">

                        <td className="px-4 py-3 font-medium text-slate-900 dark:text-white whitespace-nowrap">
                          {row.route_key}
                        </td>
                        {routeHealth.carriers.map((carrier) => {
                          const health = row.carrier_health[carrier];
                          if (!health) {
                            return (
                              <td key={carrier} className="px-3 py-3 text-center text-slate-400 dark:text-gray-600">
                                -
                              </td>
                            );
                          }
                          const isSuccess = health.status === "SUCCESS";
                          const isNoQuotes = health.status === "NO_QUOTES_AVAILABLE";
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

                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300">
                                    SUCCESS
                                  </span>
                                ) : isNoQuotes ? (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-gray-300">
                                    NO QUOTES
                                  </span>
                                ) : (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300" title={health.error_message || health.status}>
                                    FAILED
                                  </span>
                                )}

                                {isUnknownMismatch && !isMismatch && (
                                  <span className="text-[9px] text-gray-400 dark:text-gray-500" title="Carrier port string not returned">
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

      </div>
    </div>
  );
}
