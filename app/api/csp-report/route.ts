import { report } from "@/lib/server/report";
import { allow, clientIp } from "@/lib/server/rate-limit";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/csp-report/ -- Content-Security-Policy violation reports.
 *
 * The policy runs Report-Only (next.config.ts), so these say what *would*
 * have been blocked. Each one goes to the error log tagged `csp`, which is how
 * the policy gets tightened before it is enforced. Browsers send these
 * unprompted and in bursts, so they are rate limited and always answered 204.
 */
export async function POST(req: Request): Promise<Response> {
  if (!(await allow(`csp:${clientIp(req)}`, 30, 60_000))) {
    return new Response(null, { status: 204 });
  }
  try {
    const text = (await req.text()).slice(0, 8000);
    const body = JSON.parse(text) as { "csp-report"?: Record<string, unknown> };
    const r = body["csp-report"] ?? (body as Record<string, unknown>);
    const blocked = String(r["blocked-uri"] ?? r.blockedURL ?? "");
    const directive = String(r["violated-directive"] ?? r.effectiveDirective ?? "");
    // Browser extensions inject scripts into every page; their reports are noise.
    if (/^(chrome|moz|safari)-extension:/.test(blocked)) {
      return new Response(null, { status: 204 });
    }
    await report({
      source: "client",
      kind: "csp",
      message: `CSP ${directive} blocked ${blocked || "(inline)"}`,
      url: String(r["document-uri"] ?? r.documentURL ?? ""),
    });
  } catch {
    /* malformed reports are dropped */
  }
  return new Response(null, { status: 204 });
}
