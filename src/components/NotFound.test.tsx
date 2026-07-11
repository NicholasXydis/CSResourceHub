import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import NotFound from "./NotFound";
import { SITE_DATA } from "../config";

afterEach(cleanup);

describe("NotFound", () => {
  it("explains that the page does not exist", () => {
    render(<NotFound />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      /wrong turn/i,
    );
    expect(screen.getByText(/page not found/i)).toBeInTheDocument();
  });

  it("offers a way back to the directory", () => {
    render(<NotFound />);
    expect(
      screen.getByRole("link", { name: /back to the directory/i }),
    ).toHaveAttribute("href", "/");
  });

  it("reports the live resource total rather than a hardcoded number", () => {
    render(<NotFound />);
    expect(
      screen.getByText(new RegExp(`${SITE_DATA.total} resources`)),
    ).toBeInTheDocument();
  });
});
