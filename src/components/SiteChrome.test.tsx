import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Footer, Header, Hero } from "./SiteChrome";
import { CATEGORY_LABELS, GROUPS, SITE_DATA } from "../config";

afterEach(cleanup);

describe("Header", () => {
  it("toggles the mobile navigation", () => {
    render(<Header />);
    const toggle = screen.getByRole("button", { name: /toggle navigation/i });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
  });

  it("links out to the repository", () => {
    render(<Header />);
    expect(screen.getByRole("link", { name: /github/i })).toHaveAttribute(
      "href",
      expect.stringContaining("github.com"),
    );
  });
});

describe("Hero", () => {
  it("reports the query as the user types", () => {
    const setQuery = vi.fn();
    render(<Hero query="" setQuery={setQuery} />);
    fireEvent.change(
      screen.getByRole("textbox", { name: /search resources/i }),
      {
        target: { value: "ctf" },
      },
    );
    expect(setQuery).toHaveBeenCalledWith("ctf");
  });

  it("clears the query from the clear button", () => {
    const setQuery = vi.fn();
    render(<Hero query="ctf" setQuery={setQuery} />);
    fireEvent.click(screen.getByRole("button", { name: /clear search/i }));
    expect(setQuery).toHaveBeenCalledWith("");
  });

  it("focuses the search input on the / shortcut", () => {
    render(<Hero query="" setQuery={vi.fn()} />);
    const input = screen.getByRole("textbox", { name: /search resources/i });
    expect(input).not.toHaveFocus();
    fireEvent.keyDown(window, { key: "/" });
    expect(input).toHaveFocus();
  });

  it("shows stats derived from the dataset, not hardcoded numbers", () => {
    render(<Hero query="" setQuery={vi.fn()} />);
    expect(screen.getByText(`${SITE_DATA.total}+`)).toBeInTheDocument();
    expect(
      screen.getByText(String(Object.keys(CATEGORY_LABELS).length)),
    ).toBeInTheDocument();
    expect(screen.getByText(String(GROUPS.length))).toBeInTheDocument();
  });
});

describe("Footer", () => {
  it("offers a back-to-top link", () => {
    render(<Footer />);
    expect(screen.getByRole("link", { name: /back to top/i })).toHaveAttribute(
      "href",
      "#top",
    );
  });
});
