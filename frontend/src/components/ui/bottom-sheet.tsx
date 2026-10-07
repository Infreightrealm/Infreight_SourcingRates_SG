"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";
import { X } from "lucide-react";

import { cn } from "@/lib/utils";

interface BottomSheetProps {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  /** Shown under the title, e.g. the lane or carrier. */
  subtitle?: ReactNode;
  /** Sticky row at the bottom of the sheet (actions). */
  footer?: ReactNode;
  children: ReactNode;
  className?: string;
}

/**
 * Phone sheet that slides up from the bottom over a scrim: closes on the scrim,
 * the close button or Escape, locks page scroll while open, and keeps clear of
 * the home indicator.
 */
export function BottomSheet({ open, onClose, title, subtitle, footer, children, className }: BottomSheetProps) {
  const titleId = useId();
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKey);
    panelRef.current?.focus();
    return () => {
      document.body.style.overflow = prevOverflow;
      document.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[90]">
      <div className="animate-fade-in absolute inset-0 bg-slate-950/50" onClick={onClose} aria-hidden />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className={cn(
          "animate-fade-in-up absolute inset-x-0 bottom-0 flex max-h-[88dvh] flex-col rounded-t-2xl border-t border-border bg-popover text-popover-foreground shadow-card-hover outline-none",
          className,
        )}
      >
        <div className="mx-auto mb-1 mt-2 h-1.5 w-10 shrink-0 rounded-full bg-border" aria-hidden />
        <div className="flex shrink-0 items-start gap-3 border-b border-border px-5 pb-3 pt-1">
          <div className="min-w-0 flex-1">
            <h2 id={titleId} className="text-lg font-bold text-foreground">
              {title}
            </h2>
            {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="-mr-2 flex size-11 shrink-0 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground"
          >
            <X className="size-5" />
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-5 py-4">{children}</div>
        {footer && (
          <div className="shrink-0 border-t border-border px-5 pb-[calc(0.75rem+env(safe-area-inset-bottom))] pt-3">{footer}</div>
        )}
        {!footer && <div className="h-[env(safe-area-inset-bottom)] shrink-0" aria-hidden />}
      </div>
    </div>
  );
}
