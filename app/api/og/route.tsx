import { ImageResponse } from "next/og";
import { COURSES } from "@/lib/courses.data.mjs";
import { SITE_NAME } from "@/lib/site";

export const runtime = "edge";

/**
 * GET /api/og/?title=...&course=<slug>  -- a 1200x630 link-preview image.
 *
 * Made on request and cached by the CDN, rather than one file per page at
 * build time: there are 1,200 lessons, and the build is already near
 * Vercel's time limit. Lessons and course pages point their og:image here
 * (app/(docs)/[...slug]/page.tsx, app/(courses)/courses/[course]/page.tsx).
 *
 * Colours are the subject hues from components/courses/courses.css.
 */
const HUES: Record<string, string> = {
  programming: "#2f7fbf",
  "data-ai": "#7c4dff",
  mathematics: "#a86a0c",
  "computer-science": "#25895a",
  web: "#0e8284",
  engineering: "#b03a73",
};

/** The logo (components/brand/Wordmark.tsx), with fixed colours for the dark card. */
function HubMark() {
  const R = 11;
  const pts = [-90, -30, 30, 90, 150, 210].map((deg, i) => {
    const a = (deg * Math.PI) / 180;
    return { x: 16 + R * Math.cos(a), y: 16 + R * Math.sin(a), yellow: i % 2 === 1 };
  });
  return (
    <svg width="56" height="56" viewBox="0 0 32 32">
      <circle cx="16" cy="16" r={R} fill="none" stroke="#6ba9dd" strokeOpacity="0.4" strokeWidth="1.2" />
      {pts.map((p, i) => (
        <line key={`l${i}`} x1="16" y1="16" x2={p.x} y2={p.y} stroke="#6ba9dd" strokeWidth="2" strokeLinecap="round" />
      ))}
      {pts.map((p, i) => (
        <circle key={`c${i}`} cx={p.x} cy={p.y} r="2.7" fill={p.yellow ? "#ffd343" : "#6ba9dd"} stroke="#0d1117" strokeWidth="0.9" />
      ))}
      <circle cx="16" cy="16" r="5.2" fill="#6ba9dd" stroke="#0d1117" strokeWidth="1" />
      <circle cx="16" cy="16" r="2.1" fill="#ffd343" />
    </svg>
  );
}

export function GET(req: Request): Response {
  const params = new URL(req.url).searchParams;
  const title = (params.get("title") ?? SITE_NAME).slice(0, 120);
  const course = COURSES.find((c) => c.slug === params.get("course"));
  const hue = (course && HUES[course.subject]) ?? "#7c4dff";
  const size = title.length > 70 ? 56 : title.length > 40 ? 68 : 80;

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px 80px",
          background: "#0d1117",
          color: "#e6edf3",
          borderLeft: `24px solid ${hue}`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20, fontSize: 30, color: "#9aa5b1" }}>
          {course ? (
            <span
              style={{
                padding: "6px 16px",
                borderRadius: 10,
                background: hue,
                color: "#ffffff",
                fontWeight: 700,
              }}
            >
              {course.code}
            </span>
          ) : null}
          <span>{course ? course.title : "Free courses, code that runs in the page"}</span>
        </div>

        <div style={{ display: "flex", fontSize: size, fontWeight: 800, lineHeight: 1.1, letterSpacing: -1 }}>
          {title}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 18, fontSize: 36, fontWeight: 700 }}>
          <HubMark />
          <span style={{ color: "#6ba9dd" }}>Python</span>
          <span style={{ marginLeft: -8 }}>Central Hub</span>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
      headers: { "Cache-Control": "public, max-age=86400, s-maxage=31536000, immutable" },
    },
  );
}
