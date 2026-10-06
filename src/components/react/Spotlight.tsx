"use client";

import { cn } from "@/lib/utils";

/**
 * Aceternity-style Spotlight. An animated conic sweep of light rendered
 * behind the hero. Purely decorative — aria-hidden. Colors use the pch
 * brand tokens so it reads as "shell light", not a generic gradient.
 * Animation lives in landing.css (@keyframes pch-spotlight); disabled under
 * prefers-reduced-motion there.
 */
export default function Spotlight({ className }: { className?: string }) {
  return (
    <svg
      className={cn("pch-spotlight", className)}
      aria-hidden="true"
      viewBox="0 0 3787 2842"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g filter="url(#pch-spot-filter)">
        <ellipse
          cx="1924.71"
          cy="273.501"
          rx="1924.71"
          ry="273.501"
          transform="matrix(-0.822377 -0.568943 -0.568943 0.822377 3631.88 2291.09)"
          fill="currentColor"
          fillOpacity="0.22"
        />
      </g>
      <defs>
        <filter
          id="pch-spot-filter"
          x="0.860352"
          y="0.838989"
          width="3785.16"
          height="2840.26"
          filterUnits="userSpaceOnUse"
          colorInterpolationFilters="sRGB"
        >
          <feFlood floodOpacity="0" result="BackgroundImageFix" />
          <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
          <feGaussianBlur stdDeviation="151" result="effect1_foregroundBlur" />
        </filter>
      </defs>
    </svg>
  );
}
