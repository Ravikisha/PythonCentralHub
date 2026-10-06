import { afterEach, describe, expect, it, vi } from "vitest";

/** The primary address the canonical links, sitemap and feed are built from. */
async function primary(env: Record<string, string | undefined>) {
  vi.resetModules();
  for (const [k, v] of Object.entries(env)) vi.stubEnv(k, v as string);
  return (await import("./site")).SITE_URL;
}

describe("SITE_URL", () => {
  afterEach(() => vi.unstubAllEnvs());

  it("uses NEXT_PUBLIC_SITE_URL when set, without a trailing slash", async () => {
    expect(
      await primary({
        NEXT_PUBLIC_SITE_URL: "https://pythoncentralhub.live/",
        VERCEL_PROJECT_PRODUCTION_URL: "python-central-hub.vercel.app",
      }),
    ).toBe("https://pythoncentralhub.live");
  });

  it("otherwise follows Vercel's production domain", async () => {
    expect(
      await primary({ NEXT_PUBLIC_SITE_URL: "", VERCEL_PROJECT_PRODUCTION_URL: "pythoncentralhub.live" }),
    ).toBe("https://pythoncentralhub.live");
  });

  it("falls back to the vercel.app address", async () => {
    expect(
      await primary({
        NEXT_PUBLIC_SITE_URL: "",
        VERCEL_PROJECT_PRODUCTION_URL: "",
        NEXT_PUBLIC_VERCEL_PROJECT_PRODUCTION_URL: "",
      }),
    ).toBe("https://python-central-hub.vercel.app");
  });
});
