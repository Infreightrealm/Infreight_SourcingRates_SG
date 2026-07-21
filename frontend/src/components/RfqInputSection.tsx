"use client";

import { useState } from "react";
import { parseRfq } from "@/lib/api";
import type { RateSearchRequest, RFQParseResult } from "@/lib/types";
import { toast } from "sonner";

interface RfqInputSectionProps {
  onParsedSuccess: (parsedFields: RateSearchRequest) => void;
}

const DEMO_EXAMPLES = [
  {
    title: "1. Air: Hitachi Lithium",
    text: "Dear All,\nPlease quote cheap and best EXW airfreight rates;\nCollect from: Hitachi Asia Ltd (ICE), 30 Pioneer Crescent #10-15, Singapore 628560\nCommodity: HITACHI PRINTERS -LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970\nDim: 64x53x74 cm/10 pkgs\nGross weight: 320 kg\nHS CODE: 84433100\nBest Regards, Mohammed Shamnad"
  },
  {
    title: "2. Air: Hi Glenn (KUL)",
    text: "Hi Glenn,\nGood Day\nKindly advise us air rates for below:\nPOL: Singapore Airport\nPOD: KUL\nCommodity: Machines Part Accessories\n2 Crates / Sets\nDimension: 186 x 32 x 37 cm H - 2 Crates\nGross Weight: 320.00 kgs (160 kgs x 2 crates)\nPlease provide available flight schedule and transit time. Thank you"
  },
  {
    title: "3. Ocean: Steel Plate (34 Pairs)",
    text: "Hi Toby, Shona and Bethy.\nGood day.\nPlease compile rates from ex Pasir Gudang / Tanjung Pelepas for 20' & 40' as follows.\nCommodity: Steel Plate, Steel Coil.\n1) Koper, Slovenia\n2) Nagoya, Japan\n4) Thessaloniki, Greece\n5) Liverpool, England\n6) Colombo, Sri Lanka\n7) Chiba, Japan\n8) Montreal, Canada\n9) Baltimore, US\n10) Toronto (Halifax), Canada\n11) Toronto (Vancouver), Canada\n12) Winnipeg, Canada\n13) Vancouver, Canada\n14) Houston, US\n15) Kaohsiung, Taiwan\n16) Chattogram, Bangladesh\n17) Manzanillo, Mexico\n18) Bourges, France"
  },
  {
    title: "4. Guardrail: Reefer Container",
    text: "Hi team, please check ocean freight rate for 1x40' Reefer container from Singapore to Hamburg. Weight 18,000 kg."
  },
  {
    title: "5. Guardrail: LCL Shipment",
    text: "Hi team, please quote rate for 4 CBM LCL consolidation shipment from Singapore to Hamburg."
  }
];

