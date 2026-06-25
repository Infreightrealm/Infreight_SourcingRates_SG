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
    
    // Normalize MSC Timeout to No Quotes
    const status = (cr.carrier === "MSC" && cr.status === "TIMEOUT") ? "NO_QUOTES_AVAILABLE" : cr.status;

    if (cr.quotes.length === 0) {
      allRows.push({ carrier: cr.carrier, carrierColor: color, status: status, error: cr.error_message });
    } else {
      for (const q of cr.quotes) {
        allRows.push({ carrier: cr.carrier, carrierColor: color, status: status, quote: q });
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

    // Get selected container types list
    const containerTypesList = data.container_types || (data.container_type ? [data.container_type] : ["DRY 40H"]);
    const baseCurrency = quoteRows[0]?.quote?.currency || "USD";

    // Format container column header (e.g. DRY 40H -> 40HQ (USD))
    const getContainerHeader = (type: string, currency: string) => {
      let standardName = type;
      if (type === "DRY 20") standardName = "20GP";
      else if (type === "DRY 40") standardName = "40GP";
      else if (type === "DRY 40H") standardName = "40HQ";
      return `${standardName} (${currency})`;
    };

    const rateColumns = containerTypesList.map(type => ({
      type,
      header: getContainerHeader(type, baseCurrency),
      key: `rate_${type.replace(/\s+/g, "_")}`,
      width: 18
    }));

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
      ...rateColumns,
      { header: "T/T", key: "tt", width: 10 },
      { header: "Free time", key: "freetime", width: 12 },
      { header: "ETD POL", key: "validity", width: 16 },
      { header: "ETA POD", key: "eta", width: 16 },
      { header: "Validity Till", key: "validity_till", width: 16 },
      { header: "Routing", key: "routing", width: 12 },
      { header: "Remark", key: "remark", width: 35 }
    ];


    // Group and add rows side-by-side
    const groupedExcelRows: any[] = [];
    
    for (const cr of data.results) {
      const carrierInfo = CARRIERS.find(c => c.code === cr.carrier);
      const carrierName = carrierInfo?.name || cr.carrier;
      const status = (cr.carrier === "MSC" && cr.status === "TIMEOUT") ? "NO_QUOTES_AVAILABLE" : cr.status;

      if (cr.quotes.length === 0) {
        const rates: Record<string, string> = {};
        containerTypesList.forEach(ct => {
          rates[`rate_${ct.replace(/\s+/g, "_")}`] = cr.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold out";
        });
        groupedExcelRows.push({
          pol: data.origin || "",
          pod: data.destination || "",
          carrier: carrierName,
          ...rates,
          tt: "-",
          freetime: "-",
          validity: "-",
          eta: "-",
          validity_till: "-",
          routing: "-",
          remark: cr.error_message || (cr.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not available" : "No quotes returned")
        });
      } else {
        const scheduleGroups: Record<string, QuoteSchema[]> = {};
        for (const q of cr.quotes) {
          const key = `${q.etd || ""}|${q.eta || ""}|${(q.vessel || "").trim().toLowerCase()}|${(q.routing || "").trim().toLowerCase()}`;
          if (!scheduleGroups[key]) {
            scheduleGroups[key] = [];
          }
          scheduleGroups[key].push(q);
        }

        for (const key of Object.keys(scheduleGroups)) {
          const groupQuotes = scheduleGroups[key];
          const rates: Record<string, string | number> = {};
          
          containerTypesList.forEach(ct => {
            rates[`rate_${ct.replace(/\s+/g, "_")}`] = cr.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold out";
          });

          groupQuotes.forEach(q => {
            if (q.container_type) {
              rates[`rate_${q.container_type.replace(/\s+/g, "_")}`] = q.final_freight_value === 0.0 
                ? (cr.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold out") 
                : q.final_freight_value;
            }
          });

          const firstQuote = groupQuotes[0];
          const freeTimeVal = getFreeTimeValue(firstQuote, cr.carrier) ?? "-";

          groupedExcelRows.push({
            pol: data.origin || "",
            pod: data.destination || "",
            carrier: carrierName,
            ...rates,
            tt: firstQuote.transit_time_days || "-",
            freetime: freeTimeVal,
            validity: firstQuote.etd || "-",
            eta: firstQuote.eta || "-",
            validity_till: firstQuote.validity_till || "-",
            routing: firstQuote.routing || "Direct",
            remark: firstQuote.vessel || "-"
          });
        }
      }
    }

    // Add grouped rows to sheet
    groupedExcelRows.forEach((row, idx) => {
      sheet.addRow({
        pol: idx === 0 ? row.pol : "",
        pod: idx === 0 ? row.pod : "",
        carrier: row.carrier,
        ...row,
      });
    });

    if (groupedExcelRows.length > 0) {
      sheet.mergeCells(2, 1, 1 + groupedExcelRows.length, 1);
      sheet.mergeCells(2, 2, 1 + groupedExcelRows.length, 2);
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

    const numRateCols = rateColumns.length;

    // Style body cells
    for (let r = 2; r <= 1 + groupedExcelRows.length; r++) {
      // POL (Col 1)
      const cellA = sheet.getCell(r, 1);
      cellA.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'F4B183' } // Light peach
      };
      cellA.font = { name: 'Arial', size: 11, bold: true, color: { argb: '1F4E78' } };
      cellA.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellA.border = getThinBorder();

      // POD (Col 2)
      const cellB = sheet.getCell(r, 2);
      cellB.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'F4B183' } // Light peach
      };
      cellB.font = { name: 'Arial', size: 11, bold: true, color: { argb: '1F4E78' } };
      cellB.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellB.border = getThinBorder();

      // Carrier (Col 3)
      const cellC = sheet.getCell(r, 3);
      cellC.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } }; // Soft navy blue
      cellC.alignment = { horizontal: 'center', vertical: 'middle' };
      cellC.border = getThinBorder();

      // Selected Container rates (Col 4 to 3 + numRateCols)
      for (let c = 0; c < numRateCols; c++) {
        const cellRate = sheet.getCell(r, 4 + c);
        if (cellRate.value === "Sold out" || cellRate.value === "Offline rates") {
          cellRate.font = { name: 'Arial', size: 11, bold: true, color: { argb: 'C00000' } }; // Bold red
          cellRate.alignment = { horizontal: 'center', vertical: 'middle' };
        } else {
          cellRate.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
          cellRate.alignment = { horizontal: 'center', vertical: 'middle' };
          cellRate.numFmt = '#,##0'; // format as integer
        }
        cellRate.border = getThinBorder();
      }

      // T/T
      const cellTT = sheet.getCell(r, 4 + numRateCols);
      cellTT.font = { name: 'Arial', size: 11, bold: true, color: { argb: '385723' } }; // Forest green
      cellTT.alignment = { horizontal: 'center', vertical: 'middle' };
      cellTT.border = getThinBorder();

      // Free time
      const cellFreetime = sheet.getCell(r, 5 + numRateCols);
      cellFreetime.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellFreetime.alignment = { horizontal: 'center', vertical: 'middle' };
      cellFreetime.border = getThinBorder();

      // Validity
      const cellValidity = sheet.getCell(r, 6 + numRateCols);
      cellValidity.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellValidity.alignment = { horizontal: 'center', vertical: 'middle' };
      cellValidity.border = getThinBorder();

      // ETA
      const cellETA = sheet.getCell(r, 7 + numRateCols);
      cellETA.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellETA.alignment = { horizontal: 'center', vertical: 'middle' };
      cellETA.border = getThinBorder();

      // Validity Till
      const cellValidityTill = sheet.getCell(r, 8 + numRateCols);
      cellValidityTill.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellValidityTill.alignment = { horizontal: 'center', vertical: 'middle' };
      cellValidityTill.border = getThinBorder();

      // Routing
      const cellRouting = sheet.getCell(r, 9 + numRateCols);
      cellRouting.font = { name: 'Arial', size: 11, bold: true, color: { argb: '2F5597' } };
      cellRouting.alignment = { horizontal: 'center', vertical: 'middle' };
      cellRouting.border = getThinBorder();

      // Remark
      const cellRemark = sheet.getCell(r, 10 + numRateCols);
      cellRemark.font = { name: 'Arial', size: 10, bold: false, color: { argb: '000000' } };
      cellRemark.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellRemark.border = getThinBorder();

    }

    // Set row height for body rows
    for (let r = 2; r <= 1 + groupedExcelRows.length; r++) {
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
      <div className="space-y-4 animate-fade-in-up">
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
              <div className="flex gap-1.5 flex-wrap">
                {(data.container_types || (data.container_type ? [data.container_type] : [])).map((ct) => (
                  <span key={ct} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-white/70">
                    {ct === "DRY 20" ? "20GP" : ct === "DRY 40" ? "40GP" : ct === "DRY 40H" ? "40HQ" : ct} × {data.container_quantity}
                  </span>
                ))}
              </div>
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
                  className={`px-3 py-1 rounded-lg text-xs font-medium btn-interactive transition-all ${
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
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 dark:bg-white/10 dark:text-white dark:hover:bg-white/20 dark:border-white/10 transition-colors btn-interactive shine-on-hover"
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
            <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center mb-4 animate-float">
              <Inbox className="w-8 h-8 text-slate-400 dark:text-white/30" />
            </div>
            <div className="animate-fade-in-up">
              <h3 className="text-slate-700 dark:text-white/80 font-medium text-lg">No Results Found</h3>
              <p className="text-slate-500 dark:text-white/40 text-sm mt-1">Try adjusting your search parameters or selecting different carriers.</p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] max-h-[600px] overflow-y-auto">
            <table className="w-full text-sm relative">
              <thead className="sticky top-0 z-10">
                <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#1a1f2e] backdrop-blur-md">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Carrier</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Container</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">ETD POL</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">ETA POD</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Validity Till</th>

                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Transit</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 dark:text-white/60 uppercase tracking-wider">Free Time</th>
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
                  <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-all duration-200 hover:-translate-y-[1px] row-enter" style={{animationDelay: `${i * 0.04}s`}}>
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
                        {/* Container */}
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800 dark:bg-white/10 dark:text-white/80">
                            {row.quote.container_type === "DRY 20" ? "20GP" : row.quote.container_type === "DRY 40" ? "40GP" : row.quote.container_type === "DRY 40H" ? "40HQ" : row.quote.container_type || "—"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-white/70 font-mono text-xs">{row.quote.etd || "—"}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-white/70 font-mono text-xs">{row.quote.eta || "—"}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-white/70 font-mono text-xs">{row.quote.validity_till || "—"}</td>
                        <td className="px-4 py-3 text-center text-slate-600 dark:text-white/70">{row.quote.transit_time_days ? `${row.quote.transit_time_days}d` : "—"}</td>
                        <td className="px-4 py-3 text-center">
                          {row.quote.free_time != null ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                              {row.quote.free_time}d
                            </span>
                          ) : <span className="text-slate-400 dark:text-white/25 text-xs">—</span>}
                        </td>
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
                              {row.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold Out"}
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
                      <td colSpan={12} className="px-4 py-3 text-slate-500 dark:text-white/40 text-xs text-center italic">
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
