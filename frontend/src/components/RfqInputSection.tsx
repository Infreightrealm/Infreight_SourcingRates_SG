"use client";

import { useState, useRef, useEffect } from "react";
import { parseRfq } from "@/lib/api";
import type { RateSearchRequest, RFQParseResult } from "@/lib/types";
import { toast } from "sonner";

interface RfqInputSectionProps {
  onParsedSuccess: (parsedFields: RateSearchRequest) => void;
}

const DEMO_EXAMPLES = [
  {
    title: "Example: Air enquiry (Lithium DG)",
    text: "Dear All,\nPlease quote cheap and best EXW airfreight rates;\nCollect from: Hitachi Asia Ltd (ICE), 30 Pioneer Crescent #10-15, Singapore 628560\nCommodity: HITACHI PRINTERS -LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970\nDim: 64x53x74 cm/10 pkgs\nGross weight: 320 kg\nHS CODE: 84433100\nBest Regards, Mohammed Shamnad"
  },
  {
    title: "Example: Air enquiry (KUL)",
    text: "Hi Glenn,\nGood Day\nKindly advise us air rates for below:\nPOL: Singapore Airport\nPOD: KUL\nCommodity: Machines Part Accessories\n2 Crates / Sets\nDimension: 186 x 32 x 37 cm H - 2 Crates\nGross Weight: 320.00 kgs (160 kgs x 2 crates)\nPlease provide available flight schedule and transit time. Thank you"
  },
  {
    title: "Example: Ocean (Steel Plate 34 pairs)",
    text: "Hi Toby, Shona and Bethy.\nGood day.\nPlease compile rates from ex Pasir Gudang / Tanjung Pelepas for 20' & 40' as follows.\nCommodity: Steel Plate, Steel Coil.\n1) Koper, Slovenia\n2) Nagoya, Japan\n4) Thessaloniki, Greece\n5) Liverpool, England\n6) Colombo, Sri Lanka\n7) Chiba, Japan\n8) Montreal, Canada\n9) Baltimore, US\n10) Toronto (Halifax), Canada\n11) Toronto (Vancouver), Canada\n12) Winnipeg, Canada\n13) Vancouver, Canada\n14) Houston, US\n15) Kaohsiung, Taiwan\n16) Chattogram, Bangladesh\n17) Manzanillo, Mexico\n18) Bourges, France"
  },
  {
    title: "Example: Messy email (PK to JKT)",
    text: "Hi team, need rate for 10x20GP from PK to JKT. Urgent for this week. Also have another 15x20 and 10x20 coming up next week. Using 2 forwarders currently, please try USD 70-80 target rate if possible. Thanks, Pak Shaun."
  },
  {
    title: "Example: Reefer (Special Equip)",
    text: "Hi team, please check ocean freight rate for 1x40' Reefer container from Singapore to Hamburg. Weight 18,000 kg."
  },
  {
    title: "Example: LCL (Consolidation)",
    text: "Hi team, please quote rate for 4 CBM LCL consolidation shipment from Singapore to Hamburg."
  }
];

