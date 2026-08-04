import { describe, expect, it, vi } from "vitest";

import { buildTraceabilityCsv, downloadTraceabilityCsv } from "@/lib/traceabilityCsv";

describe("traceabilityCsv", () => {
  it("builds a spreadsheet-safe matrix with stable feature columns", () => {
    const csv = buildTraceabilityCsv({
      features: [
        { id: "feature-1", title: "Checkout" },
        { id: "feature-2", title: "Reporting" },
      ],
      linkedFeatureIdsByRequirement: { "requirement-1": new Set(["feature-1"]) },
      requirements: [{ id: "requirement-1", title: 'Order, "flow"' }],
    });

    expect(csv).toBe(
      "Requirement ID,Requirement,Coverage,Feature: Checkout,Feature: Reporting\r\n" +
        'requirement-1,"Order, ""flow""",PARTIAL 1/2,Linked,',
    );
  });

  it("neutralizes spreadsheet formulas in exported titles", () => {
    const csv = buildTraceabilityCsv({
      features: [{ id: "feature-1", title: "=HYPERLINK(\"https://invalid.example\")" }],
      linkedFeatureIdsByRequirement: {},
      requirements: [{ id: "requirement-1", title: "+1+1" }],
    });

    expect(csv).toContain('Feature: =HYPERLINK');
    expect(csv).toContain(",'+1+1,UNCOVERED,");
  });

  it("downloads the generated CSV and releases the temporary object URL", () => {
    const createObjectURL = vi.fn(() => "blob:traceability-csv");
    const revokeObjectURL = vi.fn();
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });

    downloadTraceabilityCsv("matrix csv", "traceability-matrix.csv");

    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:traceability-csv");
    expect(document.querySelector('a[download="traceability-matrix.csv"]')).toBeNull();
  });
});
