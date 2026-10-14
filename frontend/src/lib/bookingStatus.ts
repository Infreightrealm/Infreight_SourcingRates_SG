import type { QuoteSchema } from "./types";

export type BookingStatusType =
  | "spot_guaranteed"
  | "tariff_spot_full"
  | "booking_closed"
  | "no_online_schedule"
  | "standard";

export interface BookingStatusInfo {
  type: BookingStatusType;
  badgeLabel: string;
  isAmberAlert: boolean;
  isSpot: boolean;
  description: string;
}

/**
 * Strips technical tags like [TARIFF ONLY - ...] or [SPOT GUARANTEED]
 * from the vessel string so the vessel name remains legible without truncation.
 */
export function cleanVesselName(vessel?: string | null): string {
  if (!vessel) return "";
  return vessel
    .replace(/\[.*?\]/g, "")
    .replace(/\(QQ Tariff\)/gi, "")
    .replace(/\(SPOT\)/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Categorizes a quote's booking and space availability status.
 *
 * Rules:
 * - If spot space is guaranteed: isAmberAlert = false (renders ✅ Spot Space Guaranteed).
 * - If normal Quick Quotes tariff (even if Spot product is unavailable): isAmberAlert = false (renders clean Standard Tariff).
 * - Only genuine operational blockers (Vessel Full CAPACITY, Cut-off Expired, or No Online Schedule) trigger an Amber Alert.
 */
export function getBookingStatus(q: QuoteSchema): BookingStatusInfo {
  const vesselText = (q.vessel || "").toUpperCase();
  const warningText = (q.warning_message || "").toUpperCase();

  // 1. Cutoff Expired / Booking Closed (Operational Hard Stop)
  if (
    vesselText.includes("BOOKING CLOSED") ||
    vesselText.includes("CUTOFF EXPIRED") ||
    warningText.includes("BOOKING CUTOFF EXPIRED") ||
    warningText.includes("CUTOFF EXPIRED")
  ) {
    return {
      type: "booking_closed",
      badgeLabel: "Booking Closed",
      isAmberAlert: true,
      isSpot: false,
      description: q.warning_message || "Booking cut-off deadline has passed. Space is closed for this sailing.",
    };
  }

  // 2. Spot Full / Capacity (Vessel is physically 100% full)
  if (
    vesselText.includes("TARIFF ONLY - SPOT FULL") ||
    vesselText.includes("SPOT FULL") ||
    warningText.includes("VESSEL AT CAPACITY") ||
    warningText.includes("AT CAPACITY")
  ) {
    return {
      type: "tariff_spot_full",
      badgeLabel: "Tariff Only · Spot Full",
      isAmberAlert: true,
      isSpot: false,
      description: q.warning_message || "Spot space is at maximum capacity. Rate is base tariff; space requires manual confirmation.",
    };
  }

  // 3. No online schedule found in schedule engine
  if (
    vesselText.includes("NO ONLINE SCHEDULE") ||
    warningText.includes("NO ACTIVE COMMERCIAL SAILING")
  ) {
    return {
      type: "no_online_schedule",
      badgeLabel: "No Online Schedule",
      isAmberAlert: true,
      isSpot: false,
      description: q.warning_message || "No active sailing found in schedule engine. Offline enquiry required.",
    };
  }

  // 4. Spot Space Guaranteed
  if (
    vesselText.includes("SPOT GUARANTEED") ||
    (vesselText.includes("SPOT") && !vesselText.includes("TARIFF"))
  ) {
    return {
      type: "spot_guaranteed",
      badgeLabel: "Spot Guaranteed",
      isAmberAlert: false, // Per user rule: if spot is guaranteed, no need for amber alert
      isSpot: true,
      description: q.warning_message || "Spot space guaranteed with active schedule.",
    };
  }

  // 5. Standard Regular Tariff (Quick Quotes rate active & bookable online — NO AMBER ALERT)
  return {
    type: "standard",
    badgeLabel: "Standard Tariff",
    isAmberAlert: false,
    isSpot: false,
    description: q.warning_message || "Standard published tariff rate on active schedule.",
  };
}
