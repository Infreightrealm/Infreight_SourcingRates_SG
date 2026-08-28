import ExcelJS from "exceljs";
import type { RateSearchResultResponse, QuoteSchema } from "./types";

export interface BatchRouteResult {
  origin: string;
  destination: string;
  searchResult?: RateSearchResultResponse | null;
  status: "pending" | "running" | "completed" | "failed";
}

/**
 * Standardize container ordering: 20GP -> 40GP -> 40HQ
 */
function sortContainerTypes(types: string[]): string[] {
  const customOrder: Record<string, number> = {
    "DRY 20": 1,
    "20GP": 1,
    "20STD": 1,
    "DRY 40": 2,
    "40GP": 2,
    "40STD": 2,
    "DRY 40H": 3,
    "40HQ": 3,
    "40HC": 3,
  };
  return [...types].sort((a, b) => (customOrder[a] || 99) - (customOrder[b] || 99));
}

function formatDate(isoStr?: string | null): string {
  if (!isoStr || isoStr === "-" || isoStr.trim() === "") return "-";
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return isoStr;
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  } catch {
    return isoStr;
  }
}

function sanitizeSheetName(name: string, index: number): string {
  let clean = name.replace(/[:\\/?*\[\]]/g, "_").trim();
  if (clean.length > 25) {
    clean = clean.substring(0, 25);
  }
  return `${index + 1}. ${clean}`;
}

const CARRIERS_MAP: Record<string, string> = {
  maersk: "Maersk",
  cma: "CMA CGM",
  one: "ONE",
  hapag: "Hapag-Lloyd",
  greenx: "GreenX",
  msc: "MSC",
  oocl: "OOCL",
};

function getFreeTimeValue(q: QuoteSchema, carrierName: string): string | number | null {
  const ft = q.free_time as any;
  if (ft !== undefined && ft !== null && ft !== "N/A" && ft !== "") {
    return ft;
  }
  if (carrierName.toUpperCase() === "MAERSK" && q.service_name) {
    const match = q.service_name.match(/(\d+)\s*days?\s*(?:of\s*)?detention/i);
    if (match) return parseInt(match[1]);
    const simpleMatch = q.service_name.match(/(\d+)\s*days?/i);
    if (simpleMatch) return parseInt(simpleMatch[1]);
  }
  return null;
}

/**
 * Add a standardized route rate matrix worksheet to an Excel workbook.
 * Matches exact side-by-side container columns (20GP -> 40GP -> 40HQ), orange brand headers (#FA8C3C),
 * official blue text (#323296), merged POL/POD cells, and formatted numeric rates.
 */
