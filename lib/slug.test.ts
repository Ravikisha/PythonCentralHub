import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { routeFor } from "./slug.mjs";

/**
 * The slug rule decides 1,100+ indexed URLs. These pin its behaviour on the
 * awkward cases; scripts/verify-routes.mjs checks every real file.
 */
describe("routeFor", () => {
  it.each([
    ["tutorials/Boolean.mdx", "/tutorials/boolean/"],
    ["Data Analytics/Phase-08-Statistics-for-Data-Analytics/Statistical Power (intuition).mdx",
      "/data-analytics/phase-08-statistics-for-data-analytics/statistical-power-intuition/"],
    ["Data Analytics/Phase-08-Statistics-for-Data-Analytics/Statistical Power (intuition).md",
      "/data-analytics/phase-08-statistics-for-data-analytics/statistical-power-intuition/"],
  ])("%s -> %s", (file, url) => {
    expect(routeFor(file)).toBe(url);
  });

  it("produces only URLs that are in the baseline for a sample of real lessons", () => {
    const baseline = new Set(
      readFileSync("migration/routes-baseline-en.txt", "utf8").split(/\r?\n/).filter(Boolean),
    );
    expect(baseline.size).toBeGreaterThan(1000);
    expect(baseline.has(routeFor("tutorials/Boolean.mdx"))).toBe(true);
  });
});
