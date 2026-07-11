import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";
import { ALL_RESOURCES, PAGE_SIZE } from "./config";

afterEach(cleanup);

describe("App", () => {
  it("filters the results from the hero search box", () => {
    const { container } = render(<App />);
    expect(container.querySelectorAll(".resource-card")).toHaveLength(
      PAGE_SIZE,
    );

    const target = ALL_RESOURCES[0]!;
    fireEvent.change(
      screen.getByRole("textbox", { name: /search resources/i }),
      {
        target: { value: target.name },
      },
    );

    const cards = container.querySelectorAll(".resource-card");
    expect(cards.length).toBeGreaterThan(0);
    expect(cards.length).toBeLessThan(ALL_RESOURCES.length);
    expect(screen.getAllByText(target.name).length).toBeGreaterThan(0);
  });

  it("clears the search from the empty state, restoring every result", () => {
    const { container } = render(<App />);
    const search = screen.getByRole("textbox", { name: /search resources/i });

    fireEvent.change(search, { target: { value: "zzz-nothing-matches-this" } });
    expect(container.querySelectorAll(".resource-card")).toHaveLength(0);
    expect(
      screen.getByRole("heading", { name: /no resources found/i }),
    ).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: /clear search and filters/i }),
    );

    expect(search).toHaveValue("");
    expect(container.querySelectorAll(".resource-card")).toHaveLength(
      PAGE_SIZE,
    );
  });
});
