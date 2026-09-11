import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Input } from "../Input";

describe("Input", () => {
  it("renders label and input", () => {
    render(<Input label="Full Name" name="full_name" />);
    expect(screen.getByLabelText("Full Name")).toBeInTheDocument();
  });

  it("renders placeholder", () => {
    render(<Input label="Email" name="email" placeholder="Enter your email" />);
    expect(screen.getByPlaceholderText("Enter your email")).toBeInTheDocument();
  });

  it("renders error message", () => {
    render(<Input label="Password" name="password" error="Too short" />);
    expect(screen.getByText("Too short")).toBeInTheDocument();
  });

  it("applies error styles to input", () => {
    render(<Input label="Code" name="code" error="Invalid" />);
    const input = screen.getByLabelText("Code");
    expect(input.className).toContain("border-red-400");
  });

  it("accepts user input", async () => {
    const user = userEvent.setup();
    render(<Input label="Search" name="search" />);
    const input = screen.getByLabelText("Search");
    await user.type(input, "hello");
    expect(input).toHaveValue("hello");
  });

  it("forwards additional className", () => {
    render(<Input label="Test" name="test" className="extra-class" />);
    const input = screen.getByLabelText("Test");
    expect(input.className).toContain("extra-class");
  });

  it("renders required attribute on input", () => {
    render(<Input label="Required" name="required" required />);
    expect(screen.getByLabelText("Required")).toBeRequired();
  });
});
