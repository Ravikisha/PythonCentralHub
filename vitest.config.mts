import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

/**
 * Unit tests: plain logic only (grading, certificates, rate limiting, slugs,
 * the progress store). Firestore rules have their own suite (test:rules,
 * against the emulator) and the browser flow is Playwright (test:e2e).
 */
export default defineConfig({
  resolve: {
    alias: { "@": fileURLToPath(new URL("./", import.meta.url)) },
  },
  test: {
    include: ["lib/**/*.test.ts", "src/lib/**/*.test.ts", "components/**/*.test.ts"],
    environment: "node",
  },
});
