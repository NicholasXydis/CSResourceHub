import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import ResourceCard from "./ResourceCard";
import { CATEGORY_LABELS } from "../config";
import type { Resource } from "../types";

afterEach(cleanup);

const resource: Resource = {
  id: "leetcode",
  name: "LeetCode",
  url: "https://leetcode.com/problems",
  description: "Coding interview platform.",
  category: "interview-prep",
  type: "platform",
};

function renderCard(overrides: Partial<Resource> = {}) {
  return render(
    <ResourceCard resource={{ ...resource, ...overrides }} index={0} />,
  );
}

describe("ResourceCard", () => {
  it("shows the name, description, domain, and category", () => {
    renderCard();
    expect(screen.getByRole("heading", { level: 3 })).toHaveTextContent(
      "LeetCode",
    );
    expect(screen.getByText("Coding interview platform.")).toBeInTheDocument();
    expect(screen.getByText("leetcode.com")).toBeInTheDocument();
    expect(
      screen.getByText(CATEGORY_LABELS["interview-prep"]),
    ).toBeInTheDocument();
  });

  it("opens the resource in a new tab without leaking the referrer", () => {
    renderCard();
    const visit = screen.getByRole("link", { name: /visit leetcode/i });
    expect(visit).toHaveAttribute("href", resource.url);
    expect(visit).toHaveAttribute("target", "_blank");
    expect(visit).toHaveAttribute("rel", "noreferrer");
  });

  it("shows the resource type as a badge", () => {
    renderCard();
    expect(screen.getByText("platform")).toBeInTheDocument();
  });

  it("falls back to the resource badge when no type is set", () => {
    renderCard({ type: undefined });
    expect(screen.getByText("resource")).toBeInTheDocument();
  });

  it("colors the badge from the type", () => {
    const { container } = renderCard();
    const card = container.querySelector(".resource-card") as HTMLElement;
    expect(card.style.getPropertyValue("--badge-color")).not.toBe("");
  });
});
