import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const source = readFileSync(resolve("src/main.tsx"), "utf8");

describe("application entry point", () => {
  it("wraps the app in the error boundary", () => {
    const boundary = source.indexOf("<ErrorBoundary>");
    const app = source.indexOf("<App />");
    const close = source.indexOf("</ErrorBoundary>");
    expect(boundary).toBeGreaterThan(-1);
    expect(app).toBeGreaterThan(boundary);
    expect(close).toBeGreaterThan(app);
  });

  it("runs in strict mode", () => {
    expect(source).toContain("React.StrictMode");
  });

  it("fails loudly when the root element is missing", () => {
    expect(source).toContain("throw new Error");
  });
});
