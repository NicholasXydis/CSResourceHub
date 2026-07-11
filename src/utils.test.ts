import { describe, expect, it } from "vitest";
import {
  FALLBACK_TYPE,
  badgeHue,
  badgeStyle,
  domainOf,
  nextVisibleCount,
  originFavicon,
} from "./utils";
import { ALLOWED_TYPES, ALL_RESOURCES, GROUPS } from "./config";

const MIN_SEPARATION = 20;

function angularDistance(a: number, b: number): number {
  const raw = Math.abs(a - b) % 360;
  return Math.min(raw, 360 - raw);
}

describe("domainOf", () => {
  it("strips the scheme, www prefix, and path", () => {
    expect(domainOf("https://www.leetcode.com/problems/two-sum")).toBe(
      "leetcode.com",
    );
  });

  it("keeps subdomains that are not www", () => {
    expect(domainOf("https://ctf.uoftctf.org")).toBe("ctf.uoftctf.org");
  });

  it("returns the input unchanged when it is not a URL", () => {
    expect(domainOf("not a url")).toBe("not a url");
  });

  it("survives an empty string", () => {
    expect(domainOf("")).toBe("");
  });

  it("does not strip a domain that merely starts with www", () => {
    expect(domainOf("https://wwwtest.example.com")).toBe("wwwtest.example.com");
  });
});

describe("originFavicon", () => {
  it("points at the favicon on the site's own origin", () => {
    expect(originFavicon("https://example.com/deep/page?q=1")).toBe(
      "https://example.com/favicon.ico",
    );
  });

  it("keeps the port when the origin has one", () => {
    expect(originFavicon("https://example.com:8443/x")).toBe(
      "https://example.com:8443/favicon.ico",
    );
  });

  it("returns an empty string for an unparseable URL", () => {
    expect(originFavicon("not a url")).toBe("");
  });

  it("returns an empty string for an empty input", () => {
    expect(originFavicon("")).toBe("");
  });
});

describe("nextVisibleCount", () => {
  it("loads a full page when enough results remain", () => {
    expect(nextVisibleCount(18, 334, 18)).toBe(36);
  });

  it("stops at the total for the final partial page", () => {
    expect(nextVisibleCount(324, 334, 18)).toBe(334);
  });

  it("never exceeds the total when already past it", () => {
    expect(nextVisibleCount(400, 334, 18)).toBe(334);
  });

  it("handles an empty result set", () => {
    expect(nextVisibleCount(0, 0, 18)).toBe(0);
  });

  it("handles a total smaller than one page", () => {
    expect(nextVisibleCount(0, 5, 18)).toBe(5);
  });
});

function typesOf(group: (typeof GROUPS)[number]): string[] {
  const types = new Set<string>([FALLBACK_TYPE]);
  for (const category of group.categories) {
    for (const type of ALLOWED_TYPES[category] ?? []) types.add(type);
  }
  return [...types];
}

describe("badgeHue", () => {
  it("gives one type exactly one colour everywhere it appears", () => {
    expect(badgeHue("tool")).toBe(badgeHue("tool"));
    const seen = new Map<string, number>();
    for (const resource of ALL_RESOURCES) {
      const type = resource.type ?? FALLBACK_TYPE;
      const hue = badgeHue(type);
      if (seen.has(type)) expect(seen.get(type)).toBe(hue);
      seen.set(type, hue);
    }
  });

  it("keeps every type inside a collection visually distinct", () => {
    for (const group of GROUPS) {
      const hues = typesOf(group).map(badgeHue);
      expect(new Set(hues).size).toBe(hues.length);

      for (let i = 0; i < hues.length; i += 1) {
        for (let j = i + 1; j < hues.length; j += 1) {
          expect(
            angularDistance(hues[i] as number, hues[j] as number),
          ).toBeGreaterThanOrEqual(MIN_SEPARATION);
        }
      }
    }
  });

  it("gives every real resource a hue in range", () => {
    for (const resource of ALL_RESOURCES) {
      const hue = badgeHue(resource.type ?? FALLBACK_TYPE);
      expect(hue).toBeGreaterThanOrEqual(0);
      expect(hue).toBeLessThan(360);
    }
  });

  it("gives an unknown type the fallback hue", () => {
    expect(badgeHue("not-a-type")).toBe(badgeHue(FALLBACK_TYPE));
  });

  it("gives an empty type the fallback hue", () => {
    expect(badgeHue("")).toBe(badgeHue(FALLBACK_TYPE));
  });
});

describe("badgeStyle", () => {
  it("emits all four badge custom properties", () => {
    const style = badgeStyle("tool");
    expect(style["--badge-color"]).toMatch(/^hsl\(/);
    expect(style["--badge-bg"]).toMatch(/^hsl\(/);
    expect(style["--badge-border"]).toMatch(/^hsl\(/);
    expect(style["--badge-glow"]).toMatch(/^hsl\(/);
  });

  it("treats an empty type as the fallback type", () => {
    expect(badgeStyle("")).toEqual(badgeStyle(FALLBACK_TYPE));
  });

  it("styles the same type identically regardless of where it is used", () => {
    expect(badgeStyle("tool")).toEqual(badgeStyle("tool"));
    expect(badgeStyle("organization")).toEqual(badgeStyle("organization"));
  });
});
