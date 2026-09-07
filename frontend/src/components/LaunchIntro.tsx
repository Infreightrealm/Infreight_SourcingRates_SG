"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Image from "next/image";
import { setPreferences } from "@/lib/preferences";

const HOLD_MS = 2600;

/**
 * First-visit launch sequence. Plays once per browser, then never again unless
 * replayed from the workspace panel. Skippable by click, Escape or the button,
 * and skipped outright when the OS asks for reduced motion.
 *
 * `force` replays it on demand and does not re-write the seen flag.
 */
export default function LaunchIntro({
  seen,
  force = false,
  onDone,
}: {
  seen: boolean;
  force?: boolean;
  onDone?: () => void;
}) {
  // The parent only mounts this after hydration, so the decision can be made
  // in the initializer — that keeps the effect free of a synchronous setState.
  const [phase, setPhase] = useState<"idle" | "playing" | "leaving">(() => {
    if (typeof window === "undefined") return "idle";
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return "idle";
    return !force && seen ? "idle" : "playing";
  });
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  // Marking the intro seen flips the `seen` prop, which would otherwise re-run
  // the start effect and let its cleanup cancel the finish timer mid-sequence.
  const started = useRef(false);

  const clearTimers = () => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
  };

  const finish = useCallback(() => {
    clearTimers();
    setPhase((p) => (p === "playing" ? "leaving" : p));
    timers.current.push(
      setTimeout(() => {
        setPhase("idle");
        onDone?.();
      }, 480),
    );
  }, [onDone]);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    // Mark it seen up front: a reload mid-sequence shouldn't replay it.
    if (!force && !seen) setPreferences({ introSeen: true });
    if (phase === "playing") timers.current.push(setTimeout(finish, HOLD_MS));
    // Runs once — `seen` flips as soon as the flag above is written.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Timers are torn down on unmount only — never when `seen` changes.
  useEffect(() => clearTimers, []);

  useEffect(() => {
    if (phase !== "playing") return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" || e.key === "Enter" || e.key === " ") finish();
    };
    window.addEventListener("keydown", onKey);
    // The console behind the veil shouldn't scroll while it's up.
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [phase, finish]);

  if (phase === "idle") return null;

  const leaving = phase === "leaving";

  return (
    <div
      role="presentation"
      onClick={finish}
      className="fixed inset-0 z-[200] flex cursor-pointer items-center justify-center overflow-hidden bg-background transition-opacity duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
      style={{ opacity: leaving ? 0 : 1, pointerEvents: leaving ? "none" : "auto" }}
    >
      {/* Ambient brand glow behind the mark */}
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-1/2 size-[42rem] max-w-none -translate-x-1/2 -translate-y-1/2 rounded-full opacity-70 blur-3xl"
        style={{
          background:
            "radial-gradient(circle, color-mix(in srgb, var(--primary) 22%, transparent) 0%, transparent 68%)",
        }}
      />

      <div className="relative flex flex-col items-center gap-6 px-6 text-center">
        {/* Mark */}
        <div
          className="bg-gradient-brand relative flex size-20 items-center justify-center overflow-hidden rounded-2xl shadow-brand"
          style={{ animation: "intro-mark-in 0.7s cubic-bezier(0.34,1.4,0.64,1) both" }}
        >
          <Image
            src="/infreight_logo.png"
            alt=""
            aria-hidden
            width={48}
            height={48}
            priority
            className="size-12 object-contain"
          />
          <span
            aria-hidden
            className="absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-white/45 to-transparent"
            style={{ animation: "intro-sweep 1.1s cubic-bezier(0.16,1,0.3,1) 0.55s both" }}
          />
        </div>

        {/* Horizon rule — draws outward from the mark */}
        <div
          aria-hidden
          className="h-px w-56 origin-center bg-gradient-to-r from-transparent via-[var(--primary)] to-transparent"
          style={{ animation: "intro-rule-draw 0.8s cubic-bezier(0.16,1,0.3,1) 0.34s both" }}
        />

        <div className="flex flex-col items-center gap-2">
          <h1
            className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl"
            style={{ animation: "intro-word-in 0.6s cubic-bezier(0.16,1,0.3,1) 0.46s both" }}
          >
            Infreight <span className="text-gradient-brand">Ocean &amp; Air</span>
          </h1>
          <p
            className="text-xs uppercase tracking-[0.28em] text-muted-foreground"
            style={{ animation: "intro-word-in 0.6s cubic-bezier(0.16,1,0.3,1) 0.62s both" }}
          >
            Rate Automation
          </p>
        </div>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            finish();
          }}
          className="mt-2 rounded-full border border-border bg-card/60 px-4 py-1.5 text-[11px] font-medium text-muted-foreground backdrop-blur transition-colors hover:bg-accent hover:text-foreground"
          style={{ animation: "intro-word-in 0.5s cubic-bezier(0.16,1,0.3,1) 1.1s both" }}
        >
          Skip intro
        </button>
      </div>
    </div>
  );
}
