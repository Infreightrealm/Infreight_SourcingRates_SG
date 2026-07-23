"""
Monitoring & alerting: Sentry error tracking, Healthchecks.io heartbeat,
and direct Telegram warnings.

Everything here is driven by environment variables and is a safe no-op when
they are not set, so the app runs unchanged until you opt in by filling in
your .env:

    SENTRY_DSN            -> enables Sentry error tracking
    HEALTHCHECK_URL       -> enables the "is the laptop alive?" heartbeat
    TELEGRAM_BOT_TOKEN    -> enables live Telegram warnings (with CHAT_ID)
    TELEGRAM_CHAT_ID      -> where Telegram warnings are delivered
    HEARTBEAT_INTERVAL    -> seconds between heartbeats (default 60)
"""
import asyncio
import os

import httpx


def _telegram_creds():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if token and chat_id:
        return token, chat_id
    return None


def send_telegram(text: str) -> None:
    """Send a Telegram message synchronously. Never raises."""
    creds = _telegram_creds()
    if not creds:
        return
    token, chat_id = creds
    try:
        httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": True},
            timeout=10,
        )
    except Exception as e:  # pragma: no cover - alerting must never break the app
        print(f"[WARN] Telegram send failed: {e}")


def init_sentry() -> None:
    """Initialise Sentry error tracking if SENTRY_DSN is set."""
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        print("[MONITOR] Sentry disabled (no SENTRY_DSN)")
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
    except ImportError:
        print("[WARN] sentry-sdk not installed; run: pip install 'sentry-sdk[fastapi]'")
        return

    def _before_send(event, hint):
        # Also push a live Telegram warning for every error Sentry captures.
        exc = hint.get("exc_info")
        title = event.get("logentry", {}).get("message") or event.get("transaction") or "Error"
        if exc:
            title = f"{exc[0].__name__}: {exc[1]}"
        send_telegram(f"🔴 Backend error\n{title}")
        return event

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "laptop-backend"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
        before_send=_before_send,
    )
    print("[MONITOR] Sentry enabled")


async def _heartbeat_loop(url: str, interval: int) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        # Ping /start once so Healthchecks knows we just (re)started.
        try:
            await client.get(url.rstrip("/") + "/start")
        except Exception:
            pass
        while True:
            try:
                await client.get(url)
            except Exception as e:
                print(f"[WARN] Heartbeat ping failed: {e}")
            await asyncio.sleep(interval)


def start_heartbeat() -> "asyncio.Task | None":
    """Start the Healthchecks.io heartbeat loop if HEALTHCHECK_URL is set.

    Returns the created task (so it can be cancelled on shutdown), or None.
    """
    url = os.getenv("HEALTHCHECK_URL", "").strip()
    if not url:
        print("[MONITOR] Heartbeat disabled (no HEALTHCHECK_URL)")
        return None
    interval = int(os.getenv("HEARTBEAT_INTERVAL", "60"))
    print(f"[MONITOR] Heartbeat enabled (every {interval}s)")
    return asyncio.create_task(_heartbeat_loop(url, interval))
