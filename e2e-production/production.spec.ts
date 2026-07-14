import { expect, test } from "@playwright/test";

const expectedHeaders = {
  "content-security-policy": /default-src 'self'.*frame-ancestors 'none'/,
  "permissions-policy": /camera=\(\)/,
  "referrer-policy": /strict-origin-when-cross-origin/,
  "x-content-type-options": /nosniff/,
} as const;

test("serves the homepage, metadata, generated files, and security headers", async ({
  request,
}) => {
  const homepage = await request.get("/");
  expect(homepage.status()).toBe(200);
  for (const [name, expected] of Object.entries(expectedHeaders)) {
    expect(homepage.headers()[name], `${name} header`).toMatch(expected);
  }

  for (const path of [
    "/site.json",
    "/feed.xml",
    "/sitemap.xml",
    "/robots.txt",
    "/favicon.svg",
  ]) {
    const response = await request.get(path);
    expect(response.status(), path).toBe(200);
    expect((await response.body()).length, path).toBeGreaterThan(0);
  }
});

test("serves the application shell for an unknown route", async ({
  request,
}) => {
  const response = await request.get("/__production-smoke-not-found__");
  expect([200, 404]).toContain(response.status());
  expect(await response.text()).toContain('<div id="root"></div>');
});

test("loads assets and supports search and filtering without first-party failures", async ({
  page,
}) => {
  const failures: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`console: ${message.text()}`);
  });
  page.on("pageerror", (error) => failures.push(`page: ${error.message}`));
  page.on("requestfailed", (request) => {
    if (request.url().startsWith(page.url().split("/").slice(0, 3).join("/"))) {
      failures.push(
        `request: ${request.url()} (${request.failure()?.errorText})`,
      );
    }
  });

  await page.goto("/");
  await expect(page.locator(".resource-card").first()).toBeVisible();
  await expect(page.locator('script[src^="/assets/"]')).toHaveCount(1);

  const search = page.getByRole("textbox", { name: /search resources/i });
  await search.fill("python");
  await expect(page.locator(".resource-card").first()).toBeVisible();
  await expect(page.getByRole("status")).toHaveText(/\d+ resources found/);

  await search.fill("");
  const experience = page.getByRole("button", { name: /^Experience/ });
  await expect(experience).toHaveCSS("opacity", "1");
  await experience.click();
  await expect(experience).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".resource-card").first()).toBeVisible();

  expect(failures).toEqual([]);
});
