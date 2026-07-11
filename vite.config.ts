import { copyFileSync, existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Plugin } from "vite";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

const SITE_JSON = fileURLToPath(
  new URL("./generated/site.json", import.meta.url),
);

interface SiteMetadata {
  total: number;
  labels: Record<string, string>;
}

function siteMetadata(): Plugin {
  return {
    name: "site-metadata",
    transformIndexHtml: {
      order: "pre",
      handler(html: string) {
        const { total, labels } = JSON.parse(
          readFileSync(SITE_JSON, "utf8"),
        ) as Partial<SiteMetadata>;
        if (!labels || typeof total !== "number") {
          throw new Error(
            "generated/site.json is missing labels/total. Run: py scripts/generate_site_json.py",
          );
        }
        return html
          .replaceAll("%RESOURCE_TOTAL%", String(total))
          .replaceAll("%CATEGORY_TOTAL%", String(Object.keys(labels).length));
      },
    },
  };
}

function notFoundPage(): Plugin {
  let outDir = "dist";
  return {
    name: "not-found-page",
    apply: "build",
    configResolved(config) {
      outDir = config.build.outDir;
    },
    closeBundle() {
      const index = resolve(outDir, "index.html");
      if (existsSync(index)) {
        copyFileSync(index, resolve(outDir, "404.html"));
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), siteMetadata(), notFoundPage()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    css: true,
    globals: true,

    include: ["src/**/*.{test,spec}.{ts,tsx}"],
  },
});
