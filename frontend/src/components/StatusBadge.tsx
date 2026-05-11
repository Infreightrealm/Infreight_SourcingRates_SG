"use client";
import { STATUS_MAP } from "@/lib/types";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export default function StatusBadge({ status, size = "sm" }: StatusBadgeProps) {
  const info = STATUS_MAP[status] || { label: status, color: "text-gray-400", bg: "bg-gray-400/10" };
  const sizeClass = size === "sm" ? "px-2.5 py-0.5 text-xs" : "px-3 py-1 text-sm";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${info.bg} ${info.color} ${sizeClass}`}
    >
      {(status === "RUNNING" || status === "QUEUED") && (
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status === "RUNNING" ? "bg-blue-400" : "bg-gray-400"}`} />
          <span className={`relative inline-flex rounded-full h-2 w-2 ${status === "RUNNING" ? "bg-blue-500" : "bg-gray-500"}`} />
        </span>
      )}
      {status === "AVAILABLE_QUOTES_FOUND" && (
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      )}
      {(status === "FAILED" || status === "LOGIN_FAILED" || status === "UNKNOWN_ERROR") && (
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      )}
      {info.label}
    </span>
  );
}
