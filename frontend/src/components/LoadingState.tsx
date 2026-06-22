"use client";

export default function LoadingState({ message = "Searching carriers…" }: { message?: string }) {
  return (
    <div className="space-y-4 animate-fade-in-up">
      <div className="flex items-center gap-3 mb-6">
        <div className="orbit-spinner" />
        <p className="text-slate-600 dark:text-white/60 text-sm font-medium animate-pulse">{message}</p>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.02] shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#1a1f2e]">
              {[...Array(10)].map((_, i) => (
                <th key={i} className="px-4 py-3"><div className="h-4 bg-slate-200 dark:bg-white/10 rounded animate-shimmer w-full max-w-[80px]" /></th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...Array(5)].map((_, i) => (
              <tr key={i} className="border-b border-slate-100 dark:border-white/5" style={{animationDelay: `${i * 0.1}s`}}>
                {[...Array(10)].map((_, j) => (
                  <td key={j} className="px-4 py-4">
                    <div className={`h-4 bg-slate-100 dark:bg-white/5 rounded animate-shimmer ${j === 0 ? "w-24" : j >= 6 ? "w-16 ml-auto" : "w-20"}`} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
