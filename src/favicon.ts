import { MISSING_FAVICON_DOMAINS, SITE_FAVICON_DOMAINS } from "./config";

export type FaviconSource = "google" | "site" | "fallback";

export function initialFaviconSource(domain: string): FaviconSource {
  if (MISSING_FAVICON_DOMAINS.has(domain)) return "fallback";
  if (SITE_FAVICON_DOMAINS.has(domain)) return "site";
  return "google";
}

export function googleFaviconUrl(domain: string): string {
  return `https://www.google.com/s2/favicons?domain=${encodeURIComponent(domain)}&sz=128`;
}

export function nextFaviconSource(current: FaviconSource): FaviconSource {
  return current === "google" ? "site" : "fallback";
}
