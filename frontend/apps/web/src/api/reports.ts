/* oxlint-disable import/no-named-export, promise/prefer-await-to-then */
// Reports API stub
import { exportImportApi } from './endpoints';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: 'coverage' | 'traceability' | 'status' | 'progress' | 'custom';
  format: 'pdf' | 'html' | 'json' | 'csv' | 'xlsx';
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

const reportTemplates: ReportTemplate[] = [
  {
    description: 'Test coverage report',
    format: 'pdf',
    id: '1',
    name: 'Coverage Report',
    type: 'coverage',
  },
  {
    description: 'Full traceability matrix',
    format: 'xlsx',
    id: '2',
    name: 'Traceability Matrix',
    type: 'traceability',
  },
  {
    description: 'Project status summary',
    format: 'html',
    id: '3',
    name: 'Status Report',
    type: 'status',
  },
  {
    description: 'Sprint progress report',
    format: 'pdf',
    id: '4',
    name: 'Progress Report',
    type: 'progress',
  },
];

const fetchReportTemplates = async (): Promise<ReportTemplate[]> => reportTemplates;

const generateReport = async (
  projectId: string,
  templateId: string,
  format: string,
): Promise<GeneratedReport> => ({
  data: {},
  format,
  generatedAt: new Date().toISOString(),
  id: `report-${Date.now()}`,
  projectId,
  templateId,
});

const { exportProject, importProject } = exportImportApi;

export {
  exportProject,
  fetchReportTemplates,
  generateReport,
  importProject,
  type GeneratedReport,
  type ReportTemplate,
};
