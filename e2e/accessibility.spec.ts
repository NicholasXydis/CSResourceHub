import AxeBuilder from "@axe-core/playwright";
import type { Page } from "@playwright/test";
import { expect, test } from "@playwright/test";

const WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];

async function settle(page: Page) {
  await page.waitForFunction(
    () => {
      const animated = [
        ...document.querySelectorAll<HTMLElement>(
          ".filter-row, .resource-card, .eyebrow, .stats div, .result-bar, .filters-title, .filter-label",
        ),
      ].filter((node) => {
        const box = node.getBoundingClientRect();
        return (
          box.width > 0 &&
          box.height > 0 &&
          box.bottom > 0 &&
          box.top < window.innerHeight
        );
      });
      if (!animated.length) return false;
      return animated.every(
        (node) => Number(window.getComputedStyle(node).opacity) > 0.99,
      );
    },
    undefined,
    { timeout: 20_000 },
  );
}

async function violations(page: Page) {
  const result = await new AxeBuilder({ page }).withTags(WCAG).analyze();
  return result.violations.map((violation) => ({
    id: violation.id,
    impact: violation.impact,
    nodes: violation.nodes.map((node) => node.target.join(" ")),
  }));
}

test("the directory has no accessibility violations", async ({ page }) => {
  await page.goto("/");
  await settle(page);
  expect(await violations(page)).toEqual([]);
});

test("the empty state has no accessibility violations", async ({ page }) => {
  await page.goto("/");
  await page
    .getByRole("textbox", { name: /search resources/i })
    .fill("zzz-nothing-matches-this");
  await settle(page);
  expect(await violations(page)).toEqual([]);
});

test("the 404 page has no accessibility violations", async ({ page }) => {
  await page.goto("/this-page-does-not-exist");
  await settle(page);
  expect(await violations(page)).toEqual([]);
});

test("the mobile filter drawer has no accessibility violations", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: /^Filters/ }).click();
  await settle(page);
  expect(await violations(page)).toEqual([]);
});

test("exposes exactly one top-level main landmark", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("main")).toHaveCount(1);
  await expect(page.locator("header")).toHaveCount(1);
  await expect(page.locator("footer")).toHaveCount(1);
});

test("reaches the directory from the skip link with the keyboard", async ({
  page,
  browserName,
}) => {
  test.skip(
    browserName === "webkit",
    "Safari only tabs to links when Full Keyboard Access is enabled",
  );
  await page.goto("/");

  await page.keyboard.press("Tab");
  const skipLink = page.locator(".skip-link");
  await expect(skipLink).toBeFocused();
  await expect(skipLink).toHaveAttribute("href", "#directory");

  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#directory$/);
  await expect(page.locator("#directory")).toBeVisible();
});

test("operates the filters with the keyboard alone", async ({
  page,
  isMobile,
}) => {
  await page.goto("/");

  if (isMobile) {
    const filters = page.getByRole("button", { name: /^Filters/ });
    await filters.focus();
    await expect(filters).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(
      page.getByRole("dialog", { name: /resource filters/i }),
    ).toBeVisible();
  }

  const collection = page.getByRole("button", { name: /^Experience/ });
  await collection.focus();
  await expect(collection).toBeFocused();

  await page.keyboard.press("Enter");
  await expect(collection).toHaveAttribute("aria-pressed", "true");
  if (isMobile) {
    await expect(
      page.getByRole("dialog", { name: /resource filters/i }),
    ).toBeVisible();
    await expect(page.getByRole("status")).toContainText("62 resources found");
  }
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
