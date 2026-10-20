/**
 * Tests for Reports API
 *
 * Note: fetchReportTemplates and generateReport are currently 501 stubs
 * (see reports.ts). Tests assert the honest-error contract per #1137.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { exportProject, fetchReportTemplates, generateReport, importProject } from "@/api/reports";

// Mock the endpoints
vi.mock("@/api/endpoints", () => ({
  exportImportApi: {
    exportProject: vi.fn(),
    importProject: vi.fn(),
  },
}));

import { exportImportApi } from "@/api/endpoints";

describe("Reports API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchReportTemplates, () => {
    it("should throw 501 Not implemented yet", async () => {
      await expect(fetchReportTemplates()).rejects.toMatchObject({
        status: 501,
        statusText: "Not implemented yet",
      });
    });

    it("should throw error with not_implemented payload", async () => {
      await expect(fetchReportTemplates()).rejects.toMatchObject({
        data: expect.objectContaining({
          error: "not_implemented",
          route: "/api/v1/reports/templates",
        }),
      });
    });
  });

  describe(generateReport, () => {
    it("should throw 501 Not implemented yet", async () => {
      await expect(generateReport("proj-1", "1", "pdf")).rejects.toMatchObject({
        status: 501,
        statusText: "Not implemented yet",
      });
    });

    it("should throw error with not_implemented payload", async () => {
      await expect(generateReport("proj-1", "1", "pdf")).rejects.toMatchObject({
        data: expect.objectContaining({
          error: "not_implemented",
          route: "/api/v1/reports",
        }),
      });
    });
  });

  describe(exportProject, () => {
    it("should call exportProject endpoint", async () => {
      vi.mocked(exportImportApi.exportProject).mockResolvedValue({
        url: "http://example.com/export",
      });

      await exportProject("proj-1");

      expect(exportImportApi.exportProject).toHaveBeenCalledWith("proj-1");
    });

    it("should handle export response", async () => {
      const mockResponse = { url: "http://example.com/export.zip" };
      vi.mocked(exportImportApi.exportProject).mockResolvedValue(mockResponse);

      const result = await exportProject("proj-1");

      expect(result).toEqual(mockResponse);
    });

    it("should pass correct project ID", async () => {
      vi.mocked(exportImportApi.exportProject).mockResolvedValue({
        url: "test",
      });

      await exportProject("specific-project-id");

      expect(exportImportApi.exportProject).toHaveBeenCalledWith("specific-project-id");
    });
  });

  describe(importProject, () => {
    it("should call importProject endpoint", async () => {
      const mockFile = new File(['{"data": "test"}'], "project.json", {
        type: "application/json",
      });
      vi.mocked(exportImportApi.importProject).mockResolvedValue({
        id: "imported-proj",
      });

      await importProject(mockFile);

      expect(exportImportApi.importProject).toHaveBeenCalledWith(mockFile);
    });

    it("should handle import response", async () => {
      const mockFile = new File(["{}"], "project.json");
      const mockResponse = { id: "new-proj-123" };
      vi.mocked(exportImportApi.importProject).mockResolvedValue(mockResponse);

      const result = await importProject(mockFile);

      expect(result).toEqual(mockResponse);
    });

    it("should accept JSON files", async () => {
      const jsonFile = new File(['{"name": "test"}'], "project.json", {
        type: "application/json",
      });
      vi.mocked(exportImportApi.importProject).mockResolvedValue({
        id: "proj",
      });

      await importProject(jsonFile);

      expect(exportImportApi.importProject).toHaveBeenCalledWith(jsonFile);
    });

    it("should accept ZIP files", async () => {
      const zipFile = new File([new ArrayBuffer(10)], "project.zip", {
        type: "application/zip",
      });
      vi.mocked(exportImportApi.importProject).mockResolvedValue({
        id: "proj",
      });

      await importProject(zipFile);

      expect(exportImportApi.importProject).toHaveBeenCalledWith(zipFile);
    });
  });

  describe("Report API error handling", () => {
    it("fetchReportTemplates should throw 501 as honest error", async () => {
      await expect(fetchReportTemplates()).rejects.toMatchObject({
        status: 501,
      });
    });

    it("generateReport should throw 501 as honest error", async () => {
      await expect(generateReport("proj-1", "1", "pdf")).rejects.toMatchObject({
        status: 501,
      });
    });

    it("should handle export errors", async () => {
      vi.mocked(exportImportApi.exportProject).mockRejectedValue(new Error("Export failed"));

      await expect(exportProject("proj-1")).rejects.toThrow("Export failed");
    });

    it("should handle import errors", async () => {
      const mockFile = new File(["invalid"], "bad.json");
      vi.mocked(exportImportApi.importProject).mockRejectedValue(new Error("Import failed"));

      await expect(importProject(mockFile)).rejects.toThrow("Import failed");
    });
  });
});
