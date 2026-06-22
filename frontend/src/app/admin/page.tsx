"use client";

import { useState, useEffect } from "react";
import { User, Trash2, ShieldCheck, Search, Users, Activity, LogOut, Plus, Globe, Building2, Save } from "lucide-react";
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

  // Ports config state
  const [popularPorts, setPopularPorts] = useState<string[]>([]);
  const [boostedCountries, setBoostedCountries] = useState<string[]>([]);
  const [countriesMap, setCountriesMap] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<"users" | "ports">("users");
  const [savingConfig, setSavingConfig] = useState(false);
  const [newPortInput, setNewPortInput] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("");

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
    } catch (err) {
      setError("Incorrect admin password.");
    } finally {
      setLoading(false);
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
      alert("Please select or type a valid 5-letter port code.");
      return;
    }
    
    if (popularPorts.includes(code)) {
      alert("This port is already boosted.");
      return;
    }
    
    setPopularPorts([...popularPorts, code]);
    setNewPortInput("");
  };

  const handleRemovePort = (code: string) => {
    setPopularPorts(popularPorts.filter((p) => p !== code));
  };

  const handleAddCountry = () => {
    if (!selectedCountry) {
      alert("Please select a country to add.");
      return;
    }
    
    if (boostedCountries.includes(selectedCountry)) {
      alert("This country is already boosted.");
      return;
    }
    
    setBoostedCountries([...boostedCountries, selectedCountry]);
    setSelectedCountry("");
  };

  const handleRemoveCountry = (code: string) => {
    setBoostedCountries(boostedCountries.filter((c) => c !== code));
  };

  const handleSaveConfig = async () => {
    setSavingConfig(true);
    try {
      const { savePortsConfig } = await import("@/lib/api");
      await savePortsConfig(
        {
          popular_ports: popularPorts,
          boosted_countries: boostedCountries,
        },
        password
      );
      toast.success("Port ranking configuration saved successfully!");
    } catch (e: any) {
      toast.error(e.message || "Failed to save configuration.");
    } finally {
      setSavingConfig(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/api/users`);
      if (res.ok) {
        setUsers(await res.json());
      }
    } catch (e) {
      console.error("Failed to fetch users");
    }
  };

  const deleteUser = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete user: ${name}?`)) return;
    try {
      await fetch(`${API_URL}/api/users/${id}`, { method: "DELETE" });
      setUsers(users.filter((u) => u.id !== id));
    } catch (e) {
      alert("Failed to delete user.");
    }
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-[#0A0A0A]">
        <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl w-full max-w-md p-8 shadow-2xl mx-4 animate-scale-in-spring">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-slate-800 flex items-center justify-center text-white shadow-xl animate-float-gentle animate-glow-pulse">
              <ShieldCheck className="w-8 h-8" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-center text-slate-900 dark:text-white mb-2 animate-fade-in-up stagger-2">Admin Dashboard</h2>
          <p className="text-center text-slate-500 dark:text-gray-400 mb-8 animate-fade-in-up stagger-3">Enter master password to access user registry.</p>
          
          <form onSubmit={handleLogin} className="space-y-4 animate-fade-in-up stagger-4">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Master Password"
              autoFocus
              className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus-glow"
            />
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl px-4 py-3 font-medium transition-colors disabled:opacity-50 btn-interactive btn-gradient shine-on-hover"
            >
              {loading ? "Verifying..." : "Access Dashboard"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0A0A0A] p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="flex items-center justify-between animate-fade-in-down">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
              <ShieldCheck className="w-8 h-8 text-indigo-500" />
              Admin Registry
            </h1>
            <p className="text-slate-500 dark:text-gray-400 mt-1">Manage user access and registry across the platform.</p>
          </div>
          <button 
            onClick={() => { setAuthenticated(false); setPassword(""); }}
            className="flex items-center gap-2 px-4 py-2 bg-slate-200 dark:bg-white/10 hover:bg-slate-300 dark:hover:bg-white/20 text-slate-700 dark:text-white rounded-xl transition-colors font-medium text-sm"
          >
            <LogOut className="w-4 h-4" />
            Lock Dashboard
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm animate-fade-in-up stagger-1">
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
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm animate-fade-in-up stagger-2">
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
        </div>

        <div className="flex gap-4 border-b border-slate-200 dark:border-gray-800 pb-px">
          <button
            onClick={() => setActiveTab("users")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative btn-interactive ${
              activeTab === "users"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white"
            }`}
          >
            User Registry
            {activeTab === "users" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full animate-tab-slide" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("ports")}
            className={`pb-4 px-2 font-semibold text-sm transition-all relative btn-interactive ${
              activeTab === "ports"
                ? "text-indigo-600 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white"
            }`}
          >
            Port Ranking Config
            {activeTab === "ports" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full animate-tab-slide" />
            )}
          </button>
        </div>

        {activeTab === "users" ? (
          <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-200 dark:border-gray-800 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Registered Users</h2>
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input 
                  type="text" 
                  placeholder="Search users..." 
                  className="pl-9 pr-4 py-2 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-gray-800 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 w-64 focus-glow"
                />
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
                    users.map((user, index) => (
                      <tr key={user.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-all row-enter" style={{ animationDelay: `${index * 0.04}s` }}>
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
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Column 1: Boosted Ports */}
            <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl p-6 shadow-sm space-y-6 flex flex-col justify-between min-h-[500px] animate-fade-in-up stagger-1">
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
                    popularPorts.map((code, index) => (
                      <div
                        key={code}
                        className="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-white/[0.02] hover:bg-slate-100 dark:hover:bg-white/[0.04] border border-slate-100 dark:border-white/5 rounded-xl transition-all animate-fade-in-up"
                        style={{ animationDelay: `${index * 0.05}s` }}
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
            <div className="bg-white dark:bg-[#121212] border border-slate-200 dark:border-gray-800 rounded-3xl p-6 shadow-sm space-y-6 flex flex-col justify-between min-h-[500px] animate-fade-in-up stagger-2">
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
                    <label className="block text-xs font-medium text-slate-700 dark:text-white/80">Select Country to Add</label>
                    <select
                      value={selectedCountry}
                      onChange={(e) => setSelectedCountry(e.target.value)}
                      className="w-full px-4 py-2 bg-slate-100 dark:bg-black/50 border border-slate-200 dark:border-gray-800 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:border-indigo-500/50 transition-all h-[42px] focus-glow"
                    >
                      <option value="" className="text-slate-500 dark:bg-[#121212]">-- Select Country --</option>
                      {Object.entries(countriesMap)
                        .sort((a, b) => a[1].localeCompare(b[1]))
                        .map(([code, name]) => (
                          <option key={code} value={code} className="dark:bg-[#121212] text-slate-900 dark:text-white">
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

                {/* List of Countries */}
                <div className="max-h-[250px] overflow-y-auto space-y-2 pr-1">
                  {boostedCountries.length === 0 ? (
                    <p className="text-sm text-slate-500 dark:text-gray-400 text-center py-8">
                      No custom countries boosted yet.
                    </p>
                  ) : (
                    boostedCountries.map((code, index) => (
                      <div
                        key={code}
                        className="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-white/[0.02] hover:bg-slate-100 dark:hover:bg-white/[0.04] border border-slate-100 dark:border-white/5 rounded-xl transition-all animate-fade-in-up"
                        style={{ animationDelay: `${index * 0.05}s` }}
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
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl px-4 py-3 font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/15 btn-interactive btn-gradient shine-on-hover"
                >
                  <Save className="w-5 h-5" />
                  {savingConfig ? "Saving Configuration..." : "Save Config Settings"}
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
