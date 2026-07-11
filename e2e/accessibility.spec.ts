import { expect, test } from "@playwright/test";

test("reaches the directory from the skip link with the keyboard", async ({
  page,
}) => {
  await page.goto("/");

  await page.keyboard.press("Tab");
  const skipLink = page.locator(".skip-link");
  await expect(skipLink).toBeFocused();
  await expect(skipLink).toHaveAttribute("href", "#directory");

  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#directory$/);
  await expect(page.locator("#directory")).toBeVisible();
});

test("operates the filters with the keyboard alone", async ({ page }) => {
  await page.goto("/");

  const collection = page.getByRole("button", { name: /^Experience/ });
  await collection.focus();
  await expect(collection).toBeFocused();

  await page.keyboard.press("Enter");
  await expect(collection).toHaveAttribute("aria-pressed", "true");
});

test("announces the result count to assistive technology", async ({ page }) => {
  await page.goto("/");

  const status = page.getByRole("status");
  await expect(status).toContainText(/resources found/);
  await expect(status).toHaveAttribute("aria-live", "polite");
});

test("still renders the directory with reduced motion requested", async ({
  browser,
}) => {
  const context = await browser.newContext({ reducedMotion: "reduce" });
  const page = await context.newPage();

  await page.goto("/");

  await expect(page.locator(".resource-card").first()).toBeVisible();
  await expect(page.locator(".resource-card")).toHaveCount(18);
  await page.getByRole("button", { name: /show \d+ more/i }).click();
  await expect(page.locator(".resource-card")).toHaveCount(36);

  await context.close();
});
