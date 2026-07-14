import { cleanup, fireEvent, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import LogoMark from "./LogoMark";
import { LOGO_DOMAINS } from "../config";

afterEach(cleanup);

function imageOf(container: HTMLElement) {
  const image = container.querySelector("img");
  if (!image) throw new Error("LogoMark rendered no image");
  return image;
}

describe("LogoMark", () => {
  it("serves a self-hosted logo for a domain that has one", () => {
    const [domain] = [...LOGO_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}/page`} />);
    expect(imageOf(container)).toHaveAttribute("src", `/logos/${domain}.png`);
    expect(container.querySelector(".fallback-logo")).toBeNull();
  });

  it("never requests an icon from a third-party host", () => {
    const [domain] = [...LOGO_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}/page`} />);
    const src = imageOf(container).getAttribute("src") ?? "";
    expect(src.startsWith("/")).toBe(true);
    expect(src).not.toContain("google.com");
    expect(src).not.toContain("//");
  });

  it("uses the branded tile for a domain with no stored logo", () => {
    const { container } = render(<LogoMark url="https://no-logo.example/x" />);
    expect(imageOf(container)).toHaveAttribute("src", "/favicon.svg");
    expect(container.querySelector(".fallback-logo")).not.toBeNull();
  });

  it("falls back to the branded tile when the stored logo fails to load", () => {
    const [domain] = [...LOGO_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}/page`} />);
    fireEvent.error(imageOf(container));
    expect(imageOf(container)).toHaveAttribute("src", "/favicon.svg");
    expect(container.querySelector(".fallback-logo")).not.toBeNull();
  });

  it("stays on the tile once the logo has failed", () => {
    const [domain] = [...LOGO_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}/page`} />);
    fireEvent.error(imageOf(container));
    fireEvent.error(imageOf(container));
    expect(imageOf(container)).toHaveAttribute("src", "/favicon.svg");
  });

  it("still renders an icon for a malformed URL", () => {
    const { container } = render(<LogoMark url="not a url" />);
    expect(imageOf(container)).toBeInTheDocument();
  });

  it("hides the logo from assistive technology", () => {
    const [domain] = [...LOGO_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}/page`} />);
    expect(container.querySelector(".resource-logo")).toHaveAttribute(
      "aria-hidden",
      "true",
    );
    expect(imageOf(container)).toHaveAttribute("alt", "");
  });

  it("lazy-loads the logo", () => {
    const [domain] = [...LOGO_DOMAINS];
    const { container } = render(<LogoMark url={`https://${domain}/page`} />);
    expect(imageOf(container)).toHaveAttribute("loading", "lazy");
  });
});
