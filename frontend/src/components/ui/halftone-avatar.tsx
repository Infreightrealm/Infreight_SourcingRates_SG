"use client";

import { useId, useMemo } from "react";

/**
 * HalftoneAvatar
 * ---------------------------------------------------------------------------
 * Deterministic, monochrome "inked portrait" avatar in the editorial / risograph
 * art style used by the Orbit card deck: black linework on cream paper with a
 * halftone dot texture. Every visual trait is derived from a stable hash of the
 * seed (username), so a given colleague always renders the same face.
 */

export interface HalftoneAvatarProps {
  seed: string;
  /** Optional real photo. Rendered with the same monochrome ink treatment. */
  image?: string;
  alt?: string;
  className?: string;
}

function hashSeed(seed: string): number {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i += 1) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h);
}

/** Pull a stable pseudo-random integer in [0, max) out of the hash at `slot`. */
function pick(hash: number, slot: number, max: number): number {
  return Math.floor((hash / Math.pow(7, slot)) % 1000) % max;
}

const INK = "#111111";
const PAPER = "#f3f0e7";

export function HalftoneAvatar({ seed, image, alt, className }: HalftoneAvatarProps) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, "");
  const traits = useMemo(() => {
    const h = hashSeed(seed || "anon");
    return {
      hair: pick(h, 1, 6),
      eyes: pick(h, 2, 4),
      mouth: pick(h, 3, 4),
      glasses: pick(h, 4, 3) === 0,
      backdrop: pick(h, 5, 3),
      tiltDeg: (pick(h, 6, 5) - 2) * 1.6,
      freckles: pick(h, 7, 2) === 0,
    };
  }, [seed]);

  const dots = `dots-${uid}`;
  const dotsDense = `dotsd-${uid}`;
  const photoClip = `photo-${uid}`;
  const inkFilter = `ink-${uid}`;

  // ---- Photo mode: same paper + ink palette, so real photos sit alongside
  // generated portraits without breaking the deck's visual language.
  if (image) {
    return (
      <svg
        viewBox="0 0 200 200"
        className={className}
        role="img"
        aria-label={alt || `${seed} portrait`}
      >
        <defs>
          <clipPath id={photoClip}>
            <rect x="0" y="0" width="200" height="200" rx="14" />
          </clipPath>
          <filter id={inkFilter}>
            <feColorMatrix
              type="matrix"
              values="0.33 0.5 0.16 0 0
                      0.33 0.5 0.16 0 0
                      0.33 0.5 0.16 0 0
                      0    0   0    1 0"
            />
            <feComponentTransfer>
              <feFuncR type="gamma" exponent="1.45" amplitude="1.15" offset="-0.05" />
              <feFuncG type="gamma" exponent="1.45" amplitude="1.15" offset="-0.05" />
              <feFuncB type="gamma" exponent="1.45" amplitude="1.15" offset="-0.05" />
            </feComponentTransfer>
          </filter>
          <pattern id={dots} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(28)">
            <circle cx="3" cy="3" r="1.05" fill={INK} />
          </pattern>
        </defs>
        <g clipPath={`url(#${photoClip})`}>
          <rect width="200" height="200" fill={PAPER} />
          <image
            href={image}
            x="0"
            y="0"
            width="200"
            height="200"
            preserveAspectRatio="xMidYMid slice"
            filter={`url(#${inkFilter})`}
          />
          <rect width="200" height="200" fill={`url(#${dots})`} opacity="0.12" />
        </g>
      </svg>
    );
  }

  return (
    <svg
      viewBox="0 0 200 200"
      className={className}
      role="img"
      aria-label={alt || `${seed} portrait`}
    >
      <defs>
        <pattern id={dots} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(28)">
          <circle cx="3" cy="3" r="1.15" fill={INK} />
        </pattern>
        <pattern id={dotsDense} width="4.4" height="4.4" patternUnits="userSpaceOnUse" patternTransform="rotate(28)">
          <circle cx="2.2" cy="2.2" r="1.25" fill={INK} />
        </pattern>
        <clipPath id={photoClip}>
          <rect x="0" y="0" width="200" height="200" rx="14" />
        </clipPath>
      </defs>

      <g clipPath={`url(#${photoClip})`}>
        <rect width="200" height="200" fill={PAPER} />

        {/* Backdrop motif */}
        {traits.backdrop === 1 && (
          <circle cx="100" cy="98" r="72" fill={`url(#${dots})`} opacity="0.35" />
        )}
        {traits.backdrop === 2 && (
          <path
            d="M100 14 L112 46 L146 34 L136 66 L172 72 L144 94 L172 118 L136 124 L146 156 L112 144 L100 178 L88 144 L54 156 L64 124 L28 118 L56 94 L28 72 L64 66 L54 34 L88 46 Z"
            fill="none"
            stroke={INK}
            strokeWidth="3"
            opacity="0.5"
          />
        )}

        <g transform={`rotate(${traits.tiltDeg} 100 104)`}>
          {/* Neck + shoulders */}
          <path d="M84 148 h32 v16 c16 4 26 14 30 36 H54 c4-22 14-32 30-36 Z" fill={PAPER} stroke={INK} strokeWidth="4" strokeLinejoin="round" />

          {/* Head */}
          <path
            d="M100 44 c28 0 44 20 44 48 0 30-18 54-44 54 s-44-24-44-54 c0-28 16-48 44-48 Z"
            fill={PAPER}
            stroke={INK}
            strokeWidth="4.5"
            strokeLinejoin="round"
          />

          {/* Ears */}
          <circle cx="56" cy="100" r="7" fill={PAPER} stroke={INK} strokeWidth="4" />
          <circle cx="144" cy="100" r="7" fill={PAPER} stroke={INK} strokeWidth="4" />

          {/* Hair */}
          {traits.hair === 0 && (
            <path
              d="M54 92 c0-34 20-52 46-52 s46 18 46 52 c-8-14-18-20-30-22 -14-2-24 6-34 6 -12 0-20 4-28 16 Z"
              fill={`url(#${dotsDense})`}
              stroke={INK}
              strokeWidth="4"
              strokeLinejoin="round"
            />
          )}
          {traits.hair === 1 && (
            <g fill={INK} stroke={INK} strokeWidth="3">
              <circle cx="70" cy="60" r="20" />
              <circle cx="100" cy="46" r="23" />
              <circle cx="132" cy="60" r="20" />
              <circle cx="56" cy="82" r="14" />
              <circle cx="146" cy="82" r="14" />
            </g>
          )}
          {traits.hair === 2 && (
            <path
              d="M54 94 L62 54 L76 76 L86 40 L100 72 L114 40 L124 76 L138 54 L146 94 c-10-22-28-30-46-30 s-36 8-46 30 Z"
              fill={INK}
              stroke={INK}
              strokeWidth="3"
              strokeLinejoin="round"
            />
          )}
          {traits.hair === 3 && (
            <g>
              <circle cx="100" cy="34" r="16" fill={`url(#${dotsDense})`} stroke={INK} strokeWidth="4" />
              <path
                d="M56 90 c2-32 20-50 44-50 s42 18 44 50 c-10-20-26-28-44-28 s-34 8-44 28 Z"
                fill={`url(#${dotsDense})`}
                stroke={INK}
                strokeWidth="4"
                strokeLinejoin="round"
              />
            </g>
          )}
          {traits.hair === 4 && (
            <g>
              <path
                d="M58 72 c4-26 20-40 42-40 s38 14 42 40 Z"
                fill={INK}
                stroke={INK}
                strokeWidth="4"
                strokeLinejoin="round"
              />
              <rect x="44" y="68" width="112" height="12" rx="6" fill={INK} stroke={INK} strokeWidth="3" />
            </g>
          )}
          {traits.hair === 5 && (
            <path
              d="M54 150 c-6-44-4-76 12-92 10-10 22-16 34-16 s24 6 34 16 c16 16 18 48 12 92 -6-20-8-48-12-64 -10 10-20 14-34 14 s-24-4-34-14 c-4 16-6 44-12 64 Z"
              fill={`url(#${dots})`}
              stroke={INK}
              strokeWidth="4"
              strokeLinejoin="round"
            />
          )}

          {/* Eyes */}
          {traits.eyes === 0 && (
            <g>
              <circle cx="82" cy="104" r="11" fill={PAPER} stroke={INK} strokeWidth="4" />
              <circle cx="118" cy="104" r="11" fill={PAPER} stroke={INK} strokeWidth="4" />
              <circle cx="84" cy="106" r="4.5" fill={INK} />
              <circle cx="120" cy="106" r="4.5" fill={INK} />
            </g>
          )}
          {traits.eyes === 1 && (
            <g fill="none" stroke={INK} strokeWidth="4.5" strokeLinecap="round">
              <path d="M72 106 q10-12 20 0" />
              <path d="M108 106 q10-12 20 0" />
            </g>
          )}
          {traits.eyes === 2 && (
            <g>
              <ellipse cx="82" cy="104" rx="12" ry="9" fill={PAPER} stroke={INK} strokeWidth="4" />
              <ellipse cx="118" cy="104" rx="12" ry="9" fill={PAPER} stroke={INK} strokeWidth="4" />
              <circle cx="82" cy="104" r="5" fill={INK} />
              <circle cx="118" cy="104" r="5" fill={INK} />
              <path d="M70 94 q12-8 24-2 M106 92 q12-6 24 2" fill="none" stroke={INK} strokeWidth="4" strokeLinecap="round" />
            </g>
          )}
          {traits.eyes === 3 && (
            <g fill={INK}>
              <circle cx="82" cy="104" r="5.5" />
              <circle cx="118" cy="104" r="5.5" />
            </g>
          )}

          {/* Glasses */}
          {traits.glasses && (
            <g fill="none" stroke={INK} strokeWidth="4">
              <circle cx="82" cy="104" r="16" />
              <circle cx="118" cy="104" r="16" />
              <path d="M98 104 h4" strokeLinecap="round" />
              <path d="M66 100 l-10-3 M134 100 l10-3" strokeLinecap="round" />
            </g>
          )}

          {/* Nose */}
          <path d="M100 112 v10 q0 4 5 4" fill="none" stroke={INK} strokeWidth="3.5" strokeLinecap="round" />

          {/* Mouth */}
          {traits.mouth === 0 && <circle cx="100" cy="134" r="6" fill={INK} />}
          {traits.mouth === 1 && (
            <path d="M88 134 h24" stroke={INK} strokeWidth="4.5" strokeLinecap="round" fill="none" />
          )}
          {traits.mouth === 2 && (
            <path d="M86 130 q14 14 28 0" stroke={INK} strokeWidth="4.5" strokeLinecap="round" fill="none" />
          )}
          {traits.mouth === 3 && (
            <path d="M84 130 q16 18 32 0 Z" fill={INK} stroke={INK} strokeWidth="4" strokeLinejoin="round" />
          )}

          {/* Cheek halftone */}
          {traits.freckles && (
            <g opacity="0.55" fill={`url(#${dots})`}>
              <ellipse cx="70" cy="122" rx="10" ry="7" />
              <ellipse cx="130" cy="122" rx="10" ry="7" />
            </g>
          )}
        </g>
      </g>
    </svg>
  );
}

export default HalftoneAvatar;
