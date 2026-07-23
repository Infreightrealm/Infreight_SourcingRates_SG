import { NextRequest, NextResponse } from "next/server";
import { sendTelegram } from "@/lib/telegram";

/**
 * Receives client-side error reports and forwards them to Telegram.
 * The bot token stays on the server; the browser only POSTs a message here.
 */
export async function POST(req: NextRequest) {
  let message = "Frontend error";
  try {
    const body = await req.json();
    if (body?.message) message = String(body.message).slice(0, 1000);
  } catch {
    // ignore malformed body — fall back to the default message
  }
  await sendTelegram(`🟠 Frontend error\n${message}`);
  return NextResponse.json({ ok: true });
}
