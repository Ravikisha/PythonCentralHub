/**
 * Fixed-window rate limiting for the public route handlers.
 *
 * With UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN set (Vercel's
 * Upstash integration sets both), the count lives in Redis and the limit holds
 * across every function instance. Without them it falls back to a per-instance
 * map: still a brake on one noisy client, but each cold instance starts at
 * zero, so it is not a global guarantee. For hard limits in front of the whole
 * site, add Vercel Firewall rate-limit rules as well (docs/launch-checklist.md).
 *
 * Fails open: if Redis is unreachable the request is allowed. A limiter that
 * takes the site down with it is worse than one that briefly lets traffic by.
 */
const memory = new Map<string, { count: number; resetAt: number }>();

async function redisAllow(key: string, limit: number, windowMs: number): Promise<boolean> {
  const url = process.env.UPSTASH_REDIS_REST_URL!;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN!;
  const bucket = `rl:${key}:${Math.floor(Date.now() / windowMs)}`;
  const res = await fetch(`${url.replace(/\/$/, "")}/pipeline`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify([
      ["INCR", bucket],
      ["PEXPIRE", bucket, String(windowMs)],
    ]),
    signal: AbortSignal.timeout(1500),
  });
  if (!res.ok) return true;
  const [incr] = (await res.json()) as { result?: number }[];
  return (incr?.result ?? 0) <= limit;
}

function memoryAllow(key: string, limit: number, windowMs: number): boolean {
  const now = Date.now();
  const entry = memory.get(key);
  if (!entry || entry.resetAt <= now) {
    if (memory.size > 10_000) memory.clear();
    memory.set(key, { count: 1, resetAt: now + windowMs });
    return true;
  }
  entry.count += 1;
  return entry.count <= limit;
}

/** True if this request is within `limit` per `windowMs` for `key`. */
export async function allow(key: string, limit: number, windowMs: number): Promise<boolean> {
  if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
    try {
      return await redisAllow(key, limit, windowMs);
    } catch {
      return true;
    }
  }
  return memoryAllow(key, limit, windowMs);
}

/** The caller's address as Vercel reports it. */
export function clientIp(req: Request): string {
  return (
    req.headers.get("x-real-ip") ||
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    "unknown"
  );
}
