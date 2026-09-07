"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Modal scrim. Matches the Componentry overlay treatment: near-black wash
 * plus a backdrop blur that fades in with the panel.
 */
function Overlay({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="overlay"
      className={cn(
        "fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/55 p-4 backdrop-blur-md animate-blur-in",
        className,
      )}
      {...props}
    />
  );
}

/** Centered dialog panel that springs in from the scrim. */
function Panel({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="panel"
      className={cn(
        "w-full rounded-2xl border border-border bg-popover text-popover-foreground shadow-card-hover animate-scale-in-spring",
        className,
      )}
      {...props}
    />
  );
}

/** Thin rule using the ambient line token. */
function Separator({
  className,
  orientation = "horizontal",
  ...props
}: React.ComponentProps<"div"> & { orientation?: "horizontal" | "vertical" }) {
  return (
    <div
      data-slot="separator"
      role="separator"
      aria-orientation={orientation}
      className={cn(
        "shrink-0 bg-line",
        orientation === "horizontal" ? "h-px w-full" : "h-6 w-px",
        className,
      )}
      {...props}
    />
  );
}

/** Shimmering placeholder block. */
function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="skeleton"
      className={cn("animate-shimmer rounded-md bg-muted", className)}
      {...props}
    />
  );
}

/**
 * Section heading used above each major panel — an icon chip, a title, and
 * an optional trailing slot for controls.
 */
function SectionHeading({
  icon,
  title,
  description,
  actions,
  className,
  ...props
}: Omit<React.ComponentProps<"div">, "title"> & {
  icon?: React.ReactNode;
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <div
      data-slot="section-heading"
      className={cn(
        "flex flex-wrap items-start justify-between gap-3",
        className,
      )}
      {...props}
    >
      <div className="flex items-center gap-3">
        {icon && (
          <span className="inline-flex size-9 shrink-0 items-center justify-center rounded-xl border border-border bg-muted text-primary [&_svg:not([class*='size-'])]:size-4.5">
            {icon}
          </span>
        )}
        <div className="min-w-0">
          <h2 className="text-sm font-semibold tracking-tight text-foreground">
            {title}
          </h2>
          {description && (
            <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
          )}
        </div>
      </div>
      {actions && (
        <div className="flex flex-wrap items-center gap-2">{actions}</div>
      )}
    </div>
  );
}

export { Overlay, Panel, Separator, Skeleton, SectionHeading };
