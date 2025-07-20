import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TestRouterWrapper } from "./utils/testRouter";

// Sample test to ensure testing infrastructure works
describe("Testing Infrastructure", () => {
  it("should render without crashing", () => {
    render(
      <TestRouterWrapper>
        <div>Hello World</div>
      </TestRouterWrapper>,
    );

    expect(screen.getByText("Hello World")).toBeInTheDocument();
  });

  it("should have proper test environment setup", () => {
    expect(window.matchMedia).toBeDefined();
    expect(global.IntersectionObserver).toBeDefined();
    expect(global.ResizeObserver).toBeDefined();
  });
});
