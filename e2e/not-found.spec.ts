import { expect, test } from "@playwright/test";

test("renders the styled 404 page on an unknown path", async ({ page }) => {
  await page.goto("/this/page/does/not/exist");

  await expect(page.getByText(/page not found/i)).toBeVisible();
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    /wrong turn/i,
  );
  await expect(page.locator(".resource-card")).toHaveCount(0);
});

test("keeps the site chrome and ambient design on the 404 page", async ({
  page,
}) => {
  await page.goto("/nope");

  await expect(
    page.getByRole("link", { name: /cs resource hub home/i }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: /back to top/i })).toBeVisible();
  await expect(page.locator(".ambient.one")).toBeVisible();
  await expect(page.locator(".noise")).toBeVisible();
});

test("returns to the directory from the 404 page", async ({ page }) => {
  await page.goto("/nope");

  await page.getByRole("link", { name: /back to the directory/i }).click();

  await expect(page.locator(".resource-card").first()).toBeVisible();
  await expect(page.getByText(/page not found/i)).toHaveCount(0);
});
