/**
 * Lets any part of the page open the floating live-browser (VNC) viewer on a
 * given carrier's tab, e.g. the "Open live viewer" button on a carrier that is
 * waiting for a CAPTCHA.
 */

export const OPEN_LIVE_VIEWER_EVENT = "infreight:open-live-viewer";

/** Backend carrier codes -> the tab codes /api/vnc-status returns. */
export const VNC_TAB_BY_CARRIER: Record<string, string> = {
  MAERSK: "maersk",
  CMA_CGM: "cma",
  ONE: "one",
  HAPAG_LLOYD: "hapag",
  GREENX: "greenx",
  MSC: "msc",
  OOCL: "oocl",
};

export function openLiveViewer(carrier?: string) {
  window.dispatchEvent(new CustomEvent(OPEN_LIVE_VIEWER_EVENT, { detail: { carrier } }));
}

/** Opens the AI assistant chat, e.g. from the phone "More" menu where its floating button is hidden. */
export const OPEN_ASSISTANT_EVENT = "infreight:open-assistant";
/** Opens the colleague messages panel, e.g. from the phone "More" menu. */
export const OPEN_MESSAGES_EVENT = "infreight:open-messages";
/** SocialWidget announces its unread total so the phone tab bar can badge "More". */
export const MESSAGES_UNREAD_EVENT = "infreight:messages-unread";
