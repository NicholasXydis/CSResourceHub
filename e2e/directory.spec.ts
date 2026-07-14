import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";

const siteJson = JSON.parse(
  readFileSync(
    fileURLToPath(new URL("../generated/site.json", import.meta.url)),
    "utf8",
  ),
) as {
  total: number;
  groups: Record<string, { total: number }>;
  categories: Record<string, unknown[]>;
};

const PAGE_SIZE = 18;
const CARD = ".resource-card";

async function openFiltersOnMobile(
  page: import("@playwright/test").Page,
  isMobile: boolean,
) {
  if (isMobile) await page.getByRole("button", { name: /^Filters/ }).click();
}

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("renders the first page of resources", async ({ page }) => {
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.locator(CARD)).toHaveCount(PAGE_SIZE);
  await expect(
    page.getByText(`${siteJson.total} resources found`),
  ).toBeVisible();
});

test("loads another page of resources", async ({ page }) => {
  await page.getByRole("button", { name: /show \d+ more/i }).click();
  await expect(page.locator(CARD)).toHaveCount(PAGE_SIZE * 2);
});

test("searches, then clears from the empty state", async ({ page }) => {
  const search = page.getByRole("textbox", { name: /search resources/i });

  await search.fill("zzz-nothing-matches-this");
  await expect(page.locator(CARD)).toHaveCount(0);
  await expect(
    page.getByRole("heading", { name: /no resources found/i }),
  ).toBeVisible();

  await page.getByRole("button", { name: /clear search and filters/i }).click();

  await expect(search).toHaveValue("");
  await expect(page.locator(CARD)).toHaveCount(PAGE_SIZE);
});

test("focuses search with the / shortcut", async ({ page }) => {
  const search = page.getByRole("textbox", { name: /search resources/i });
  await expect(search).not.toBeFocused();
  await page.keyboard.press("/");
  await expect(search).toBeFocused();
});

test("filters to a collection and narrows the results", async ({
  page,
  isMobile,
}) => {
  const experience = siteJson.groups["Experience"]!;

  await openFiltersOnMobile(page, isMobile);

  await page.getByRole("button", { name: /^Experience/ }).click();

  await expect(
    page.getByText(`${experience.total} resources found`),
  ).toBeVisible();
  await expect(page.locator(CARD).first()).toBeVisible();
});

test("sorts the results alphabetically", async ({ page, isMobile }) => {
  await openFiltersOnMobile(page, isMobile);
  await page
    .getByRole("combobox", { name: /sort resources/i })
    .selectOption("name");

  const names = await page.locator(`${CARD} h3`).allTextContents();
  expect(names).toEqual([...names].sort((a, b) => a.localeCompare(b)));
});

test("narrows to a single category", async ({ page, isMobile }) => {
  await openFiltersOnMobile(page, isMobile);
  await page.getByRole("button", { name: /^CTFs/ }).click();

  const count = siteJson.categories["ctfs"]!.length;
  await expect(page.getByText(`${count} resources found`)).toBeVisible();
  await expect(page.locator(CARD)).toHaveCount(Math.min(count, PAGE_SIZE));
});

test("opens a resource card link to the right domain", async ({ page }) => {
  const first = page.locator(CARD).first();
  const visit = first.getByRole("link", { name: /^Visit / });
  await expect(visit).toHaveAttribute("target", "_blank");
  await expect(visit).toHaveAttribute("href", /^https:/);
});
