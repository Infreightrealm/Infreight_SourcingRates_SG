"use client";

import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/surfaces";

export default function LoadingState({ message = "Searching carriers…" }: { message?: string }) {
  return (
    <div className="animate-fade-in-up space-y-4">
      <div className="mb-6 flex items-center gap-3">
        <div className="orbit-spinner" />
        <p className="animate-pulse text-sm font-medium text-muted-foreground">{message}</p>
      </div>

      <Card className="w-full overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              {[...Array(10)].map((_, i) => (
                <th key={i} className="px-4 py-3">
                  <Skeleton className="h-3.5 w-full max-w-[80px]" />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <tr key={i} className="border-b border-line last:border-0">
                {[...Array(10)].map((_, j) => (
                  <td key={j} className="px-4 py-4">
                    <Skeleton
                      className={`h-3.5 ${j === 0 ? "w-24" : j >= 6 ? "ml-auto w-16" : "w-20"}`}
                      style={{ animationDelay: `${(i * 10 + j) * 0.03}s` }}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
