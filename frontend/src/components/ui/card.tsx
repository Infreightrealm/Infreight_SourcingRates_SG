"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const cardVariants = cva(
  "rounded-2xl border text-card-foreground transition-shadow",
  {
    variants: {
      variant: {
        /** Standard raised surface. */
        default: "border-border bg-card shadow-card",
        /** Frosted panel that lets the page mesh show through. */
        glass:
          "border-border bg-card/70 shadow-panel backdrop-blur-xl supports-[backdrop-filter]:bg-card/60",
        /** Flat, for nesting inside another card. */
        subtle: "border-border/70 bg-muted/40 shadow-none",
        /** Tinted callouts. */
        info: "border-info/25 bg-info/8 shadow-none",
        success: "border-success/25 bg-success/8 shadow-none",
        warning: "border-warning/30 bg-warning/8 shadow-none",
        destructive: "border-destructive/25 bg-destructive/8 shadow-none",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

function Card({
  className,
  variant,
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof cardVariants>) {
  return (
    <div
      data-slot="card"
      className={cn(cardVariants({ variant }), className)}
      {...props}
    />
  );
}

function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        "flex flex-wrap items-center justify-between gap-3 px-5 py-4 sm:px-6",
        className,
      )}
      {...props}
    />
  );
}

function CardTitle({ className, ...props }: React.ComponentProps<"h2">) {
  return (
    <h2
      data-slot="card-title"
      className={cn(
        "flex items-center gap-2 text-sm font-semibold tracking-tight text-foreground",
        className,
      )}
      {...props}
    />
  );
}

function CardDescription({ className, ...props }: React.ComponentProps<"p">) {
  return (
    <p
      data-slot="card-description"
      className={cn("text-xs text-muted-foreground", className)}
      {...props}
    />
  );
}

function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-content"
      className={cn("px-5 pb-5 sm:px-6 sm:pb-6", className)}
      {...props}
    />
  );
}

/**
 * Hairline that bleeds to the card edges — separates a header from content
 * without the inset look of a padded border.
 */
function CardSeparator({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-separator"
      className={cn("h-px w-full bg-line", className)}
      {...props}
    />
  );
}

/**
 * Small square glyph slot that sits to the left of a card title.
 */
function CardIcon({ className, ...props }: React.ComponentProps<"span">) {
  return (
    <span
      data-slot="card-icon"
      className={cn(
        "inline-flex size-8 shrink-0 items-center justify-center rounded-lg border border-border bg-muted text-muted-foreground [&_svg:not([class*='size-'])]:size-4",
        className,
      )}
      {...props}
    />
  );
}

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardSeparator,
  CardIcon,
  cardVariants,
};
