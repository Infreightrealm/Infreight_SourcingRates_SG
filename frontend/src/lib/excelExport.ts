import ExcelJS from "exceljs";
import type { RateSearchResultResponse } from "./types";

export interface BatchRouteResult {
  origin: string;
  destination: string;
  searchResult?: RateSearchResultResponse | null;
  status: "pending" | "running" | "completed" | "failed";
}

/**
 * Clean sheet name to conform to Excel's 31-character limit and invalid char restrictions
 */
function sanitizeSheetName(name: string, index: number): string {
  let clean = name.replace(/[:\\/?*\[\]]/g, "_").trim();
  if (clean.length > 28) {
    clean = clean.substring(0, 28);
  }
  return `${index + 1}. ${clean}`;
}

function is20ftContainer(type?: string): boolean {
  if (!type) return false;
  const t = type.toUpperCase();
  return t.includes("20") || t.includes("20GP") || t.includes("20FT") || t.includes("20'");
}

function is40ftContainer(type?: string): boolean {
  if (!type) return false;
  const t = type.toUpperCase();
  return t.includes("40") || t.includes("40GP") || t.includes("40HQ") || t.includes("40HC") || t.includes("40FT") || t.includes("40'");
}

export async function exportMultiRouteResultsToExcel(batchResults: BatchRouteResult[], filename = "Infreight_Multi_Port_Ocean_Rates.xlsx") {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = "Infreight Ocean Rate Automation";
  workbook.created = new Date();

  // --- 1. OVERVIEW SUMMARY SHEET ---
  const summarySheet = workbook.addWorksheet("Summary Overview");
  
  summarySheet.columns = [
    { header: "#", key: "index", width: 6 },
    { header: "Origin Port", key: "origin", width: 22 },
    { header: "Destination Port", key: "destination", width: 25 },
    { header: "Status", key: "status", width: 26 },
    { header: "Carriers Found", key: "carriers", width: 24 },
    { header: "Cheapest 20GP Rate ($)", key: "rate20", width: 22 },
    { header: "Cheapest 40GP/40HQ Rate ($)", key: "rate40", width: 26 },
    { header: "Port Match Status", key: "mismatch", width: 22 },
  ];

  // Header Styling for Summary
  const summaryHeaderRow = summarySheet.getRow(1);
  summaryHeaderRow.font = { bold: true, color: { argb: "FFFFFF" } };
  summaryHeaderRow.fill = {
    type: "pattern",
    pattern: "solid",
    fgColor: { argb: "1E293B" } // Slate 800
  };
  summaryHeaderRow.alignment = { vertical: "middle", horizontal: "center" };

  batchResults.forEach((item, idx) => {
    const res = item.searchResult;
    const quotes = res?.results?.flatMap(r => r.quotes || []) || [];
    
    // Flexible matching for 20ft & 40ft containers
    const quotes20 = quotes.filter(q => is20ftContainer(q.container_type));
    const quotes40 = quotes.filter(q => is40ftContainer(q.container_type));

    const rates20 = quotes20.map(q => q.final_freight_value).filter(val => typeof val === "number" && val > 0);
    const rates40 = quotes40.map(q => q.final_freight_value).filter(val => typeof val === "number" && val > 0);
    
    const min20 = rates20.length > 0 ? Math.min(...rates20) : null;
    const min40 = rates40.length > 0 ? Math.min(...rates40) : null;
    const carriersList = Array.from(new Set(res?.results?.map(r => r.carrier) || [])).join(", ");
    
    const hasMismatch = res?.results?.some(cr => cr.has_port_mismatch === true);

    summarySheet.addRow({
      index: idx + 1,
      origin: item.origin,
      destination: item.destination,
      status: item.status === "completed" ? (quotes.length > 0 ? "Quotes Found" : "No Quotes (No Direct Schedule)") : item.status.toUpperCase(),
      carriers: carriersList || (res ? "None" : "Pending"),
      rate20: min20 !== null ? `$${min20.toLocaleString()}` : "-",
      rate40: min40 !== null ? `$${min40.toLocaleString()}` : "-",
      mismatch: hasMismatch ? "⚠️ Port Mismatch" : "✅ Verified Match"
    });
  });


  // --- 2. INDIVIDUAL WORKSHEETS PER DESTINATION PORT ---
  batchResults.forEach((item, idx) => {
    const sheetTitle = sanitizeSheetName(item.destination, idx);
    const sheet = workbook.addWorksheet(sheetTitle);

    sheet.columns = [
      { header: "Carrier", key: "carrier", width: 16 },
      { header: "Container Type", key: "container_type", width: 16 },
      { header: "Base Rate ($)", key: "base_rate", width: 16 },
      { header: "Surcharges / Local ($)", key: "local_charges", width: 22 },
      { header: "Total Rate ($)", key: "total_amount", width: 16 },
      { header: "Currency", key: "currency", width: 12 },
      { header: "Free Time (Days)", key: "free_time", width: 18 },
      { header: "Demurrage (Days)", key: "demurrage", width: 18 },
      { header: "Detention (Days)", key: "detention", width: 18 },
      { header: "Transit Time (Days)", key: "transit_time", width: 18 },
      { header: "Validity Until", key: "validity_till", width: 18 },
      { header: "Matched Port Location", key: "matched_port", width: 32 },
    ];

    // Sheet Title Header Box
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true, color: { argb: "FFFFFF" } };
    headerRow.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "2563EB" } // Blue 600
    };
    headerRow.alignment = { vertical: "middle", horizontal: "center" };

    const resultsList = item.searchResult?.results || [];
    let rowCount = 0;

    resultsList.forEach((cr) => {
      const matchedStr = cr.matched_destination || cr.matched_origin || "Verified";
      (cr.quotes || []).forEach((q) => {
        rowCount++;
        const surchargesTotal = (q.included_freight_surcharges || []).reduce((acc, c) => acc + (c.amount || 0), 0);

        sheet.addRow({
          carrier: cr.carrier,
          container_type: q.container_type === "DRY 20" ? "20GP" : q.container_type === "DRY 40" ? "40GP" : q.container_type === "DRY 40H" ? "40HQ" : (q.container_type || "FCL"),
          base_rate: q.basic_ocean_freight ? `$${q.basic_ocean_freight.toLocaleString()}` : "-",
          local_charges: surchargesTotal > 0 ? `$${surchargesTotal.toLocaleString()}` : "$0",
          total_amount: `$${q.final_freight_value.toLocaleString()}`,
          currency: q.currency || "USD",
          free_time: q.free_time ? `${q.free_time} Days` : "N/A",
          demurrage: q.demurrage ? `${q.demurrage} Days` : "-",
          detention: q.detention ? `${q.detention} Days` : "-",
          transit_time: q.transit_time_days ? `${q.transit_time_days} Days` : "Direct",
          validity_till: q.validity_till || "Standard",
          matched_port: matchedStr,
        });
      });
    });

    if (rowCount === 0) {
      sheet.addRow({
        carrier: "No quotes returned for this route.",
      });
    }
  });



  // Generate buffer and trigger browser download
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
}
