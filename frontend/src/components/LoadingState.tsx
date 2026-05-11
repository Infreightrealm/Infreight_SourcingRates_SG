"use client";

export default function LoadingState({ message = "Searching carriers…" }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <div className="relative">
        <div className="w-12 h-12 rounded-full border-4 border-white/10 border-t-blue-500 animate-spin" />
        <div className="absolute inset-0 w-12 h-12 rounded-full border-4 border-transparent border-b-purple-500 animate-spin" style={{ animationDirection: "reverse", animationDuration: "1.5s" }} />
      </div>
      <p className="text-white/60 text-sm font-medium animate-pulse">{message}</p>
    </div>
  );
}
