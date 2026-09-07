"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Shared field surface. Exported as a plain string so existing raw
 * `<input>` / `<select>` / `<textarea>` elements can adopt the Componentry
 * look without being restructured.
 */
export const fieldClassName = cn(
  "w-full min-w-0 rounded-lg border border-input bg-card px-3.5 py-2.5 text-sm text-foreground",
  "shadow-xs transition-[color,box-shadow,border-color,background-color]",
  "placeholder:text-muted-foreground/70",
  "outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/22",
  "disabled:cursor-not-allowed disabled:opacity-60",
  "aria-invalid:border-destructive/50 aria-invalid:ring-destructive/20",
  "dark:bg-white/[0.04]",
);

export const labelClassName =
  "block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5";

function Input({
  className,
  type,
  ...props
}: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        fieldClassName,
        type === "search" &&
          "[&::-webkit-search-cancel-button]:appearance-none [&::-webkit-search-decoration]:appearance-none",
        type === "file" &&
          "file:me-3 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
        className,
      )}
      {...props}
    />
  );
}

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(fieldClassName, "min-h-24 resize-y leading-relaxed", className)}
      {...props}
    />
  );
}

function Label({ className, ...props }: React.ComponentProps<"label">) {
  return (
    <label data-slot="label" className={cn(labelClassName, className)} {...props} />
  );
}

export { Input, Textarea, Label };
