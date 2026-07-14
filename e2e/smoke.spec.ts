import { expect, test } from "@playwright/test";

test("loads without console errors or failed page requests", async ({
  page,
}) => {
  const errors: string[] = [];
  const thirdParty: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  const response = await page.goto("/");
  const origin = new URL(response!.url()).origin;

  page.on("request", (request) => {
    if (!request.url().startsWith(origin)) thirdParty.push(request.url());
  });

  await expect(page.locator(".resource-card").first()).toBeVisible();
  await page.locator(".resource-card img").last().scrollIntoViewIfNeeded();

  expect(errors).toEqual([]);
  expect(thirdParty, "the page must not request any third-party asset").toEqual(
    [],
  );
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