export default function RfqInputSection({ onParsedSuccess }: RfqInputSectionProps) {
  const [rfqText, setRfqText] = useState("");
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [imageMime, setImageMime] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [parseResult, setParseResult] = useState<RFQParseResult | null>(null);
  const [clarificationInput, setClarificationInput] = useState("");
  const [showDebug, setShowDebug] = useState(false);
  const [selectedPairIndex, setSelectedPairIndex] = useState<number>(0);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = (file: File) => {
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload an image file (PNG, JPG, or WEBP).");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error("File size exceeds 5MB limit. Please upload a smaller screenshot.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      setImagePreview(result);
      setImageMime(file.type);
      setImageBase64(result);
      if (parseResult) setParseResult(null);
      toast.success(`Loaded screenshot (${(file.size / 1024).toFixed(0)} KB)`);
    };
    reader.readAsDataURL(file);
  };

  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      if (e.clipboardData && e.clipboardData.items) {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
          if (items[i].type.startsWith("image/")) {
            const file = items[i].getAsFile();
            if (file) {
              processFile(file);
              toast.success("📋 Screenshot pasted from clipboard!");
              break;
            }
          }
        }
      }
    };

    window.addEventListener("paste", handlePaste);

    // Restore persisted RFQ session state if available
    try {
      const savedText = sessionStorage.getItem("rfq_input_text");
      const savedResult = sessionStorage.getItem("rfq_parse_result");
      const savedPairIndex = sessionStorage.getItem("rfq_selected_pair_index");

      if (savedText) {
        setRfqText(savedText);
      }
      if (savedResult) {
        const parsed: RFQParseResult = JSON.parse(savedResult);
        setParseResult(parsed);
        const idx = savedPairIndex ? parseInt(savedPairIndex, 10) : 0;
        setSelectedPairIndex(idx);
        if (parsed.status === "success" && parsed.all_parsed_pairs && parsed.all_parsed_pairs[idx] && parsed.parsed_fields) {
          const p = parsed.all_parsed_pairs[idx];
          onParsedSuccess({
            ...parsed.parsed_fields,
            origin: p.origin,
            destination: p.destination,
            container_types: p.container_types || parsed.parsed_fields.container_types
          });
        }
      }
    } catch (e) {
      console.error("Failed to restore RFQ session state", e);
    }

    return () => window.removeEventListener("paste", handlePaste);
  }, []);


  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleParse = async (textToParse: string, imgB64?: string | null, imgMime?: string | null) => {
    if (!textToParse.trim() && !imgB64) {
      toast.error("Please paste an enquiry text or upload a screenshot image.");
      return;
    }

    setIsParsing(true);
    setParseResult(null);
    setSelectedPairIndex(0);

    try {
      const result = await parseRfq(textToParse, imgB64 || undefined, imgMime || undefined);
      setParseResult(result);

      // Save to sessionStorage to prevent wiping on search or page navigation
      try {
        if (textToParse) sessionStorage.setItem("rfq_input_text", textToParse);
        sessionStorage.setItem("rfq_parse_result", JSON.stringify(result));
        sessionStorage.setItem("rfq_selected_pair_index", "0");
      } catch (e) {}

      if (result.status === "air_draft_generated") {
        toast.info("✈️ Air freight enquiry detected! Partner email drafts generated below.");
      } else if (result.status === "unsupported_cargo") {
        toast.warning(result.unsupported_reason || "Unsupported cargo equipment or LCL mode detected.");
      } else if (result.status === "success" && result.parsed_fields) {
        toast.success("🚢 Ocean enquiry read successfully! Search details filled below.");
        onParsedSuccess(result.parsed_fields);
      } else if (result.status === "needs_clarification") {
        toast.warning("Clarification required before search.");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to read enquiry details");
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
    handleParse(updatedText, imageBase64, imageMime);
  };

  const handlePairSelect = (index: number) => {
    setSelectedPairIndex(index);
    try {
      sessionStorage.setItem("rfq_selected_pair_index", index.toString());
    } catch (e) {}

    if (!parseResult || !parseResult.all_parsed_pairs || !parseResult.parsed_fields) return;

    const pair = parseResult.all_parsed_pairs[index];
    if (pair) {
      const updatedReq: RateSearchRequest = {
        ...parseResult.parsed_fields,
        origin: pair.origin,
        destination: pair.destination,
        container_types: pair.container_types || parseResult.parsed_fields.container_types
      };
      onParsedSuccess(updatedReq);
      toast.info(`Pre-filled search form for Pair #${index + 1}: ${pair.origin} ➔ ${pair.destination}`);
    }
  };

  const handleClear = () => {
    setRfqText("");
    setImageBase64(null);
    setImageMime(null);
    setImagePreview(null);
    setParseResult(null);
    setSelectedPairIndex(0);
    try {
      sessionStorage.removeItem("rfq_input_text");
      sessionStorage.removeItem("rfq_parse_result");
      sessionStorage.removeItem("rfq_selected_pair_index");
    } catch (e) {}
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
            ✉️
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              Quote from an email
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                Air & Ocean Reader (Text + Multimodal Vision)
              </span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-white/50">
              Paste a customer's enquiry email or upload a screenshot — AI vision fills in the search for you.
            </p>
          </div>
        </div>

        {/* Preset Demo Buttons */}
        <div className="hidden lg:flex items-center gap-1.5 flex-wrap justify-end">
          <span className="text-[11px] text-slate-400 font-medium mr-1">Examples:</span>
          {DEMO_EXAMPLES.map((ex, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setRfqText(ex.text);
                setImageBase64(null);
                setImageMime(null);
                setImagePreview(null);
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
        {/* Dual Input Section: Textarea + Multimodal Screenshot Drop Zone Side-by-Side */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          
          {/* Text Area (Left / Top Column: 7 cols) */}
          <div className="md:col-span-7 flex flex-col space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-white/40 flex items-center justify-between">
              <span>Paste Enquiry Text</span>
              <span className="text-[10px] text-slate-400 font-normal">Plain text email / chat</span>
            </label>
            <textarea
              value={rfqText}
              onChange={(e) => {
                setRfqText(e.target.value);
                if (parseResult) setParseResult(null);
              }}
              placeholder={`Paste a customer enquiry here, e.g.—\n"Hi, please quote 2x40HQ from Singapore to Rotterdam, commodity furniture, ready early August."\nWorks for ocean and air enquiries, including multiple destinations.`}
              rows={4}
              className="w-full flex-1 min-h-[110px] px-4 py-3 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-white/40 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/20 transition-all font-mono resize-y"
            />
          </div>

          {/* Screenshot Drop Zone (Right / Bottom Column: 5 cols) */}
          <div className="md:col-span-5 flex flex-col space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-white/40 flex items-center justify-between">
              <span>Upload Screenshot</span>
              <span className="text-[10px] text-purple-600 dark:text-purple-400 font-normal">AI Vision Input</span>
            </label>

            {imagePreview ? (
              <div className="relative border border-purple-500/30 rounded-xl p-2 bg-slate-50 dark:bg-white/5 flex flex-col items-center justify-center flex-1 min-h-[110px]">
                <img
                  src={imagePreview}
                  alt="RFQ Screenshot Preview"
                  className="max-h-24 max-w-full object-contain rounded-lg shadow-sm"
                />
                <button
                  type="button"
                  onClick={() => {
                    setImageBase64(null);
                    setImageMime(null);
                    setImagePreview(null);
                    if (parseResult) setParseResult(null);
                  }}
                  className="mt-2 text-xs font-medium text-rose-600 dark:text-rose-400 hover:underline flex items-center gap-1"
                >
                  ✕ Remove Screenshot
                </button>
              </div>
            ) : (
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl p-4 flex flex-col items-center justify-center flex-1 min-h-[110px] text-center cursor-pointer transition-all ${
                  isDragging
                    ? "border-purple-500 bg-purple-500/10"
                    : "border-slate-300 dark:border-white/15 hover:border-purple-500/50 hover:bg-slate-100 dark:hover:bg-white/5"
                }`}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <span className="text-xl mb-1">📋 🖼️</span>
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                  Paste screenshot (Ctrl+V / Cmd+V), drop file, or click
                </span>
                <span className="text-[10px] text-purple-600 dark:text-purple-400 font-medium mt-0.5">
                  Direct clipboard paste supported | PNG, JPG, WEBP (Max 5MB)
                </span>

              </div>
            )}
          </div>
        </div>

        {/* Preset Buttons for mobile / small screens */}
        <div className="flex lg:hidden flex-wrap gap-1.5">
          {DEMO_EXAMPLES.map((ex, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setRfqText(ex.text);
                setImageBase64(null);
                setImageMime(null);
                setImagePreview(null);
                setParseResult(null);
              }}
              className="px-2 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10"
            >
              {ex.title}
            </button>
          ))}
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => handleParse(rfqText, imageBase64, imageMime)}
            disabled={isParsing || (!rfqText.trim() && !imageBase64)}
            className="px-6 py-3 min-h-[44px] justify-center rounded-xl font-semibold text-xs text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md shadow-purple-500/20 flex items-center gap-2"
          >
            {isParsing ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                {imageBase64 ? "Reading screenshot with AI vision…" : "Reading enquiry & filling details…"}
              </>
            ) : (
              <>
                ✨ Read enquiry & fill form
              </>
            )}
          </button>

          {(rfqText || imageBase64 || parseResult) && (
            <button
              type="button"
              onClick={handleClear}
              className="text-xs text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 py-2 sm:py-0 text-center flex items-center gap-1"
            >
              <span>✕</span> Clear Enquiry
            </button>
          )}
        </div>

        {/* Mode Indicator & Plain Caption Banner */}
        {parseResult && parseResult.status !== "unsupported_cargo" && (
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-200 dark:border-white/10 text-xs">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Detected Mode:</span>
            {parseResult.mode === "air" ? (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-sky-500/20 text-sky-600 dark:text-sky-300 border border-sky-500/30 flex items-center gap-1.5" title="AI detected this is an air enquiry.">
                ✈️ AIR FREIGHT (AI detected this is an air enquiry)
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-600 dark:text-blue-300 border border-blue-500/30 flex items-center gap-1.5" title="AI detected this is an ocean enquiry.">
                🚢 OCEAN FREIGHT (AI detected this is an ocean enquiry)
              </span>
            )}

            {parseResult.matched_keywords && parseResult.matched_keywords.length > 0 && (
              <span className="text-[11px] text-slate-400">
                Matched terms: <code className="text-slate-700 dark:text-slate-300">{parseResult.matched_keywords.join(", ")}</code>
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
                  Air Freight Partner Email Drafts
                </span>
                <p className="text-slate-600 dark:text-slate-300">
                  Three competing draft emails generated for human review before sending to our air-freight rate partners.
                </p>

                {/* Resolved Airport Displays */}
                {(parseResult.origin_display || parseResult.destination_display) && (
                  <div className="mt-2 flex flex-wrap gap-2 text-[11px] font-mono">
                    {parseResult.origin_display && (
                      <span className="px-2.5 py-1 bg-sky-500/20 rounded-lg border border-sky-500/30 text-sky-900 dark:text-sky-100 font-semibold">
                        📍 POL Airport: {parseResult.origin_display}
                      </span>
                    )}
                    {parseResult.destination_display && (
                      <span className="px-2.5 py-1 bg-sky-500/20 rounded-lg border border-sky-500/30 text-sky-900 dark:text-sky-100 font-semibold">
                        🏁 POD Airport: {parseResult.destination_display}
                      </span>
                    )}
                  </div>
                )}
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
                    <span className="font-medium text-amber-600 dark:text-amber-400">Missing / Unmapped:</span>
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
                placeholder="Type missing info (e.g. 'Origin is Port Klang') and hit Enter…"
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

        {/* Ocean Success Banner */}
        {parseResult && parseResult.status === "success" && (
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-700 dark:text-emerald-300 text-xs space-y-3 backdrop-blur-md animate-fade-in-up">
            
            {/* Draft Review Frame Confirmation Banner */}
            <div className="p-2.5 bg-purple-500/15 border border-purple-500/25 rounded-lg text-purple-900 dark:text-purple-200 font-medium text-xs flex items-center gap-2">
              <span className="text-base flex-shrink-0">📝</span>
              <span>We read your enquiry and filled in the details below — please check and edit before searching.</span>
            </div>

            <div className="flex items-start gap-2.5">
              <span className="text-base flex-shrink-0">✅</span>
              <div className="flex-1">
                <span className="font-semibold block text-sm mb-0.5 text-emerald-800 dark:text-emerald-200">
                  Enquiry Details Extracted Successfully (FCL Dry)
                </span>
                Search parameters pre-filled below. Review before submitting rate search.
                
                {/* Resolved Port Displays */}
                {(parseResult.origin_display || parseResult.destination_display) && (
                  <div className="mt-1.5 flex flex-wrap gap-2 text-[11px] font-mono">
                    {parseResult.origin_display && (
                      <span className="px-2 py-0.5 bg-emerald-500/20 rounded border border-emerald-500/30 text-emerald-900 dark:text-emerald-100">
                        📍 POL: {parseResult.origin_display}
                      </span>
                    )}
                    {parseResult.destination_display && (
                      <span className="px-2 py-0.5 bg-emerald-500/20 rounded border border-emerald-500/30 text-emerald-900 dark:text-emerald-100">
                        🏁 POD: {parseResult.destination_display}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Sales Desk Intelligence Alert Box */}
            {parseResult.sales_notes && (
              <div className="p-3 bg-purple-500/15 border border-purple-500/30 rounded-xl text-purple-900 dark:text-purple-200 text-xs space-y-2">
                <div className="font-bold flex items-center gap-1.5 text-purple-800 dark:text-purple-300">
                  <span>💼 Sales Desk Notes (Commercial Signals Extracted):</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
                  {parseResult.sales_notes.target_rate && (
                    <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                      <span className="font-bold text-purple-700 dark:text-purple-300 block">🎯 Target Rate:</span>
                      {parseResult.sales_notes.target_rate}
                    </div>
                  )}
                  {parseResult.sales_notes.future_volume && (
                    <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                      <span className="font-bold text-purple-700 dark:text-purple-300 block">📈 Follow-up Volume:</span>
                      {parseResult.sales_notes.future_volume}
                    </div>
                  )}
                  {parseResult.sales_notes.urgency && (
                    <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                      <span className="font-bold text-purple-700 dark:text-purple-300 block">⏰ Urgency:</span>
                      {parseResult.sales_notes.urgency}
                    </div>
                  )}
                  {parseResult.sales_notes.competitive_pressure && (
                    <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                      <span className="font-bold text-purple-700 dark:text-purple-300 block">⚔️ Competitive Pressure:</span>
                      {parseResult.sales_notes.competitive_pressure}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Multi-Pair Destination Routing Summary Banner & Interactive Chips Selector */}
            {parseResult.total_pairs_found && parseResult.total_pairs_found > 1 && (
              <div className="p-4 bg-gradient-to-r from-blue-500/10 via-indigo-500/10 to-purple-500/10 border border-blue-500/30 rounded-2xl text-blue-900 dark:text-blue-100 text-xs space-y-3 backdrop-blur-md shadow-sm">
                <div className="font-bold flex items-center justify-between flex-wrap gap-2 border-b border-blue-500/20 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-base">📍</span>
                    <span className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                      Multi-Destination Routing Summary ({parseResult.total_pairs_found} pairs total)
                    </span>
                  </div>
                  <span className="px-2.5 py-0.5 bg-blue-500/20 text-blue-700 dark:text-blue-300 border border-blue-500/30 rounded-full font-mono text-[10px] font-semibold">
                    Showing 10 pairs ({parseResult.pairs_omitted_count} omitted due to search cap)
                  </span>
                </div>

                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                    Click any route below to pre-fill search form:
                  </span>
                  {parseResult.all_parsed_pairs && parseResult.all_parsed_pairs[selectedPairIndex] && (
                    <span className="text-[11px] font-bold text-indigo-600 dark:text-indigo-300 bg-indigo-500/20 px-2.5 py-1 rounded-lg border border-indigo-500/30">
                      Active Form Route: Pair #{selectedPairIndex + 1} ({parseResult.all_parsed_pairs[selectedPairIndex].origin} ➔ {parseResult.all_parsed_pairs[selectedPairIndex].destination})
                    </span>
                  )}
                </div>

                {/* Interactive Route Pill Badges */}
                <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto pr-1 py-1">
                  {parseResult.all_parsed_pairs?.slice(0, 10).map((pair, idx) => {
                    const isSelected = selectedPairIndex === idx;
                    return (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handlePairSelect(idx)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all flex items-center gap-1.5 select-none cursor-pointer ${
                          isSelected
                            ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold shadow-md shadow-blue-500/25 scale-[1.02] border border-blue-400"
                            : "bg-white/80 dark:bg-white/5 hover:bg-blue-500/10 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-white/10"
                        }`}
                      >
                        <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                          isSelected ? "bg-white text-blue-600" : "bg-slate-200 dark:bg-white/15 text-slate-600 dark:text-slate-300"
                        }`}>
                          {idx + 1}
                        </span>
                        <span>{pair.origin}</span>
                        <span className="opacity-60">➔</span>
                        <span>{pair.destination}</span>
                        {isSelected && <span className="text-[10px] ml-0.5">✓</span>}
                      </button>
                    );
                  })}
                </div>

                {/* Dropdown Selector */}
                <div className="pt-2 border-t border-blue-500/15 flex items-center gap-2">
                  <label className="text-[11px] font-medium text-slate-500 dark:text-slate-400 whitespace-nowrap">
                    Dropdown Selector:
                  </label>
                  <select
                    value={selectedPairIndex}
                    onChange={(e) => handlePairSelect(parseInt(e.target.value, 10))}
                    className="flex-1 px-3 py-1 bg-white/90 dark:bg-black/60 border border-blue-500/30 rounded-lg text-slate-900 dark:text-white font-mono text-xs focus:outline-none focus:border-blue-500"
                  >
                    {parseResult.all_parsed_pairs?.slice(0, 10).map((pair, idx) => (
                      <option key={idx} value={idx}>
                        Pair #{idx + 1}: {pair.origin} ➔ {pair.destination}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {/* Extracted vs Injected Defaults Tracking */}
            <div className="pt-2 border-t border-emerald-500/20 grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">

              <div>
                <span className="font-semibold text-emerald-800 dark:text-emerald-200 block mb-1">
                  🔍 Extracted fields ({parseResult.extracted_fields?.length || 0}):
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
