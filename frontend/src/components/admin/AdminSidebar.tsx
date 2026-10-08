"use client";

import type { LucideIcon } from "lucide-react";
import { Activity, ArrowLeftRight, History, LayoutDashboard, ListOrdered, MapPin, Power, Table2, Users } from "lucide-react";
import { cn } from "@/lib/utils";

export type AdminSection =
  | "overview"
  | "analytics"
  | "users"
  | "history"
  | "overrides"
  | "ports"
  | "exchange_rates"
  | "route_health"
  | "carriers";

interface NavItem {
  id: AdminSection;
  label: string;
  icon: LucideIcon;
}

const GROUPS: Array<{ label: string | null; items: NavItem[] }> = [
  { label: null, items: [{ id: "overview", label: "Overview", icon: LayoutDashboard }] },
  {
    label: "People",
    items: [
      { id: "users", label: "Users & approvals", icon: Users },
      { id: "history", label: "Search history", icon: History },
    ],
  },
  {
    label: "Search data",
    items: [
      { id: "overrides", label: "Port name fixes", icon: MapPin },
      { id: "ports", label: "Port ranking", icon: ListOrdered },
      { id: "exchange_rates", label: "Exchange rates", icon: ArrowLeftRight },
    ],
  },
  {
    label: "Health",
    items: [
      { id: "carriers", label: "Carriers on / off", icon: Power },
      { id: "analytics", label: "Carrier & lane analytics", icon: Activity },
      { id: "route_health", label: "Route reliability", icon: Table2 },
    ],
  },
];

interface AdminSidebarProps {
  active: AdminSection;
  onSelect: (section: AdminSection) => void;
  /** Shown as a count next to the section, e.g. pending sign-ups on Users. */
  badges?: Partial<Record<AdminSection, number>>;
}

/**
 * v2 admin navigation: grouped sections in a sticky sidebar on wide screens, and a
 * single scrollable row of the same items on narrow ones.
 */
export default function AdminSidebar({ active, onSelect, badges = {} }: AdminSidebarProps) {
  return (
    <nav
      aria-label="Admin sections"
      className="-mx-4 flex gap-1 overflow-x-auto px-4 pb-1 lg:sticky lg:top-6 lg:mx-0 lg:w-60 lg:shrink-0 lg:flex-col lg:gap-5 lg:overflow-visible lg:px-0"
    >
      {GROUPS.map((group, gi) => (
        <div key={gi} className="flex shrink-0 gap-1 lg:flex-col lg:gap-0.5">
          {group.label && (
            <p className="hidden px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground lg:block">
              {group.label}
            </p>
          )}
          {group.items.map(({ id, label, icon: Icon }) => {
            const isActive = active === id;
            const count = badges[id] ?? 0;
            return (
              <button
                key={id}
                type="button"
                onClick={() => onSelect(id)}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "flex min-h-10 shrink-0 items-center gap-2.5 whitespace-nowrap rounded-lg px-3 text-left text-sm transition-colors",
                  isActive
                    ? "bg-primary/10 font-semibold text-primary"
                    : "font-medium text-muted-foreground hover:bg-accent hover:text-foreground",
                )}
              >
                <Icon className="size-4 shrink-0" aria-hidden />
                <span className="lg:flex-1">{label}</span>
                {count > 0 && (
                  <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-warning/15 px-1.5 text-xs font-bold text-warning-foreground">
                    {count}
                    <span className="sr-only"> waiting</span>
                  </span>
                )}
              </button>
            );
          })}
        </div>
      ))}
    </nav>
  );
}
