/* oxlint-disable import/no-named-export, promise/prefer-await-to-then */
// Reports API stub
import { exportImportApi } from "./endpoints";
import { ApiError } from "./client-errors";

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: "coverage" | "traceability" | "status" | "progress" | "custom";
  format: "pdf" | "html" | "json" | "csv" | "xlsx";
}

interface GeneratedReport {
  id: string;
  templateId: string;
  projectId: string;
  generatedAt: string;
  format: string;
  url?: string;
  data?: Record<string, unknown>;
}

const fetchReportTemplates = async (): Promise<ReportTemplate[]> => {
  throw new ApiError(501, "Not implemented yet", {
    error: "not_implemented",
    route: "/api/v1/reports/templates",
    since: "2026-10-16",
  });
};

const generateReport = async (
  _projectId: string,
  _templateId: string,
  _format: string,
): Promise<GeneratedReport> => {
  throw new ApiError(501, "Not implemented yet", {
    error: "not_implemented",
    route: "/api/v1/reports",
    since: "2026-10-16",
  });
};

const { exportProject, importProject } = exportImportApi;

export {
  exportProject,
  fetchReportTemplates,
  generateReport,
  importProject,
  type GeneratedReport,
  type ReportTemplate,
};