export function addStandardRouteSheetToWorkbook(
  workbook: ExcelJS.Workbook,
  data: RateSearchResultResponse,
  sheetName: string
) {
  const sheet = workbook.addWorksheet(sheetName);

  const rawContainerTypes = data.container_types || (data.container_type ? [data.container_type] : ["DRY 40H"]);
  const containerTypesList = sortContainerTypes(rawContainerTypes);

  // Find base currency
  let baseCurrency = "USD";
  for (const cr of data.results || []) {
    if (cr.quotes && cr.quotes.length > 0 && cr.quotes[0].currency) {
      baseCurrency = cr.quotes[0].currency;
      break;
    }
  }

  const getContainerHeader = (type: string, currency: string) => {
    let standardName = type;
    if (type === "DRY 20") standardName = "20GP";
    else if (type === "DRY 40") standardName = "40GP";
    else if (type === "DRY 40H") standardName = "40HQ";
    return `${standardName} (${currency})`;
  };

  const rateColumns = containerTypesList.map((type) => ({
    type,
    header: getContainerHeader(type, baseCurrency),
    key: `rate_${type.replace(/\s+/g, "_")}`,
    width: 18,
  }));

  sheet.columns = [
    { header: "POL", key: "pol", width: 14 },
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
    { header: "Remark", key: "remark", width: 35 },
  ];

  const groupedExcelRows: any[] = [];

  for (const cr of data.results || []) {
    const carrierName = CARRIERS_MAP[cr.carrier.toLowerCase()] || cr.carrier;

    if (!cr.quotes || cr.quotes.length === 0) {
      const rates: Record<string, string> = {};
      containerTypesList.forEach((ct) => {
        rates[`rate_${ct.replace(/\s+/g, "_")}`] = cr.carrier.toUpperCase() === "OOCL" ? "Offline rates" : "Sold out";
      });
      groupedExcelRows.push({
        pol: data.origin || "",
        pod: data.destination || "",
        carrier: carrierName,
        ...rates,
        tt: "-",
        freetime: "-",
        demurrage: "-",
        detention: "-",
        validity: "-",
        eta: "-",
        validity_till: "-",
        routing: "-",
        remark: cr.error_message || (cr.status === "CONNECTOR_NOT_AVAILABLE" ? "Connector not available" : "No quotes returned"),
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
        const isSpot = groupQuotes.some(
          (q) => (q.vessel || "").toUpperCase().includes("SPOT") || (q.service_name || "").toUpperCase().includes("SPOT")
        );

        containerTypesList.forEach((ct) => {
          rates[`rate_${ct.replace(/\s+/g, "_")}`] = isSpot
            ? "-"
            : cr.carrier.toUpperCase() === "OOCL"
            ? "Offline rates"
            : "Sold out";
        });

        groupQuotes.forEach((q) => {
          if (q.container_type) {
            rates[`rate_${q.container_type.replace(/\s+/g, "_")}`] =
              q.final_freight_value === 0.0
                ? isSpot
                  ? "-"
                  : cr.carrier.toUpperCase() === "OOCL"
                  ? "Offline rates"
                  : "Sold out"
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
          routing: firstQuote.routing || "Direct",
          remark: firstQuote.vessel || "-",
        });
      }
    }
  }

  // Add rows to sheet
  groupedExcelRows.forEach((row, idx) => {
    sheet.addRow({
      pol: idx === 0 ? row.pol : "",
      pod: idx === 0 ? row.pod : "",
      carrier: row.carrier,
      ...row,
    });
  });

  // Merge POL and POD cells vertically
  if (groupedExcelRows.length > 0) {
    sheet.mergeCells(2, 1, 1 + groupedExcelRows.length, 1);
    sheet.mergeCells(2, 2, 1 + groupedExcelRows.length, 2);
  }

  const getThinBorder = () => ({
    top: { style: "thin" as const, color: { argb: "808080" } },
    left: { style: "thin" as const, color: { argb: "808080" } },
    bottom: { style: "thin" as const, color: { argb: "808080" } },
    right: { style: "thin" as const, color: { argb: "808080" } },
  });

  // Style Header Row (Brand Orange #FA8C3C)
  const headerRow = sheet.getRow(1);
  headerRow.height = 32;
  headerRow.eachCell((cell) => {
    cell.font = { name: "Arial", size: 11, bold: true, color: { argb: "000000" } };
    cell.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FA8C3C" },
    };
    cell.alignment = { horizontal: "center", vertical: "middle" };
    cell.border = getThinBorder();
  });

  const numRateCols = rateColumns.length;

  // Style body cells (Official Blue #323296, Bold, numeric #,##0 format for rates)
  for (let r = 2; r <= 1 + groupedExcelRows.length; r++) {
    sheet.getRow(r).height = 28;

    // POL (Col 1)
    const cellA = sheet.getCell(r, 1);
    cellA.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellA.alignment = { horizontal: "center", vertical: "middle", wrapText: true };
    cellA.border = getThinBorder();

    // POD (Col 2)
    const cellB = sheet.getCell(r, 2);
    cellB.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellB.alignment = { horizontal: "center", vertical: "middle", wrapText: true };
    cellB.border = getThinBorder();

    // Carrier (Col 3)
    const cellC = sheet.getCell(r, 3);
    cellC.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellC.alignment = { horizontal: "center", vertical: "middle" };
    cellC.border = getThinBorder();

    // Container Rate Columns
    for (let c = 0; c < numRateCols; c++) {
      const cellRate = sheet.getCell(r, 4 + c);
      if (cellRate.value === "Sold out" || cellRate.value === "Offline rates") {
        cellRate.font = { name: "Arial", size: 11, bold: true, color: { argb: "C00000" } };
        cellRate.alignment = { horizontal: "center", vertical: "middle" };
      } else {
        cellRate.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
        cellRate.alignment = { horizontal: "center", vertical: "middle" };
        if (typeof cellRate.value === "number") {
          cellRate.numFmt = "#,##0";
        }
      }
      cellRate.border = getThinBorder();
    }

    // T/T
    const cellTT = sheet.getCell(r, 4 + numRateCols);
    cellTT.font = { name: "Arial", size: 11, bold: true, color: { argb: "385723" } };
    cellTT.alignment = { horizontal: "center", vertical: "middle" };
    cellTT.border = getThinBorder();

    // Free time
    const cellFreetime = sheet.getCell(r, 5 + numRateCols);
    cellFreetime.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellFreetime.alignment = { horizontal: "center", vertical: "middle" };
    cellFreetime.border = getThinBorder();

    // Demurrage
    const cellDemurrage = sheet.getCell(r, 6 + numRateCols);
    cellDemurrage.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellDemurrage.alignment = { horizontal: "center", vertical: "middle" };
    cellDemurrage.border = getThinBorder();

    // Detention
    const cellDetention = sheet.getCell(r, 7 + numRateCols);
    cellDetention.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellDetention.alignment = { horizontal: "center", vertical: "middle" };
    cellDetention.border = getThinBorder();

    // ETD POL
    const cellValidity = sheet.getCell(r, 8 + numRateCols);
    cellValidity.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellValidity.alignment = { horizontal: "center", vertical: "middle" };
    cellValidity.border = getThinBorder();

    // ETA POD
    const cellETA = sheet.getCell(r, 9 + numRateCols);
    cellETA.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellETA.alignment = { horizontal: "center", vertical: "middle" };
    cellETA.border = getThinBorder();

    // Validity Till
    const cellValidityTill = sheet.getCell(r, 10 + numRateCols);
    cellValidityTill.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellValidityTill.alignment = { horizontal: "center", vertical: "middle" };
    cellValidityTill.border = getThinBorder();

    // Routing
    const cellRouting = sheet.getCell(r, 11 + numRateCols);
    cellRouting.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellRouting.alignment = { horizontal: "center", vertical: "middle" };
    cellRouting.border = getThinBorder();

    // Remark
    const cellRemark = sheet.getCell(r, 12 + numRateCols);
    cellRemark.font = { name: "Arial", size: 10, bold: true, color: { argb: "323296" } };
    cellRemark.alignment = { horizontal: "center", vertical: "middle", wrapText: true };
    cellRemark.border = getThinBorder();
  }

  return sheet;
}

/**
 * Export Multi-Route or Single-Route results to Excel with standardized matrix layout matching ResultsTable.tsx.
 */
export async function exportMultiRouteResultsToExcel(
  batchResults: BatchRouteResult[],
  filename = "Infreight_Ocean_Rates.xlsx"
) {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = "Infreight Ocean Rate Automation";
  workbook.created = new Date();

  // If there are multiple routes, create a Summary Overview sheet first
  if (batchResults.length > 1) {
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

    const summaryHeaderRow = summarySheet.getRow(1);
    summaryHeaderRow.height = 28;
    summaryHeaderRow.font = { bold: true, color: { argb: "FFFFFF" } };
    summaryHeaderRow.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "1E293B" }, // Slate 800
    };
    summaryHeaderRow.alignment = { vertical: "middle", horizontal: "center" };

    batchResults.forEach((item, idx) => {
      const res = item.searchResult;
      const quotes = res?.results?.flatMap((r) => r.quotes || []) || [];

      const quotes20 = quotes.filter((q) => {
        const t = (q.container_type || "").toUpperCase();
        return t.includes("20") || t.includes("20GP");
      });
      const quotes40 = quotes.filter((q) => {
        const t = (q.container_type || "").toUpperCase();
        return t.includes("40") || t.includes("40GP") || t.includes("40HQ") || t.includes("40HC");
      });

      const rates20 = quotes20.map((q) => q.final_freight_value).filter((v) => typeof v === "number" && v > 0);
      const rates40 = quotes40.map((q) => q.final_freight_value).filter((v) => typeof v === "number" && v > 0);

      const min20 = rates20.length > 0 ? Math.min(...rates20) : null;
      const min40 = rates40.length > 0 ? Math.min(...rates40) : null;
      const carriersList = Array.from(new Set(res?.results?.map((r) => CARRIERS_MAP[r.carrier.toLowerCase()] || r.carrier) || [])).join(", ");
      const hasMismatch = res?.results?.some((cr) => cr.has_port_mismatch === true);

      summarySheet.addRow({
        index: idx + 1,
        origin: item.origin,
        destination: item.destination,
        status: item.status === "completed" ? (quotes.length > 0 ? "Quotes Found" : "No Quotes (No Direct Schedule)") : item.status.toUpperCase(),
        carriers: carriersList || (res ? "None" : "Pending"),
        rate20: min20 !== null ? `$${min20.toLocaleString()}` : "-",
        rate40: min40 !== null ? `$${min40.toLocaleString()}` : "-",
        mismatch: hasMismatch ? "⚠️ Port Mismatch" : "✅ Verified Match",
      });
    });
  }

  // Add standardized matrix worksheet per route
  batchResults.forEach((item, idx) => {
    if (item.searchResult) {
      let sheetTitle = `${item.origin || "Origin"} to ${item.destination || "Destination"}`;
      sheetTitle = sanitizeSheetName(sheetTitle, idx);
      addStandardRouteSheetToWorkbook(workbook, item.searchResult, sheetTitle);
    }
  });

  // Generate buffer and trigger browser download
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
