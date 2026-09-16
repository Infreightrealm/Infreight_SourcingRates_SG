"use client";

import { cn } from "@/lib/utils";
import { MessageSquare, Camera, Sparkles, User, ArrowUpRight } from "lucide-react";
import {
  type CSSProperties,
  type FocusEvent,
  useMemo,
  useRef,
  useState,
  useEffect,
} from "react";

export interface OrbitStackItem {
  id: string;
  name: string;
  username: string;
  role: string;
  description?: string;
  accent?: string;
  initials?: string;
  stat?: string;
  image?: string;
  isSelf?: boolean;
  unreadCount?: number;
  searchStats?: {
    total_searches: number;
    top_lanes: Array<{ origin: string; destination: string; count: number }>;
    last_searched_at: string | null;
  };
}

interface OrbitCardStackProps {
  items: OrbitStackItem[];
  className?: string;
  cardClassName?: string;
  defaultActiveIndex?: number;
  spread?: number;
  lift?: number;
  isAdmin?: boolean;
  onActiveChange?: (item: OrbitStackItem, index: number) => void;
  onSelectMember?: (item: OrbitStackItem) => void;
  onUploadAvatar?: (item: OrbitStackItem) => void;
}

function useReducedMotion() {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setMatches(mq.matches);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);
  return matches;
}

function inRange(index: number, length: number) {
  return Math.min(Math.max(0, index), Math.max(0, length - 1));
}

function initialsFor(item: OrbitStackItem) {
  return (
    item.initials ??
    item.name
      .split(/\s+/)
      .map((part) => part.at(0))
      .join("")
      .slice(0, 2)
      .toUpperCase()
  );
}

function Portrait({
  item,
  isAdmin,
  onUploadAvatar,
}: {
  item: OrbitStackItem;
  isAdmin?: boolean;
  onUploadAvatar?: (item: OrbitStackItem) => void;
}) {
  const initials = initialsFor(item);
  const shared =
    "relative flex aspect-[1.38] w-full overflow-hidden rounded-[1.35rem] border border-white/10 bg-slate-950/40 shadow-inner";

  return (
    <div className="relative group/portrait">
      {item.image ? (
        <div className={shared}>
          <img
            src={item.image}
            alt={item.name}
            className="h-full w-full object-cover transition-transform duration-500 group-hover/portrait:scale-105"
          />
          <span className="absolute bottom-3 right-3 rounded-full bg-slate-950/85 backdrop-blur-md px-2.5 py-0.5 text-[11px] font-bold tracking-[0.16em] text-white border border-white/10 shadow">
            {initials}
          </span>
        </div>
      ) : (
        <div
          className={shared}
          style={{ "--portrait-accent": item.accent ?? "#0284c7" } as CSSProperties}
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_22%_20%,var(--portrait-accent),transparent_35%),radial-gradient(circle_at_85%_72%,rgba(56,189,248,0.25),transparent_40%)] opacity-70" />
          <div className="absolute inset-x-8 bottom-0 h-[68%] rounded-t-[999px] border border-white/15 bg-slate-900/80 backdrop-blur-sm" />
          <div className="absolute left-1/2 top-[24%] size-20 -translate-x-1/2 rounded-[45%_55%_48%_52%] border border-white/20 bg-slate-800/90 shadow-md flex items-center justify-center">
            <span className="text-xl font-bold tracking-wider text-white">
              {initials}
            </span>
          </div>
          <span className="absolute bottom-3 right-3 rounded-full bg-slate-950/85 backdrop-blur-md px-2.5 py-0.5 text-[11px] font-bold tracking-[0.16em] text-white border border-white/10 shadow">
            {initials}
          </span>
        </div>
      )}

      {/* Admin Photo Upload Trigger */}
      {isAdmin && onUploadAvatar && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onUploadAvatar(item);
          }}
          className="absolute top-2.5 left-2.5 z-20 flex items-center gap-1 rounded-full bg-slate-950/85 backdrop-blur-md border border-white/20 px-2.5 py-1 text-[10px] font-semibold text-sky-300 shadow hover:bg-sky-500 hover:text-white transition-all cursor-pointer"
          title={`Upload profile picture for ${item.name}`}
        >
          <Camera className="size-3" />
          <span>Edit Photo</span>
        </button>
      )}
    </div>
  );
}

