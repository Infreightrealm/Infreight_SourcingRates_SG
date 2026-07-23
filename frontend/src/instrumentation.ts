/**
 * Next.js instrumentation. `onRequestError` fires for uncaught server-side
 * errors (route handlers, server components) and forwards them to Telegram.
 */
export async function onRequestError(err: unknown) {
  const { sendTelegram } = await import("@/lib/telegram");
  const msg =
    err instanceof Error ? `${err.name}: ${err.message}` : String(err);
  await sendTelegram(`🔴 Frontend server error\n${msg}`);
}
