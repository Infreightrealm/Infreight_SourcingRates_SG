/**
 * Server-side Telegram notifier.
 *
 * WARNING: server-only. Never import this from a client component — it reads
 * secret env vars (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID). Use it from route
 * handlers (e.g. /api/alert) and instrumentation only.
 *
 * Safe no-op when the env vars are not set.
 */
export async function sendTelegram(text: string): Promise<void> {
  const token = process.env.TELEGRAM_BOT_TOKEN?.trim();
  const chatId = process.env.TELEGRAM_CHAT_ID?.trim();
  if (!token || !chatId) return;
  try {
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: text.slice(0, 4000),
        disable_web_page_preview: true,
      }),
    });
  } catch (e) {
    console.error("[telegram] send failed", e);
  }
}
