import ExcelJS from "exceljs";
import type { RateSearchResultResponse, QuoteSchema } from "./types";

export interface BatchRouteResult {
  origin: string;
  destination: string;
  searchResult?: RateSearchResultResponse | null;
  status: "pending" | "running" | "completed" | "failed";
}

const CONTAINER_ORDER: Record<string, number> = {
  "DRY 20": 1,
  "20GP": 1,
  "20'": 1,
  "DRY 40": 2,
  "40GP": 2,
  "40'": 2,
  "DRY 40H": 3,
  "40HQ": 3,
  "40HC": 3,
  "40'HQ": 3,
  "40'HC": 3,
};

function sortContainerTypes(types: string[]): string[] {
  return [...types].sort((a, b) => {
    const orderA = CONTAINER_ORDER[a.toUpperCase()] ?? 99;
    const orderB = CONTAINER_ORDER[b.toUpperCase()] ?? 99;
    if (orderA !== orderB) return orderA - orderB;
    return a.localeCompare(b);
  });
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

const CARRIERS_LIST = [
  { code: "maersk", name: "Maersk" },
  { code: "cma", name: "CMA CGM" },
  { code: "one", name: "ONE" },
  { code: "hapag", name: "Hapag-Lloyd" },
  { code: "greenx", name: "GreenX" },
  { code: "msc", name: "MSC" },
  { code: "oocl", name: "OOCL" },
];

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
 * Single Search Rate Export — Pixel-perfect matching ResultsTable.tsx styling.
 */
export async function exportSingleSearchToExcel(
  data: RateSearchResultResponse,
  customFilename?: string
) {
  if (!data || !data.results) return;

  // Extract all quotes across carrier results
  const allQuotes = data.results.flatMap((cr) => cr.quotes || []);

  const uniqueContainerTypes = sortContainerTypes(
    Array.from(
      new Set(
        allQuotes
          .map((q) => q.container_type)
          .filter((ct): ct is string => !!ct)
      )
    )
  );

  const rawContainerTypes = data.container_types || (data.container_type ? [data.container_type] : ["DRY 40H"]);
  const containerTypesList = uniqueContainerTypes.length > 0 ? uniqueContainerTypes : sortContainerTypes(rawContainerTypes);
  const baseCurrency = allQuotes[0]?.currency || "USD";

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

  let sheetName = `${data.origin || "Origin"} to ${data.destination || "Destination"}`;
  sheetName = sheetName.replace(/[\\\/\?\*\[\]]/g, "");
  if (sheetName.length > 31) {
    sheetName = sheetName.substring(0, 31);
  }

  const workbook = new ExcelJS.Workbook();
  const sheet = workbook.addWorksheet(sheetName);

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

  for (const cr of data.results) {
    const carrierInfo = CARRIERS_LIST.find((c) => c.code === cr.carrier.toLowerCase());
    const carrierName = carrierInfo?.name || cr.carrier;

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
    top: { style: "thin" as const, color: { argb: "808080" } },
    left: { style: "thin" as const, color: { argb: "808080" } },
    bottom: { style: "thin" as const, color: { argb: "808080" } },
    right: { style: "thin" as const, color: { argb: "808080" } },
  });

  // Style header row (Brand Orange #FA8C3C)
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

  // Style body cells (Official Blue #323296)
  for (let r = 2; r <= 1 + groupedExcelRows.length; r++) {
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

    // Validity
    const cellValidity = sheet.getCell(r, 8 + numRateCols);
    cellValidity.font = { name: "Arial", size: 11, bold: true, color: { argb: "323296" } };
    cellValidity.alignment = { horizontal: "center", vertical: "middle" };
    cellValidity.border = getThinBorder();

    // ETA
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

  // Set row height for body rows
  for (let r = 2; r <= 1 + groupedExcelRows.length; r++) {
    sheet.getRow(r).height = 28;
  }

  // Generate buffer and trigger browser download
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const safeOrig = (data.origin || "Origin").replace(/[^a-zA-Z0-9]/g, "_");
  const safeDest = (data.destination || "Destination").replace(/[^a-zA-Z0-9]/g, "_");
  a.download = customFilename || `Infreight_${safeOrig}_to_${safeDest}_Rates.xlsx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

/**
 * Export Multi-Route results to Excel with standardized matrix layout matching ResultsTable.tsx.
 */
export async function exportMultiRouteResultsToExcel(
  batchResults: BatchRouteResult[],
  filename = "Infreight_Ocean_Rates.xlsx"
) {
  if (batchResults.length === 1 && batchResults[0].searchResult) {
    return exportSingleSearchToExcel(batchResults[0].searchResult, filename);
  }

  const workbook = new ExcelJS.Workbook();
  workbook.creator = "Infreight Ocean Rate Automation";
  workbook.created = new Date();

  // Summary Overview sheet
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
    fgColor: { argb: "1E293B" },
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
    const carriersList = Array.from(new Set(res?.results?.map((r) => CARRIERS_LIST.find((c) => c.code === r.carrier.toLowerCase())?.name || r.carrier) || [])).join(", ");
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

  // Add individual worksheets using identical exporter logic
  for (let idx = 0; idx < batchResults.length; idx++) {
    const item = batchResults[idx];
    if (item.searchResult) {
      let sheetTitle = `${item.origin || "Origin"} to ${item.destination || "Destination"}`;
      sheetTitle = sanitizeSheetName(sheetTitle, idx);
      
      // Temporary workbook sheet building
      const tempWb = new ExcelJS.Workbook();
      await exportSingleSearchToExcel(item.searchResult, "temp.xlsx");
    }
  }

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


/**
 * Export Tariff Rate Matrix (1st Half / 2nd Half) — Matches the exact format of the customer's RFQ sheet.
 * EX PASIR GUDANG/TG PELEPAS TO POR BELOW
 */
export async function exportTariffMatrixToExcel(
  batchResults: BatchRouteResult[],
  originName = "PASIR GUDANG / TG PELEPAS",
  filename = "Pasir_Gudang_Tariff_Rates.xlsx"
) {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = "Infreight Ocean Rate Automation";
  workbook.created = new Date();

  const sheet = workbook.addWorksheet("Tariff Rate Matrix");

  // Title Banner
  sheet.mergeCells("A1:G1");
  const titleCell = sheet.getCell("A1");
  titleCell.value = `EX ${originName.toUpperCase()} TO POR BELOW`;
  titleCell.font = { bold: true, size: 12, color: { argb: "000000" } };
  titleCell.alignment = { vertical: "middle", horizontal: "left" };
  sheet.getRow(1).height = 25;

  // Header Row 2 & Row 3
  sheet.mergeCells("A2:A3");
  sheet.getCell("A2").value = "PORT DESTINATION";
  sheet.getCell("A2").font = { bold: true, size: 10 };
  sheet.getCell("A2").fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFFEE0" } };
  sheet.getCell("A2").alignment = { vertical: "middle", horizontal: "center", wrapText: true };

  sheet.mergeCells("B2:B3");
  sheet.getCell("B2").value = "PAYMENT BY";
  sheet.getCell("B2").font = { bold: true, size: 10 };
  sheet.getCell("B2").fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFFEE0" } };
  sheet.getCell("B2").alignment = { vertical: "middle", horizontal: "center", wrapText: true };

  // Agent / Carrier Name Headers
  sheet.mergeCells("C2:F2");
  sheet.getCell("C2").value = "CARRIER / AGENT QUOTE (CHEAPEST IN 14-DAY WINDOW)";
  sheet.getCell("C2").font = { bold: true, size: 10 };
  sheet.getCell("C2").fill = { type: "pattern", pattern: "solid", fgColor: { argb: "D1E7DD" } };
  sheet.getCell("C2").alignment = { vertical: "middle", horizontal: "center" };

  sheet.mergeCells("C3:D3");
  sheet.getCell("C3").value = "1ST HALF (1-14 Days)";
  sheet.getCell("C3").font = { bold: true, size: 9 };
  sheet.getCell("C3").fill = { type: "pattern", pattern: "solid", fgColor: { argb: "E2F0D9" } };
  sheet.getCell("C3").alignment = { vertical: "middle", horizontal: "center" };

  sheet.mergeCells("E3:F3");
  sheet.getCell("E3").value = "2ND HALF (15-28 Days)";
  sheet.getCell("E3").font = { bold: true, size: 9 };
  sheet.getCell("E3").fill = { type: "pattern", pattern: "solid", fgColor: { argb: "E2F0D9" } };
  sheet.getCell("E3").alignment = { vertical: "middle", horizontal: "center" };

  // Column Sub-headers Row 4
  sheet.getCell("A4").value = "";
  sheet.getCell("B4").value = "";
  sheet.getCell("C4").value = "20'";
  sheet.getCell("D4").value = "40'";
  sheet.getCell("E4").value = "20'";
  sheet.getCell("F4").value = "40'";
  sheet.getCell("G4").value = "CARRIER / NOTES";

  sheet.getRow(4).height = 20;
  ["C4", "D4", "E4", "F4", "G4"].forEach((pos) => {
    const c = sheet.getCell(pos);
    c.font = { bold: true, size: 9 };
    c.fill = { type: "pattern", pattern: "solid", fgColor: { argb: "D1E7DD" } };
    c.alignment = { vertical: "middle", horizontal: "center" };
  });

  sheet.columns = [
    { key: "destination", width: 26 },
    { key: "payment_by", width: 14 },
    { key: "rate20_1st", width: 14 },
    { key: "rate40_1st", width: 14 },
    { key: "rate20_2nd", width: 14 },
    { key: "rate40_2nd", width: 14 },
    { key: "carrier_notes", width: 28 },
  ];

  // Populate data rows
  batchResults.forEach((item) => {
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

    const carrierNames = Array.from(new Set(res?.results?.filter(r => (r.quotes?.length || 0) > 0).map(r => r.carrier) || [])).join(", ");
    const etdList = Array.from(new Set(quotes.map(q => q.etd).filter(Boolean))).join(", ");

    const row = sheet.addRow({
      destination: item.destination.toUpperCase(),
      payment_by: "USD",
      rate20_1st: min20 !== null ? min20 : "",
      rate40_1st: min40 !== null ? min40 : "",
      rate20_2nd: "",
      rate40_2nd: "",
      carrier_notes: carrierNames ? `${carrierNames} (ETD: ${etdList || 'In Window'})` : (item.status === "completed" ? "No Direct Schedule" : item.status.toUpperCase()),
    });

    row.height = 22;
    row.getCell(1).fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFFEE0" } };
    row.getCell(1).font = { bold: true, size: 9 };
    row.getCell(1).alignment = { vertical: "middle", horizontal: "left" };

    row.getCell(2).fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFFEE0" } };
    row.getCell(2).alignment = { vertical: "middle", horizontal: "center" };

    row.getCell(3).alignment = { vertical: "middle", horizontal: "center" };
    row.getCell(4).alignment = { vertical: "middle", horizontal: "center" };
    row.getCell(5).alignment = { vertical: "middle", horizontal: "center" };
    row.getCell(6).alignment = { vertical: "middle", horizontal: "center" };
    row.getCell(7).alignment = { vertical: "middle", horizontal: "left" };
  });

  // Apply borders to all table cells
  sheet.eachRow((row, rowNumber) => {
    if (rowNumber >= 2) {
      row.eachCell((cell) => {
        cell.border = {
          top: { style: "thin", color: { argb: "D3D3D3" } },
          left: { style: "thin", color: { argb: "D3D3D3" } },
          bottom: { style: "thin", color: { argb: "D3D3D3" } },
          right: { style: "thin", color: { argb: "D3D3D3" } },
        };
      });
    }
  });

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

