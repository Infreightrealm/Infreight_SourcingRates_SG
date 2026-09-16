"use client";

import { cn } from "@/lib/utils";
import { HalftoneAvatar } from "@/components/ui/halftone-avatar";
import { ArrowUpRight, Camera, ChevronLeft, ChevronRight, User } from "lucide-react";
import {
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  useCallback,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
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
  isAdmin?: boolean;
  onActiveChange?: (item: OrbitStackItem, index: number) => void;
  onSelectMember?: (item: OrbitStackItem) => void;
  onUploadAvatar?: (item: OrbitStackItem) => void;
}

const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";

function subscribeReducedMotion(onChange: () => void) {
  if (typeof window === "undefined") return () => {};
  const mq = window.matchMedia(REDUCED_MOTION_QUERY);
  mq.addEventListener("change", onChange);
  return () => mq.removeEventListener("change", onChange);
}

function useReducedMotion() {
  return useSyncExternalStore(
    subscribeReducedMotion,
    () => window.matchMedia(REDUCED_MOTION_QUERY).matches,
    () => false,
  );
}

/** Tracks the stage width so the fan never spills outside its container. */
function useStageWidth<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [width, setWidth] = useState(0);

  useLayoutEffect(() => {
    const node = ref.current;
    if (!node) return;
    const update = () => setWidth(node.getBoundingClientRect().width);
    update();
    if (typeof ResizeObserver === "undefined") {
      window.addEventListener("resize", update);
      return () => window.removeEventListener("resize", update);
    }
    const observer = new ResizeObserver(update);
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return { ref, width };
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function initialsFor(item: OrbitStackItem) {
  return (
    item.initials ??
    item.name
      .split(/\s+/)
      .map((part) => part.at(0))
      .filter(Boolean)
      .join("")
      .slice(0, 2)
      .toUpperCase()
  );
}

function laneLabel(item: OrbitStackItem) {
  const lane = item.searchStats?.top_lanes?.[0];
  if (!lane) return null;
  const strip = (value: string) => value.split(",")[0]?.trim() || value;
  return `${strip(lane.origin)} → ${strip(lane.destination)}`;
}

export function OrbitCardStack({
  items,
  className,
  cardClassName,
  defaultActiveIndex = 0,
  isAdmin = false,
  onActiveChange,
  onSelectMember,
  onUploadAvatar,
}: OrbitCardStackProps) {
  const reduceMotion = useReducedMotion();
  const { ref: stageRef, width } = useStageWidth<HTMLDivElement>();
  const [rawIndex, setActiveIndex] = useState(defaultActiveIndex);
  const [seededFrom, setSeededFrom] = useState(defaultActiveIndex);
  const dragRef = useRef<{ x: number; handled: boolean } | null>(null);
  const wheelLockRef = useRef(0);

  const count = items.length;

  // Re-seed during render (not in an effect) when the caller moves the resting
  // card; the clamp below keeps the deck valid when the roster shrinks.
  if (seededFrom !== defaultActiveIndex) {
    setSeededFrom(defaultActiveIndex);
    setActiveIndex(defaultActiveIndex);
  }

  const activeIndex = clamp(rawIndex, 0, Math.max(0, count - 1));

  // Geometry is derived from the measured stage, so a 4-person team and a
  // 40-person team both fan out inside the same box without clipping.
  const metrics = useMemo(() => {
    const stage = width || 960;
    const cardWidth = clamp(stage * 0.54, 198, 268);
    // Cards keep a minimum height so the name block can never be squeezed away
    // on narrow screens.
    const cardHeight = Math.round(clamp(cardWidth * 1.52, 330, 400));
    const half = stage < 560 ? 1 : stage < 820 ? 2 : 3;
    // Leave a gutter so the outermost (rotated) card corners stay inside the stage.
    const maxSpread = Math.max(0, (stage - cardWidth) / 2 - 26);
    const spacing = clamp(cardWidth * 0.66, 56, Math.max(56, maxSpread / half));
    return { cardWidth, cardHeight, half, spacing };
  }, [width]);

  const goTo = useCallback(
    (index: number) => {
      if (count === 0) return;
      const next = clamp(index, 0, count - 1);
      setActiveIndex(next);
      const item = items[next];
      if (item) onActiveChange?.(item, next);
    },
    [count, items, onActiveChange],
  );

  const step = useCallback((delta: number) => goTo(activeIndex + delta), [activeIndex, goTo]);

  const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
    const delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;
    if (Math.abs(delta) < 4) return;
    const now = Date.now();
    if (now - wheelLockRef.current < 220) return;
    wheelLockRef.current = now;
    step(delta > 0 ? 1 : -1);
  };

  const handlePointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    dragRef.current = { x: event.clientX, handled: false };
  };

  const handlePointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.handled) return;
    const dx = event.clientX - drag.x;
    if (Math.abs(dx) > 48) {
      drag.handled = true;
      step(dx < 0 ? 1 : -1);
    }
  };

  const endDrag = () => {
    const wasHandled = dragRef.current?.handled ?? false;
    dragRef.current = null;
    return wasHandled;
  };

  if (count === 0) {
    return (
      <div className="flex h-64 w-full items-center justify-center px-6 text-center text-sm text-slate-400">
        No team members match this view yet.
      </div>
    );
  }

  const activeItem = items[activeIndex];



  return (
    <div className={cn("flex w-full flex-col items-center gap-4", className)}>
      <div
        ref={stageRef}
        className="relative w-full select-none overflow-hidden"
        style={{ height: metrics.cardHeight + 96 }}
        onWheel={handleWheel}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        onKeyDown={(event) => {
          if (event.key === "ArrowRight" || event.key === "ArrowDown") {
            event.preventDefault();
            step(1);
          } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
            event.preventDefault();
            step(-1);
          } else if (event.key === "Home") {
            event.preventDefault();
            goTo(0);
          } else if (event.key === "End") {
            event.preventDefault();
            goTo(count - 1);
          } else if ((event.key === "Enter" || event.key === " ") && activeItem && !activeItem.isSelf) {
            event.preventDefault();
            onSelectMember?.(activeItem);
          }
        }}
        tabIndex={0}
        role="listbox"
        aria-label="Team orbit card deck"
        aria-activedescendant={activeItem ? `orbit-card-${activeItem.id}` : undefined}
      >
        {items.map((item, index) => {
          const offset = index - activeIndex;
          const rank = index - activeIndex; // distance from the focused card
          const distance = Math.abs(rank);
          const visible = distance <= metrics.half;
          const active = rank === 0;
          const direction = Math.sign(rank) || 1;

          // Off-window cards park just outside the last visible slot and fade,
          // which keeps the DOM stable for very long rosters.
          const parked = distance > metrics.half;
          const slot = parked ? direction * (metrics.half + 0.6) : offset;
          const slotDistance = Math.abs(slot);

          const x = slot * metrics.spacing;
          const y = Math.pow(slotDistance, 1.25) * (metrics.cardHeight * 0.035) - (active ? 12 : 0);
          const rotation = slot * 6.5;
          const scale = clamp(1 - distance * 0.045, 0.7, 1);

          const style: CSSProperties = {
            width: metrics.cardWidth,
            height: metrics.cardHeight,
            zIndex: 100 - Math.round(slotDistance * 10),
            opacity: visible ? 1 : 0,
            pointerEvents: visible ? "auto" : "none",
            transform: `translate(-50%, -50%) translate(${x}px, ${y}px) rotate(${rotation}deg) scale(${scale})`,
            transitionDuration: reduceMotion ? "0ms" : "420ms",
          };

          const initials = initialsFor(item);
          const lane = laneLabel(item);
          const isSelf = !!item.isSelf;

          return (
            <article
              id={`orbit-card-${item.id}`}
              key={item.id}
              role="option"
              aria-selected={active}
              aria-hidden={!visible}
              aria-label={`${item.name}, @${item.username}`}
              className={cn(
                "absolute left-1/2 top-1/2 flex cursor-pointer flex-col overflow-hidden rounded-[1.4rem] border border-black/10 bg-[#f3f0e7] text-[#111111] shadow-[0_18px_50px_-18px_rgba(0,0,0,0.85)] outline-none",
                "transition-[transform,opacity,box-shadow] ease-[cubic-bezier(.2,.8,.2,1)]",
                active && "shadow-[0_28px_70px_-20px_rgba(0,0,0,0.95)] ring-1 ring-black/15",
                cardClassName,
              )}
              style={style}
              onClick={() => {
                if (endDrag()) return;
                if (!active) {
                  goTo(index);
                  return;
                }
                if (!isSelf) onSelectMember?.(item);
              }}
            >
              {/* Portrait */}
              <div className="relative min-h-0 shrink px-3 pt-3">
                <div
                  className="relative h-full w-full overflow-hidden rounded-[1.05rem] bg-[#e9e5d9]"
                  style={{ aspectRatio: "1.12" }}
                >
                  <HalftoneAvatar
                    seed={item.username || item.id}
                    image={item.image}
                    alt={item.name}
                    className="h-full w-full"
                  />
                  <span className="absolute bottom-2 right-2 rounded-full bg-[#111111] px-2 py-0.5 text-[10px] font-bold tracking-[0.14em] text-[#f3f0e7]">
                    {initials}
                  </span>
                </div>

                {/* Action bubble */}
                <div className="absolute right-5 top-5 z-20">
                  {isSelf ? (
                    <span
                      className="grid size-9 place-items-center rounded-full border border-black/10 bg-[#f3f0e7] text-[#111111]"
                      title="This is you"
                    >
                      <User className="size-4" />
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        if (!active) {
                          goTo(index);
                          return;
                        }
                        onSelectMember?.(item);
                      }}
                      tabIndex={visible ? 0 : -1}
                      className="relative grid size-9 place-items-center rounded-full bg-[#111111] text-[#f3f0e7] transition-transform hover:scale-105"
                      title={`Text @${item.username} privately`}
                    >
                      <ArrowUpRight className="size-4" />
                      {(item.unreadCount ?? 0) > 0 && (
                        <span className="absolute -right-1.5 -top-1.5 grid min-w-5 place-items-center rounded-full bg-rose-600 px-1 text-[10px] font-extrabold text-white">
                          {item.unreadCount}
                        </span>
                      )}
                    </button>
                  )}
                </div>

                {isAdmin && onUploadAvatar && active && (
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      onUploadAvatar(item);
                    }}
                    className="absolute left-5 top-5 z-20 inline-flex items-center gap-1 rounded-full border border-black/10 bg-[#f3f0e7]/95 px-2 py-1 text-[10px] font-semibold text-[#111111] transition-colors hover:bg-[#111111] hover:text-[#f3f0e7]"
                    title={`Upload profile picture for ${item.name}`}
                  >
                    <Camera className="size-3" />
                    <span>Edit Photo</span>
                  </button>
                )}
              </div>

              {/* Body */}
              <div className="flex min-h-0 flex-1 flex-col px-4 pb-3 pt-3">
                <div className="flex shrink-0 items-center justify-between gap-2">
                  <p className="truncate text-[9px] font-bold uppercase tracking-[0.18em] text-black/55">
                    {item.role === "admin" ? "Administrator" : "Rate Specialist"}
                  </p>
                  {isSelf && (
                    <span className="shrink-0 rounded bg-[#111111] px-1.5 py-0.5 text-[9px] font-extrabold uppercase tracking-[0.12em] text-[#f3f0e7]">
                      You
                    </span>
                  )}
                </div>

                <h3 className="mt-1 shrink-0 truncate text-[1.15rem] font-bold leading-tight tracking-tight">
                  {item.name}
                </h3>
                <p className="shrink-0 truncate text-[11px] font-medium text-black/50">@{item.username}</p>

                <div className="mt-2 flex shrink-0 items-baseline justify-between gap-2 border-t border-black/10 pt-2">
                  <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-black/55">
                    Quotes
                  </span>
                  <span className="text-base font-bold tabular-nums">
                    {item.searchStats?.total_searches ?? 0}
                  </span>
                </div>

                <p className="mt-1 shrink-0 truncate text-[10px] font-medium uppercase tracking-[0.1em] text-black/45">
                  {lane ?? "No lane history"}
                </p>

                <div className="mt-auto flex shrink-0 items-center justify-between gap-2 pt-2 text-[10px] font-bold uppercase tracking-[0.16em] text-black/45">
                  <span className="truncate">
                    {isSelf ? "Your card" : active ? "Click to text" : "Click to focus"}
                  </span>
                  <span className="shrink-0 tabular-nums">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
              </div>

              {/* Depth scrim — cards stay fully opaque so stacked neighbours
                  never bleed their text through the card in front. */}
              {!active && (
                <div
                  aria-hidden
                  className="pointer-events-none absolute inset-0 rounded-[1.4rem] bg-slate-950 transition-opacity duration-300"
                  style={{ opacity: clamp(distance * 0.16, 0, 0.55) }}
                />
              )}
            </article>
          );
        })}
      </div>

      {/* Deck navigation */}
      <div className="flex w-full items-center justify-center gap-4 px-4">
        <button
          type="button"
          onClick={() => step(-1)}
          disabled={activeIndex === 0}
          className="grid size-9 shrink-0 place-items-center rounded-full border border-white/15 bg-white/5 text-slate-200 transition-colors hover:bg-white/15 disabled:opacity-30"
          title="Previous colleague"
        >
          <ChevronLeft className="size-4" />
        </button>

        <div className="flex min-w-0 flex-1 max-w-sm flex-col items-center gap-1.5">
          <p className="truncate text-center text-xs font-semibold text-slate-200">
            {activeItem?.name}
            <span className="ml-1.5 font-mono text-[11px] font-normal text-slate-500">
              {activeIndex + 1} / {count}
            </span>
          </p>
          <div className="h-1 w-full overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-sky-400 transition-[width,margin] duration-300"
              style={{
                width: `${100 / count}%`,
                marginLeft: `${(activeIndex * 100) / count}%`,
              }}
            />
          </div>
        </div>

        <button
          type="button"
          onClick={() => step(1)}
          disabled={activeIndex >= count - 1}
          className="grid size-9 shrink-0 place-items-center rounded-full border border-white/15 bg-white/5 text-slate-200 transition-colors hover:bg-white/15 disabled:opacity-30"
          title="Next colleague"
        >
          <ChevronRight className="size-4" />
        </button>
      </div>
    </div>
  );
}
