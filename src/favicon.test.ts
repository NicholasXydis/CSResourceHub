import { describe, expect, it } from "vitest";
import {
  googleFaviconUrl,
  initialFaviconSource,
  nextFaviconSource,
} from "./favicon";
import { MISSING_FAVICON_DOMAINS, SITE_FAVICON_DOMAINS } from "./config";

describe("initialFaviconSource", () => {
  it("uses Google for a domain it knows an icon for", () => {
    expect(initialFaviconSource("example.com")).toBe("google");
  });

  it("uses the site's own icon when Google has none", () => {
    const [domain] = [...SITE_FAVICON_DOMAINS];
    expect(domain).toBeDefined();
    expect(initialFaviconSource(domain as string)).toBe("site");
  });

  it("skips straight to the placeholder when no icon exists anywhere", () => {
    const [domain] = [...MISSING_FAVICON_DOMAINS];
    expect(domain).toBeDefined();
    expect(initialFaviconSource(domain as string)).toBe("fallback");
  });

  it("never lists a domain as both missing and site-only", () => {
    const overlap = [...SITE_FAVICON_DOMAINS].filter((domain) =>
      MISSING_FAVICON_DOMAINS.has(domain),
    );
    expect(overlap).toEqual([]);
  });

  it("treats an empty domain as a Google lookup", () => {
    expect(initialFaviconSource("")).toBe("google");
  });
});

describe("nextFaviconSource", () => {
  it("degrades from Google to the site's own icon", () => {
    expect(nextFaviconSource("google")).toBe("site");
  });

  it("degrades from the site's icon to the placeholder", () => {
    expect(nextFaviconSource("site")).toBe("fallback");
  });

  it("stays on the placeholder once it is reached", () => {
    expect(nextFaviconSource("fallback")).toBe("fallback");
  });
});

describe("googleFaviconUrl", () => {
  it("requests a high-resolution icon", () => {
    expect(googleFaviconUrl("example.com")).toContain("sz=128");
  });

  it("encodes the domain", () => {
    expect(googleFaviconUrl("a b.com")).toContain("a%20b.com");
  });
});
