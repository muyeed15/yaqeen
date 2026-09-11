import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Select } from "../Select";

describe("Select", () => {
  it("renders label associated with the select", () => {
    render(
      <Select label="Plan" name="plan">
        <option value="1">One</option>
      </Select>,
    );
    expect(screen.getByLabelText("Plan")).toBeInTheDocument();
  });

  it("renders options and allows selection", async () => {
    const user = userEvent.setup();
    render(
      <Select label="Plan" name="plan" defaultValue="1">
        <option value="1">One</option>
        <option value="2">Two</option>
      </Select>,
    );
    const select = screen.getByLabelText("Plan");
    await user.selectOptions(select, "2");
    expect(select).toHaveValue("2");
  });

  it("renders error message and error styles", () => {
    render(
      <Select label="Bank" name="bank" error="Required">
        <option value="">Select</option>
      </Select>,
    );
    expect(screen.getByText("Required")).toBeInTheDocument();
    expect(screen.getByLabelText("Bank").className).toContain("border-red-400");
  });

  it("renders hint when there is no error", () => {
    render(
      <Select label="Bank" name="bank" hint="Choose one">
        <option value="">Select</option>
      </Select>,
    );
    expect(screen.getByText("Choose one")).toBeInTheDocument();
  });

  it("forwards additional className", () => {
    render(
      <Select label="Bank" name="bank" className="extra-class">
        <option value="">Select</option>
      </Select>,
    );
    expect(screen.getByLabelText("Bank").className).toContain("extra-class");
  });

  it("renders required attribute on select", () => {
    render(
      <Select label="Bank" name="bank" required>
        <option value="">Select</option>
      </Select>,
    );
    expect(screen.getByLabelText("Bank")).toBeRequired();
  });
});
