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
    return <div className="size-8 animate-pulse rounded-lg border border-border bg-muted" />;
  }

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="btn-interactive relative flex size-8 items-center justify-center overflow-hidden rounded-lg border border-border bg-secondary text-muted-foreground hover:bg-accent hover:text-foreground"
      aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
      title={isDark ? "Switch to light theme" : "Switch to dark theme"}
    >
      {/* Both glyphs are mounted and slide past each other, so the swap reads
          as one motion rather than a pop. */}
      <Sun
        className={`absolute size-4 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
          isDark ? "translate-y-0 rotate-0 opacity-100" : "-translate-y-6 rotate-90 opacity-0"
        }`}
      />
      <Moon
        className={`absolute size-4 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
          isDark ? "translate-y-6 -rotate-90 opacity-0" : "translate-y-0 rotate-0 opacity-100"
        }`}
      />
    </button>
  );
}
