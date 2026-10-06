import { defineConfig, devices } from "@playwright/test";

/**
 * End-to-end tests.
 *
 *   npm run test:e2e        guest flows, against a dev server it starts
 *                           (or E2E_BASE_URL if you already run one)
 *   npm run test:e2e:full   adds signup -> exam -> certificate, against the
 *                           Firebase Auth and Firestore emulators (needs Java)
 *
 * With E2E_EMULATORS=1 the dev server is started pointed at the emulators:
 * the browser through NEXT_PUBLIC_FIREBASE_EMULATORS, the route handlers
 * through the emulator host variables the Admin SDK reads.
 */
const emulators =
  process.env.E2E_EMULATORS === "1" || Boolean(process.env.FIREBASE_AUTH_EMULATOR_HOST);
const port = Number(process.env.E2E_PORT ?? 3100);
const baseURL = process.env.E2E_BASE_URL ?? `http://localhost:${port}`;

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 180_000,
  expect: { timeout: 30_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL,
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: `npx next dev -p ${port}`,
        url: baseURL,
        timeout: 300_000,
        reuseExistingServer: !process.env.CI,
        env: emulators
          ? {
              NEXT_PUBLIC_FIREBASE_EMULATORS: "1",
              NEXT_PUBLIC_FIREBASE_PROJECT_ID: "demo-pythoncentralhub",
              FIRESTORE_EMULATOR_HOST: "127.0.0.1:8080",
              FIREBASE_AUTH_EMULATOR_HOST: "127.0.0.1:9099",
              GCLOUD_PROJECT: "demo-pythoncentralhub",
            }
          : {},
      },
});