export function OrbitCardStack({
  items,
  className,
  cardClassName,
  defaultActiveIndex = 0,
  spread = 155,
  lift = 32,
  isAdmin = false,
  onActiveChange,
  onSelectMember,
  onUploadAvatar,
}: OrbitCardStackProps) {
  const reduceMotion = useReducedMotion();
  const cards = items.length ? items : [];
  const restingIndex = inRange(defaultActiveIndex, cards.length || 1);
  const [activeIndex, setActiveIndex] = useState(restingIndex);
  const [open, setOpen] = useState(false);
  const stageRef = useRef<HTMLDivElement>(null);
  const midpoint = (cards.length - 1) / 2;

  // Sync resting index if items change
  useEffect(() => {
    setActiveIndex(restingIndex);
  }, [restingIndex]);

  const layouts = useMemo(
    () =>
      cards.map((_, index) => {
        const orbit = index - midpoint;
        const stack = index - restingIndex;
        return {
          open: {
            x: orbit * spread,
            y: Math.abs(orbit) * 26 + Math.max(0, Math.abs(orbit) - 1) * 8,
            rotation: orbit * 7.5,
          },
          closed: {
            x: stack * 12,
            y: Math.abs(stack) * 6,
            rotation: stack * 3.2,
          },
        };
      }),
    [cards, midpoint, restingIndex, spread],
  );

  if (cards.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-400">
        No active team members registered yet.
      </div>
    );
  }

  const activate = (index: number) => {
    const next = inRange(index, cards.length);
    setOpen(true);
    setActiveIndex(next);
    onActiveChange?.(cards[next]!, next);
  };

  const close = () => {
    setOpen(false);
    setActiveIndex(restingIndex);
  };

  const leaveFocus = (event: FocusEvent<HTMLDivElement>) => {
    if (!event.currentTarget.contains(event.relatedTarget)) close();
  };

  return (
    <div
      className={cn(
        "relative flex min-h-[500px] w-full items-center justify-center overflow-x-auto overflow-y-visible px-4 py-8 select-none",
        className,
      )}
    >
      <div
        ref={stageRef}
        className="relative h-[480px] w-full max-w-[1020px]"
        onMouseLeave={close}
        onBlur={leaveFocus}
        role="list"
        aria-label="Team Orbit Card Stack"
      >
        {cards.map((item, index) => {
          const position = open ? layouts[index]?.open : layouts[index]?.closed;
          const pos = position || { x: 0, y: 0, rotation: 0 };
          const active = index === activeIndex;
          const isSelf = !!item.isSelf;

          const style: CSSProperties = {
            zIndex: active ? 80 : 50 - Math.abs(index - activeIndex),
            transform: `translate(calc(-50% + ${pos.x}px), calc(-50% + ${
              pos.y - (open && active ? lift : 0)
            }px)) rotate(${pos.rotation}deg) scale(${open ? 0.985 : 0.96})`,
            transitionDuration: reduceMotion ? "0ms" : "400ms",
          };

          return (
            <article
              key={`${item.id}-${index}`}
              role="listitem"
              tabIndex={0}
              aria-current={active ? "true" : undefined}
              className={cn(
                "absolute left-1/2 top-1/2 w-[min(82vw,20.5rem)] origin-bottom cursor-pointer rounded-[1.8rem] border border-white/15 bg-slate-900/90 text-slate-100 p-4 shadow-2xl backdrop-blur-2xl outline-none",
                "transition-[transform,box-shadow,border-color] ease-[cubic-bezier(.2,.8,.2,1)] hover:border-sky-400/50 hover:shadow-sky-500/10 focus-visible:ring-2 focus-visible:ring-sky-400",
                isSelf && "ring-1 ring-amber-400/30",
                cardClassName,
              )}
              style={style}
              onMouseEnter={() => activate(index)}
              onFocus={() => activate(index)}
              onClick={() => {
                activate(index);
                if (!isSelf && onSelectMember) {
                  onSelectMember(item);
                }
              }}
              onKeyDown={(event) => {
                if (event.key === "ArrowRight" || event.key === "ArrowDown") {
                  event.preventDefault();
                  const next = (index + 1) % cards.length;
                  activate(next);
                  stageRef.current?.querySelectorAll<HTMLElement>("[role=listitem]")[next]?.focus();
                }
                if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
                  event.preventDefault();
                  const next = (index - 1 + cards.length) % cards.length;
                  activate(next);
                  stageRef.current?.querySelectorAll<HTMLElement>("[role=listitem]")[next]?.focus();
                }
                if (event.key === "Enter" || event.key === " ") {
                  if (!isSelf && onSelectMember) {
                    onSelectMember(item);
                  }
                }
                if (event.key === "Escape") {
                  event.currentTarget.blur();
                  close();
                }
              }}
            >
              <div className="relative">
                <Portrait item={item} isAdmin={isAdmin} onUploadAvatar={onUploadAvatar} />

                {/* Top Right Chat Action Icon */}
                <div className="absolute right-2.5 top-2.5 z-20">
                  {isSelf ? (
                    <span className="grid size-9 place-items-center rounded-full bg-slate-950/80 backdrop-blur-md border border-amber-400/30 text-amber-300 shadow">
                      <User className="size-4" />
                    </span>
                  ) : (
                    <span className="relative grid size-9 place-items-center rounded-full bg-sky-500 text-white shadow-lg shadow-sky-500/30 hover:bg-sky-400 transition-colors">
                      <MessageSquare className="size-4" />
                      {(item.unreadCount ?? 0) > 0 && (
                        <span className="absolute -top-1 -right-1 flex size-5 items-center justify-center rounded-full bg-rose-500 text-[10px] font-extrabold text-white animate-pulse">
                          {item.unreadCount}
                        </span>
                      )}
                    </span>
                  )}
                </div>
              </div>

              {/* Card Body */}
              <div className="px-1 pt-4 pb-2">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-[10px] font-mono font-bold uppercase tracking-wider text-sky-400">
                    {item.role === "admin" ? "Administrator" : "Rate Specialist"}
                  </p>
                  {isSelf && (
                    <span className="px-2 py-0.5 rounded text-[9px] font-extrabold tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      You
                    </span>
                  )}
                </div>

                <h3 className="mt-1 text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
                  <span>{item.name}</span>
                  <span className="text-xs font-mono font-normal text-slate-400">
                    @{item.username}
                  </span>
                </h3>

                {/* Colleague Search Stats */}
                <div className="mt-3.5 space-y-1.5 rounded-xl border border-white/10 bg-slate-950/50 p-2.5 text-xs text-slate-300">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] text-slate-400 font-medium">Quotes Sourced:</span>
                    <span className="font-mono font-bold text-sky-300 text-sm">
                      {item.searchStats?.total_searches ?? 0}
                    </span>
                  </div>

                  {item.searchStats?.top_lanes && item.searchStats.top_lanes.length > 0 ? (
                    <div className="flex items-center justify-between pt-1 border-t border-white/5 text-[11px]">
                      <span className="text-slate-400 truncate max-w-[90px]">Top Lane:</span>
                      <span className="font-mono text-emerald-400 font-semibold truncate max-w-[160px]">
                        {item.searchStats.top_lanes[0]?.origin} → {item.searchStats.top_lanes[0]?.destination}
                      </span>
                    </div>
                  ) : (
                    <div className="text-[10px] text-slate-500 italic pt-1 border-t border-white/5">
                      No active lane history
                    </div>
                  )}
                </div>

                {/* Card Action Footer */}
                <div className="mt-3.5 flex items-center justify-between pt-2 text-[11px]">
                  {isSelf ? (
                    <span className="text-[11px] text-slate-500 italic font-mono">
                      (Your personal card)
                    </span>
                  ) : (
                    <button
                      type="button"
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-sky-400 hover:text-sky-300 group/btn"
                    >
                      <span>Click to text privately</span>
                      <ArrowUpRight className="size-3.5 transition-transform group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5" />
                    </button>
                  )}
                  <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                    {item.role}
                  </span>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
