"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import { MoreHorizontal, RefreshCw, Search, UserCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface AdminUserRecord {
  id: string;
  username?: string;
  display_name?: string;
  name?: string;
  role: "admin" | "user";
  status: "active" | "pending" | "disabled";
  is_active: boolean;
  created_at?: string;
  last_login_at?: string;
  needs_password?: boolean;
}

export interface AuditEntry {
  id: string;
  at: string | null;
  actor: string;
  action: string;
  detail: string;
}

export type UserAction = "reject" | "disable" | "enable" | "role" | "password" | "delete";

interface AdminUsersProps {
  users: AdminUserRecord[];
  currentUser: { id?: string; username?: string } | null;
  audit: AuditEntry[];
  /** Approves a pending request and, when `role` is admin, promotes it too. */
  onApprove: (userId: string, role: "admin" | "user") => void;
  /** The existing confirm/prompt flow in the admin page. */
  onAction: (userId: string, action: UserAction, payload?: Record<string, unknown>) => void;
  onRefresh: () => void;
  onResetAllSessions: () => void;
  /** Opens search history filtered to this person (matched by username, as the history filter is). */
  onShowSearches: (userKey: string) => void;
}

type Filter = "all" | "active" | "disabled";

/** Audit actions that are changes to people; logins and sign-ups are left out. */
const PEOPLE_ACTIONS = new Set([
  "approve_user",
  "reject_user",
  "disable_user",
  "enable_user",
  "change_role",
  "reset_password",
  "delete_user",
  "reset_all_users",
]);

const nameOf = (u: AdminUserRecord) => u.display_name || u.name || u.username || "Unnamed";
const isActive = (u: AdminUserRecord) => u.status === "active" && u.is_active !== false;

function initials(name: string) {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0]!.toUpperCase())
      .join("") || "?"
  );
}

/** Backend timestamps are UTC but may lack a zone suffix. */
function parseUtc(iso: string | null | undefined): Date | null {
  if (!iso) return null;
  const d = new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : `${iso}Z`);
  return Number.isNaN(d.getTime()) ? null : d;
}

