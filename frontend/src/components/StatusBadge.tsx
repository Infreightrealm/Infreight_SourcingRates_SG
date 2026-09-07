"use client";
import { STATUS_MAP } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Check, X } from "lucide-react";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export default function StatusBadge({ status, size = "sm" }: StatusBadgeProps) {
  const isRunning = status === "RUNNING" || status.startsWith("RUNNING");
  let info = STATUS_MAP[status];
  if (!info && status.startsWith("RUNNING")) {
    const rawDetail = status.substring(7).trim().replace(/[()]/g, "");
    let detail = rawDetail;
    if (rawDetail === "DRY 20") detail = "20GP";
    else if (rawDetail === "DRY 40") detail = "40GP";
    else if (rawDetail === "DRY 40H") detail = "40HQ";
    info = {
      label: detail ? `Searching ${detail}…` : "Searching…",
      color: "text-blue-400",
      bg: "bg-blue-400/10"
    };
  }
  if (!info) {
    info = { label: status, color: "text-gray-400", bg: "bg-gray-400/10" };
  }

  const isWaiting = status === "WAITING_FOR_HUMAN_VERIFICATION";
  const isQueued = status === "QUEUED";
  const showDot = isRunning || isQueued || isWaiting;

  return (
    <Badge
      size={size === "sm" ? "sm" : "default"}
      className={cn(
        "animate-scale-in border-transparent",
        // A live search gets the animated brand gradient; everything else keeps
        // the status colour from STATUS_MAP.
        isRunning
          ? "btn-gradient bg-gradient-to-r from-blue-500 via-violet-500 to-blue-500 text-white"
          : cn(info.bg, info.color),
      )}
    >
      {showDot && (
        <span className="relative flex size-2 shrink-0">
          <span
            className={cn(
              "absolute inline-flex size-full animate-ping rounded-full opacity-75",
              isRunning ? "bg-white" : isWaiting ? "bg-amber-400" : "bg-slate-400",
            )}
          />
          <span
            className={cn(
              "relative inline-flex size-2 rounded-full",
              isRunning ? "bg-white" : isWaiting ? "bg-amber-500" : "bg-slate-500",
            )}
          />
        </span>
      )}
      {status === "AVAILABLE_QUOTES_FOUND" && <Check className="size-3.5" />}
      {(status === "FAILED" || status === "LOGIN_FAILED" || status === "UNKNOWN_ERROR") && (
        <X className="size-3.5" />
      )}
      {info.label}
    </Badge>
  );
}
