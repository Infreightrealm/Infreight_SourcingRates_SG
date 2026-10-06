"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, LogOut, OctagonX, RotateCcw, SlidersHorizontal } from "lucide-react";
import StatusBadge from "./StatusBadge";
import { ThemeToggle } from "./ThemeToggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AppHeaderProps {
  /** The current search's status, or null when no search is open. */
  searchStatus: string | null;
  mockMode: boolean | null;
  backendLabel: string;
  isPrimaryBackend: boolean;
  userName: string | null;
  userRole: string | null;
  userAvatar: string | null;
  showRfq: boolean;
  onNewSearch: () => void;
  onForceStop: () => void;
  onOpenBackend: () => void;
  onOpenWorkspace: () => void;
  onOpenHistory: () => void;
  onOpenAdmin: () => void;
  onSignOut: () => void;
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join("");
}

const navItem =
  "inline-flex min-h-9 shrink-0 items-center whitespace-nowrap rounded-lg px-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground";

/**
 * v2 header: brand and navigation on the left; one system-status pill, the open
 * search's status, New search / Force Stop, Workspace, theme and a user menu on
 * the right. Classic keeps its own header in page.tsx.
 */
export default function AppHeader(p: AppHeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const onPointer = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMenuOpen(false);
    document.addEventListener("mousedown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [menuOpen]);

  const healthy = p.mockMode === false && p.isPrimaryBackend;
  const systemText = `${p.mockMode === null ? "Connecting" : p.mockMode ? "Mock mode" : "Live"} · ${p.backendLabel.replace(" (Configure Server)", "")}`;
  const isAdmin = p.userRole === "admin";

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/85">
      <div className="mx-auto flex max-w-[98%] flex-wrap items-center gap-x-6 gap-y-2 px-4 py-2.5 sm:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg border border-border bg-background p-1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/infreight_logo.png" alt="" className="size-full object-contain" />
          </div>
          <p className="whitespace-nowrap text-base font-bold text-foreground">
            Infreight <span className="font-medium text-muted-foreground">Rate Sourcing</span>
          </p>
        </div>

        <nav
          aria-label="Primary"
          className="order-3 -mx-1 flex w-full items-center gap-1 overflow-x-auto px-1 md:order-none md:mx-0 md:w-auto md:flex-1 md:px-0"
        >
          <button
            type="button"
            aria-current="page"
            onClick={() => (p.searchStatus ? p.onNewSearch() : window.scrollTo({ top: 0, behavior: "smooth" }))}
            className={cn(navItem, "bg-primary/10 font-semibold text-primary hover:bg-primary/15 hover:text-primary")}
          >
            Search
          </button>
          {p.showRfq && (
            <a href="#rfq" className={navItem}>
              RFQ from email
            </a>
          )}
          <button type="button" onClick={p.onOpenHistory} className={navItem}>
            History
          </button>
          {isAdmin && (
            <button type="button" onClick={p.onOpenAdmin} className={navItem}>
              Admin
            </button>
          )}
        </nav>

        <div className="ml-auto flex flex-wrap items-center justify-end gap-2">
          <button
            type="button"
            onClick={p.onOpenBackend}
            title="Backend connection: click to configure the server or reconnect"
            className={cn(
              "inline-flex min-h-9 items-center gap-2 rounded-full border px-3 text-xs font-semibold transition-colors",
              healthy
                ? "border-success/30 bg-success/10 text-success-foreground hover:bg-success/15"
                : "border-warning/35 bg-warning/12 text-warning-foreground hover:bg-warning/20",
            )}
          >
            <span className={cn("size-2 rounded-full", healthy ? "bg-success" : "animate-pulse bg-warning")} aria-hidden />
            {systemText}
          </button>

          {p.searchStatus && <StatusBadge status={p.searchStatus} size="md" />}

          {p.searchStatus && (
            <Button variant="outline" size="sm" onClick={p.onNewSearch}>
              <RotateCcw className="size-3.5" />
              New search
            </Button>
          )}
          <Button variant="destructive" size="sm" onClick={p.onForceStop} title="Stop every queued and running search and close all carrier browsers">
            <OctagonX className="size-3.5" />
            Force Stop
          </Button>

          <Button variant="ghost" size="icon" onClick={p.onOpenWorkspace} aria-label="Workspace: activity, saved lanes, appearance and panels" title="Workspace">
            <SlidersHorizontal className="size-4" />
          </Button>
          <ThemeToggle />

          {p.userName && (
            <div ref={menuRef} className="relative">
              <button
                type="button"
                aria-haspopup="menu"
                aria-expanded={menuOpen}
                onClick={() => setMenuOpen((o) => !o)}
                className="inline-flex min-h-9 items-center gap-2 rounded-full border border-border bg-background py-1 pl-1 pr-2.5 text-sm font-medium text-foreground hover:bg-accent"
              >
                {p.userAvatar ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={p.userAvatar} alt="" className="size-7 rounded-full object-cover" />
                ) : (
                  <span className="flex size-7 items-center justify-center rounded-full bg-foreground text-[11px] font-bold text-background">
                    {initials(p.userName)}
                  </span>
                )}
                <span className="hidden sm:inline">{p.userName}</span>
                <ChevronDown className="size-3.5 text-muted-foreground" aria-hidden />
              </button>
              {menuOpen && (
                <div role="menu" className="absolute right-0 top-full z-40 mt-2 w-56 rounded-xl border border-border bg-popover p-1.5 shadow-card">
                  <div className="px-2.5 py-2">
                    <p className="text-sm font-semibold text-foreground">{p.userName}</p>
                    <p className="text-xs text-muted-foreground">{isAdmin ? "Administrator" : "Team member"}</p>
                  </div>
                  <div className="my-1 h-px bg-border" />
                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => {
                      setMenuOpen(false);
                      p.onSignOut();
                    }}
                    className="flex min-h-10 w-full items-center gap-2 rounded-lg px-2.5 text-left text-sm text-destructive-foreground hover:bg-destructive/10"
                  >
                    <LogOut className="size-4" />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
