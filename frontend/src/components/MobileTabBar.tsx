"use client";

import { useEffect, useState, type ReactNode } from "react";
import {
  Bot,
  ChevronRight,
  History,
  LogOut,
  Mail,
  MessagesSquare,
  MonitorPlay,
  MoreHorizontal,
  OctagonX,
  RotateCcw,
  Search,
  Server,
  Shield,
  SlidersHorizontal,
} from "lucide-react";
import { BottomSheet } from "@/components/ui/bottom-sheet";
import { ThemeToggle } from "./ThemeToggle";
import { MESSAGES_UNREAD_EVENT, OPEN_ASSISTANT_EVENT, OPEN_MESSAGES_EVENT, openLiveViewer } from "@/lib/liveViewer";
import { cn } from "@/lib/utils";

export type MobileTab = "search" | "rfq";

interface MobileTabBarProps {
  active: MobileTab;
  showRfq: boolean;
  isAdmin: boolean;
  /** A search is open, so "New search" is offered. */
  hasSearch: boolean;
  liveViewerEnabled: boolean;
  assistantEnabled: boolean;
  systemText: string;
  healthy: boolean;
  onTab: (tab: MobileTab) => void;
  onHistory: () => void;
  onNewSearch: () => void;
  onForceStop: () => void;
  onOpenBackend: () => void;
  onOpenWorkspace: () => void;
  onOpenAdmin: () => void;
  onSignOut: () => void;
}

const tabClass = (on: boolean) =>
  cn(
    "relative flex flex-col items-center justify-center gap-0.5 text-[11px] transition-colors",
    on ? "font-semibold text-primary" : "font-medium text-muted-foreground",
  );

function MenuRow({ icon, label, detail, onClick, tone }: { icon: ReactNode; label: string; detail?: ReactNode; onClick: () => void; tone?: "danger" }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex min-h-12 w-full items-center gap-3 rounded-xl px-2 text-left text-[15px] hover:bg-accent",
        tone === "danger" ? "text-destructive-foreground" : "text-foreground",
      )}
    >
      <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-muted [&_svg]:size-[18px]">{icon}</span>
      <span className="min-w-0 flex-1">
        <span className="block font-medium">{label}</span>
        {detail && <span className="block truncate text-xs text-muted-foreground">{detail}</span>}
      </span>
      <ChevronRight className="size-4 text-muted-foreground" aria-hidden />
    </button>
  );
}

/**
 * Phone navigation for the v2 layout (hidden from md up): Search, RFQ, History and
 * More. More holds what the desktop header and floating buttons offer.
 */
export default function MobileTabBar(p: MobileTabBarProps) {
  const [moreOpen, setMoreOpen] = useState(false);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    const onUnread = (e: Event) => setUnread(Number((e as CustomEvent<number>).detail) || 0);
    window.addEventListener(MESSAGES_UNREAD_EVENT, onUnread);
    return () => window.removeEventListener(MESSAGES_UNREAD_EVENT, onUnread);
  }, []);

  const run = (fn: () => void) => () => {
    setMoreOpen(false);
    fn();
  };

  return (
    <>
      <nav
        aria-label="Main"
        className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-card/95 pb-[env(safe-area-inset-bottom)] backdrop-blur supports-[backdrop-filter]:bg-card/85 md:hidden"
      >
        <div className={cn("grid h-16", p.showRfq ? "grid-cols-4" : "grid-cols-3")}>
          <button type="button" aria-current={p.active === "search" ? "page" : undefined} onClick={() => p.onTab("search")} className={tabClass(p.active === "search")}>
            <Search className="size-[22px]" aria-hidden />
            Search
          </button>
          {p.showRfq && (
            <button type="button" aria-current={p.active === "rfq" ? "page" : undefined} onClick={() => p.onTab("rfq")} className={tabClass(p.active === "rfq")}>
              <Mail className="size-[22px]" aria-hidden />
              RFQ
            </button>
          )}
          <button type="button" onClick={p.onHistory} className={tabClass(false)}>
            <History className="size-[22px]" aria-hidden />
            History
          </button>
          <button type="button" onClick={() => setMoreOpen(true)} aria-haspopup="dialog" className={tabClass(false)}>
            <MoreHorizontal className="size-[22px]" aria-hidden />
            More
            {unread > 0 && (
              <span className="absolute left-1/2 top-2 ml-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-bold text-white">
                {unread > 9 ? "9+" : unread}
                <span className="sr-only"> unread messages</span>
              </span>
            )}
          </button>
        </div>
      </nav>

      <BottomSheet open={moreOpen} onClose={() => setMoreOpen(false)} title="More">
        <div className="flex flex-col gap-1">
          <MenuRow
            icon={<Server />}
            label="Connection"
            detail={
              <span className="inline-flex items-center gap-1.5">
                <span className={cn("size-2 rounded-full", p.healthy ? "bg-success" : "bg-warning")} aria-hidden />
                {p.systemText}
              </span>
            }
            onClick={run(p.onOpenBackend)}
          />
          {p.hasSearch && <MenuRow icon={<RotateCcw />} label="New search" onClick={run(p.onNewSearch)} />}
          {p.liveViewerEnabled && <MenuRow icon={<MonitorPlay />} label="Live browser tabs" detail="Watch carriers or solve a CAPTCHA" onClick={run(() => openLiveViewer())} />}
          {p.assistantEnabled && (
            <MenuRow icon={<Bot />} label="AI assistant" onClick={run(() => window.dispatchEvent(new Event(OPEN_ASSISTANT_EVENT)))} />
          )}
          <MenuRow
            icon={<MessagesSquare />}
            label="Messages"
            detail={unread > 0 ? `${unread} unread` : undefined}
            onClick={run(() => window.dispatchEvent(new Event(OPEN_MESSAGES_EVENT)))}
          />
          <MenuRow icon={<SlidersHorizontal />} label="Workspace" detail="Saved lanes, activity, layout" onClick={run(p.onOpenWorkspace)} />
          {p.isAdmin && <MenuRow icon={<Shield />} label="Admin" onClick={run(p.onOpenAdmin)} />}
          <div className="flex min-h-12 items-center gap-3 px-2">
            <span className="flex-1 text-[15px] font-medium text-foreground">Appearance</span>
            <ThemeToggle />
          </div>
          <div className="my-1 h-px bg-border" />
          <MenuRow icon={<OctagonX />} label="Force Stop" detail="Stop every search and close carrier browsers" onClick={run(() => confirm("Stop every queued and running search and close all carrier browsers?") && p.onForceStop())} tone="danger" />
          <MenuRow icon={<LogOut />} label="Sign out" onClick={run(p.onSignOut)} tone="danger" />
        </div>
      </BottomSheet>
    </>
  );
}
