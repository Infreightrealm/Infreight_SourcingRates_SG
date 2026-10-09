"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Power, RefreshCw, RotateCcw, Upload } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  getCarrierSession,
  getCarrierSwitches,
  getWorkers,
  resetCarrierProfile,
  setCarrierSwitch,
  uploadCarrierSession,
  type CarrierSession,
  type CarrierSwitch,
  type WorkerInfo,
} from "@/lib/api";
import { CARRIERS } from "@/lib/types";
import { cn } from "@/lib/utils";

// Carriers whose connector keeps a saved browser profile (chrome_profile_<name>).
const PROFILE_NAMES: Record<string, string> = { MAERSK: "maersk", ONE: "one", CMA_CGM: "cma" };

function when(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? "" : d.toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

/**
 * v2 admin "Carriers": switch a carrier off for everyone while its site is down or
 * under maintenance (with an optional reason shown in the search form), and back on.
 */
export default function AdminCarriers({ adminPassword }: { adminPassword?: string }) {
  const [switches, setSwitches] = useState<Record<string, CarrierSwitch>>({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  // Carrier being switched off: the reason box is open for it.
  const [pending, setPending] = useState<{ code: string; reason: string } | null>(null);
  // Maersk saved login uploaded from an admin's PC (EXPORT_MAERSK_LOGIN.bat).
  const [maerskSession, setMaerskSession] = useState<CarrierSession | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  // Worker machines that run some carriers (WORKER_CARRIERS on the office laptop).
  const [workers, setWorkers] = useState<WorkerInfo[]>([]);

  const load = useCallback(async () => {
    getWorkers(adminPassword).then(setWorkers);
    try {
      setSwitches(await getCarrierSwitches());
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load carriers");
    } finally {
      setLoading(false);
    }
  }, [adminPassword]);

  useEffect(() => {
    let alive = true;
    getCarrierSwitches()
      .then((s) => alive && setSwitches(s))
      .catch((e) => alive && toast.error(e instanceof Error ? e.message : "Failed to load carriers"))
      .finally(() => alive && setLoading(false));
    getCarrierSession("maersk", adminPassword).then((s) => alive && setMaerskSession(s));
    getWorkers(adminPassword).then((w) => alive && setWorkers(w));
    return () => {
      alive = false;
    };
  }, [adminPassword]);

  const uploadSession = async (file: File) => {
    setBusy("MAERSK");
    try {
      const info = await uploadCarrierSession("maersk", await file.text(), adminPassword);
      setMaerskSession(info);
      toast.success(`Maersk saved login uploaded (${info.cookies} cookies). The next Maersk search uses it.`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(null);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const apply = async (code: string, enabled: boolean, reason?: string) => {
    const name = CARRIERS.find((c) => c.code === code)?.name ?? code;
    setBusy(code);
    try {
      const entry = await setCarrierSwitch(code, enabled, reason, adminPassword);
      setSwitches((s) => ({ ...s, [code]: entry }));
      setPending(null);
      toast.success(enabled ? `${name} is back on.` : `${name} is switched off. Searches will skip it.`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : `Failed to switch ${name}`);
    } finally {
      setBusy(null);
    }
  };

  const resetProfile = async (code: string) => {
    const name = CARRIERS.find((c) => c.code === code)?.name ?? code;
    if (!confirm(`Reset ${name}'s saved login? The next ${name} search starts with a clean browser and will need logging in again in the live browser tab.`)) return;
    setBusy(code);
    try {
      const res = await resetCarrierProfile(PROFILE_NAMES[code], adminPassword);
      toast.success(res.purged_directories.length ? `${name}'s saved login was reset.` : `${name} had no saved login to reset.`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : `Failed to reset ${name}`);
    } finally {
      setBusy(null);
    }
  };

  const offCount = Object.values(switches).filter((s) => !s.enabled).length;

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="max-w-3xl">
          <h1 className="text-2xl font-bold text-foreground">Carriers</h1>
          <p className="text-sm text-muted-foreground">
            Switch a carrier off while its website is down or under maintenance. Everyone sees it greyed out in the search form, and
            searches skip it instead of waiting for it to fail.
          </p>
        </div>
        <Button variant="outline" size="icon" onClick={() => void load()} aria-label="Refresh">
          <RefreshCw className="size-4" />
        </Button>
      </div>

      <Card className="overflow-hidden p-0">
        <div className="flex items-center gap-2.5 border-b border-border px-5 py-3.5">
          <h2 className="text-base font-bold text-foreground">All carriers</h2>
          {offCount > 0 && (
            <span className="rounded-full bg-destructive/10 px-2 py-0.5 text-xs font-bold text-destructive-foreground">{offCount} off</span>
          )}
        </div>
        <ul>
          {CARRIERS.map((c) => {
            const s = switches[c.code];
            const on = s?.enabled ?? true;
            const isPending = pending?.code === c.code;
            return (
              <li key={c.code} className="flex flex-col gap-3 border-b border-border/60 px-5 py-3.5 last:border-b-0">
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                  <span className="size-3 shrink-0 rounded-full ring-1 ring-foreground/15" style={{ backgroundColor: c.color }} aria-hidden />
                  <div className="min-w-0 flex-[1_1_220px]">
                    <p className="font-semibold text-foreground">{c.name}</p>
                    {(() => {
                      const w = workers.filter((x) => x.carriers.includes(c.code));
                      if (!w.length) return null;
                      const online = w.find((x) => x.online);
                      return (
                        <p className={cn("text-xs font-semibold", online ? "text-success-foreground" : "text-muted-foreground")}>
                          {online
                            ? `Runs on ${online.worker_id} (online)`
                            : `${w[0].worker_id} offline (last seen ${when(w[0].last_seen)}), so this server runs it`}
                        </p>
                      );
                    })()}
                    <p className="text-sm text-muted-foreground">
                      {loading
                        ? "Loading…"
                        : on
                          ? "On: included in searches"
                          : `Off${s?.reason ? `: ${s.reason}` : ""}`}
                      {s?.updated_by && !loading && (
                        <span className="text-xs">
                          {" "}
                          · changed by {s.updated_by} {when(s.updated_at)}
                        </span>
                      )}
                    </p>
                  </div>
                  {PROFILE_NAMES[c.code] && (
                    <Button
                      type="button"
                      variant="ghost"
                      className="min-h-11 gap-1.5 text-sm text-muted-foreground"
                      disabled={loading || busy === c.code}
                      onClick={() => void resetProfile(c.code)}
                      title="Delete the saved browser login so the next search starts clean"
                    >
                      <RotateCcw className="size-4" aria-hidden />
                      Reset saved login
                    </Button>
                  )}
                  <button
                    type="button"
                    role="switch"
                    aria-checked={on}
                    aria-label={`${c.name} ${on ? "on" : "off"}`}
                    disabled={loading || busy === c.code}
                    onClick={() => (on ? setPending(isPending ? null : { code: c.code, reason: "" }) : void apply(c.code, true))}
                    className={cn(
                      "inline-flex min-h-11 items-center gap-2 rounded-full border px-3 text-sm font-semibold transition-colors disabled:opacity-50",
                      on
                        ? "border-success/30 bg-success/12 text-success-foreground hover:bg-success/18"
                        : "border-destructive/30 bg-destructive/10 text-destructive-foreground hover:bg-destructive/16",
                    )}
                  >
                    <Power className="size-4" aria-hidden />
                    {on ? "On" : "Off"}
                  </button>
                </div>
                {c.code === "MAERSK" && (
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 rounded-xl bg-muted/50 px-3 py-2 text-sm">
                    <span className="min-w-0 flex-[1_1_240px] text-muted-foreground">
                      {maerskSession
                        ? `Saved login uploaded ${when(maerskSession.uploaded_at)}${maerskSession.uploaded_by ? ` by ${maerskSession.uploaded_by}` : ""} · ${maerskSession.cookies} cookies`
                        : "No saved login uploaded. Run EXPORT_MAERSK_LOGIN.bat on your PC, log in, then upload maersk_session.json."}
                    </span>
                    <input
                      ref={fileRef}
                      type="file"
                      accept=".json,application/json"
                      className="hidden"
                      onChange={(e) => {
                        const f = e.target.files?.[0];
                        if (f) void uploadSession(f);
                      }}
                    />
                    <Button type="button" variant="outline" className="h-9 gap-1.5" disabled={busy === "MAERSK"} onClick={() => fileRef.current?.click()}>
                      <Upload className="size-4" aria-hidden />
                      Upload saved login
                    </Button>
                  </div>
                )}
                {isPending && (
                  <form
                    className="flex flex-wrap items-end gap-2 rounded-xl bg-muted/50 p-3"
                    onSubmit={(e) => {
                      e.preventDefault();
                      void apply(c.code, false, pending.reason);
                    }}
                  >
                    <label className="flex min-w-0 flex-[1_1_260px] flex-col gap-1 text-sm text-muted-foreground">
                      Reason (shown to everyone)
                      <input
                        autoFocus
                        value={pending.reason}
                        onChange={(e) => setPending({ code: c.code, reason: e.target.value })}
                        placeholder="e.g. Portal under maintenance until 6pm"
                        className="min-h-10 rounded-lg border border-border bg-card px-2.5 text-sm text-foreground placeholder:text-muted-foreground"
                      />
                    </label>
                    <Button type="button" variant="ghost" className="h-10" onClick={() => setPending(null)}>
                      Cancel
                    </Button>
                    <Button type="submit" variant="destructive" className="h-10" disabled={busy === c.code}>
                      Switch off {c.name}
                    </Button>
                  </form>
                )}
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
}
