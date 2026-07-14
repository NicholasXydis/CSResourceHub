import { createHash } from "node:crypto";
import { copyFileSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Plugin } from "vite";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

const SITE_JSON = fileURLToPath(
  new URL("./generated/site.json", import.meta.url),
);

const SITE_URL = "https://csresourcehub.pages.dev";

interface SiteMetadata {
  generated: string;
  total: number;
  labels: Record<string, string>;
}

function structuredData(site: SiteMetadata): string {
  const description = `A curated directory of ${site.total} useful resources across ${Object.keys(site.labels).length} categories for Canadian computer science students.`;
  return JSON.stringify({
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "CS Resource Hub",
    url: `${SITE_URL}/`,
    description,
    inLanguage: "en-CA",
    dateModified: site.generated,
    license: "https://creativecommons.org/licenses/by/4.0/",
    mainEntity: {
      "@type": "ItemList",
      name: "Canadian computer science student resources",
      numberOfItems: site.total,
    },
  });
}

function siteMetadata(): Plugin {
  return {
    name: "site-metadata",
    transformIndexHtml: {
      order: "pre",
      handler(html: string) {
        const site = JSON.parse(
          readFileSync(SITE_JSON, "utf8"),
        ) as Partial<SiteMetadata>;
        if (!site.labels || typeof site.total !== "number" || !site.generated) {
          throw new Error(
            "generated/site.json is missing labels/total/generated. Run: py scripts/generate_site_json.py",
          );
        }
        return html
          .replaceAll("%RESOURCE_TOTAL%", String(site.total))
          .replaceAll(
            "%CATEGORY_TOTAL%",
            String(Object.keys(site.labels).length),
          )
          .replaceAll("%SITE_URL%", SITE_URL)
          .replaceAll("%JSON_LD%", structuredData(site as SiteMetadata));
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
      copyFileSync(SITE_JSON, resolve(outDir, "site.json"));

      const headers = resolve(outDir, "_headers");
      if (!existsSync(headers)) return;
      const html = readFileSync(index, "utf8");
      const jsonLd = html.match(
        /<script type="application\/ld\+json">([\s\S]*?)<\/script>/,
      )?.[1];
      if (jsonLd === undefined) {
        throw new Error("Unable to locate JSON-LD while generating CSP hash");
      }
      const hash = createHash("sha256").update(jsonLd).digest("base64");
      const source = readFileSync(headers, "utf8");
      if (!source.includes("%CSP_SCRIPT_HASH%")) {
        throw new Error("public/_headers is missing %CSP_SCRIPT_HASH%");
      }
      writeFileSync(
        headers,
        source.replace("%CSP_SCRIPT_HASH%", `'sha256-${hash}'`),
        "utf8",
      );
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
    coverage: {
      provider: "v8",
      reporter: ["text", "json-summary", "lcov"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.{ts,tsx}", "src/test/**", "src/vite-env.d.ts"],
      thresholds: {
        statements: 85,
        branches: 85,
        functions: 85,
        lines: 85,
      },
    },
  },
});
