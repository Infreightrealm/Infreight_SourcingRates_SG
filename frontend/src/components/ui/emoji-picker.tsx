"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Smile } from "lucide-react";
import { cn } from "@/lib/utils";

// A compact, dependency-free emoji picker. Curated rather than exhaustive —
// covers the reactions/expressions people actually reach for in a work chat,
// plus a freight-flavoured "Shipping" row since this is a logistics tool.
const EMOJI_GROUPS: Array<{ label: string; emojis: string[] }> = [
  {
    label: "Smileys",
    emojis: ["😀", "😂", "🙂", "😉", "😅", "😍", "🤔", "😮", "😢", "😭", "😡", "🥳", "😴", "🤝", "🙏", "👏"],
  },
  {
    label: "Reactions",
    emojis: ["👍", "👎", "✅", "❌", "🔥", "🚀", "⭐", "💯", "⚡", "❤️", "🎉", "👀", "💡", "⏰", "📌", "🙌"],
  },
  {
    label: "Shipping",
    emojis: ["📦", "🚢", "🚚", "✈️", "⚓", "🌊", "🗺️", "📋", "💰", "📝", "📎", "🏷️"],
  },
];

const RECENTS_KEY = "orbit_recent_emojis_v1";
const MAX_RECENTS = 8;

function loadRecents(): string[] {
  try {
    const raw = window.localStorage.getItem(RECENTS_KEY);
    return raw ? (JSON.parse(raw) as string[]).slice(0, MAX_RECENTS) : [];
  } catch {
    return [];
  }
}

function saveRecent(emoji: string) {
  try {
    const next = [emoji, ...loadRecents().filter((e) => e !== emoji)].slice(0, MAX_RECENTS);
    window.localStorage.setItem(RECENTS_KEY, JSON.stringify(next));
  } catch {
    // localStorage unavailable (private mode, etc.) — non-fatal.
  }
}

interface EmojiPickerProps {
  onSelect: (emoji: string) => void;
  className?: string;
}

export function EmojiPicker({ onSelect, className }: EmojiPickerProps) {
  const [open, setOpen] = useState(false);
  const [recents, setRecents] = useState<string[]>([]);
  const rootRef = useRef<HTMLDivElement>(null);

  const openPicker = () => {
    setRecents(loadRecents());
    setOpen(true);
  };

  useEffect(() => {
    if (!open) return;
    const onClickAway = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    const onEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClickAway);
    document.addEventListener("keydown", onEscape);
    return () => {
      document.removeEventListener("mousedown", onClickAway);
      document.removeEventListener("keydown", onEscape);
    };
  }, [open]);

  const groups = useMemo(() => {
    if (recents.length === 0) return EMOJI_GROUPS;
    return [{ label: "Recent", emojis: recents }, ...EMOJI_GROUPS];
  }, [recents]);

  const pick = (emoji: string) => {
    saveRecent(emoji);
    onSelect(emoji);
    setOpen(false);
  };

  return (
    <div ref={rootRef} className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => (open ? setOpen(false) : openPicker())}
        className="flex size-8 shrink-0 items-center justify-center rounded-xl text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
        title="Add an emoji"
        aria-label="Add an emoji"
        aria-expanded={open}
      >
        <Smile className="size-4.5" />
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Emoji picker"
          className="absolute bottom-full right-0 z-50 mb-2 max-h-72 w-64 overflow-y-auto rounded-2xl border border-white/15 bg-slate-900/98 p-3 shadow-2xl backdrop-blur-2xl"
        >
          {groups.map((group) => (
            <div key={group.label} className="mb-2.5 last:mb-0">
              <p className="mb-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                {group.label}
              </p>
              <div className="grid grid-cols-8 gap-0.5">
                {group.emojis.map((emoji, i) => (
                  <button
                    key={`${group.label}-${emoji}-${i}`}
                    type="button"
                    onClick={() => pick(emoji)}
                    className="flex size-7 items-center justify-center rounded-lg text-lg leading-none hover:bg-white/10 transition-colors cursor-pointer"
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default EmojiPicker;
