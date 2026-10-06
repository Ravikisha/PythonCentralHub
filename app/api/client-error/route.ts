import { report } from "@/lib/server/report";
import { allow, clientIp } from "@/lib/server/rate-limit";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/client-error/ -- errors from readers' browsers.
 *
 * Unauthenticated by necessity (most readers are signed out), so it is
 * bounded: small bodies only, and a per-address limit (lib/server/rate-limit).
 * It only ever writes a log line; nothing is stored.
 */
export async function POST(req: Request): Promise<Response> {
  if (!(await allow(`err:${clientIp(req)}`, 20, 60_000))) {
    return new Response(null, { status: 429 });
  }

  const text = await req.text();
  if (text.length > 8000) return new Response(null, { status: 413 });

  let body: Record<string, unknown>;
  try {
    body = JSON.parse(text) as Record<string, unknown>;
  } catch {
    return new Response(null, { status: 400 });
  }

  const str = (v: unknown) => (typeof v === "string" ? v : undefined);
  const message = str(body.message);
  if (!message) return new Response(null, { status: 400 });

  await report({
    source: "client",
    message,
    stack: str(body.stack),
    url: str(body.url),
    kind: str(body.kind),
    userAgent: req.headers.get("user-agent")?.slice(0, 200),
  });
  return new Response(null, { status: 204 });
}
