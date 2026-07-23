"use client";

import { useEffect } from "react";

/**
 * Root error boundary. Catches client-side rendering errors, reports them to
 * Telegram via /api/alert (server-side), and shows a minimal fallback.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    fetch("/api/alert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: `${error.name}: ${error.message}` }),
    }).catch(() => {
      // alerting must never break the error page
    });
  }, [error]);

  return (
    <html>
      <body style={{ fontFamily: "system-ui, sans-serif", padding: "2rem" }}>
        <h2>Something went wrong.</h2>
        <p>The team has been notified. Please try again.</p>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  );
}
