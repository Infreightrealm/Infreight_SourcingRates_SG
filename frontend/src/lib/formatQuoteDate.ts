/** "2026-10-08" / "08-Oct-2026" / "2026/10/08" -> "8 Oct 2026"; anything else as given; empty -> "—". */
export function formatQuoteDate(dateVal: string | null | undefined): string {
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
