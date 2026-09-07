"use client";

import React from "react";

import { cn } from "@/lib/utils";

interface PulsatingButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  pulseColor?: string;
  duration?: string;
}

/**
 * Componentry `pulsating-button` — emits an expanding ring. Reserved for
 * controls that need attention while work is in flight (live viewer, stop).
 */
const PulsatingButton = React.forwardRef<
  HTMLButtonElement,
  PulsatingButtonProps
>(
  (
    {
      className,
      children,
      pulseColor = "rgba(59, 130, 246, 0.55)",
      duration = "1.5s",
      ...props
    },
    ref,
  ) => {
    return (
      <button
        ref={ref}
        className={cn(
          "relative flex cursor-pointer items-center justify-center rounded-full bg-primary px-4 py-2 text-center text-sm font-medium text-primary-foreground",
          "disabled:pointer-events-none disabled:opacity-50",
          className,
        )}
        style={
          {
            "--pulse-color": pulseColor,
            "--duration": duration,
          } as React.CSSProperties
        }
        {...props}
      >
        <div className="relative z-10 flex items-center gap-1.5">{children}</div>
        <div className="absolute left-1/2 top-1/2 size-full -translate-x-1/2 -translate-y-1/2 animate-pulse-ring rounded-full bg-inherit" />
      </button>
    );
  },
);

PulsatingButton.displayName = "PulsatingButton";

export { PulsatingButton };
