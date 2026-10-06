"use client";

import { useEffect, useState } from "react";

/**
 * A learner's picture: their provider photo when there is one, otherwise an
 * emoji on a coloured disc.
 *
 * The fallback is derived, not stored. The emoji and the colour are picked by
 * hashing the account's uid, so the same person gets the same face on every
 * device and every page, and nothing is uploaded, saved or synced for it --
 * an email-and-password account costs no storage for its avatar at all.
 *
 * Provider photos are loaded with `referrerPolicy="no-referrer"`: Google's
 * avatar host refuses many hotlinked requests that carry a Referer, which is
 * why Google sign-ins used to show an empty circle. If the photo still fails
 * (revoked, offline, rate-limited) the emoji takes its place instead of a
 * broken image.
 */

/** Friendly, unambiguous faces. Order is part of the mapping; append only. */
const FACES = [
  "🦊", "🐼", "🐨", "🐯", "🦁", "🐸", "🐙", "🦉",
  "🐧", "🐢", "🦄", "🐝", "🦋", "🐳", "🦔", "🐻",
  "🐰", "🦦", "🦥", "🐿️", "🦜", "🐬", "🦩", "🐞",
];

/** Background tints, in the site's own hues. Append only. */
const TINTS = [
  "#dbe9f6", "#e6dcff", "#fdefc4", "#d6f0e1",
  "#d3f0f0", "#f7dcea", "#e9ecef", "#ffe1cc",
];

/** FNV-1a: small, fast, and stable across browsers. */
function hash(text: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

export function faceFor(seed: string): { emoji: string; tint: string } {
  const h = hash(seed || "guest");
  return {
    emoji: FACES[h % FACES.length],
    tint: TINTS[Math.floor(h / FACES.length) % TINTS.length],
  };
}

export function Avatar({
  photo,
  seed,
  size = 32,
  className,
  label,
}: {
  /** Provider photo URL, or empty. */
  photo?: string | null;
  /** Stable per account: the uid. */
  seed: string;
  size?: number;
  className?: string;
  /** Accessible name; omit when the avatar sits next to the name already. */
  label?: string;
}) {
  const [failed, setFailed] = useState(false);

  // A new photo (another account, or one just linked) gets its own chance.
  useEffect(() => setFailed(false), [photo]);

  const { emoji, tint } = faceFor(seed);
  const a11y = label
    ? { role: "img" as const, "aria-label": label }
    : { "aria-hidden": true as const };

  return (
    <span
      className={["avatar", className].filter(Boolean).join(" ")}
      style={{ width: size, height: size, fontSize: size * 0.5, background: tint }}
      {...a11y}
    >
      {photo && !failed ? (
        // eslint-disable-next-line @next/next/no-img-element -- provider hosts
        // vary (Google, GitHub) and are not worth routing through next/image.
        <img
          src={photo}
          alt=""
          width={size}
          height={size}
          referrerPolicy="no-referrer"
          loading="lazy"
          decoding="async"
          onError={() => setFailed(true)}
        />
      ) : (
        <span className="avatar__face">{emoji}</span>
      )}
    </span>
  );
}

export default Avatar;
