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
    title: "1. Complete RFQ (18t Total)",
    text: "Hi team,\nPlease quote rate from Shanghai to Rotterdam for 2x40HQ containers, weight 18,000 kg total for 2 containers, commodity Furniture. Target ETD early August 2026.\nThanks!"
  },
  {
    title: "2. Missing POD (Clarification)",
    text: "Hi Infreight, need rate for 1x20GP container loaded from Singapore. Weight is 15 MT. Please quote asap."
  },
  {
    title: "3. Relative Date (No Weight Fabricated)",
    text: "Good day, please check rate for 1x40HQ Electronics from Singapore to Hamburg. Departure scheduled for early August."
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

      if (result.status === "success" && result.parsed_fields) {
        toast.success("RFQ parsed successfully! Fields pre-filled below for review.");
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
                gemini-2.5-flash
              </span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-white/50">
              Paste an email or customer request — AI extracts parameters without fabricating missing data.
            </p>
          </div>
        </div>
        
        {/* Preset Demo Buttons */}
        <div className="hidden md:flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium mr-1">Demo presets:</span>
          {DEMO_EXAMPLES.map((ex, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setRfqText(ex.text);
                setParseResult(null);
              }}
              className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 transition-all select-none"
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
            placeholder="Paste raw RFQ email or chat message here (e.g. 'Please quote 2x40HQ from Shanghai to Rotterdam, weight 18,000 kg total for 2 containers, departure early August...')"
            rows={3}
            className="w-full px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-white/30 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/20 transition-all font-mono resize-y"
          />
        </div>

        {/* Preset Buttons for mobile */}
        <div className="flex md:hidden flex-wrap gap-2">
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
                Parsing RFQ with Gemini…
              </>
            ) : (
              <>
                ✨ Parse RFQ & Pre-fill
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

        {/* Success Banner */}
        {parseResult && parseResult.status === "success" && (
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-700 dark:text-emerald-300 text-xs space-y-3 backdrop-blur-md animate-fade-in-up">
            <div className="flex items-start gap-2.5">
              <span className="text-base flex-shrink-0">✅</span>
              <div className="flex-1">
                <span className="font-semibold block text-sm mb-0.5 text-emerald-800 dark:text-emerald-200">
                  RFQ Parsed Successfully (Gemini 2.5 Flash)
                </span>
                Search parameters have been populated into the search form below. Review before submitting search.
              </div>
            </div>

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
