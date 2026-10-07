"use client";

import { useRef, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  ClipboardCopy,
  FileSpreadsheet,
  Loader2,
  Mail,
  Plane,
  Search,
  Sparkles,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { containerLabel, isReeferType, type RFQParseResult } from "@/lib/types";
import { cn } from "@/lib/utils";

/** The batch handler in page.tsx runs at most this many lanes per batch. */
const BATCH_LIMIT = 200;

export interface RfqLane {
  origin: string;
  destination: string;
  container_types?: string[];
  weight_per_container_kg?: number;
  commodity?: string;
}

interface RfqWorkspaceProps {
  rfqText: string;
  onTextChange: (text: string) => void;
  imagePreview: string | null;
  onRemoveImage: () => void;
  isDragging: boolean;
  onDragChange: (dragging: boolean) => void;
  onDrop: (e: React.DragEvent) => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  examples: Array<{ title: string; text: string }>;
  onUseExample: (text: string) => void;
  model: string;
  onModelChange: (model: string) => void;
  isParsing: boolean;
  onParse: () => void;
  onClearText: () => void;
  parseResult: RFQParseResult | null;
  selectedPairIndex: number;
  onFillForm: (index: number) => void;
  onClearForm: () => void;
  clarification: string;
  onClarificationChange: (text: string) => void;
  onClarify: (e: React.FormEvent) => void;
  onAnswerMode: (mode: "Air" | "Ocean") => void;
  quickMode: boolean;
  onQuickModeChange: (quick: boolean) => void;
  onRunLanes?: (lanes: RfqLane[], mode: "quick" | "detailed") => void;
  onCopy: (text: string, label: string) => void;
}

/** "weight_per_container_kg" -> "weight", "container_types" -> "container sizes". */
function fieldName(field: string) {
  const names: Record<string, string> = {
    weight_per_container_kg: "weight",
    container_types: "container sizes",
    departure_date: "departure date",
    origins: "origins",
    destinations: "destinations",
  };
  return names[field] ?? field.replace(/_/g, " ");
}

function laneFlags(lane: RfqLane) {
  const flags: Array<{ text: string; tone: "warn" | "info" }> = [];
  const sizes = lane.container_types ?? [];
  if (sizes.length === 0) flags.push({ text: "Size not in the email", tone: "warn" });
  if (sizes.some(isReeferType)) flags.push({ text: "Reefer: Hapag-Lloyd API only", tone: "info" });
  if (/\bRAMP\b/i.test(lane.destination)) flags.push({ text: "Ramp: CMA CGM only", tone: "info" });
  return flags;
}

function Box({ tone, children }: { tone: "warn" | "info" | "bad"; children: React.ReactNode }) {
  return (
    <div
      className={cn(
        "rounded-xl border p-4 text-sm",
        tone === "warn" && "border-warning/30 bg-warning/10",
        tone === "info" && "border-border bg-muted",
        tone === "bad" && "border-destructive/30 bg-destructive/8",
      )}
    >
      {children}
    </div>
  );
}

/**
 * v2 RFQ screen: paste or attach an enquiry, then review every lane the reader
 * found (tick lanes in or out, see what needs checking, fill the search form from
 * one lane) and search the ticked lanes together. All state and parsing stay in
 * RfqInputSection; Classic renders its own layout.
 */
export default function RfqWorkspace(p: RfqWorkspaceProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [excluded, setExcluded] = useState<number[]>([]);
  const [lanesFor, setLanesFor] = useState<RFQParseResult | null>(null);
  const [showDebug, setShowDebug] = useState(false);

  // A new parse result starts with every lane ticked.
  if (lanesFor !== p.parseResult) {
    setLanesFor(p.parseResult);
    setExcluded([]);
  }

  const r = p.parseResult;
  const lanes: RfqLane[] = (r?.status === "success" && (r.all_parsed_pairs as RfqLane[] | undefined)) || [];
  const ticked = lanes.filter((_, i) => !excluded.includes(i));
  const weightDefaulted = !!r?.default_injected_fields?.includes("weight_per_container_kg");
  const weight = r?.parsed_fields?.weight_per_container_kg;
  const toggle = (i: number) => setExcluded((x) => (x.includes(i) ? x.filter((n) => n !== i) : [...x, i]));

  return (
    <Card className="flex flex-col gap-5 p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-bold text-foreground">
            <Mail className="size-5 text-muted-foreground" aria-hidden />
            Quote from an email
          </h2>
          <p className="text-sm text-muted-foreground">
            Paste the customer&apos;s enquiry, a table from Excel, or attach a screenshot or spreadsheet. Each lane is read into a list you check before anything is searched.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-muted-foreground">Try an example</span>
          {p.examples.map((ex) => (
            <button
              key={ex.title}
              type="button"
              onClick={() => p.onUseExample(ex.text)}
              className="min-h-8 rounded-full border border-border bg-muted px-3 text-xs font-medium text-foreground hover:bg-accent"
            >
              {ex.title.replace(/^Example:\s*/, "")}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-4">
        <div className="flex min-w-0 flex-[3_1_26rem] flex-col gap-2">
          <label htmlFor="rfq-text" className="text-xs font-semibold text-muted-foreground">
            Enquiry text
          </label>
          <textarea
            id="rfq-text"
            value={p.rfqText}
            onChange={(e) => p.onTextChange(e.target.value)}
            rows={7}
            placeholder={'e.g. "Hi team, please quote 2 x 40HQ Ho Chi Minh to Hamburg and 1 x 20GP Surabaya to Jeddah, approx 18 t each."'}
            className="min-h-40 w-full resize-y rounded-xl border border-input bg-background px-3.5 py-3 text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/25"
          />
        </div>
        <div className="flex min-w-0 flex-[2_1_16rem] flex-col gap-2">
          <span className="text-xs font-semibold text-muted-foreground">Attachment</span>
          {p.imagePreview ? (
            <div className="flex min-h-40 flex-1 flex-col items-center justify-center gap-2 rounded-xl border border-border bg-muted p-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={p.imagePreview} alt="Attached enquiry screenshot" className="max-h-28 max-w-full rounded-lg object-contain" />
              <Button variant="ghost" size="sm" onClick={p.onRemoveImage}>
                <X className="size-3.5" />
                Remove screenshot
              </Button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                p.onDragChange(true);
              }}
              onDragLeave={() => p.onDragChange(false)}
              onDrop={p.onDrop}
              className={cn(
                "flex min-h-40 flex-1 flex-col items-center justify-center gap-1.5 rounded-xl border-2 border-dashed px-4 text-center transition-colors",
                p.isDragging ? "border-primary bg-primary/8" : "border-input hover:bg-accent",
              )}
            >
              <FileSpreadsheet className="size-6 text-muted-foreground" aria-hidden />
              <span className="text-sm font-semibold text-foreground">Drop a screenshot or spreadsheet</span>
              <span className="text-xs text-muted-foreground">or click to choose · Ctrl+V pastes a screenshot</span>
            </button>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/png,image/jpeg,image/webp,.xlsx,.xls,.csv"
            onChange={p.onFileSelect}
            className="hidden"
          />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button size="lg" onClick={p.onParse} disabled={p.isParsing || (!p.rfqText.trim() && !p.imagePreview)} className="font-semibold">
          {p.isParsing ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
          {p.isParsing ? "Reading the enquiry…" : "Read enquiry"}
        </Button>
        <label className="flex min-h-11 items-center gap-2 rounded-lg border border-border bg-background px-3 text-xs text-muted-foreground">
          Reader
          <select
            value={p.model}
            onChange={(e) => p.onModelChange(e.target.value)}
            className="bg-transparent text-sm font-medium text-foreground outline-none"
          >
            <option value="gemini-2.5-flash">Fast (Gemini 2.5 Flash)</option>
            <option value="gemini-pro-latest">Thorough (Gemini Pro)</option>
            <option value="gemini-3.1-pro-preview">Most capable (Gemini 3.1 Pro)</option>
          </select>
        </label>
        {(p.rfqText || p.imagePreview) && (
          <Button variant="ghost" onClick={p.onClearText}>
            <X className="size-4" />
            Clear
          </Button>
        )}
      </div>

      {r && (r.status === "unsupported_cargo" ? (
        <Box tone="bad">
          <p className="font-semibold text-destructive-foreground">
            {r.is_unsupported_equipment ? "This equipment isn't searchable yet" : "LCL isn't searchable yet"}
          </p>
          <p className="mt-1 text-muted-foreground">
            {r.unsupported_reason || "Automated search covers FCL dry containers (20GP, 40GP, 40HQ), plus 20RF / 40RH through the Hapag-Lloyd API."}
          </p>
        </Box>
      ) : r.status === "booking_confirmation" || r.is_booking_confirmation ? (
        <Box tone="info">
          <p className="font-semibold text-foreground">This looks like a booking instruction, not a rate request</p>
          <p className="mt-1 text-muted-foreground">
            {r.clarification_question || "Nothing will be searched. Paste a rate request to search for rates."}
          </p>
        </Box>
      ) : r.status === "needs_clarification" ? (
        <Box tone="warn">
          <p className="flex items-center gap-2 font-semibold text-warning-foreground">
            <AlertTriangle className="size-4" aria-hidden />
            One thing to confirm
          </p>
          <p className="mt-1 text-foreground">{r.clarification_question || "Some details are missing or unclear."}</p>
          {r.missing_fields && r.missing_fields.length > 0 && (
            <p className="mt-1 text-xs text-muted-foreground">Missing: {r.missing_fields.join(", ")}</p>
          )}
          {r.is_dual_mode && (
            <div className="mt-3 flex flex-wrap gap-2">
              <Button variant="outline" onClick={() => p.onAnswerMode("Air")}>
                <Plane className="size-4" />
                It&apos;s air freight
              </Button>
              <Button variant="outline" onClick={() => p.onAnswerMode("Ocean")}>
                It&apos;s ocean freight
              </Button>
            </div>
          )}
          <form onSubmit={p.onClarify} className="mt-3 flex flex-wrap gap-2">
            <label htmlFor="rfq-clarify" className="sr-only">
              Your answer
            </label>
            <input
              id="rfq-clarify"
              value={p.clarification}
              onChange={(e) => p.onClarificationChange(e.target.value)}
              placeholder="Type the missing detail, e.g. 40HQ or Port Klang"
              className="min-h-10 flex-1 rounded-lg border border-input bg-background px-3 text-sm text-foreground outline-none focus-visible:border-ring"
            />
            <Button type="submit" disabled={!p.clarification.trim() || p.isParsing}>
              Read again
            </Button>
          </form>
        </Box>
      ) : r.status === "air_draft_generated" ? (
        <div className="flex flex-col gap-3">
          <Box tone="info">
            <p className="flex items-center gap-2 font-semibold text-foreground">
              <Plane className="size-4" aria-hidden />
              Air freight enquiry: draft emails to our air partners
            </p>
            <p className="mt-1 text-muted-foreground">
              {[r.origin_display && `From ${r.origin_display}`, r.destination_display && `to ${r.destination_display}`].filter(Boolean).join(" ") ||
                "Review each draft before sending."}
            </p>
            {r.is_dangerous_goods && (
              <p className="mt-2 text-warning-foreground">
                Dangerous goods: {r.compliance_notes || "compliance notes present"}
                {r.hs_code && ` · HS code ${r.hs_code}`}
              </p>
            )}
          </Box>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {r.air_drafts?.map((d) => (
              <Card key={d.contact_email} variant="subtle" className="flex flex-col gap-2 p-4 text-sm">
                <p className="font-semibold text-foreground">
                  {d.company_name} · {d.contact_person}
                </p>
                <p className="text-xs text-muted-foreground">{d.contact_email}</p>
                <p className="text-xs">
                  <span className="text-muted-foreground">Subject: </span>
                  {d.email_subject}
                </p>
                <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-background p-3 font-sans text-xs leading-relaxed text-foreground">
                  {d.email_body}
                </pre>
                <Button variant="outline" size="sm" onClick={() => p.onCopy(d.email_body, `draft to ${d.contact_person}`)}>
                  <ClipboardCopy className="size-3.5" />
                  Copy draft
                </Button>
              </Card>
            ))}
          </div>
        </div>
      ) : r.status === "success" ? (
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-foreground">
                {lanes.length} lane{lanes.length === 1 ? "" : "s"} found
              </h3>
              <p className="text-xs text-muted-foreground">
                {lanes.length > 1
                  ? "Untick anything you don't want, check the flagged lanes, then search them together. Fill form loads one lane into the search form below."
                  : "The search form below is filled in with this lane. Check it, then press Search."}
              </p>
            </div>
            {lanes.length > 1 && p.onRunLanes && (
              <div className="flex flex-wrap items-center gap-2">
                <div role="radiogroup" aria-label="How many sailings per carrier" className="flex gap-0.5 rounded-lg bg-secondary p-0.5">
                  {(
                    [
                      [true, "Cheapest sailing"],
                      [false, "All sailings"],
                    ] as const
                  ).map(([quick, label]) => (
                    <button
                      key={label}
                      type="button"
                      role="radio"
                      aria-checked={p.quickMode === quick}
                      onClick={() => p.onQuickModeChange(quick)}
                      title={quick ? "Fastest: the cheapest quote per carrier in the next 14 days" : "Every sailing in the date window"}
                      className={cn(
                        "min-h-9 whitespace-nowrap rounded-md px-3 text-sm font-semibold transition-colors",
                        p.quickMode === quick ? "bg-card text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground",
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <Button
                  size="lg"
                  disabled={ticked.length === 0}
                  onClick={() => p.onRunLanes!(ticked, p.quickMode ? "quick" : "detailed")}
                  className="font-semibold"
                >
                  <Search className="size-4" />
                  Search {Math.min(ticked.length, BATCH_LIMIT)} lane{ticked.length === 1 ? "" : "s"}
                </Button>
              </div>
            )}
          </div>

          {(weightDefaulted || ticked.length > BATCH_LIMIT || (r.pairs_omitted_count ?? 0) > 0) && (
            <ul className="flex flex-col gap-1 rounded-lg bg-warning/10 px-3 py-2 text-xs text-warning-foreground">
              {weightDefaulted && (
                <li>Weight isn&apos;t in the email: every lane uses {weight ? `${weight.toLocaleString("en-US")} kg` : "the default weight"}. Change it in the search form if needed.</li>
              )}
              {ticked.length > BATCH_LIMIT && <li>Only the first {BATCH_LIMIT} ticked lanes run in one batch.</li>}
              {(r.pairs_omitted_count ?? 0) > 0 && <li>{r.pairs_omitted_count} more lanes were found but are over the reader&apos;s 300-lane limit.</li>}
            </ul>
          )}

          {r.sales_notes && Object.values(r.sales_notes).some(Boolean) && (
            <div className="flex flex-wrap gap-2 text-xs">
              {(
                [
                  ["Target rate", r.sales_notes.target_rate],
                  ["Future volume", r.sales_notes.future_volume],
                  ["Urgency", r.sales_notes.urgency],
                  ["Competition", r.sales_notes.competitive_pressure],
                ] as const
              )
                .filter(([, v]) => v)
                .map(([k, v]) => (
                  <span key={k} className="rounded-lg border border-border bg-muted px-2.5 py-1.5">
                    <span className="font-semibold text-foreground">{k}: </span>
                    <span className="text-muted-foreground">{v}</span>
                  </span>
                ))}
            </div>
          )}

          <div className="overflow-hidden rounded-xl border border-border">
            {lanes.length > 1 && (
              <div className="flex items-center justify-between gap-2 border-b border-border bg-muted px-3 py-2 text-xs text-muted-foreground">
                <span>
                  {ticked.length} of {lanes.length} ticked
                </span>
                <span className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => setExcluded([])}>
                    Tick all
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => setExcluded(lanes.map((_, i) => i))}>
                    Untick all
                  </Button>
                </span>
              </div>
            )}
            <ol className="max-h-[28rem] overflow-y-auto">
              {lanes.map((lane, i) => {
                const on = !excluded.includes(i);
                const flags = laneFlags(lane);
                const inForm = p.selectedPairIndex === i;
                return (
                  <li
                    key={`${lane.origin}-${lane.destination}-${i}`}
                    className={cn(
                      "flex flex-wrap items-center gap-x-3 gap-y-1.5 border-b border-border px-3 py-2 last:border-0",
                      !on && "opacity-55",
                      flags.some((f) => f.tone === "warn") && on && "bg-warning/6",
                    )}
                  >
                    {lanes.length > 1 && (
                      <button
                        type="button"
                        aria-pressed={on}
                        aria-label={`${on ? "Leave out" : "Include"} lane ${i + 1}`}
                        onClick={() => toggle(i)}
                        className="flex size-10 items-center justify-center"
                      >
                        <span
                          className={cn(
                            "flex size-5 items-center justify-center rounded border-[1.5px]",
                            on ? "border-primary bg-primary text-primary-foreground" : "border-input bg-card",
                          )}
                        >
                          {on && <Check className="size-3" strokeWidth={3.5} />}
                        </span>
                      </button>
                    )}
                    <span className="w-7 text-xs font-semibold text-muted-foreground">{i + 1}</span>
                    <span className="flex min-w-0 flex-[1_1_18rem] flex-wrap items-center gap-1.5 text-sm font-semibold text-foreground">
                      <span>{lane.origin}</span>
                      <ArrowRight className="size-3.5 text-muted-foreground" aria-hidden />
                      <span>{lane.destination}</span>
                    </span>
                    <span className="flex flex-wrap gap-1">
                      {(lane.container_types ?? []).map((t) => (
                        <span key={t} className="rounded-md bg-secondary px-2 py-0.5 text-xs font-semibold text-foreground">
                          {containerLabel(t)}
                        </span>
                      ))}
                    </span>
                    {flags.map((f) => (
                      <span
                        key={f.text}
                        className={cn(
                          "rounded-md px-2 py-0.5 text-xs font-medium",
                          f.tone === "warn" ? "bg-warning/15 text-warning-foreground" : "bg-primary/10 text-primary",
                        )}
                      >
                        {f.text}
                      </span>
                    ))}
                    <span className="ml-auto">
                      <Button variant={inForm ? "secondary" : "ghost"} size="sm" onClick={() => p.onFillForm(i)} aria-pressed={inForm}>
                        {inForm ? "In the form" : "Fill form"}
                      </Button>
                    </span>
                  </li>
                );
              })}
            </ol>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
            <span>
              {r.extracted_fields?.length ? `Read from the email: ${r.extracted_fields.map(fieldName).join(", ")}` : ""}
              {r.default_injected_fields?.length ? ` · Defaults used: ${r.default_injected_fields.map(fieldName).join(", ")}` : ""}
            </span>
            <span className="flex gap-1">
              <Button variant="ghost" size="sm" onClick={p.onClearForm}>
                Clear search form
              </Button>
              {r.debug_raw_llm_response && (
                <Button variant="ghost" size="sm" onClick={() => setShowDebug((v) => !v)}>
                  {showDebug ? "Hide" : "Show"} reader output
                </Button>
              )}
            </span>
          </div>
          {showDebug && r.debug_raw_llm_response && (
            <pre className="max-h-48 overflow-auto rounded-lg bg-muted p-3 text-[11px] text-foreground">{r.debug_raw_llm_response}</pre>
          )}
        </div>
      ) : null)}
    </Card>
  );
}
