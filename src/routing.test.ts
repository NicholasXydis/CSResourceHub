import { describe, expect, it } from "vitest";
import { isKnownPath } from "./routing";

describe("isKnownPath", () => {
  it("accepts the site root in its usual forms", () => {
    expect(isKnownPath("/")).toBe(true);
    expect(isKnownPath("")).toBe(true);
    expect(isKnownPath("/index.html")).toBe(true);
  });

  it("ignores trailing slashes", () => {
    expect(isKnownPath("//")).toBe(true);
    expect(isKnownPath("/index.html/")).toBe(true);
  });

  it("rejects any other path", () => {
    expect(isKnownPath("/missing")).toBe(false);
    expect(isKnownPath("/resources/ctfs")).toBe(false);
  });

  it("rejects a path that merely contains the root", () => {
    expect(isKnownPath("/nested/index.html")).toBe(false);
  });

  it("is case sensitive", () => {
    expect(isKnownPath("/INDEX.HTML")).toBe(false);
  });
});