function ago(iso: string | null | undefined, never = "never"): string {
  const d = parseUtc(iso);
  if (!d) return never;
  const mins = Math.round((Date.now() - d.getTime()) / 60000);
  if (mins < 2) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours} h ago`;
  const days = Math.round(hours / 24);
  if (days === 1) return "yesterday";
  if (days < 45) return `${days} days ago`;
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

function Avatar({ name, muted }: { name: string; muted?: boolean }) {
  return (
    <span
      aria-hidden
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-full text-[11px] font-bold",
        muted ? "bg-muted text-muted-foreground" : "bg-foreground text-background",
      )}
    >
      {initials(name)}
    </span>
  );
}

/** Height of the open row menu (5 items, a divider, padding), for choosing up or down. */
const MENU_HEIGHT = 230;

/** "…" menu for one person: role, password, their searches, disable, delete. */
function RowMenu({
  user,
  open,
  onOpenChange,
  onAction,
  onShowSearches,
}: {
  user: AdminUserRecord;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAction: AdminUsersProps["onAction"];
  onShowSearches: AdminUsersProps["onShowSearches"];
}) {
  const ref = useRef<HTMLDivElement>(null);
  // The table scrolls and its card clips overflow, so the menu is placed against the
  // viewport: under the button, or above it when the row is near the bottom.
  const [place, setPlace] = useState<CSSProperties>({});

  const toggle = () => {
    if (!open && ref.current) {
      const r = ref.current.getBoundingClientRect();
      const right = window.innerWidth - r.right;
      setPlace(r.bottom + MENU_HEIGHT + 8 > window.innerHeight ? { bottom: window.innerHeight - r.top + 4, right } : { top: r.bottom + 4, right });
    }
    onOpenChange(!open);
  };

  useEffect(() => {
    if (!open) return;
    const onPointer = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) onOpenChange(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onOpenChange(false);
    const close = () => onOpenChange(false);
    document.addEventListener("mousedown", onPointer);
    document.addEventListener("keydown", onKey);
    window.addEventListener("scroll", close, true);
    window.addEventListener("resize", close);
    return () => {
      document.removeEventListener("mousedown", onPointer);
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("scroll", close, true);
      window.removeEventListener("resize", close);
    };
  }, [open, onOpenChange]);

  const run = (fn: () => void) => () => {
    onOpenChange(false);
    fn();
  };
  const item = "flex min-h-10 w-full items-center rounded-lg px-2.5 text-left text-sm hover:bg-accent";

  return (
    <div ref={ref} className="relative inline-block">
      <Button
        variant="ghost"
        size="icon"
        aria-label={`More actions for ${nameOf(user)}`}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={toggle}
        className={cn(open && "bg-accent text-foreground")}
      >
        <MoreHorizontal className="size-4" />
      </Button>
      {open && (
        <div role="menu" style={place} className="fixed z-50 w-56 rounded-xl border border-border bg-popover p-1.5 text-left shadow-card">
          <button
            type="button"
            role="menuitem"
            className={item}
            onClick={run(() => onAction(user.id, "role", { role: user.role === "admin" ? "user" : "admin" }))}
          >
            {user.role === "admin" ? "Make team member" : "Make admin"}
          </button>
          <button type="button" role="menuitem" className={item} onClick={run(() => onAction(user.id, "password"))}>
            {user.needs_password ? "Set password" : "Reset password"}
          </button>
          <button type="button" role="menuitem" className={item} onClick={run(() => onShowSearches(user.username || user.name || user.display_name || ""))}>
            See their searches
          </button>
          <div className="my-1 h-px bg-border" />
          {isActive(user) ? (
            <button type="button" role="menuitem" className={cn(item, "text-destructive-foreground")} onClick={run(() => onAction(user.id, "disable"))}>
              Disable and sign out
            </button>
          ) : (
            <button type="button" role="menuitem" className={item} onClick={run(() => onAction(user.id, "enable"))}>
              Re-enable
            </button>
          )}
          <button type="button" role="menuitem" className={cn(item, "text-destructive-foreground")} onClick={run(() => onAction(user.id, "delete"))}>
            Delete account…
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * v2 Users & approvals: pending sign-ups with Approve/Decline and a role, everyone
 * else in one table with the rarer actions in a per-row menu, and recent changes
 * to people from the audit log.
 */
export default function AdminUsers({
  users,
  currentUser,
  audit,
  onApprove,
  onAction,
  onRefresh,
  onResetAllSessions,
  onShowSearches,
}: AdminUsersProps) {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [pendingRoles, setPendingRoles] = useState<Record<string, "admin" | "user">>({});

  const pending = users.filter((u) => u.status === "pending");
  const people = users.filter((u) => u.status !== "pending");
  const term = query.trim().toLowerCase();
  const shown = people.filter((u) => {
    if (filter === "active" && !isActive(u)) return false;
    if (filter === "disabled" && isActive(u)) return false;
    if (!term) return true;
    return [nameOf(u), u.username ?? "", u.role === "admin" ? "admin" : "team member"].some((v) => v.toLowerCase().includes(term));
  });
  const isMe = (u: AdminUserRecord) => !!currentUser && (u.id === currentUser.id || (!!currentUser.username && u.username === currentUser.username));
  const changes = audit.filter((a) => PEOPLE_ACTIONS.has(a.action)).slice(0, 8);
  const counts: Record<Filter, number> = {
    all: people.length,
    active: people.filter(isActive).length,
    disabled: people.filter((u) => !isActive(u)).length,
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Users &amp; approvals</h1>
          <p className="text-sm text-muted-foreground">Who can sign in, and what they can do.</p>
        </div>
        <Button variant="outline" size="icon" onClick={onRefresh} aria-label="Refresh">
          <RefreshCw className="size-4" />
        </Button>
      </div>

      {pending.length > 0 && (
        <Card className="overflow-hidden p-0">
          <div className="flex items-center gap-2.5 border-b border-border px-5 py-3.5">
            <h2 className="text-base font-bold text-foreground">Waiting for approval</h2>
            <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-warning/15 px-1.5 text-xs font-bold text-warning-foreground">
              {pending.length}
            </span>
          </div>
          <ul>
            {pending.map((u) => {
              const role = pendingRoles[u.id] ?? "user";
              return (
                <li key={u.id} className="flex flex-wrap items-center gap-x-4 gap-y-3 border-b border-border/60 px-5 py-3.5 last:border-b-0">
                  <Avatar name={nameOf(u)} muted />
                  <div className="min-w-0 flex-[1_1_220px]">
                    <p className="font-semibold text-foreground">{nameOf(u)}</p>
                    <p className="text-sm text-muted-foreground">
                      {u.username ? `@${u.username} · ` : ""}requested {ago(u.created_at, "recently")}
                    </p>
                  </div>
                  <label className="flex items-center gap-2 text-sm text-muted-foreground">
                    Role
                    <select
                      value={role}
                      onChange={(e) => setPendingRoles((r) => ({ ...r, [u.id]: e.target.value as "admin" | "user" }))}
                      className="min-h-10 rounded-lg border border-border bg-card px-2.5 text-sm text-foreground"
                    >
                      <option value="user">Team member</option>
                      <option value="admin">Admin</option>
                    </select>
                  </label>
                  <div className="flex gap-2">
                    <Button variant="outline" className="h-10 text-destructive-foreground" onClick={() => onAction(u.id, "reject")}>
                      Decline
                    </Button>
                    <Button className="h-10" onClick={() => onApprove(u.id, role)}>
                      <UserCheck className="size-4" />
                      Approve
                    </Button>
                  </div>
                </li>
              );
            })}
          </ul>
        </Card>
      )}

      <Card className="overflow-hidden p-0">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-3.5">
          <h2 className="text-base font-bold text-foreground">
            Everyone <span className="font-medium text-muted-foreground">· {people.length}</span>
          </h2>
          <div className="flex flex-wrap items-center gap-2">
            <div role="radiogroup" aria-label="Show" className="flex gap-0.5 rounded-lg border border-border bg-muted/50 p-0.5">
              {(["all", "active", "disabled"] as Filter[]).map((f) => (
                <button
                  key={f}
                  type="button"
                  role="radio"
                  aria-checked={filter === f}
                  onClick={() => setFilter(f)}
                  className={cn(
                    "min-h-9 rounded-md px-3 text-sm capitalize transition-colors",
                    filter === f ? "bg-card font-semibold text-foreground shadow-xs" : "font-medium text-muted-foreground hover:text-foreground",
                  )}
                >
                  {f} <span className="opacity-70">{counts[f]}</span>
                </button>
              ))}
            </div>
            <label className="relative flex items-center">
              <span className="sr-only">Search people</span>
              <Search className="pointer-events-none absolute left-3 size-4 text-muted-foreground" aria-hidden />
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Name or username"
                className="min-h-10 w-56 rounded-lg border border-border bg-card pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground"
              />
            </label>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] text-sm">
            <thead>
              <tr className="text-left text-xs text-muted-foreground">
                <th scope="col" className="px-5 py-2.5 font-semibold">Person</th>
                <th scope="col" className="px-2 py-2.5 font-semibold">Role</th>
                <th scope="col" className="px-2 py-2.5 font-semibold">Status</th>
                <th scope="col" className="px-2 py-2.5 font-semibold">Last signed in</th>
                <th scope="col" className="px-2 py-2.5 font-semibold">Joined</th>
                <th scope="col" className="px-5 py-2.5 text-right font-semibold">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {shown.map((u) => {
                const active = isActive(u);
                const me = isMe(u);
                return (
                  <tr key={u.id} className="border-t border-border/60">
                    <td className="px-5 py-2.5">
                      <div className="flex items-center gap-2.5">
                        <Avatar name={nameOf(u)} muted={!active} />
                        <div className="min-w-0">
                          <p className={cn("font-semibold", active ? "text-foreground" : "text-muted-foreground")}>
                            {nameOf(u)}
                            {me && <span className="font-medium text-muted-foreground"> (you)</span>}
                          </p>
                          <p className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                            {u.username && <span>@{u.username}</span>}
                            {u.needs_password && <span className="rounded bg-warning/15 px-1.5 font-semibold text-warning-foreground">No password yet</span>}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-2 py-2.5">{u.role === "admin" ? "Admin" : "Team member"}</td>
                    <td className="px-2 py-2.5">
                      <span
                        className={cn(
                          "rounded-md px-2 py-0.5 text-xs font-semibold",
                          active ? "bg-success/12 text-success-foreground" : "bg-muted text-muted-foreground",
                        )}
                      >
                        {active ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td className="px-2 py-2.5 text-muted-foreground">{ago(u.last_login_at)}</td>
                    <td className="px-2 py-2.5 text-muted-foreground">{ago(u.created_at, "–")}</td>
                    <td className="px-5 py-2.5 text-right">
                      {me ? (
                        <span className="text-xs text-muted-foreground">Signed in now</span>
                      ) : (
                        <div className="flex items-center justify-end gap-1">
                          {!active && (
                            <Button variant="outline" size="sm" onClick={() => onAction(u.id, "enable")}>
                              Re-enable
                            </Button>
                          )}
                          <RowMenu
                            user={u}
                            open={openMenu === u.id}
                            onOpenChange={(o) => setOpenMenu(o ? u.id : null)}
                            onAction={onAction}
                            onShowSearches={onShowSearches}
                          />
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
              {shown.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-muted-foreground">
                    {people.length === 0 ? "No accounts yet." : "Nobody matches."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="overflow-hidden p-0">
        <div className="border-b border-border px-5 py-3.5">
          <h2 className="text-base font-bold text-foreground">Recent changes to people</h2>
        </div>
        {changes.length === 0 ? (
          <p className="px-5 py-4 text-sm text-muted-foreground">No changes yet.</p>
        ) : (
          <ol className="py-1.5">
            {changes.map((a) => (
              <li key={a.id} className="flex flex-wrap gap-x-3 px-5 py-2 text-sm">
                <span className="w-32 shrink-0 text-muted-foreground">{ago(a.at, "–")}</span>
                <span className="min-w-0 flex-1 text-foreground">
                  <strong className="font-semibold">{a.actor}</strong> · {a.detail}
                </span>
              </li>
            ))}
          </ol>
        )}
      </Card>

      <Card variant="subtle" className="flex flex-wrap items-center justify-between gap-3 px-5 py-4">
        <div className="min-w-0 flex-[1_1_320px]">
          <h2 className="text-sm font-semibold text-foreground">Sign everyone out</h2>
          <p className="text-sm text-muted-foreground">Ends every session and resets the account list. Use only for a fresh start.</p>
        </div>
        <Button variant="destructive" onClick={onResetAllSessions}>
          Reset all sessions
        </Button>
      </Card>
    </div>
  );
}
