import { LOGO_DOMAINS } from "./config";

export type FaviconSource = "local" | "fallback";

export function initialFaviconSource(domain: string): FaviconSource {
  return LOGO_DOMAINS.has(domain) ? "local" : "fallback";
}

export function localLogoUrl(domain: string): string {
  return `/logos/${encodeURIComponent(domain)}.png`;
}

export function nextFaviconSource(): FaviconSource {
  return "fallback";
}
