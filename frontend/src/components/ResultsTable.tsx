"use client";
import { useState } from "react";
import type { RateSearchResultResponse, QuoteSchema } from "@/lib/types";
import { CARRIERS } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import QuoteBreakdownDrawer from "./QuoteBreakdownDrawer";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CalendarDays, CircleDollarSign, Download, Inbox, MoveRight, Timer, TriangleAlert } from "lucide-react";
import { generateRatesExportFilename } from "@/lib/excelExport";

function formatDate(dateVal: string | null | undefined): string {
  if (!dateVal || dateVal === "—" || dateVal === "-") return "—";
  const dateStr = dateVal.trim();
  if (!dateStr) return "—";

  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  // Check for ISO format: YYYY-MM-DD
  const matchISO = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})(?:T.*)?$/);
  if (matchISO) {
    const year = parseInt(matchISO[1], 10);
    const month = parseInt(matchISO[2], 10);
    const day = parseInt(matchISO[3], 10);
    if (month >= 1 && month <= 12) {
      return `${day} ${months[month - 1]} ${year}`;
    }
  }

  // Check for DD-Mon-YYYY or DD Mon YYYY
  const matchAbbr = dateStr.match(/^(\d{1,2})[ \-/\\]([A-Za-z]{3})[ \-/\\](\d{4})$/);
  if (matchAbbr) {
    const day = parseInt(matchAbbr[1], 10);
    const monthStr = matchAbbr[2];
    const year = matchAbbr[3];
    const formattedMonth = monthStr.charAt(0).toUpperCase() + monthStr.slice(1).toLowerCase();
    return `${day} ${formattedMonth} ${year}`;
  }

  // Generic Date parsing fallback
  const matchSlash = dateStr.match(/^(\d{4})\/(\d{2})\/(\d{2})$/);
  if (matchSlash) {
    const year = parseInt(matchSlash[1], 10);
    const month = parseInt(matchSlash[2], 10);
    const day = parseInt(matchSlash[3], 10);
    if (month >= 1 && month <= 12) {
      return `${day} ${months[month - 1]} ${year}`;
    }
  }

  const d = new Date(dateStr);
  if (!isNaN(d.getTime())) {
    if (!dateStr.includes("T") && !dateStr.includes(" ")) {
      return `${d.getUTCDate()} ${months[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
    }
    return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
  }

  return dateStr;
}

interface ResultsTableProps {
  data: RateSearchResultResponse | null;
}

export default function ResultsTable({ data }: ResultsTableProps) {
  const [selectedQuote, setSelectedQuote] = useState<{ quote: QuoteSchema; carrier: string } | null>(null);
  const [sortBy, setSortBy] = useState<"freight" | "etd" | "transit">("freight");
  const [containerFilter, setContainerFilter] = useState<string>("ALL");

  if (!data) return null;

  // Flatten all quotes from all carriers into one table
  const allRows: {
    carrier: string;
    carrierColor: string;
    status: string;
    error?: string;
    quote?: QuoteSchema;
    hasPortMismatch?: boolean | null;
    mismatchWarning?: string;
  }[] = [];

  for (const cr of data.results) {
    const carrierInfo = CARRIERS.find((c) => c.code === cr.carrier);
    const color = carrierInfo?.color || "#666";
    
    // If quotes are present, status is AVAILABLE_QUOTES_FOUND regardless of transient errors; normalize MSC Timeout
    let status = cr.quotes.length > 0 ? "AVAILABLE_QUOTES_FOUND" : cr.status;
    if (cr.carrier === "MSC" && status === "TIMEOUT") {
      status = "NO_QUOTES_AVAILABLE";
    }

    if (cr.quotes.length === 0) {
      allRows.push({
        carrier: cr.carrier,
        carrierColor: color,
        status: status,
        error: cr.error_message,
        hasPortMismatch: cr.has_port_mismatch,
        mismatchWarning: cr.mismatch_warning,
      });
    } else {
      for (const q of cr.quotes) {
        allRows.push({
          carrier: cr.carrier,
          carrierColor: color,
          status: status,
          quote: q,
          hasPortMismatch: cr.has_port_mismatch,
          mismatchWarning: cr.mismatch_warning,
        });
      }
    }
  }

  const quoteRows = allRows.filter((r) => r.quote);
  const nonQuoteRows = allRows.filter((r) => !r.quote);


  const CONTAINER_ORDER: Record<string, number> = {
    "DRY 20": 1, "20GP": 1, "20'": 1,
    "DRY 40": 2, "40GP": 2, "40'": 2,
    "DRY 40H": 3, "40HQ": 3, "40HC": 3, "40'HQ": 3, "40'HC": 3,
  };

  const sortContainerTypes = (types: string[]): string[] => {
    return [...types].sort((a, b) => {
      const orderA = CONTAINER_ORDER[a.toUpperCase()] ?? 99;
      const orderB = CONTAINER_ORDER[b.toUpperCase()] ?? 99;
      if (orderA !== orderB) return orderA - orderB;
      return a.localeCompare(b);
    });
  };

  const uniqueContainerTypes = sortContainerTypes(
    Array.from(
      new Set(
        quoteRows
          .map((r) => r.quote?.container_type)
          .filter((ct): ct is string => !!ct)
      )
    )
  );

  const getContainerDisplayName = (type: string) => {
    if (type === "DRY 20") return "20GP";
    if (type === "DRY 40") return "40GP";
    if (type === "DRY 40H") return "40HQ";
    return type;
  };

  const filteredQuoteRows = quoteRows.filter((r) => {
    if (!r.quote) return false;
    if (containerFilter === "ALL") return true;
    return r.quote.container_type === containerFilter;
  });

  filteredQuoteRows.sort((a, b) => {
    if (!a.quote || !b.quote) return 0;
    if (sortBy === "freight") return a.quote.final_freight_value - b.quote.final_freight_value;
    if (sortBy === "etd") return (a.quote.etd || "").localeCompare(b.quote.etd || "");
    if (sortBy === "transit") return (a.quote.transit_time_days || 99) - (b.quote.transit_time_days || 99);
    return 0;
  });

  const sortedRows = [...filteredQuoteRows, ...nonQuoteRows];

  const surchargeTotal = (q: QuoteSchema) =>
    q.included_freight_surcharges.reduce((s, c) => s + c.amount, 0);

  const exportToExcel = async () => {
    if (sortedRows.length === 0) return;

    // Get selected container types list in standard order: 20GP -> 40GP -> 40HQ
    const rawContainerTypes = data.container_types || (data.container_type ? [data.container_type] : ["DRY 40H"]);
    const containerTypesList = sortContainerTypes(rawContainerTypes);
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
      { header: "Demurrage", key: "demurrage", width: 12 },
      { header: "Detention", key: "detention", width: 12 },
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
          const key = `${q.etd || ""}|${q.eta || ""}|${(q.vessel || "").trim().toLowerCase()}|${(q.port_of_discharge || q.routing || "").trim().toLowerCase()}`;
          if (!scheduleGroups[key]) {
            scheduleGroups[key] = [];
          }
          scheduleGroups[key].push(q);
        }

        for (const key of Object.keys(scheduleGroups)) {
          const groupQuotes = scheduleGroups[key];
          const rates: Record<string, string | number> = {};
          const isSpot = groupQuotes.some(q => 
            (q.vessel || "").toUpperCase().includes("SPOT") || 
            (q.service_name || "").toUpperCase().includes("SPOT")
          );

          containerTypesList.forEach(ct => {
            rates[`rate_${ct.replace(/\s+/g, "_")}`] = isSpot 
              ? "-" 
              : (cr.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold out");
          });

          groupQuotes.forEach(q => {
            if (q.container_type) {
              rates[`rate_${q.container_type.replace(/\s+/g, "_")}`] = q.final_freight_value === 0.0 
                ? (isSpot ? "-" : (cr.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold out")) 
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
            demurrage: firstQuote.demurrage != null ? `${firstQuote.demurrage}d` : "-",
            detention: firstQuote.detention != null ? `${firstQuote.detention}d` : "-",
            validity: formatDate(firstQuote.etd),
            eta: formatDate(firstQuote.eta),
            validity_till: formatDate(firstQuote.validity_till),
            routing: firstQuote.port_of_discharge || firstQuote.routing || "Direct",
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
      cell.font = { name: 'Arial', size: 11, bold: true, color: { argb: '000000' } }; // Automatic black
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FA8C3C' } // Brand orange #FA8C3C
      };
      cell.alignment = { horizontal: 'center', vertical: 'middle' };
      cell.border = getThinBorder();
    });

    const numRateCols = rateColumns.length;

    // Style body cells
    for (let r = 2; r <= 1 + groupedExcelRows.length; r++) {
      // POL (Col 1)
      const cellA = sheet.getCell(r, 1);
      cellA.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } }; // Official Blue #323296
      cellA.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellA.border = getThinBorder();

      // POD (Col 2)
      const cellB = sheet.getCell(r, 2);
      cellB.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellB.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
      cellB.border = getThinBorder();

      // Carrier (Col 3)
      const cellC = sheet.getCell(r, 3);
      cellC.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellC.alignment = { horizontal: 'center', vertical: 'middle' };
      cellC.border = getThinBorder();

      // Selected Container rates (Col 4 to 3 + numRateCols)
      for (let c = 0; c < numRateCols; c++) {
        const cellRate = sheet.getCell(r, 4 + c);
        if (cellRate.value === "Sold out" || cellRate.value === "Offline rates") {
          cellRate.font = { name: 'Arial', size: 11, bold: true, color: { argb: 'C00000' } }; // Bold red
          cellRate.alignment = { horizontal: 'center', vertical: 'middle' };
        } else {
          cellRate.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
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
      cellFreetime.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellFreetime.alignment = { horizontal: 'center', vertical: 'middle' };
      cellFreetime.border = getThinBorder();

      // Demurrage
      const cellDemurrage = sheet.getCell(r, 6 + numRateCols);
      cellDemurrage.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellDemurrage.alignment = { horizontal: 'center', vertical: 'middle' };
      cellDemurrage.border = getThinBorder();

      // Detention
      const cellDetention = sheet.getCell(r, 7 + numRateCols);
      cellDetention.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellDetention.alignment = { horizontal: 'center', vertical: 'middle' };
      cellDetention.border = getThinBorder();

      // Validity (ETD POL)
      const cellValidity = sheet.getCell(r, 8 + numRateCols);
      cellValidity.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellValidity.alignment = { horizontal: 'center', vertical: 'middle' };
      cellValidity.border = getThinBorder();

      // ETA (ETA POD)
      const cellETA = sheet.getCell(r, 9 + numRateCols);
      cellETA.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellETA.alignment = { horizontal: 'center', vertical: 'middle' };
      cellETA.border = getThinBorder();

      // Validity Till
      const cellValidityTill = sheet.getCell(r, 10 + numRateCols);
      cellValidityTill.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellValidityTill.alignment = { horizontal: 'center', vertical: 'middle' };
      cellValidityTill.border = getThinBorder();

      // Routing
      const cellRouting = sheet.getCell(r, 11 + numRateCols);
      cellRouting.font = { name: 'Arial', size: 11, bold: true, color: { argb: '323296' } };
      cellRouting.alignment = { horizontal: 'center', vertical: 'middle' };
      cellRouting.border = getThinBorder();

      // Remark
      const cellRemark = sheet.getCell(r, 12 + numRateCols);
      cellRemark.font = { name: 'Arial', size: 10, bold: true, color: { argb: '323296' } };
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
    link.download = generateRatesExportFilename(data.origin, data.destination);
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="space-y-4 animate-fade-in-up">
        {/* Header */}
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h2 className="flex flex-wrap items-center gap-x-2 gap-y-1 text-lg font-semibold tracking-tight text-foreground">
              Search Results
              {data.origin && data.destination && (
                <span className="inline-flex items-center gap-1.5 text-sm font-normal text-muted-foreground">
                  {data.origin}
                  <MoveRight className="size-4 shrink-0 text-primary" />
                  {data.destination}
                </span>
              )}
            </h2>
            <div className="mt-1.5 flex flex-wrap items-center gap-2">
              <StatusBadge status={data.status} size="md" />
              <div className="flex flex-wrap gap-1.5">
                {sortContainerTypes(data.container_types || (data.container_type ? [data.container_type] : [])).map((ct) => (
                  <Badge key={ct} size="sm" variant="outline" className="rounded-md font-mono">
                    {ct === "DRY 20" ? "20GP" : ct === "DRY 40" ? "40GP" : ct === "DRY 40H" ? "40HQ" : ct} × {data.container_quantity}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 w-full sm:w-auto">
            {/* Container Type Filter */}
            {uniqueContainerTypes.length > 1 && (
              <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                <span className="text-xs font-medium text-muted-foreground">Container:</span>
                <button
                  onClick={() => setContainerFilter("ALL")}
                  className={`btn-interactive flex min-h-[34px] items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
                    containerFilter === "ALL"
                      ? "border border-primary/30 bg-primary/12 text-primary shadow-panel"
                      : "border border-transparent text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  All
                </button>
                {uniqueContainerTypes.map((ct) => (
                  <button
                    key={ct}
                    onClick={() => setContainerFilter(ct)}
                    className={`btn-interactive flex min-h-[34px] items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
                      containerFilter === ct
                        ? "border border-primary/30 bg-primary/12 text-primary shadow-panel"
                        : "border border-transparent text-muted-foreground hover:bg-accent hover:text-foreground"
                    }`}
                  >
                    {getContainerDisplayName(ct)}
                  </button>
                ))}
              </div>
            )}

            <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
              <span className="text-xs font-medium text-muted-foreground">Sort by:</span>
              {(["freight", "etd", "transit"] as const).map((key) => (
                <button
                  key={key}
                  onClick={() => setSortBy(key)}
                  className={`btn-interactive flex min-h-[34px] items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium ${
                    sortBy === key 
                      ? "border border-primary/30 bg-primary/12 text-primary shadow-panel" 
                      : "border border-transparent text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  {key === "freight" ? <><CircleDollarSign className="size-3.5" /> Price</>
                    : key === "etd" ? <><CalendarDays className="size-3.5" /> ETD</>
                    : <><Timer className="size-3.5" /> Transit</>}
                </button>
              ))}
            </div>
            
            {quoteRows.length > 0 && (
              <button
                onClick={exportToExcel}
                className="btn-interactive shine-on-hover flex min-h-[34px] items-center justify-center gap-1.5 rounded-md border border-border bg-secondary px-3.5 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-accent"
              >
                <Download className="w-3.5 h-3.5" />
                Export Excel
              </button>
            )}
          </div>
        </div>

        {/* Mismatch Warning Banner */}
        {data.results.some((cr) => cr.has_port_mismatch === true) && (
          <Card variant="warning" className="flex items-start gap-3 p-4 text-xs text-warning-foreground animate-in fade-in duration-300">
            <TriangleAlert className="mt-0.5 size-4 shrink-0" />
            <div className="space-y-1">
              <p className="font-bold text-sm">Port Selection Mismatch Warning</p>
              <p className="text-muted-foreground">The carrier matched a port that differs from your requested port location. Please review:</p>
              <div className="mt-2 space-y-1">
                {data.results.filter((cr) => cr.has_port_mismatch === true).map((cr) => (
                  <div key={cr.carrier} className="rounded-lg bg-warning/10 px-2.5 py-1 font-mono text-[11px]">
                    <strong className="font-semibold">{cr.carrier.replace("_", " ")}:</strong> {cr.mismatch_warning || "Carrier matched a different port than requested."}
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Table / Empty State */}
        {sortedRows.length === 0 ? (
          <Card variant="glass" className="flex flex-col items-center justify-center px-6 py-20 text-center">
            <div className="animate-float mb-4 flex size-16 items-center justify-center rounded-full border border-border bg-muted">
              <Inbox className="size-8 text-muted-foreground" />
            </div>
            <div className="animate-fade-in-up">
              <h3 className="text-lg font-medium text-foreground">No Results Found</h3>
              <p className="mt-1 text-sm text-muted-foreground">Try adjusting your search parameters or selecting different carriers.</p>
            </div>
          </Card>
        ) : (
          <div className="max-h-[600px] w-full max-w-full overflow-x-auto overflow-y-auto rounded-2xl border border-border bg-card shadow-card">

            <table data-table="rates" className="w-full text-xs relative">
              <thead className="sticky top-0 z-10">
                <tr className="border-b border-border bg-muted/95 backdrop-blur-md">
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Carrier</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Status</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Container</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">ETD POL</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">ETA POD</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Validity</th>

                  <th className="whitespace-nowrap px-1.5 py-2.5 text-center text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Transit</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-center text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Free Time</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-center text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Demurrage</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-center text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Detention</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Service / Vessel</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">BOF</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Discount</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Surcharges</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Final Value</th>
                  <th className="whitespace-nowrap px-1.5 py-2.5 text-center text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedRows.map((row, i) => (
                  <tr key={i} className="row-enter border-b border-line transition-colors last:border-0 hover:bg-accent/60" style={{animationDelay: `${i * 0.04}s`}}>
                    {/* Carrier */}
                    <td className="px-1 py-2">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full flex-shrink-0 shadow-sm" style={{ backgroundColor: row.carrierColor }} />
                        <span className="font-medium text-foreground">{row.carrier.replace("_", " ")}</span>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="px-1 py-2">
                      <div className="flex flex-col gap-1">
                        <StatusBadge status={row.status} />
                        {row.hasPortMismatch === true && (
                          <span className="inline-flex items-center gap-1 rounded border border-warning/25 bg-warning/12 px-1.5 py-0.5 text-[10px] font-semibold text-warning-foreground" title={row.mismatchWarning || "Port Mismatch"}>
                            ⚠️ Mismatch
                          </span>
                        )}
                      </div>
                    </td>


                    {row.quote ? (
                      <>
                        {/* Container */}
                        <td className="px-1 py-2">
                          <span className="inline-flex items-center rounded border border-border bg-muted px-1.5 py-0.5 font-mono text-[11px] font-medium text-foreground">
                            {row.quote.container_type === "DRY 20" ? "20GP" : row.quote.container_type === "DRY 40" ? "40GP" : row.quote.container_type === "DRY 40H" ? "40HQ" : row.quote.container_type || "—"}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-1.5 py-2 font-mono text-[11px] text-muted-foreground">{formatDate(row.quote.etd)}</td>
                        <td className="whitespace-nowrap px-1.5 py-2 font-mono text-[11px] text-muted-foreground">{formatDate(row.quote.eta)}</td>
                        <td className="whitespace-nowrap px-1.5 py-2 font-mono text-[11px] text-muted-foreground">{formatDate(row.quote.validity_till)}</td>
                        <td className="whitespace-nowrap px-1.5 py-2 text-center tabular-nums text-muted-foreground">{row.quote.transit_time_days ? `${row.quote.transit_time_days}d` : "—"}</td>
                        <td className="px-1 py-2 text-center">
                          {row.quote.free_time != null ? (
                            <span className="inline-flex items-center rounded border border-success/25 bg-success/12 px-1.5 py-0.5 text-[11px] font-semibold text-success-foreground">
                              {String(row.quote.free_time).endsWith("d") || String(row.quote.free_time).includes(" ") ? row.quote.free_time : `${row.quote.free_time}d`}
                            </span>
                          ) : <span className="text-[11px] text-muted-foreground/50">—</span>}
                        </td>
                        <td className="px-1 py-2 text-center font-mono text-[11px]">
                          {row.quote.demurrage ? (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">
                              {row.quote.demurrage}d
                            </span>
                          ) : <span className="text-[11px] text-muted-foreground/50">—</span>}
                        </td>
                        <td className="px-1 py-2 text-center font-mono text-[11px]">
                          {row.quote.detention ? (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300">
                              {row.quote.detention}d
                            </span>
                          ) : <span className="text-[11px] text-muted-foreground/50">—</span>}
                        </td>
                        <td className="px-1 py-2">
                          <div className="text-[11px] font-medium leading-tight text-foreground">{row.quote.service_name || "—"}</div>
                          <div className="mt-0.5 text-[10px] leading-none text-muted-foreground">{row.quote.vessel || ""}</div>
                        </td>
                        <td className="px-1.5 py-2 text-right font-mono tabular-nums text-foreground">
                          {row.quote.final_freight_value === 0.0 ? "—" : row.quote.basic_ocean_freight.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className="px-1 py-2 text-right font-mono text-red-600 dark:text-red-400">
                          {row.quote.discount !== 0 ? row.quote.discount.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "—"}
                        </td>
                        <td className="px-1 py-2 text-right font-mono">
                          {row.quote.is_breakdown_unavailable ? (
                            <div className="flex flex-col items-end">
                              <span className="text-[11px] font-semibold text-warning-foreground">0.00*</span>
                              <span className="flex items-center gap-0.5 font-sans text-[9px] leading-tight text-warning-foreground" title={row.quote.warning_message || "Some selected container types are currently unavailable for this sailing. Please update the container type or select another departure date."}>
                                ⚠️ Breakdown N/A
                              </span>
                            </div>
                          ) : row.quote.final_freight_value === 0.0 ? "—" : (
                            <span className="text-blue-600 dark:text-blue-300">
                              {surchargeTotal(row.quote).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </span>
                          )}
                        </td>
                        <td className="px-1 py-2 text-right">
                          {row.quote.final_freight_value === 0.0 ? (
                            <span className="inline-flex items-center rounded border border-destructive/25 bg-destructive/12 px-1.5 py-0.5 text-[10px] font-medium text-destructive-foreground">
                              {row.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold Out"}
                            </span>
                          ) : (
                            <div className="flex flex-col items-end">
                              <span className={`font-mono font-bold text-sm ${row.quote.is_breakdown_unavailable ? "text-warning-foreground" : "text-success-foreground"}`}>
                                {row.quote.final_freight_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                              </span>
                              <div className="flex items-center gap-1">
                                <span className="text-[10px] leading-none text-muted-foreground">{row.quote.currency}</span>
                                {row.quote.is_breakdown_unavailable && (
                                  <span className="rounded border border-warning/25 bg-warning/12 px-1 py-0.5 text-[9px] font-medium text-warning-foreground" title={row.quote.warning_message || "Some selected container types are currently unavailable for this sailing. Please update the container type or select another departure date."}>
                                    ⚠️ Incomplete
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                        </td>
                        <td className="px-1 py-2 text-center">
                          {row.quote.final_freight_value === 0.0 ? (
                            <button
                              disabled
                              className="cursor-not-allowed rounded-md border border-border bg-muted px-2 py-1 text-[10px] font-medium text-muted-foreground/60"
                            >
                              Unavailable
                            </button>
                          ) : (
                            <button
                              onClick={() => setSelectedQuote({ quote: row.quote!, carrier: row.carrier })}
                              className="btn-interactive rounded-md border border-primary/25 bg-primary/10 px-2 py-1 text-[10px] font-medium text-primary hover:bg-primary/18"
                            >
                              View
                            </button>
                          )}
                        </td>
                      </>
                    ) : (
                      <td colSpan={12} className="px-1 py-2 text-[11px] text-center">
                        {row.status === "WAITING_FOR_HUMAN_VERIFICATION" ? (
                          <span className="animate-pulse font-semibold text-warning-foreground">
                            ⚠️ Cloudflare Security Check / CAPTCHA: Solve in VNC tab to resume crawler
                          </span>
                        ) : (
                          <span className="italic text-muted-foreground">
                            {row.error || (row.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not yet implemented" : "No quotes returned")}
                          </span>
                        )}
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
