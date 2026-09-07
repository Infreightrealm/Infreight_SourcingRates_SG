"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-full border font-medium transition-colors [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-3",
  {
    variants: {
      variant: {
        default: "border-border bg-muted text-muted-foreground",
        outline: "border-border bg-transparent text-foreground",
        primary: "border-primary/25 bg-primary/10 text-primary",
        info: "border-info/25 bg-info/12 text-info-foreground",
        success: "border-success/25 bg-success/12 text-success-foreground",
        warning: "border-warning/30 bg-warning/12 text-warning-foreground",
        destructive:
          "border-destructive/25 bg-destructive/12 text-destructive-foreground",
      },
      size: {
        sm: "px-2 py-0.5 text-[11px]",
        default: "px-2.5 py-1 text-xs",
        lg: "px-3 py-1.5 text-sm",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

function Badge({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span";

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant, size }), className)}
      {...props}
    />
  );
}

/** Small pulsing status dot, for live/queued indicators. */
function Dot({
  className,
  pulse = false,
  ...props
}: React.ComponentProps<"span"> & { pulse?: boolean }) {
  return (
    <span
      data-slot="dot"
      className={cn("relative flex size-2 shrink-0", className)}
      {...props}
    >
      {pulse && (
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-current opacity-70" />
      )}
      <span className="relative inline-flex size-2 rounded-full bg-current" />
    </span>
  );
}

export { Badge, Dot, badgeVariants };
