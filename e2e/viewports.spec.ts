import { expect, test } from "@playwright/test";

const SIZES = [
  { name: "small phone", width: 320, height: 568 },
  { name: "android", width: 360, height: 640 },
  { name: "iphone 8", width: 375, height: 667 },
  { name: "iphone 14", width: 390, height: 844 },
  { name: "pixel", width: 412, height: 915 },
  { name: "phone landscape", width: 844, height: 390 },
  { name: "ipad portrait", width: 768, height: 1024 },
  { name: "ipad air portrait", width: 820, height: 1180 },
  { name: "ipad landscape", width: 1024, height: 768 },
  { name: "small laptop", width: 1280, height: 800 },
  { name: "windows laptop", width: 1366, height: 768 },
  { name: "macbook air", width: 1440, height: 900 },
  { name: "windows scaled", width: 1536, height: 864 },
  { name: "full hd", width: 1920, height: 1080 },
  { name: "1440p", width: 2560, height: 1440 },
  { name: "below sm breakpoint", width: 639, height: 900 },
  { name: "at sm breakpoint", width: 640, height: 900 },
  { name: "below md breakpoint", width: 759, height: 900 },
  { name: "at md breakpoint", width: 760, height: 900 },
  { name: "above md breakpoint", width: 761, height: 900 },
  { name: "below lg breakpoint", width: 1099, height: 900 },
  { name: "at lg breakpoint", width: 1100, height: 900 },
];

test.describe("layout holds at every viewport", () => {
  for (const size of SIZES) {
    test(`${size.name} (${size.width}x${size.height})`, async ({ page }) => {
      await page.setViewportSize({ width: size.width, height: size.height });
      await page.goto("/");
      await expect(page.locator(".resource-card").first()).toBeVisible();

      const overflow = await page.evaluate(() => {
        const viewport = document.documentElement.clientWidth;
        const offenders: string[] = [];
        document.querySelectorAll<HTMLElement>("body *").forEach((node) => {
          if (node.classList.contains("ambient")) return;
          const box = node.getBoundingClientRect();
          if (box.width > 0 && box.right > viewport + 1) {
            offenders.push(
              `${node.tagName}.${node.className} right=${Math.round(box.right)} vw=${viewport}`,
            );
          }
        });
        return {
          offenders: offenders.slice(0, 5),
          scrollWidth: document.documentElement.scrollWidth,
          viewport,
        };
      });

      expect(overflow.offenders, "elements overflowing the viewport").toEqual(
        [],
      );
      expect(
        overflow.scrollWidth,
        "page must not scroll horizontally",
      ).toBeLessThanOrEqual(overflow.viewport);

      await expect(page.getByRole("link", { name: /github/i })).toBeVisible();
      await expect(
        page.getByRole("textbox", { name: /search resources/i }),
      ).toBeVisible();
    });
  }
});
