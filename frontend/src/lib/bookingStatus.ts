import type { QuoteSchema } from "./types";

export type BookingStatusType =
  | "spot_guaranteed"
  | "tariff_spot_full"
  | "tariff_restricted"
  | "tariff_can_not_be_offered"
  | "booking_closed"
  | "tariff_general"
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
 * - If tariff-only (spot full, restrictions, closed): isAmberAlert = true (renders ⚠️ Amber Alert).
 * - If normal regular tariff without errors: isAmberAlert = false (renders neutral Standard Tariff).
 */
export function getBookingStatus(q: QuoteSchema): BookingStatusInfo {
  const vesselText = (q.vessel || "").toUpperCase();
  const warningText = (q.warning_message || "").toUpperCase();

  // 1. Cutoff Expired / Booking Closed
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

  // 2. Spot Full / Capacity
  if (
    vesselText.includes("TARIFF ONLY - SPOT FULL") ||
    vesselText.includes("SPOT FULL") ||
    warningText.includes("CAPACITY")
  ) {
    return {
      type: "tariff_spot_full",
      badgeLabel: "Tariff Only · Spot Full",
      isAmberAlert: true,
      isSpot: false,
      description: q.warning_message || "Spot space is at maximum capacity. Rate is base tariff; space requires manual confirmation.",
    };
  }

  // 3. Online Restrictions (e.g., trade desk lock, embargo, quota)
  if (
    vesselText.includes("TARIFF ONLY - RESTRICTIONS") ||
    vesselText.includes("RESTRICTIONS") ||
    warningText.includes("RESTRICTIONS")
  ) {
    return {
      type: "tariff_restricted",
      badgeLabel: "Tariff Only · Restricted",
      isAmberAlert: true,
      isSpot: false,
      description: q.warning_message || "Online spot booking restricted on carrier portal. Booking requires manual confirmation.",
    };
  }

  // 4. Can Not Be Offered
  if (
    vesselText.includes("TARIFF ONLY - CAN_NOT_BE_OFFERED") ||
    vesselText.includes("CAN_NOT_BE_OFFERED") ||
    warningText.includes("CAN_NOT_BE_OFFERED")
  ) {
    return {
      type: "tariff_can_not_be_offered",
      badgeLabel: "Tariff Only · Unavailable",
      isAmberAlert: true,
      isSpot: false,
      description: q.warning_message || "Routing currently unavailable for online booking. Manual enquiry required.",
    };
  }

  // 5. Explicit Tariff Only / Unconfirmed Space (when tagged [TARIFF ONLY])
  if (
    vesselText.includes("TARIFF ONLY") ||
    warningText.includes("TARIFF QUOTE (QQ)")
  ) {
    return {
      type: "tariff_general",
      badgeLabel: "Tariff Only",
      isAmberAlert: true,
      isSpot: false,
      description: q.warning_message || "Published tariff rate. Online space allocation not confirmed.",
    };
  }

  // 6. Spot Space Guaranteed
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

  // 7. Standard Regular Tariff (normal healthy quotation without spot or errors)
  return {
    type: "standard",
    badgeLabel: "Standard Tariff",
    isAmberAlert: false,
    isSpot: false,
    description: q.warning_message || "Standard published tariff rate on active schedule.",
  };
}
