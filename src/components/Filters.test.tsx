import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import Filters from "./Filters";
import { CATEGORY_LABELS, GROUPS, GROUP_COUNTS, SITE_DATA } from "../config";
import type { Category, CollectionFilter, Group } from "../types";

afterEach(cleanup);

const group = GROUPS[0] as Group;
const insideCategory = group.categories[0] as Category;
const outsideCategory = (GROUPS[1] as Group).categories[0] as Category;
const nameOf = (text: string) =>
  new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));

function renderFilters(overrides: Partial<Parameters<typeof Filters>[0]> = {}) {
  const props = {
    collection: "all" as const,
    category: "all" as const,
    setCollection: vi.fn(),
    setCategory: vi.fn(),
    ...overrides,
  };
  render(<Filters {...props} />);
  return props;
}

describe("Filters", () => {
  it("shows the dataset total against all collections", () => {
    renderFilters();
    expect(
      screen.getByRole("button", { name: /All collections/i }),
    ).toHaveTextContent(String(SITE_DATA.total));
  });

  it("shows each collection with its own count", () => {
    renderFilters();
    expect(
      screen.getByRole("button", { name: nameOf(group.name) }),
    ).toHaveTextContent(String(GROUP_COUNTS[group.name]));
  });

  it("resets the category when a new collection is chosen", () => {
    const props = renderFilters();
    fireEvent.click(screen.getByRole("button", { name: nameOf(group.name) }));
    expect(props.setCollection).toHaveBeenCalledWith(group.name);
    expect(props.setCategory).toHaveBeenCalledWith("all");
  });

  it("clears both filters from the clear-all button", () => {
    const props = renderFilters({ collection: group.name, category: "all" });
    fireEvent.click(
      screen.getByRole("button", { name: /clear all resource filters/i }),
    );
    expect(props.setCollection).toHaveBeenCalledWith("all");
    expect(props.setCategory).toHaveBeenCalledWith("all");
  });

  it("applies a chosen category so several filters can be combined", () => {
    const props = renderFilters({});
    fireEvent.click(
      screen.getByRole("button", {
        name: nameOf(CATEGORY_LABELS[insideCategory]),
      }),
    );
    expect(props.setCategory).toHaveBeenCalledWith(insideCategory);
  });

  it("enables every category when no collection is selected", () => {
    renderFilters();
    expect(
      screen.getByRole("button", {
        name: nameOf(CATEGORY_LABELS[outsideCategory]),
      }),
    ).toBeEnabled();
  });

  it("treats an unrecognised collection as no collection", () => {
    renderFilters({
      collection: "Not A Real Collection" as CollectionFilter,
    });
    expect(
      screen.getByRole("button", {
        name: nameOf(CATEGORY_LABELS[outsideCategory]),
      }),
    ).toBeEnabled();
    expect(
      screen.getByRole("button", { name: /All categories/i }),
    ).toHaveTextContent(String(SITE_DATA.total));
  });

  it("disables categories outside the selected collection", () => {
    renderFilters({ collection: group.name });
    expect(
      screen.getByRole("button", {
        name: nameOf(CATEGORY_LABELS[insideCategory]),
      }),
    ).toBeEnabled();
    expect(
      screen.getByRole("button", {
        name: nameOf(CATEGORY_LABELS[outsideCategory]),
      }),
    ).toBeDisabled();
  });
});
