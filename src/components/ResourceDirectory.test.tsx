import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import ResourceDirectory from "./ResourceDirectory";
import {
  ALL_RESOURCES,
  CATEGORY_LABELS,
  GROUPS,
  PAGE_SIZE,
  SITE_DATA,
} from "../config";
import type { Category, Group } from "../types";

afterEach(cleanup);

function requireGroup(index: number): Group {
  const group = GROUPS[index];
  if (!group) throw new Error(`site.json has no group at index ${index}`);
  return group;
}

function firstLabelOf(group: Group): string {
  const [category] = group.categories as [Category, ...Category[]];
  return CATEGORY_LABELS[category];
}

const firstGroup = requireGroup(0);
const secondGroup = requireGroup(1);

const nameOf = (text: string) =>
  new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
const insideLabel = firstLabelOf(firstGroup);
const outsideLabel = firstLabelOf(secondGroup);
const secondPage = Math.min(PAGE_SIZE * 2, SITE_DATA.total);
const noop = () => {};

describe("ResourceDirectory search edge cases", () => {
  const cards = (container: HTMLElement) =>
    container.querySelectorAll(".resource-card").length;

  it("treats a whitespace-only query as no query", () => {
    const { container } = render(
      <ResourceDirectory query="   " setQuery={noop} />,
    );
    expect(cards(container)).toBe(PAGE_SIZE);
  });

  it("matches regardless of case", () => {
    const { container: lower } = render(
      <ResourceDirectory query="leetcode" setQuery={noop} />,
    );
    const lowerCount = cards(lower);
    cleanup();
    const { container: upper } = render(
      <ResourceDirectory query="LEETCODE" setQuery={noop} />,
    );
    expect(cards(upper)).toBe(lowerCount);
  });

  it("treats regular expression characters as literal text", () => {
    const { container } = render(
      <ResourceDirectory query=".*+?(" setQuery={noop} />,
    );
    expect(cards(container)).toBe(0);
    expect(
      screen.getByRole("heading", { name: /no resources found/i }),
    ).toBeInTheDocument();
  });

  it("hides the load-more button when a query returns one page or fewer", () => {
    const { container } = render(
      <ResourceDirectory query="zzz-no-such-resource" setQuery={noop} />,
    );
    expect(cards(container)).toBe(0);
    expect(screen.queryByRole("button", { name: /show \d+ more/i })).toBeNull();
  });

  it("trims surrounding whitespace before matching", () => {
    const { container } = render(
      <ResourceDirectory query="  leetcode  " setQuery={noop} />,
    );
    expect(cards(container)).toBeGreaterThan(0);
  });
});

