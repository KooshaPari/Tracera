import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Settings } from "@/pages/settings/Settings";

describe("Settings page shell", () => {
  it("renders current settings controls", () => {
    render(<Settings />);
    expect(screen.getByRole("heading", { name: "Settings" })).toBeInTheDocument();
    expect(screen.getByText("General")).toBeInTheDocument();
    expect(screen.getByText("API Configuration")).toBeInTheDocument();
    expect(screen.getByText("Theme")).toBeInTheDocument();
    expect(screen.getByText("Backend URL")).toBeInTheDocument();
  });
});
