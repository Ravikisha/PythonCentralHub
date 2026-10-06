import { defineConfig } from "vitest/config";

/** Firestore rules tests. Run through `npm run test:rules`, which starts the emulator. */
export default defineConfig({
  test: {
    include: ["tests/rules/**/*.test.ts"],
    environment: "node",
    testTimeout: 20_000,
    hookTimeout: 60_000,
    fileParallelism: false,
  },
});
