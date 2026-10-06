import { afterEach, describe, expect, it, vi } from "vitest";
import { allow, clientIp } from "./rate-limit";

describe("allow (in-memory fallback)", () => {
  afterEach(() => vi.useRealTimers());

  it("allows up to the limit, then refuses until the window resets", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(0);
    const key = `test-${Math.random()}`;
    for (let i = 0; i < 3; i++) expect(await allow(key, 3, 1_000)).toBe(true);
    expect(await allow(key, 3, 1_000)).toBe(false);
    vi.setSystemTime(1_001);
    expect(await allow(key, 3, 1_000)).toBe(true);
  });

  it("counts keys separately", async () => {
    const a = `a-${Math.random()}`;
    const b = `b-${Math.random()}`;
    expect(await allow(a, 1, 60_000)).toBe(true);
    expect(await allow(a, 1, 60_000)).toBe(false);
    expect(await allow(b, 1, 60_000)).toBe(true);
  });
});

describe("clientIp", () => {
  it("prefers x-real-ip, then the first forwarded address", () => {
    expect(clientIp(new Request("http://x", { headers: { "x-real-ip": "1.1.1.1" } }))).toBe("1.1.1.1");
    expect(
      clientIp(new Request("http://x", { headers: { "x-forwarded-for": "2.2.2.2, 10.0.0.1" } })),
    ).toBe("2.2.2.2");
    expect(clientIp(new Request("http://x"))).toBe("unknown");
  });
});
