"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Plus, RefreshCw, Search } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { addCarrierOverride, deleteCarrierOverride, getPortFixes, type PortFix, type PortMiss } from "@/lib/api";
import { cn } from "@/lib/utils";

/** Keys port name fixes are stored under, with the names people know. */
const CARRIER_LABELS: Record<string, string> = {
  maersk: "Maersk",
  cma: "CMA CGM",
  one: "ONE",
  hapag: "Hapag-Lloyd",
  msc: "MSC",
  greenx: "GreenX",
  oocl: "OOCL",
};
const carrierLabel = (key: string) => CARRIER_LABELS[key] ?? key.toUpperCase();

/** How many days of searches the "couldn't find" list covers. */
const MISS_DAYS = 14;

const input =
  "min-h-10 w-full rounded-lg border border-border bg-card px-2.5 text-sm text-foreground placeholder:text-muted-foreground";

function ago(iso: string | null): string {
  if (!iso) return "";
  const t = new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : `${iso}Z`).getTime();
  if (Number.isNaN(t)) return "";
  const hours = Math.round((Date.now() - t) / 3_600_000);
  if (hours < 1) return "within the hour";
  if (hours < 24) return `${hours} h ago`;
  const days = Math.round(hours / 24);
  return days === 1 ? "yesterday" : `${days} days ago`;
}

/** A port key is shown as its LOCODE when it is one. */
const portCode = (key: string) => (/^[a-z]{5}$/.test(key) ? key.toUpperCase() : null);

interface AdminPortFixesProps {
  adminPassword?: string;
  /** Told the latest misses after each load, to keep the sidebar count current. */
  onMissesLoaded?: (misses: PortMiss[]) => void;
}

/**
 * v2 Port name fixes: ports a carrier's own search couldn't find recently, each with
 * a box for the name that carrier uses, and every saved fix by carrier. A fix tells
 * the bot what to type into that carrier's port box for that port.
 */
