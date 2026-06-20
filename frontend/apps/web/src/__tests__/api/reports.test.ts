/**
 * Tests for Reports API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { exportProject, fetchReportTemplates, generateReport, importProject } from '@/api/reports';

// Mock the endpoints
vi.mock('@/api/endpoints', () => ({
  exportImportApi: {
    exportProject: vi.fn(),
    importProject: vi.fn(),
  },
}));

import { exportImportApi } from '@/api/endpoints';

describe('Reports API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchReportTemplates, () => {
    it('should fetch report templates', async () => {
      const templates = await fetchReportTemplates();

      expect(templates).toBeInstanceOf(Array);
      expect(templates.length).toBeGreaterThan(0);
    });

    it('should return coverage report template', async () => {
      const templates = await fetchReportTemplates();
      const coverageTemplate = templates.find((t) => t.type === 'coverage');

      expect(coverageTemplate).toBeDefined();
      expect(coverageTemplate?.name).toBe('Coverage Report');
      expect(coverageTemplate?.format).toBe('pdf');
    });

    it('should return traceability report template', async () => {
      const templates = await fetchReportTemplates();
      const traceabilityTemplate = templates.find((t) => t.type === 'traceability');

      expect(traceabilityTemplate).toBeDefined();
      expect(traceabilityTemplate?.name).toBe('Traceability Matrix');
      expect(traceabilityTemplate?.format).toBe('xlsx');
    });

    it('should return status report template', async () => {
      const templates = await fetchReportTemplates();
      const statusTemplate = templates.find((t) => t.type === 'status');

      expect(statusTemplate).toBeDefined();
      expect(statusTemplate?.name).toBe('Status Report');
      expect(statusTemplate?.format).toBe('html');
    });

    it('should return progress report template', async () => {
      const templates = await fetchReportTemplates();
      const progressTemplate = templates.find((t) => t.type === 'progress');

      expect(progressTemplate).toBeDefined();
      expect(progressTemplate?.name).toBe('Progress Report');
      expect(progressTemplate?.format).toBe('pdf');
    });

    it('should have all required template fields', async () => {
      const templates = await fetchReportTemplates();

      templates.forEach((template) => {
        expect(template).toHaveProperty('id');
        expect(template).toHaveProperty('name');
        expect(template).toHaveProperty('description');
        expect(template).toHaveProperty('type');
        expect(template).toHaveProperty('format');
      });
    });

    it('should have unique template IDs', async () => {
      const templates = await fetchReportTemplates();
      const ids = templates.map((t) => t.id);

      expect(new Set(ids).size).toBe(ids.length);
    });

    it('should support valid report types', async () => {
      const templates = await fetchReportTemplates();
      const validTypes = ['coverage', 'traceability', 'status', 'progress', 'custom'];

      templates.forEach((template) => {
        expect(validTypes).toContain(template.type);
      });
    });

    it('should support valid export formats', async () => {
      const templates = await fetchReportTemplates();
      const validFormats = ['pdf', 'html', 'json', 'csv', 'xlsx'];

      templates.forEach((template) => {
        expect(validFormats).toContain(template.format);
      });
    });
  });

  describe(generateReport, () => {
    it('should generate a report with timestamp', async () => {
      const report = await generateReport('proj-1', '1', 'pdf');

      expect(report).toHaveProperty('id');
      expect(report).toHaveProperty('generatedAt');
      expect(new Date(report.generatedAt)).toBeInstanceOf(Date);
    });

    it('should generate report with correct metadata', async () => {
      const report = await generateReport('proj-1', '1', 'pdf');

      expect(report.templateId).toBe('1');
      expect(report.projectId).toBe('proj-1');
      expect(report.format).toBe('pdf');
    });

    it('should generate unique report IDs', async () => {
      const report1 = await generateReport('proj-1', '1', 'pdf');
      // Small delay to ensure different timestamp
      await new Promise((resolve) => setTimeout(resolve, 10));
      const report2 = await generateReport('proj-1', '1', 'pdf');

      expect(report1.id).not.toBe(report2.id);
    });

    it('should include data object in report', async () => {
      const report = await generateReport('proj-1', '1', 'pdf');

      expect(report).toHaveProperty('data');
      expect(typeof report.data).toBe('object');
    });

    it('should support different report formats', async () => {
      const formats = ['pdf', 'html', 'json', 'csv', 'xlsx'];

      for (const format of formats) {
        const report = await generateReport('proj-1', '1', format);
        expect(report.format).toBe(format);
      }
    });

    it('should support different template IDs', async () => {
      const templateIds = ['1', '2', '3', '4'];

      for (const templateId of templateIds) {
        const report = await generateReport('proj-1', templateId, 'pdf');
        expect(report.templateId).toBe(templateId);
      }
    });

    it('should preserve project context in report', async () => {
      const projectIds = ['proj-1', 'proj-2', 'proj-3'];

      for (const projectId of projectIds) {
        const report = await generateReport(projectId, '1', 'pdf');
        expect(report.projectId).toBe(projectId);
      }
    });

    it('should generate report with ISO timestamp', async () => {
      const report = await generateReport('proj-1', '1', 'pdf');

      expect(report.generatedAt).toMatch(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
    });

    it('should include report metadata', async () => {
      const report = await generateReport('proj-1', 'coverage', 'pdf');

      expect(report).toMatchObject({
        format: 'pdf',
        projectId: 'proj-1',
        templateId: 'coverage',
      });
    });
  });

  describe(exportProject, () => {
    it('should call exportProject endpoint', async () => {
      vi.mocked(exportImportApi.exportProject).mockResolvedValue({
        url: 'http://example.com/export',
      });

      await exportProject('proj-1');

      expect(exportImportApi.exportProject).toHaveBeenCalledWith('proj-1');
    });

    it('should handle export response', async () => {
      const mockResponse = { url: 'http://example.com/export.zip' };
      vi.mocked(exportImportApi.exportProject).mockResolvedValue(mockResponse);

      const result = await exportProject('proj-1');

      expect(result).toEqual(mockResponse);
    });

    it('should pass correct project ID', async () => {
      vi.mocked(exportImportApi.exportProject).mockResolvedValue({
        url: 'test',
      });

      await exportProject('specific-project-id');

      expect(exportImportApi.exportProject).toHaveBeenCalledWith('specific-project-id');
    });
  });

  describe(importProject, () => {
    it('should call importProject endpoint', async () => {
      const mockFile = new File(['{"data": "test"}'], 'project.json', {
        type: 'application/json',
      });
      vi.mocked(exportImportApi.importProject).mockResolvedValue({
        id: 'imported-proj',
      });

      await importProject(mockFile);

      expect(exportImportApi.importProject).toHaveBeenCalledWith(mockFile);
    });

    it('should handle import response', async () => {
      const mockFile = new File(['{}'], 'project.json');
      const mockResponse = { id: 'new-proj-123' };
      vi.mocked(exportImportApi.importProject).mockResolvedValue(mockResponse);

      const result = await importProject(mockFile);

      expect(result).toEqual(mockResponse);
    });

    it('should accept JSON files', async () => {
      const jsonFile = new File(['{"name": "test"}'], 'project.json', {
        type: 'application/json',
      });
      vi.mocked(exportImportApi.importProject).mockResolvedValue({
        id: 'proj',
      });

      await importProject(jsonFile);

      expect(exportImportApi.importProject).toHaveBeenCalledWith(jsonFile);
    });

    it('should accept ZIP files', async () => {
      const zipFile = new File([new ArrayBuffer(10)], 'project.zip', {
        type: 'application/zip',
      });
      vi.mocked(exportImportApi.importProject).mockResolvedValue({
        id: 'proj',
      });

      await importProject(zipFile);

      expect(exportImportApi.importProject).toHaveBeenCalledWith(zipFile);
    });
  });

  describe('Report API error handling', () => {
    it('should handle template fetch errors gracefully', async () => {
      // Templates are hardcoded, so should always succeed
      const templates = await fetchReportTemplates();
      expect(templates).toBeDefined();
    });

    it('should generate reports even without data', async () => {
      const report = await generateReport('proj-1', '1', 'pdf');

      expect(report.data).toBeDefined();
    });

    it('should handle export errors', async () => {
      vi.mocked(exportImportApi.exportProject).mockRejectedValue(new Error('Export failed'));

      await expect(exportProject('proj-1')).rejects.toThrow('Export failed');
    });

    it('should handle import errors', async () => {
      const mockFile = new File(['invalid'], 'bad.json');
      vi.mocked(exportImportApi.importProject).mockRejectedValue(new Error('Import failed'));

      await expect(importProject(mockFile)).rejects.toThrow('Import failed');
    });
  });

  describe('Report types and formats', () => {
    it('should have templates for all report types', async () => {
      const templates = await fetchReportTemplates();
      const types = templates.map((t) => t.type);

      expect(types).toContain('coverage');
      expect(types).toContain('traceability');
      expect(types).toContain('status');
      expect(types).toContain('progress');
    });

    it('should return correct number of templates', async () => {
      const templates = await fetchReportTemplates();

      expect(templates).toHaveLength(4);
    });

    it('should have valid descriptions for all templates', async () => {
      const templates = await fetchReportTemplates();

      templates.forEach((template) => {
        expect(template.description).toBeTruthy();
        expect(template.description.length).toBeGreaterThan(0);
      });
    });
  });
});
