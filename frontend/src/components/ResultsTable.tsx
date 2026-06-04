"use client";
import { useState } from "react";
import type { RateSearchResultResponse, QuoteSchema } from "@/lib/types";
import { CARRIERS } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import QuoteBreakdownDrawer from "./QuoteBreakdownDrawer";
import { Download, Inbox } from "lucide-react";

interface ResultsTableProps {
  data: RateSearchResultResponse | null;
}

export default function ResultsTable({ data }: ResultsTableProps) {
  const [selectedQuote, setSelectedQuote] = useState<{ quote: QuoteSchema; carrier: string } | null>(null);
  const [sortBy, setSortBy] = useState<"freight" | "etd" | "transit">("freight");

  if (!data) return null;

  // Flatten all quotes from all carriers into one table
  const allRows: { carrier: string; carrierColor: string; status: string; error?: string; quote?: QuoteSchema }[] = [];

  for (const cr of data.results) {
    const carrierInfo = CARRIERS.find((c) => c.code === cr.carrier);
    const color = carrierInfo?.color || "#666";

    if (cr.quotes.length === 0) {
      allRows.push({ carrier: cr.carrier, carrierColor: color, status: cr.status, error: cr.error_message });
    } else {
      for (const q of cr.quotes) {
        allRows.push({ carrier: cr.carrier, carrierColor: color, status: cr.status, quote: q });
      }
    }
  }

  const quoteRows = allRows.filter((r) => r.quote);
  const nonQuoteRows = allRows.filter((r) => !r.quote);

  quoteRows.sort((a, b) => {
    if (!a.quote || !b.quote) return 0;
    if (sortBy === "freight") return a.quote.final_freight_value - b.quote.final_freight_value;
    if (sortBy === "etd") return (a.quote.etd || "").localeCompare(b.quote.etd || "");
    if (sortBy === "transit") return (a.quote.transit_time_days || 99) - (b.quote.transit_time_days || 99);
    return 0;
  });

  const sortedRows = [...quoteRows, ...nonQuoteRows];

  const surchargeTotal = (q: QuoteSchema) =>
    q.included_freight_surcharges.reduce((s, c) => s + c.amount, 0);

  const exportToExcel = async () => {
    if (sortedRows.length === 0) return;

    // Get selected container type and currency
    const containerType = data.container_type || "20GP";
    const baseCurrency = quoteRows[0]?.quote?.currency || "USD";

    // Format container column header (e.g. DRY 40H -> 40HQ (USD))
    const getContainerHeader = (type: string, currency: string) => {
      let standardName = type;
      if (type === "DRY 20") standardName = "20GP";
      else if (type === "DRY 40") standardName = "40GP";
      else if (type === "DRY 40H") standardName = "40HQ";
      else if (type === "REEFER 20") standardName = "20RF";
      else if (type === "REEFER 40") standardName = "40RF";
      else if (type === "REEFER 40H") standardName = "40RH";
      return `${standardName} (${currency})`;
    };

    const containerHeader = getContainerHeader(containerType, baseCurrency);

    // Helpers to extract free time values
    const getFreeTimeValue = (q: QuoteSchema, carrierName: string) => {
      if (q.free_time !== undefined && q.free_time !== null) return q.free_time;
      if (carrierName.toUpperCase() === "MAERSK" && q.service_name) {
        const match = q.service_name.match(/(\d+)\s*days?\s*(?:of\s*)?detention/i);
        if (match) return parseInt(match[1]);
        const simpleMatch = q.service_name.match(/(\d+)\s*days?/i);
        if (simpleMatch) return parseInt(simpleMatch[1]);
      }
      return null;
    };

    // Clean sheet name (Excel limit is 31 chars, no special chars)
    let sheetName = `${data.origin || "Origin"} to ${data.destination || "Destination"}`;
    sheetName = sheetName.replace(/[\\\/\?\*\[\]]/g, "");
    if (sheetName.length > 31) {
      sheetName = sheetName.substring(0, 31);
    }

    const ExcelJS = (await import("exceljs")).default;
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet(sheetName);

    sheet.columns = [
      { header: "POL", key: "pol", width: 12 },
      { header: "POD", key: "pod", width: 25 },
      { header: "Carrier", key: "carrier", width: 16 },
      { header: containerHeader, key: "rate", width: 18 },
      { header: "T/T", key: "tt", width: 10 },
      { header: "Free time", key: "freetime", width: 12 },
      { header: "Validity(ETD)", key: "validity", width: 16 },
      { header: "ETA", key: "eta", width: 16 },
      { header: "Routing", key: "routing", width: 12 },
      { header: "Remark", key: "remark", width: 35 }
    ];

    // Add rows
    sortedRows.forEach((r, idx) => {
      const carrierName = CARRIERS.find(c => c.code === r.carrier)?.name || r.carrier;
      
      if (r.quote) {
        const q = r.quote;
        const freeTimeVal = getFreeTimeValue(q, r.carrier) ?? "-";
        const remarkVal = q.vessel || "-";
        const rateVal = q.final_freight_value === 0.0 ? "Sold out" : q.final_freight_value;
        
        sheet.addRow({
          pol: idx === 0 ? (data.origin || "") : "",
          pod: idx === 0 ? (data.destination || "") : "",
          carrier: carrierName,
          rate: rateVal,
          tt: q.transit_time_days || "-",
          freetime: freeTimeVal,
          validity: q.etd || "-",
          eta: q.eta || "-",
          routing: q.routing || "Direct",
          remark: remarkVal
        });
      } else {
        // Missing quotes (Sold out or error)
        sheet.addRow({
          pol: idx === 0 ? (data.origin || "") : "",
          pod: idx === 0 ? (data.destination || "") : "",
          carrier: carrierName,
          rate: "Sold out",
          tt: "-",
          freetime: "-",
          validity: "-",
          eta: "-",
          routing: "-",
          remark: r.error || (r.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not available" : "No quotes returned")
        });
      }
    });

    // Merge POL and POD columns
    if (sortedRows.length > 0) {
      sheet.mergeCells(2, 1, 1 + sortedRows.length, 1); // Merge A2 to A(1+N)
      sheet.mergeCells(2, 2, 1 + sortedRows.length, 2); // Merge B2 to B(1+N)
    }

    const getThinBorder = () => ({
      top: { style: 'thin' as const, color: { argb: '808080' } },
      left: { style: 'thin' as const, color: { argb: '808080' } },
      bottom: { style: 'thin' as const, color: { argb: '808080' } },
      right: { style: 'thin' as const, color: { argb: '808080' } }
    });

    // Style header row
    const headerRow = sheet.getRow(1);
    headerRow.height = 32;
    headerRow.eachCell((cell) => {
      cell.font = { name: 'Arial', size: 11, bold: true, color: { argb: 'FFFFFF' } };
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'ED7D31' } // Warm orange
      };
      cell.alignment = { horizontal: 'center', vertical: 'middle' };
      cell.border = getThinBorder();
    });

    // Style body cells
    for (let r = 2; r <= 1 + sortedRows.length; r++) {
      // POL (Col A)
      const cellA = sheet.getCell(`A${r}`);
      cellA.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'F4B183' } // Light peach
      };
      cellA.font = { name: 'Arial', size: 11, bold: true, color: { argb: '1F4E78' } };
      cellA.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellA.border = getThinBorder();

      // POD (Col B)
      const cellB = sheet.getCell(`B${r}`);
      cellB.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'F4B183' } // Light peach
      };
      cellB.font = { name: 'Arial', size: 11, bold: true, color: { argb: '1F4E78' } };
      cellB.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellB.border = getThinBorder();

      // Carrier (Col C)
      const cellC = sheet.getCell(`C${r}`);
      cellC.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } }; // Soft navy blue
      cellC.alignment = { horizontal: 'center', vertical: 'middle' };
      cellC.border = getThinBorder();

      // Selected Container (Col D)
      const cellD = sheet.getCell(`D${r}`);
      if (cellD.value === "Sold out") {
        cellD.font = { name: 'Arial', size: 11, bold: true, color: { argb: 'C00000' } }; // Bold red for Sold out
        cellD.alignment = { horizontal: 'center', vertical: 'middle' };
        cellD.border = getThinBorder();
      } else {
        cellD.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
        cellD.alignment = { horizontal: 'center', vertical: 'middle' };
        cellD.border = getThinBorder();
        cellD.numFmt = '#,##0'; // format as integer
      }

      // T/T (Col E)
      const cellE = sheet.getCell(`E${r}`);
      cellE.font = { name: 'Arial', size: 11, bold: true, color: { argb: '385723' } }; // Forest green
      cellE.alignment = { horizontal: 'center', vertical: 'middle' };
      cellE.border = getThinBorder();

      // Free time (Col F)
      const cellF = sheet.getCell(`F${r}`);
      cellF.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellF.alignment = { horizontal: 'center', vertical: 'middle' };
      cellF.border = getThinBorder();

      // Validity (Col G)
      const cellG = sheet.getCell(`G${r}`);
      cellG.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellG.alignment = { horizontal: 'center', vertical: 'middle' };
      cellG.border = getThinBorder();

      // ETA (Col H)
      const cellH = sheet.getCell(`H${r}`);
      cellH.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellH.alignment = { horizontal: 'center', vertical: 'middle' };
      cellH.border = getThinBorder();

      // Routing (Col I)
      const cellI = sheet.getCell(`I${r}`);
      cellI.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellI.alignment = { horizontal: 'center', vertical: 'middle' };
      cellI.border = getThinBorder();

      // Remark (Col J)
      const cellJ = sheet.getCell(`J${r}`);
      cellJ.font = { name: 'Arial', size: 10, bold: false, color: { argb: '000000' } };
      cellJ.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellJ.border = getThinBorder();
    }

    // Set row height for body rows
    for (let r = 2; r <= 1 + sortedRows.length; r++) {
      sheet.getRow(r).height = 28;
    }

    // Generate buffer and trigger browser download
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `rates_${new Date().toISOString().split("T")[0]}.xlsx`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              Search Results
              {data.origin && data.destination && (
                <span className="text-slate-500 dark:text-white/50 font-normal text-sm ml-2">
                  {data.origin} → {data.destination}
                </span>
              )}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <StatusBadge status={data.status} size="md" />
              {data.container_type && (
                <span className="text-xs text-slate-500 dark:text-white/40">{data.container_type} × {data.container_quantity}</span>
              )}
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 dark:text-white/40">Sort by:</span>
              {(["freight", "etd", "transit"] as const).map((key) => (
                <button
                  key={key}
                  onClick={() => setSortBy(key)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    sortBy === key 
                      ? "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-600/30 dark:text-blue-300 border dark:border-blue-500/30" 
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200 border border-transparent dark:bg-white/5 dark:text-white/50 dark:hover:text-white/70"
                  }`}
                >
                  {key === "freight" ? "💰 Price" : key === "etd" ? "📅 ETD" : "⏱ Transit"}
                </button>
              ))}
            </div>
            
            {quoteRows.length > 0 && (
              <button
                onClick={exportToExcel}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 dark:bg-white/10 dark:text-white dark:hover:bg-white/20 dark:border-white/10 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Export Excel
              </button>
            )}
          </div>
        </div>

        {/* Table / Empty State */}
        {sortedRows.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 bg-white/50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/10 rounded-2xl">
            <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-4">
              <Inbox className="w-8 h-8 text-slate-400 dark:text-white/30" />
            </div>
            <h3 className="text-slate-700 dark:text-white/80 font-medium text-lg">No Results Found</h3>
            <p className="text-slate-500 dark:text-white/40 text-sm mt-1">Try adjusting your search parameters or selecting different carriers.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] max-h-[600px] overflow-y-auto">
            <table className="w-full text-sm relative">
              <thead className="sticky top-0 z-10">
                <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#1a1f2e] backdrop-blur-md">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Carrier</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">ETD</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">ETA</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Transit</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Service / Vessel</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">BOF</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Discount</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Surcharges</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Final Value</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedRows.map((row, i) => (
                  <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors">
                    {/* Carrier */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-sm" style={{ backgroundColor: row.carrierColor }} />
                        <span className="font-medium text-slate-900 dark:text-white/90">{row.carrier.replace("_", " ")}</span>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      <StatusBadge status={row.status} />
                    </td>

                    {row.quote ? (
                      <>
                        <td className="px-4 py-3 text-slate-600 dark:text-white/70 font-mono text-xs">{row.quote.etd || "—"}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-white/70 font-mono text-xs">{row.quote.eta || "—"}</td>
                        <td className="px-4 py-3 text-center text-slate-600 dark:text-white/70">{row.quote.transit_time_days ? `${row.quote.transit_time_days}d` : "—"}</td>
                        <td className="px-4 py-3">
                          <div className="text-slate-700 dark:text-white/70 text-xs font-medium">{row.quote.service_name || "—"}</div>
                          <div className="text-slate-500 dark:text-white/40 text-xs">{row.quote.vessel || ""}</div>
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-slate-700 dark:text-white/80">
                          {row.quote.final_freight_value === 0.0 ? "—" : row.quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-red-600 dark:text-red-400">
                          {row.quote.discount !== 0 ? row.quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "—"}
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-blue-600 dark:text-blue-300">
                          {row.quote.final_freight_value === 0.0 ? "—" : surchargeTotal(row.quote).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {row.quote.final_freight_value === 0.0 ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400">
                              Sold Out
                            </span>
                          ) : (
                            <>
                              <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-base">
                                {row.quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                              </span>
                              <span className="block text-xs text-slate-500 dark:text-white/40">{row.quote.currency}</span>
                            </>
                          )}
                        </td>
                        <td className="px-4 py-3 text-center">
                          {row.quote.final_freight_value === 0.0 ? (
                            <button
                              disabled
                              className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-400 dark:bg-white/5 dark:text-white/20 text-xs font-medium cursor-not-allowed border border-transparent shadow-sm"
                            >
                              Unavailable
                            </button>
                          ) : (
                            <button
                              onClick={() => setSelectedQuote({ quote: row.quote!, carrier: row.carrier })}
                              className="px-3 py-1.5 rounded-lg bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-600/20 dark:text-blue-300 text-xs font-medium dark:hover:bg-blue-600/30 border border-blue-200 dark:border-blue-500/20 hover:border-blue-300 dark:hover:border-blue-500/40 transition-all shadow-sm"
                            >
                              View
                            </button>
                          )}
                        </td>
                      </>
                    ) : (
                      <td colSpan={9} className="px-4 py-3 text-slate-500 dark:text-white/40 text-xs text-center italic">
                        {row.error || (row.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not yet implemented" : "No quotes returned")}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Breakdown Drawer */}
      <QuoteBreakdownDrawer
        quote={selectedQuote?.quote || null}
        carrier={selectedQuote?.carrier || ""}
        onClose={() => setSelectedQuote(null)}
      />
    </>
  );
}