export default function AdminPortFixes({ adminPassword, onMissesLoaded }: AdminPortFixesProps) {
  const [fixes, setFixes] = useState<PortFix[]>([]);
  const [misses, setMisses] = useState<PortMiss[]>([]);
  const [loading, setLoading] = useState(true);
  const [missDrafts, setMissDrafts] = useState<Record<string, string>>({});
  const [carrier, setCarrier] = useState<string>("all");
  const [query, setQuery] = useState("");
  const [editing, setEditing] = useState<{ id: string; text: string } | null>(null);
  const [adding, setAdding] = useState(false);
  const [draft, setDraft] = useState({ carrier: "maersk", key: "", text: "" });

  const apply = useCallback(
    (data: { fixes: PortFix[]; misses: PortMiss[] }) => {
      setFixes(data.fixes);
      setMisses(data.misses);
      onMissesLoaded?.(data.misses);
    },
    [onMissesLoaded],
  );

  const load = async () => {
    setLoading(true);
    try {
      apply(await getPortFixes(MISS_DAYS, adminPassword));
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load port name fixes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let alive = true;
    getPortFixes(MISS_DAYS, adminPassword)
      .then((data) => alive && apply(data))
      .catch((e) => alive && toast.error(e instanceof Error ? e.message : "Failed to load port name fixes"))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [adminPassword, apply]);

  const save = async (carrierKey: string, key: string, text: string, label: string) => {
    if (!text.trim()) return;
    try {
      await addCarrierOverride(carrierKey, key, text.trim(), adminPassword);
      toast.success(`Saved: ${carrierLabel(carrierKey)} will search "${text.trim()}" for ${label}.`);
      await load();
      return true;
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to save the fix");
      return false;
    }
  };

  const remove = async (f: PortFix) => {
    const label = f.port_name ?? f.key;
    if (!confirm(`Remove the ${carrierLabel(f.carrier)} fix for ${label}?`)) return;
    try {
      await deleteCarrierOverride(f.carrier, f.key, adminPassword);
      toast.success("Fix removed.");
      await load();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to remove the fix");
    }
  };

  const onAdd = async (e: FormEvent) => {
    e.preventDefault();
    const key = draft.key.trim().toLowerCase();
    if (!key || !draft.text.trim()) return;
    if (await save(draft.carrier, key, draft.text, portCode(key) ?? draft.key.trim())) {
      setDraft((d) => ({ ...d, key: "", text: "" }));
      setAdding(false);
    }
  };

  const open = misses.filter((m) => !m.fix);
  const carriers = Array.from(new Set(fixes.map((f) => f.carrier))).sort((a, b) => carrierLabel(a).localeCompare(carrierLabel(b)));
  const term = query.trim().toLowerCase();
  const shownFixes = fixes.filter(
    (f) =>
      (carrier === "all" || f.carrier === carrier) &&
      (!term || [f.key, f.text, f.port_name ?? ""].some((v) => v.toLowerCase().includes(term))),
  );

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="max-w-3xl">
          <h1 className="text-2xl font-bold text-foreground">Port name fixes</h1>
          <p className="text-sm text-muted-foreground">
            When a carrier&apos;s website calls a port something different from our port list, its search finds nothing. Tell the bot the
            name that carrier uses.
          </p>
        </div>
        <Button variant="outline" size="icon" onClick={() => void load()} disabled={loading} aria-label="Refresh">
          <RefreshCw className={cn("size-4", loading && "animate-spin")} />
        </Button>
      </div>

      <Card className="overflow-hidden p-0">
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-border px-5 py-3.5">
          <div className="flex items-center gap-2.5">
            <h2 className="text-base font-bold text-foreground">Ports a carrier couldn&apos;t find</h2>
            {open.length > 0 && (
              <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-warning/15 px-1.5 text-xs font-bold text-warning-foreground">
                {open.length}
              </span>
            )}
          </div>
          <span className="text-sm text-muted-foreground">From the last {MISS_DAYS} days of searches</span>
        </div>
        {misses.length === 0 ? (
          <p className="px-5 py-5 text-sm text-muted-foreground">
            {loading ? "Loading…" : "Nothing to fix. When a carrier's site can't find a port, it shows up here with the name the bot typed."}
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-sm">
              <thead>
                <tr className="text-left text-xs text-muted-foreground">
                  <th scope="col" className="px-5 py-2.5 font-semibold">Carrier</th>
                  <th scope="col" className="px-2 py-2.5 font-semibold">Port</th>
                  <th scope="col" className="px-2 py-2.5 font-semibold">The bot typed</th>
                  <th scope="col" className="px-2 py-2.5 text-right font-semibold">Searches hit</th>
                  <th scope="col" className="w-[38%] px-5 py-2.5 font-semibold">Name this carrier uses</th>
                </tr>
              </thead>
              <tbody>
                {misses.map((m) => {
                  const id = `${m.carrier}:${m.key}`;
                  const value = missDrafts[id] ?? m.fix ?? "";
                  const label = m.locode ?? m.port_name;
                  return (
                    <tr key={id} className="border-t border-border/60 align-top">
                      <td className="px-5 py-3 font-semibold text-foreground">{carrierLabel(m.carrier)}</td>
                      <td className="px-2 py-3">
                        <p className="font-semibold text-foreground">{m.port_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {[m.locode, m.last_seen && `last ${ago(m.last_seen)}`].filter(Boolean).join(" · ")}
                        </p>
                      </td>
                      <td className="px-2 py-3 font-mono text-xs">{m.typed ?? "–"}</td>
                      <td className="px-2 py-3 text-right">{m.searches}</td>
                      <td className="px-5 py-3">
                        <form
                          className="flex gap-2"
                          onSubmit={async (e) => {
                            e.preventDefault();
                            if (await save(m.carrier, m.key, value, label)) {
                              setMissDrafts((d) => {
                                const next = { ...d };
                                delete next[id];
                                return next;
                              });
                            }
                          }}
                        >
                          <label className="min-w-0 flex-1">
                            <span className="sr-only">
                              {carrierLabel(m.carrier)}&apos;s name for {m.port_name}
                            </span>
                            <input
                              value={value}
                              onChange={(e) => setMissDrafts((d) => ({ ...d, [id]: e.target.value }))}
                              placeholder={`e.g. ${m.port_name}, [country]`}
                              className={input}
                            />
                          </label>
                          <Button type="submit" className="h-10" variant={m.fix ? "outline" : "default"} disabled={!value.trim() || value.trim() === m.fix}>
                            Save fix
                          </Button>
                        </form>
                        {m.fix && <p className="mt-1 text-xs text-success-foreground">Fix saved. It applies from the next search.</p>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        <p className="border-t border-border/60 px-5 py-2.5 text-xs text-muted-foreground">
          Tip: open the carrier&apos;s own site, type the port, and copy the name its dropdown shows. Maersk, CMA CGM and ONE report
          ports they couldn&apos;t find; other carriers don&apos;t yet.
        </p>
      </Card>

      <Card className="overflow-hidden p-0">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-3.5">
          <h2 className="text-base font-bold text-foreground">
            Saved fixes <span className="font-medium text-muted-foreground">· {fixes.length}</span>
          </h2>
          <div className="flex flex-wrap items-center gap-2">
            <label className="relative flex items-center">
              <span className="sr-only">Search saved fixes</span>
              <Search className="pointer-events-none absolute left-3 size-4 text-muted-foreground" aria-hidden />
              <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Port or code" className={cn(input, "w-52 pl-9")} />
            </label>
            <Button variant="outline" onClick={() => setAdding((a) => !a)} aria-expanded={adding}>
              <Plus className="size-4" />
              Add a fix
            </Button>
          </div>
        </div>

        {adding && (
          <form onSubmit={onAdd} className="grid grid-cols-1 gap-3 border-b border-border bg-muted/30 px-5 py-4 md:grid-cols-[160px_1fr_1.4fr_auto] md:items-end">
            <label className="flex flex-col gap-1 text-sm text-muted-foreground">
              Carrier
              <select value={draft.carrier} onChange={(e) => setDraft((d) => ({ ...d, carrier: e.target.value }))} className={input}>
                {Object.entries(CARRIER_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm text-muted-foreground">
              Port code (or name)
              <input value={draft.key} onChange={(e) => setDraft((d) => ({ ...d, key: e.target.value }))} placeholder="e.g. JOAQJ" className={input} required />
            </label>
            <label className="flex flex-col gap-1 text-sm text-muted-foreground">
              Name this carrier uses
              <input value={draft.text} onChange={(e) => setDraft((d) => ({ ...d, text: e.target.value }))} placeholder="e.g. Aqaba, Jordan" className={input} required />
            </label>
            <div className="flex gap-2">
              <Button type="button" variant="ghost" className="h-10" onClick={() => setAdding(false)}>
                Cancel
              </Button>
              <Button type="submit" className="h-10">
                Save fix
              </Button>
            </div>
          </form>
        )}

        <div role="radiogroup" aria-label="Show fixes for" className="flex flex-wrap gap-1.5 border-b border-border/60 px-5 py-3">
          {["all", ...carriers].map((c) => {
            const count = c === "all" ? fixes.length : fixes.filter((f) => f.carrier === c).length;
            return (
              <button
                key={c}
                type="button"
                role="radio"
                aria-checked={carrier === c}
                onClick={() => setCarrier(c)}
                className={cn(
                  "min-h-9 rounded-full border px-3 text-sm transition-colors",
                  carrier === c
                    ? "border-primary bg-primary/10 font-semibold text-primary"
                    : "border-border font-medium text-muted-foreground hover:bg-accent hover:text-foreground",
                )}
              >
                {c === "all" ? "All" : carrierLabel(c)} <span className="opacity-70">{count}</span>
              </button>
            );
          })}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-sm">
            <thead>
              <tr className="text-left text-xs text-muted-foreground">
                <th scope="col" className="px-5 py-2.5 font-semibold">Carrier</th>
                <th scope="col" className="px-2 py-2.5 font-semibold">When the search is for</th>
                <th scope="col" className="px-2 py-2.5 font-semibold">The bot types</th>
                <th scope="col" className="px-2 py-2.5 font-semibold">Added</th>
                <th scope="col" className="px-5 py-2.5 text-right font-semibold">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {shownFixes.map((f) => {
                const id = `${f.carrier}:${f.key}`;
                const code = portCode(f.key);
                const isEditing = editing?.id === id;
                return (
                  <tr key={id} className="border-t border-border/60">
                    <td className="px-5 py-2.5 font-semibold text-foreground">{carrierLabel(f.carrier)}</td>
                    <td className="px-2 py-2.5">
                      {f.port_name ?? f.key}
                      {code && <span className="text-muted-foreground"> · {code}</span>}
                    </td>
                    <td className="px-2 py-2.5">
                      {isEditing ? (
                        <form
                          className="flex gap-2"
                          onSubmit={async (e) => {
                            e.preventDefault();
                            if (await save(f.carrier, f.key, editing.text, code ?? f.key)) setEditing(null);
                          }}
                        >
                          <label className="min-w-0 flex-1">
                            <span className="sr-only">New name for {f.port_name ?? f.key}</span>
                            <input autoFocus value={editing.text} onChange={(e) => setEditing({ id, text: e.target.value })} className={input} />
                          </label>
                          <Button type="submit" size="sm" className="h-10">
                            Save
                          </Button>
                          <Button type="button" size="sm" variant="ghost" className="h-10" onClick={() => setEditing(null)}>
                            Cancel
                          </Button>
                        </form>
                      ) : (
                        <span className="font-mono text-xs">{f.text}</span>
                      )}
                    </td>
                    <td className="px-2 py-2.5 text-muted-foreground">{f.source === "user" ? "by an admin" : "built in"}</td>
                    <td className="whitespace-nowrap px-5 py-2.5 text-right">
                      {!isEditing && (
                        <Button variant="ghost" size="sm" onClick={() => setEditing({ id, text: f.text })}>
                          Edit
                        </Button>
                      )}
                      {f.source === "user" && !isEditing && (
                        <Button variant="ghost" size="sm" className="text-destructive-foreground" onClick={() => void remove(f)}>
                          Remove
                        </Button>
                      )}
                    </td>
                  </tr>
                );
              })}
              {shownFixes.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-5 py-8 text-center text-muted-foreground">
                    {loading ? "Loading…" : "No fixes match."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
