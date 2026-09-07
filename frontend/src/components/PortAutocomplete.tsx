"use client";
import { useState, useEffect, useRef } from "react";
import { getPortSuggestions } from "@/lib/api";
import { Input, Label } from "@/components/ui/input";
import { Anchor, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

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
  const justSelectedRef = useRef(false);

  useEffect(() => {
    if (justSelectedRef.current) {
      justSelectedRef.current = false;
      return;
    }

    const timer = setTimeout(async () => {
      if (value.length >= 2) {
        setIsSearching(true);
        try {
          const results = await getPortSuggestions(value);
          setSuggestions(results);
          if (results.length > 0 && !justSelectedRef.current) {
            setShowDropdown(true);
          }
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
    justSelectedRef.current = true;
    // Format: 'Kochi, India [INCOK]' to lock in exact port and country
    const country = port.country_name || port.country;
    const displayValue = country ? `${port.name}, ${country} [${port.code}]` : `${port.name} [${port.code}]`;
    onChange(displayValue);
    setShowDropdown(false);
  };

  const fieldId = `port-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;

  // Sibling form rows animate in with `fade-in-up`, whose held transform gives
  // them their own stacking context — so the open dropdown has to be lifted
  // above them explicitly or it renders behind the next row.
  return (
    <div className={cn("relative", showDropdown && "z-50")} ref={containerRef}>
      <Label htmlFor={fieldId}>{label}</Label>
      <div className="relative">
        <Anchor className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          id={fieldId}
          type="text"
          value={value}
          onChange={(e) => {
            justSelectedRef.current = false;
            onChange(e.target.value);
          }}
          className="min-h-[44px] pl-10 pr-10"
          placeholder={placeholder}
          required={required}
          autoComplete="off"
          role="combobox"
          aria-expanded={showDropdown && suggestions.length > 0}
          aria-autocomplete="list"
          onFocus={() => !justSelectedRef.current && value.length >= 2 && suggestions.length > 0 && setShowDropdown(true)}
        />
        {isSearching && (
          <div className="absolute right-3.5 top-1/2 -translate-y-1/2">
            <Loader2 className="size-4 animate-spin text-primary" />
          </div>
        )}
      </div>

      {showDropdown && suggestions.length > 0 && (
        <div
          role="listbox"
          className="animate-dropdown-in absolute left-0 right-0 z-50 mt-2 max-h-64 overflow-y-auto overflow-x-hidden rounded-xl border border-border bg-popover shadow-card-hover backdrop-blur-xl"
        >
          {suggestions.map((port, index) => (
            <button
              key={port.code}
              type="button"
              role="option"
              aria-selected={false}
              onClick={() => handleSelect(port)}
              className="animate-fade-in-up flex w-full flex-col gap-0.5 border-b border-line px-4 py-2.5 text-left transition-colors last:border-0 hover:bg-accent"
              style={{ animationDelay: `${index * 0.03}s` }}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate text-sm font-medium text-foreground">{port.name}</span>
                <span className="shrink-0 rounded border border-primary/20 bg-primary/10 px-1.5 py-0.5 font-mono text-[10px] uppercase text-primary">{port.code}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{port.country_name || port.country}</span>
                {port.status === 'AI' && <span className="size-1.5 rounded-full bg-success" title="Approved" />}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