describe("ResourceDirectory", () => {
  it("loads another page of visible resource cards", async () => {
    const { container } = render(
      <ResourceDirectory query="" setQuery={noop} />,
    );
    expect(container.querySelectorAll(".resource-card")).toHaveLength(
      PAGE_SIZE,
    );
    fireEvent.click(
      screen.getByRole("button", {
        name: new RegExp(`show ${secondPage - PAGE_SIZE} more`, "i"),
      }),
    );
    await waitFor(() =>
      expect(container.querySelectorAll(".resource-card")).toHaveLength(
        secondPage,
      ),
    );
  });

  it("sorts results alphabetically by name", () => {
    const { container } = render(
      <ResourceDirectory query="" setQuery={noop} />,
    );
    fireEvent.change(
      screen.getByRole("combobox", { name: /sort resources/i }),
      {
        target: { value: "name" },
      },
    );
    const names = [...container.querySelectorAll(".resource-card h3")].map(
      (node) => node.textContent ?? "",
    );
    expect(names).toEqual([...names].sort((a, b) => a.localeCompare(b)));
  });

  it("sorts results from newest to oldest", () => {
    const { container } = render(
      <ResourceDirectory query="" setQuery={noop} />,
    );
    fireEvent.change(
      screen.getByRole("combobox", { name: /sort resources/i }),
      {
        target: { value: "newest" },
      },
    );
    const names = [...container.querySelectorAll(".resource-card h3")].map(
      (node) => node.textContent ?? "",
    );
    const expected = [...ALL_RESOURCES]
      .sort((a, b) => (b.date_added || "").localeCompare(a.date_added || ""))
      .slice(0, PAGE_SIZE)
      .map((resource) => resource.name);
    expect(names).toEqual(expected);
  });

  it("opens and closes the filter drawer", async () => {
    render(<ResourceDirectory query="" setQuery={noop} />);
    fireEvent.click(screen.getByRole("button", { name: /^Filters/ }));
    expect(
      screen.getByRole("dialog", { name: /resource filters/i }),
    ).toBeInTheDocument();
    expect(document.body.style.overflow).toBe("hidden");
    fireEvent.keyDown(window, { key: "Escape" });
    await waitFor(() =>
      expect(
        screen.queryByRole("dialog", { name: /resource filters/i }),
      ).toBeNull(),
    );
    await waitFor(() => expect(document.body.style.overflow).toBe(""));
  });

  it("moves focus into the drawer and restores it on close", async () => {
    render(<ResourceDirectory query="" setQuery={noop} />);
    const trigger = screen.getByRole("button", { name: /^Filters/ });
    fireEvent.click(trigger);

    const drawer = screen.getByRole("dialog", { name: /resource filters/i });
    await waitFor(() =>
      expect(drawer.contains(document.activeElement)).toBe(true),
    );

    fireEvent.keyDown(window, { key: "Escape" });
    await waitFor(() => expect(trigger).toHaveFocus());
  });

  it("keeps Tab inside the open drawer", async () => {
    render(<ResourceDirectory query="" setQuery={noop} />);
    fireEvent.click(screen.getByRole("button", { name: /^Filters/ }));
    const drawer = screen.getByRole("dialog", { name: /resource filters/i });

    const focusable = [
      ...drawer.querySelectorAll<HTMLElement>("button:not([disabled])"),
    ];
    const last = focusable[focusable.length - 1] as HTMLElement;
    last.focus();
    fireEvent.keyDown(window, { key: "Tab" });

    await waitFor(() => expect(focusable[0]).toHaveFocus());
  });

  it("resets pagination when the collection changes", async () => {
    const { container } = render(
      <ResourceDirectory query="" setQuery={noop} />,
    );
    fireEvent.click(
      screen.getByRole("button", {
        name: new RegExp(`show ${secondPage - PAGE_SIZE} more`, "i"),
      }),
    );
    await waitFor(() =>
      expect(container.querySelectorAll(".resource-card")).toHaveLength(
        secondPage,
      ),
    );
    fireEvent.click(
      screen.getByRole("button", { name: nameOf(firstGroup.name) }),
    );
    expect(
      container.querySelectorAll(".resource-card").length,
    ).toBeLessThanOrEqual(PAGE_SIZE);
  });

  it("clears the search query and the filters from the empty state", () => {
    const setQuery = vi.fn();
    render(
      <ResourceDirectory query="zzz-no-such-resource" setQuery={setQuery} />,
    );
    fireEvent.click(screen.getByRole("button", { name: nameOf(outsideLabel) }));
    expect(
      screen.getByRole("heading", { name: /no resources found/i }),
    ).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: /clear search and filters/i }),
    );
    expect(setQuery).toHaveBeenCalledWith("");
    expect(
      screen.getByRole("button", { name: /All collections/i }),
    ).toHaveAttribute("aria-pressed", "true");
    expect(
      screen.getByRole("button", { name: /All categories/i }),
    ).toHaveAttribute("aria-pressed", "true");
  });

  it("enables only categories in the selected collection", () => {
    render(<ResourceDirectory query="" setQuery={noop} />);
    fireEvent.click(
      screen.getByRole("button", { name: nameOf(firstGroup.name) }),
    );
    const inside = screen.getByRole("button", { name: nameOf(insideLabel) });
    const outside = screen.getByRole("button", {
      name: nameOf(outsideLabel),
    });
    expect(inside).toBeEnabled();
    expect(outside).toBeDisabled();
    expect(
      inside.compareDocumentPosition(outside) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /All collections/i }));
    expect(
      screen.getByRole("button", { name: nameOf(outsideLabel) }),
    ).toBeEnabled();
  });
});
