import { cleanup, fireEvent, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import LogoMark from "./LogoMark";
import { MISSING_FAVICON_DOMAINS, SITE_FAVICON_DOMAINS } from "../config";

afterEach(cleanup);

const LIVE_URL = "https://example.com/some/page";

function imageOf(container: HTMLElement) {
  const image = container.querySelector("img");
  if (!image) throw new Error("LogoMark rendered no image");
  return image;
}

describe("LogoMark", () => {
  it("starts with the high-resolution Google icon", () => {
    const { container } = render(<LogoMark url={LIVE_URL} />);
    const src = imageOf(container).getAttribute("src") ?? "";
    expect(src).toContain("google.com/s2/favicons");
    expect(src).toContain("sz=128");
    expect(src).toContain("example.com");
    expect(container.querySelector(".fallback-logo")).toBeNull();
  });

  it("falls back to the site's own favicon when Google has none", () => {
    const { container } = render(<LogoMark url={LIVE_URL} />);
    fireEvent.error(imageOf(container));
    expect(imageOf(container)).toHaveAttribute(
      "src",
      "https://example.com/favicon.ico",
    );
  });

  it("falls back to the local placeholder when both sources fail", () => {
    const { container } = render(<LogoMark url={LIVE_URL} />);
    fireEvent.error(imageOf(container));
    fireEvent.error(imageOf(container));
    expect(imageOf(container)).toHaveAttribute("src", "/favicon.svg");
    expect(container.querySelector(".fallback-logo")).not.toBeNull();
  });

  it("skips straight to the placeholder for a known icon-less domain", () => {
    const [domain] = [...MISSING_FAVICON_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}`} />);
    expect(imageOf(container)).toHaveAttribute("src", "/favicon.svg");
    expect(container.querySelector(".fallback-logo")).not.toBeNull();
  });

  it("starts at the site's own icon when Google has none", () => {
    const [domain] = [...SITE_FAVICON_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}/page`} />);
    const src = imageOf(container).getAttribute("src") ?? "";
    expect(src).toContain(`https://${domain}/favicon.ico`);
    expect(src).not.toContain("google.com");
  });

  it("still renders an icon for a malformed URL", () => {
    const { container } = render(<LogoMark url="not a url" />);
    expect(imageOf(container)).toBeInTheDocument();
  });

  it("stays on the placeholder once both sources have failed", () => {
    const { container } = render(<LogoMark url={LIVE_URL} />);
    fireEvent.error(imageOf(container));
    fireEvent.error(imageOf(container));
    fireEvent.error(imageOf(container));
    expect(imageOf(container)).toHaveAttribute("src", "/favicon.svg");
  });

  it("hides the logo from assistive technology", () => {
    const { container } = render(<LogoMark url={LIVE_URL} />);
    expect(container.querySelector(".resource-logo")).toHaveAttribute(
      "aria-hidden",
      "true",
    );
    expect(imageOf(container)).toHaveAttribute("alt", "");
  });

  it("requests the icon without leaking the referrer", () => {
    const { container } = render(<LogoMark url={LIVE_URL} />);
    expect(imageOf(container)).toHaveAttribute("referrerPolicy", "no-referrer");
    expect(imageOf(container)).toHaveAttribute("loading", "lazy");
  });
});
