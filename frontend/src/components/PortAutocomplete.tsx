"use client";
import { useState, useEffect, useRef } from "react";
import { getPortSuggestions } from "@/lib/api";

interface PortAutocompleteProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
}

export default function PortAutocomplete({ label, value, onChange, placeholder, required }: PortAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (value.length >= 2) {
        setIsSearching(true);
        try {
          const results = await getPortSuggestions(value);
          setSuggestions(results);
          if (results.length > 0) setShowDropdown(true);
        } catch (err) {
          console.error("Failed to fetch suggestions", err);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSuggestions([]);
        setShowDropdown(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (port: any) => {
    // Format: "Port Name (CODE), Country"
    const displayValue = `${port.name} (${port.code})`;
    onChange(displayValue);
    setShowDropdown(false);
  };

  const inputClass =
    "w-full px-4 py-2.5 bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-white/30 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all";
  const labelClass = "block text-sm font-medium text-slate-700 dark:text-white/80 mb-1.5";

  return (
    <div className="relative" ref={containerRef}>
      <label className={labelClass}>{label}</label>
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={inputClass}
          placeholder={placeholder}
          required={required}
          onFocus={() => value.length >= 2 && suggestions.length > 0 && setShowDropdown(true)}
        />
        {isSearching && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-slate-200 dark:border-white/20 border-t-blue-500 rounded-full animate-spin" />
          </div>
        )}
      </div>

      {showDropdown && suggestions.length > 0 && (
        <div className="absolute z-50 left-0 right-0 mt-2 bg-white dark:bg-[#1a1c2e] border border-slate-200 dark:border-white/10 rounded-xl shadow-2xl overflow-hidden backdrop-blur-xl max-h-64 overflow-y-auto">
          {suggestions.map((port) => (
            <button
              key={port.code}
              type="button"
              onClick={() => handleSelect(port)}
              className="w-full px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-white/5 border-b border-slate-100 dark:border-white/5 last:border-0 transition-colors flex flex-col gap-0.5"
            >
              <div className="flex items-center justify-between">
                <span className="text-slate-900 dark:text-white font-medium text-sm">{port.name}</span>
                <span className="text-blue-600 dark:text-blue-400 font-mono text-[10px] bg-blue-100 dark:bg-blue-500/10 px-1.5 py-0.5 rounded uppercase">{port.code}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-500 dark:text-white/40 text-xs">{port.country_name || port.country}</span>
                {port.status === 'AI' && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" title="Approved" />}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
