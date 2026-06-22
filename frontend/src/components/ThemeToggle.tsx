"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch by waiting until mounted
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="w-9 h-9 rounded-md bg-white/10 dark:bg-slate-800/50 animate-pulse"></div>;
  }

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="p-2 flex items-center justify-center rounded-md bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors text-slate-700 dark:text-slate-300 btn-interactive hover:shadow-[0_0_12px_rgba(99,102,241,0.3)]"
      aria-label="Toggle theme"
    >
      {isDark ? (
        <Sun key="sun" className="w-5 h-5 animate-icon-rotate-in" />
      ) : (
        <Moon key="moon" className="w-5 h-5 animate-icon-rotate-in" />
      )}
    </button>
  );
}
