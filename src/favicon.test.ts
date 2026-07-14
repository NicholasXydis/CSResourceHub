import { describe, expect, it } from "vitest";
import {
  initialFaviconSource,
  localLogoUrl,
  nextFaviconSource,
} from "./favicon";
import { LOGO_DOMAINS } from "./config";

describe("initialFaviconSource", () => {
  it("uses the self-hosted logo for a domain that has one", () => {
    const [domain] = [...LOGO_DOMAINS];
    expect(domain).toBeDefined();
    expect(initialFaviconSource(domain as string)).toBe("local");
  });

  it("uses the branded tile for a domain with no stored logo", () => {
    expect(initialFaviconSource("no-logo.example")).toBe("fallback");
  });

  it("treats an empty domain as a tile", () => {
    expect(initialFaviconSource("")).toBe("fallback");
  });
});

describe("nextFaviconSource", () => {
  it("degrades to the branded tile", () => {
    expect(nextFaviconSource()).toBe("fallback");
  });
});

describe("localLogoUrl", () => {
  it("points at a same-origin path", () => {
    expect(localLogoUrl("example.com")).toBe("/logos/example.com.png");
  });

  it("never produces an absolute or protocol-relative URL", () => {
    const url = localLogoUrl("example.com");
    expect(url.startsWith("/")).toBe(true);
    expect(url.startsWith("//")).toBe(false);
  });

  it("encodes a domain with unsafe characters", () => {
    expect(localLogoUrl("a b.com")).toBe("/logos/a%20b.com.png");
  });
});
