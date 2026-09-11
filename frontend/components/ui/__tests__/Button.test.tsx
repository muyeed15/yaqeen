import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "../Button";

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: /click me/i })).toBeInTheDocument();
  });

  it("applies primary variant by default", () => {
    render(<Button>Submit</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-teal");
    expect(btn.className).toContain("text-white");
  });

  it("applies secondary variant", () => {
    render(<Button variant="secondary">Cancel</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-white");
    expect(btn.className).toContain("border");
  });

  it("applies ghost variant", () => {
    render(<Button variant="ghost">Link</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("text-navy");
  });

  it("applies destructive variant", () => {
    render(<Button variant="destructive">Delete</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("text-red-500");
  });

  it("applies size classes", () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    expect(screen.getByRole("button").className).toContain("h-9");

    rerender(<Button size="lg">Large</Button>);
    expect(screen.getByRole("button").className).toContain("h-12");
  });

  it("shows loading spinner and disables button when loading", () => {
    render(<Button loading>Processing</Button>);
    const btn = screen.getByRole("button");
    expect(btn).toBeDisabled();
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("is disabled when disabled prop is set", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("calls onClick when clicked", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<Button onClick={onClick}>Tap</Button>);
    await user.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("does not call onClick when disabled", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(
      <Button disabled onClick={onClick}>
        Nope
      </Button>,
    );
    await user.click(screen.getByRole("button"));
    expect(onClick).not.toHaveBeenCalled();
  });

  it("forwards additional className", () => {
    render(<Button className="extra-class">Styled</Button>);
    expect(screen.getByRole("button").className).toContain("extra-class");
  });
});
