import { expect, test } from "@playwright/test";

test("loads without console errors or failed page requests", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("/");
  await expect(page.locator(".resource-card").first()).toBeVisible();

  const ownAssetErrors = errors.filter(
    (message) => !/favicon|s2\/favicons|net::ERR/i.test(message),
  );
  expect(ownAssetErrors).toEqual([]);
});

test("opens and closes the mobile filter drawer", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await page.getByRole("button", { name: /^Filters/ }).click();
  const drawer = page.getByRole("dialog", { name: /resource filters/i });
  await expect(drawer).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(drawer).not.toBeVisible();
});