export default function RfqInputSection({ onParsedSuccess }: RfqInputSectionProps) {
  const [rfqText, setRfqText] = useState("");
  const [isParsing, setIsParsing] = useState(false);
  const [parseResult, setParseResult] = useState<RFQParseResult | null>(null);
  const [clarificationInput, setClarificationInput] = useState("");
  const [showDebug, setShowDebug] = useState(false);

  const handleParse = async (textToParse: string) => {
    if (!textToParse.trim()) {
      toast.error("Please paste an RFQ email or message before parsing.");
      return;
    }

    setIsParsing(true);
    setParseResult(null);

    try {
      const result = await parseRfq(textToParse);
      setParseResult(result);

      if (result.status === "air_draft_generated") {
        toast.info("✈️ Air freight RFQ detected! Dual forwarder email drafts generated below.");
      } else if (result.status === "unsupported_cargo") {
        toast.warning(result.unsupported_reason || "Unsupported cargo equipment or LCL mode detected.");
      } else if (result.status === "success" && result.parsed_fields) {
        toast.success("🚢 Ocean RFQ parsed successfully! Search fields pre-filled below.");
        onParsedSuccess(result.parsed_fields);
      } else if (result.status === "needs_clarification") {
        toast.warning("Clarification required before search.");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to parse RFQ");
    } finally {
      setIsParsing(false);
    }
  };

  const handleClarifySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!clarificationInput.trim()) return;

    const updatedText = `${rfqText}\nClarification update: ${clarificationInput.trim()}`;
    setRfqText(updatedText);
    setClarificationInput("");
    handleParse(updatedText);
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`Copied ${label} to clipboard!`);
  };

  return (
    <section className="bg-white/80 dark:bg-white/[0.04] border border-purple-500/20 dark:border-purple-500/30 rounded-2xl p-6 backdrop-blur-md transition-all shadow-sm">
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-white text-sm shadow-md">
            🤖
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              Gemini AI RFQ Front Door
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                Air & FCL Ocean Classifier
              </span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-white/50">
              Paste an email inquiry — AI classifies Air/Ocean mode, checks FCL Dry container compatibility, or drafts partner emails.
            </p>
          </div>
        </div>

        {/* Preset Demo Buttons */}
        <div className="hidden lg:flex items-center gap-1.5 flex-wrap justify-end">
          <span className="text-[11px] text-slate-400 font-medium mr-1">Presets:</span>
          {DEMO_EXAMPLES.map((ex, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setRfqText(ex.text);
                setParseResult(null);
              }}
              className="px-2 py-1 rounded-lg text-[11px] font-medium bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 transition-all select-none"
            >
              {ex.title}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <textarea
            value={rfqText}
            onChange={(e) => {
              setRfqText(e.target.value);
              if (parseResult) setParseResult(null);
            }}
            placeholder="Paste raw RFQ email or chat message here (Airfreight, FCL Ocean, Multi-destination)..."
            rows={3}
            className="w-full px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-white/30 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/20 transition-all font-mono resize-y"
          />
        </div>

        {/* Preset Buttons for mobile / small screens */}
        <div className="flex lg:hidden flex-wrap gap-1.5">
          {DEMO_EXAMPLES.map((ex, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setRfqText(ex.text);
                setParseResult(null);
              }}
              className="px-2 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10"
            >
              {ex.title}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => handleParse(rfqText)}
            disabled={isParsing || !rfqText.trim()}
            className="px-6 py-2.5 rounded-xl font-semibold text-xs text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md shadow-purple-500/20 flex items-center gap-2"
          >
            {isParsing ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Classifying & Parsing RFQ…
              </>
            ) : (
              <>
                ✨ Parse RFQ & Classify
              </>
            )}
          </button>

          {rfqText && (
            <button
              type="button"
              onClick={() => {
                setRfqText("");
                setParseResult(null);
              }}
              className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              Clear
            </button>
          )}
        </div>

        {/* Mode Indicator & Confidence Banner */}
        {parseResult && parseResult.status !== "unsupported_cargo" && (
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-200 dark:border-white/10 text-xs">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Classification:</span>
            {parseResult.mode === "air" ? (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-sky-500/20 text-sky-600 dark:text-sky-300 border border-sky-500/30 flex items-center gap-1.5">
                ✈️ AIR FREIGHT ({Math.round((parseResult.confidence || 1) * 100)}% Confidence)
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-600 dark:text-blue-300 border border-blue-500/30 flex items-center gap-1.5">
                🚢 OCEAN FREIGHT (FCL) ({Math.round((parseResult.confidence || 1) * 100)}% Confidence)
              </span>
            )}

            {parseResult.matched_keywords && parseResult.matched_keywords.length > 0 && (
              <span className="text-[11px] text-slate-400">
                Matched signals: <code className="text-slate-700 dark:text-slate-300">{parseResult.matched_keywords.join(", ")}</code>
              </span>
            )}
          </div>
        )}

        {/* Unsupported Equipment or LCL Warning Banner */}
        {parseResult && parseResult.status === "unsupported_cargo" && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-700 dark:text-rose-300 text-xs space-y-3 backdrop-blur-md animate-fade-in-up">
            <div className="flex items-start gap-2.5">
              <span className="text-lg flex-shrink-0">🛑</span>
              <div>
                <span className="font-bold block text-sm mb-1 text-rose-800 dark:text-rose-200">
                  {parseResult.is_unsupported_equipment ? "Special Equipment Not Supported" : "LCL Mode Not Supported"}
                </span>
                <p className="leading-relaxed font-medium">
                  {parseResult.unsupported_reason || "Our automated ocean rate engine currently supports Standard FCL Dry Containers (20GP, 40GP, 40HQ) only."}
                </p>
                <div className="mt-2.5 p-2.5 bg-rose-500/15 rounded-lg border border-rose-500/20 text-[11px] font-mono leading-relaxed">
                  ✅ Supported: Standard FCL Dry Containers (20GP, 40GP, 40HQ).
                  <br />
                  🚫 Unsupported: Reefer, Open Top, Flat Rack, ISO Tank, Hard Top, and LCL / Consolidation.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Air Freight Dual Draft Emails Banner */}
        {parseResult && parseResult.status === "air_draft_generated" && (
          <div className="p-5 bg-sky-500/10 border border-sky-500/30 rounded-2xl text-slate-900 dark:text-white text-xs space-y-4 backdrop-blur-md animate-fade-in-up">
            <div className="flex items-start gap-3">
              <span className="text-xl flex-shrink-0">✉️</span>
              <div className="flex-1">
                <span className="font-bold text-sm text-sky-700 dark:text-sky-300 block mb-0.5">
                  Air Freight Inquiries (No Ocean Scrape Triggered)
                </span>
                <p className="text-slate-600 dark:text-slate-300">
                  Two competing draft emails generated for human review before sending to our air-freight rate partners.
                </p>
              </div>
            </div>

            {/* Dangerous Goods Alert */}
            {parseResult.is_dangerous_goods && (
              <div className="p-3 bg-amber-500/15 border border-amber-500/30 rounded-xl text-amber-800 dark:text-amber-200 text-xs flex items-start gap-2">
                <span className="text-base">⚠️</span>
                <div>
                  <span className="font-bold">Dangerous Goods / Compliance Preserved:</span>
                  <p className="mt-0.5 font-mono text-[11px] text-amber-900 dark:text-amber-100">
                    {parseResult.compliance_notes || "Special hazardous compliance notes present"}
                    {parseResult.hs_code && ` | HS CODE: ${parseResult.hs_code}`}
                  </p>
                </div>
              </div>
            )}

            {/* Dual Email Draft Cards Side-by-Side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              {parseResult.air_drafts?.map((draft, idx) => (
                <div key={idx} className="bg-white/80 dark:bg-black/40 border border-sky-500/20 rounded-xl p-4 space-y-3 flex flex-col justify-between shadow-sm">
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-200 dark:border-white/10">
                      <span className="font-bold text-sky-700 dark:text-sky-300 text-xs">
                        Partner {idx + 1}: {draft.company_name} ({draft.contact_person})
                      </span>
                      <span className="text-[10px] px-2 py-0.5 bg-sky-500/20 text-sky-700 dark:text-sky-300 rounded font-mono">
                        {draft.contact_email}
                      </span>
                    </div>

                    <div className="space-y-1.5 text-[11px] font-mono text-slate-800 dark:text-slate-200">
                      <div><span className="font-semibold text-slate-500 dark:text-slate-400">Subject:</span> {draft.email_subject}</div>
                      <pre className="p-2.5 bg-slate-100 dark:bg-black/60 rounded-lg text-[10px] leading-relaxed overflow-x-auto whitespace-pre-wrap text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-white/10">
                        {draft.email_body}
                      </pre>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => copyToClipboard(draft.email_body, `Draft to ${draft.contact_person}`)}
                    className="w-full py-2 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                  >
                    📋 Copy Draft Email ({draft.contact_person})
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Needs Clarification Banner */}
        {parseResult && parseResult.status === "needs_clarification" && (
          <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-700 dark:text-amber-300 text-xs space-y-3 backdrop-blur-md animate-fade-in-up">
            <div className="flex items-start gap-2.5">
              <span className="text-base flex-shrink-0">❓</span>
              <div>
                <span className="font-semibold block text-sm mb-1 text-amber-800 dark:text-amber-200">
                  Clarification Required
                </span>
                <p>{parseResult.clarification_question || "Some required fields are missing or ambiguous."}</p>
                {parseResult.missing_fields && parseResult.missing_fields.length > 0 && (
                  <div className="mt-1 flex items-center gap-1.5 flex-wrap">
                    <span className="font-medium text-amber-600 dark:text-amber-400">Missing:</span>
                    {parseResult.missing_fields.map((f) => (
                      <span key={f} className="px-1.5 py-0.5 bg-amber-500/20 rounded font-mono text-[11px]">
                        {f}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <form onSubmit={handleClarifySubmit} className="flex gap-2">
              <input
                type="text"
                value={clarificationInput}
                onChange={(e) => setClarificationInput(e.target.value)}
                placeholder="Type missing info (e.g. 'Destination is Rotterdam') and hit Enter…"
                className="flex-1 px-3 py-2 bg-white/80 dark:bg-black/40 border border-amber-500/30 rounded-lg text-slate-900 dark:text-white text-xs focus:outline-none focus:border-amber-500"
              />
              <button
                type="submit"
                disabled={!clarificationInput.trim() || isParsing}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs rounded-lg transition-colors disabled:opacity-50"
              >
                Submit & Re-parse
              </button>
            </form>
          </div>
        )}

        {/* Ocean Success Banner & Multi-Pair Omission Banner */}
        {parseResult && parseResult.status === "success" && (
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-700 dark:text-emerald-300 text-xs space-y-3 backdrop-blur-md animate-fade-in-up">
            <div className="flex items-start gap-2.5">
              <span className="text-base flex-shrink-0">✅</span>
              <div className="flex-1">
                <span className="font-semibold block text-sm mb-0.5 text-emerald-800 dark:text-emerald-200">
                  Ocean RFQ Parsed Successfully (FCL Dry)
                </span>
                Search parameters pre-filled below. Review before submitting rate search.
              </div>
            </div>

            {/* Multi-Pair Destination Omission Counter Banner */}
            {parseResult.total_pairs_found && parseResult.total_pairs_found > 1 && (
              <div className="p-3 bg-blue-500/15 border border-blue-500/30 rounded-xl text-blue-800 dark:text-blue-200 text-xs space-y-1.5">
                <div className="font-bold flex items-center justify-between">
                  <span>📍 Multi-Destination Routing Summary:</span>
                  <span className="px-2 py-0.5 bg-blue-500/20 rounded-full font-mono text-[10px]">
                    Showing 10 of {parseResult.total_pairs_found} pairs ({parseResult.pairs_omitted_count} omitted due to search cap)
                  </span>
                </div>
                <div className="text-[11px] text-blue-700 dark:text-blue-300">
                  Parsed expanded origin-destination pairs ({parseResult.all_parsed_pairs?.length} total). Sequential 3-worker FIFO queue prevents carrier site rate-limiting.
                </div>
              </div>
            )}

            {/* Extracted vs Injected Defaults Tracking */}
            <div className="pt-2 border-t border-emerald-500/20 grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
              <div>
                <span className="font-semibold text-emerald-800 dark:text-emerald-200 block mb-1">
                  🔍 Extracted from raw text ({parseResult.extracted_fields?.length || 0}):
                </span>
                <div className="flex flex-wrap gap-1">
                  {parseResult.extracted_fields?.map((f) => (
                    <span key={f} className="px-2 py-0.5 bg-emerald-500/20 text-emerald-800 dark:text-emerald-200 rounded font-mono">
                      {f}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                  ⚙️ System Defaults Injected ({parseResult.default_injected_fields?.length || 0}):
                </span>
                <div className="flex flex-wrap gap-1">
                  {parseResult.default_injected_fields?.map((f) => (
                    <span key={f} className="px-2 py-0.5 bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-slate-300 rounded font-mono">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Toggle Debug View */}
            {parseResult.debug_raw_llm_response && (
              <div className="pt-2 border-t border-emerald-500/20">
                <button
                  type="button"
                  onClick={() => setShowDebug(!showDebug)}
                  className="text-[11px] font-semibold text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1"
                >
                  {showDebug ? "Hide Gemini Raw JSON Output ▲" : "View Gemini Raw JSON Output ▼"}
                </button>
                {showDebug && (
                  <pre className="mt-2 p-3 bg-black/80 text-green-400 font-mono text-[10px] rounded-lg overflow-x-auto max-h-48">
                    {parseResult.debug_raw_llm_response}
                  </pre>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
