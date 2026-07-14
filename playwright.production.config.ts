import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PRODUCTION_URL ?? "https://csresourcehub.pages.dev";

export default defineConfig({
  testDir: "./e2e-production",
  fullyParallel: true,
  forbidOnly: true,
  retries: 2,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  projects: [
    { name: "production-chromium", use: { ...devices["Desktop Chrome"] } },
  ],
});
