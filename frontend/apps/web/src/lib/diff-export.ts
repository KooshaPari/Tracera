/**
 * Diff Export Utilities
 *
 * Handles exporting version diffs in various formats:
 * - JSON: Structured diff data
 * - CSV: Spreadsheet-compatible format
 * - Markdown: Human-readable documentation format
 * - HTML: Styled report format
 */

import type { DiffExportOptions, DiffExportResult, DiffItem, VersionDiff } from '@tracertm/types';

/**
 * Export a version diff in the specified format
 */
export async function exportDiff(
  diff: VersionDiff,
  options: DiffExportOptions,
): Promise<DiffExportResult> {
  const timestamp = new Date().toISOString().split('T')[0];
  const baseFilename = `diff-v${diff.versionANumber}-v${diff.versionBNumber}-${timestamp}`;

  switch (options.format) {
    case 'json':
      return exportAsJSON(diff, baseFilename, options);
    case 'csv':
      return exportAsCSV(diff, baseFilename, options);
    case 'markdown':
      return exportAsMarkdown(diff, baseFilename, options);
    case 'html':
      return exportAsHTML(diff, baseFilename, options);
    default:
      throw new Error(`Unsupported export format: ${options.format}`);
  }
}

/**
 * Export as JSON
 */
function exportAsJSON(
  diff: VersionDiff,
  baseFilename: string,
  options: DiffExportOptions,
): DiffExportResult {
  const exportData = {
    metadata: {
      exportedAt: new Date().toISOString(),
      versionA: diff.versionA,
      versionB: diff.versionB,
      versionANumber: diff.versionANumber,
      versionBNumber: diff.versionBNumber,
    },
    statistics: diff.stats,
    added: diff.added.map((item) => serializeItem(item, options)),
    removed: diff.removed.map((item) => serializeItem(item, options)),
    modified: diff.modified.map((item) => serializeItem(item, options)),
  };

  const content = JSON.stringify(exportData, null, 2);

  return {
    filename: `${baseFilename}.json`,
    mimeType: 'application/json',
    content,
  };
}

/**
 * Export as CSV
 */
function exportAsCSV(
  diff: VersionDiff,
  baseFilename: string,
  options: DiffExportOptions,
): DiffExportResult {
  const rows: string[] = [];

  // Header
  rows.push('Item ID,Title,Type,Change Type,Significance,Field Count');

  // Added items
  diff.added.forEach((item) => {
    rows.push(
      escapeCSVField(item.itemId),
      escapeCSVField(item.title),
      escapeCSVField(item.type),
      'added',
      item.significance,
      '0',
    );
  });

  // Removed items
  diff.removed.forEach((item) => {
    rows.push(
      escapeCSVField(item.itemId),
      escapeCSVField(item.title),
      escapeCSVField(item.type),
      'removed',
      item.significance,
      '0',
    );
  });

  // Modified items
  diff.modified.forEach((item) => {
    rows.push(
      escapeCSVField(item.itemId),
      escapeCSVField(item.title),
      escapeCSVField(item.type),
      'modified',
      item.significance,
      String(item.fieldChanges?.length || 0),
    );

    // Add field changes if requested
    if (options.includeFieldChanges && item.fieldChanges) {
      item.fieldChanges.forEach((change) => {
        rows.push(
          `"${item.itemId}",,${escapeCSVField(change.field)},${change.changeType}`,
          `Old Value,${escapeCSVField(formatValue(change.oldValue))}`,
          `New Value,${escapeCSVField(formatValue(change.newValue))}`,
        );
      });
    }
  });

  const content = rows.join('\n');

  return {
    filename: `${baseFilename}.csv`,
    mimeType: 'text/csv',
    content,
  };
}

/**
 * Export as Markdown
 */
function exportAsMarkdown(
  diff: VersionDiff,
  baseFilename: string,
  options: DiffExportOptions,
): DiffExportResult {
  const lines: string[] = [];

  // Header
  lines.push('# Version Diff Report');
  lines.push('');
  lines.push(`**Version ${diff.versionANumber}** → **Version ${diff.versionBNumber}**`);
  lines.push('');
  lines.push(`Generated: ${new Date().toLocaleString()}`);
  lines.push('');

  // Statistics
  lines.push('## Statistics');
  lines.push('');
  lines.push('| Metric | Count |');
  lines.push('|--------|-------|');
  lines.push(`| Added | ${diff.stats.addedCount} |`);
  lines.push(`| Removed | ${diff.stats.removedCount} |`);
  lines.push(`| Modified | ${diff.stats.modifiedCount} |`);
  lines.push(`| Unchanged | ${diff.stats.unchangedCount} |`);
  lines.push(`| Total Changes | ${diff.stats.totalChanges} |`);
  lines.push('');

  // Added items
  if (diff.added.length > 0) {
    lines.push('## Added Items');
    lines.push('');
    diff.added.forEach((item) => {
      lines.push(`### ${item.title}`);
      lines.push('');
      lines.push(`- **ID**: ${item.itemId}`);
      lines.push(`- **Type**: ${item.type}`);
      lines.push(`- **Significance**: ${item.significance}`);
      lines.push('');
    });
  }

  // Removed items
  if (diff.removed.length > 0) {
    lines.push('## Removed Items');
    lines.push('');
    diff.removed.forEach((item) => {
      lines.push(`### ${item.title}`);
      lines.push('');
      lines.push(`- **ID**: ${item.itemId}`);
      lines.push(`- **Type**: ${item.type}`);
      lines.push(`- **Significance**: ${item.significance}`);
      lines.push('');
    });
  }

  // Modified items
  if (diff.modified.length > 0) {
    lines.push('## Modified Items');
    lines.push('');
    diff.modified.forEach((item) => {
      lines.push(`### ${item.title}`);
      lines.push('');
      lines.push(`- **ID**: ${item.itemId}`);
      lines.push(`- **Type**: ${item.type}`);
      lines.push(`- **Significance**: ${item.significance}`);

      if (options.includeFieldChanges && item.fieldChanges) {
        lines.push('');
        lines.push('#### Field Changes');
        lines.push('');
        item.fieldChanges.forEach((change) => {
          lines.push(`**${change.field}** (${change.changeType})`);
          lines.push(`- Old: \`${formatValue(change.oldValue)}\``);
          lines.push(`- New: \`${formatValue(change.newValue)}\``);
          lines.push('');
        });
      }
    });
  }

  const content = lines.join('\n');

  return {
    filename: `${baseFilename}.md`,
    mimeType: 'text/markdown',
    content,
  };
}

/**
 * Export as HTML
 */
function exportAsHTML(
  diff: VersionDiff,
  baseFilename: string,
  options: DiffExportOptions,
): DiffExportResult {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Version Diff Report</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f5f5;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 { color: #1a1a1a; margin-bottom: 10px; }
    h2 { color: #2c3e50; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
    h3 { color: #34495e; margin-top: 20px; }
    .header-info {
      background: #ecf0f1;
      padding: 15px;
      border-radius: 4px;
      margin-bottom: 20px;
      font-size: 14px;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }
    .stat-card {
      padding: 15px;
      border-radius: 4px;
      text-align: center;
    }
    .stat-added { background: #d4edda; color: #155724; }
    .stat-removed { background: #f8d7da; color: #721c24; }
    .stat-modified { background: #cce5ff; color: #004085; }
    .stat-value { font-size: 24px; font-weight: bold; }
    .stat-label { font-size: 12px; margin-top: 5px; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
    }
    th {
      background: #34495e;
      color: white;
      padding: 12px;
      text-align: left;
      font-weight: 600;
    }
    td {
      padding: 10px 12px;
      border-bottom: 1px solid #ecf0f1;
    }
    tr:hover { background: #f9f9f9; }
    .change-type {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 3px;
      font-size: 12px;
      font-weight: 600;
    }
    .change-added { background: #d4edda; color: #155724; }
    .change-removed { background: #f8d7da; color: #721c24; }
    .change-modified { background: #cce5ff; color: #004085; }
    .significance {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 600;
    }
    .sig-minor { background: #e2e3e5; color: #383d41; }
    .sig-moderate { background: #fff3cd; color: #856404; }
    .sig-major { background: #ffe0b2; color: #bf5f3f; }
    .sig-breaking { background: #ffcdd2; color: #c62828; }
    .field-change {
      margin: 10px 0;
      padding: 10px;
      background: #f5f5f5;
      border-left: 4px solid #3498db;
      border-radius: 4px;
    }
    .field-old { background: #ffebee; border-left-color: #e74c3c; }
    .field-new { background: #e8f5e9; border-left-color: #27ae60; }
    .value-box {
      background: white;
      border: 1px solid #ddd;
      padding: 10px;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      word-break: break-all;
      max-height: 200px;
      overflow-y: auto;
    }
    .footer {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #ecf0f1;
      font-size: 12px;
      color: #7f8c8d;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Version Diff Report</h1>
    <div class="header-info">
      <strong>Version ${diff.versionANumber}</strong> → <strong>Version ${diff.versionBNumber}</strong><br>
      Generated: ${new Date().toLocaleString()}
    </div>

    <h2>Statistics</h2>
    <div class="stats">
      <div class="stat-card stat-added">
        <div class="stat-value">${diff.stats.addedCount}</div>
        <div class="stat-label">Added</div>
      </div>
      <div class="stat-card stat-removed">
        <div class="stat-value">${diff.stats.removedCount}</div>
        <div class="stat-label">Removed</div>
      </div>
      <div class="stat-card stat-modified">
        <div class="stat-value">${diff.stats.modifiedCount}</div>
        <div class="stat-label">Modified</div>
      </div>
    </div>

    ${
      diff.added.length > 0
        ? `
      <h2>Added Items (${diff.added.length})</h2>
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>ID</th>
            <th>Type</th>
            <th>Significance</th>
          </tr>
        </thead>
        <tbody>
          ${diff.added
            .map(
              (item) => `
            <tr>
              <td>${escapeHtml(item.title)}</td>
              <td><code>${item.itemId}</code></td>
              <td>${item.type}</td>
              <td><span class="significance sig-${item.significance}">${item.significance}</span></td>
            </tr>
          `,
            )
            .join('')}
        </tbody>
      </table>
    `
        : ''
    }

    ${
      diff.removed.length > 0
        ? `
      <h2>Removed Items (${diff.removed.length})</h2>
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>ID</th>
            <th>Type</th>
            <th>Significance</th>
          </tr>
        </thead>
        <tbody>
          ${diff.removed
            .map(
              (item) => `
            <tr>
              <td>${escapeHtml(item.title)}</td>
              <td><code>${item.itemId}</code></td>
              <td>${item.type}</td>
              <td><span class="significance sig-${item.significance}">${item.significance}</span></td>
            </tr>
          `,
            )
            .join('')}
        </tbody>
      </table>
    `
        : ''
    }

    ${
      diff.modified.length > 0
        ? `
      <h2>Modified Items (${diff.modified.length})</h2>
      ${diff.modified
        .map(
          (item) => `
        <div style="margin-bottom: 30px; border: 1px solid #ecf0f1; padding: 20px; border-radius: 4px;">
          <h3>${escapeHtml(item.title)}</h3>
          <p>
            <strong>ID:</strong> <code>${item.itemId}</code><br>
            <strong>Type:</strong> ${item.type}<br>
            <strong>Significance:</strong> <span class="significance sig-${item.significance}">${item.significance}</span>
          </p>
          ${
            options.includeFieldChanges && item.fieldChanges
              ? `
            <h4>Field Changes</h4>
            ${item.fieldChanges
              .map(
                (change) => `
              <div class="field-change">
                <strong>${change.field}</strong>
                <div class="field-old" style="margin-top: 5px;">
                  <div><strong>Old Value:</strong></div>
                  <div class="value-box">${escapeHtml(formatValue(change.oldValue))}</div>
                </div>
                <div class="field-new" style="margin-top: 5px;">
                  <div><strong>New Value:</strong></div>
                  <div class="value-box">${escapeHtml(formatValue(change.newValue))}</div>
                </div>
              </div>
            `,
              )
              .join('')}
          `
              : ''
          }
        </div>
      `,
        )
        .join('')}
    `
        : ''
    }

    <div class="footer">
      <p>This diff report was automatically generated by TraceRTM.</p>
    </div>
  </div>
</body>
</html>
  `.trim();

  return {
    filename: `${baseFilename}.html`,
    mimeType: 'text/html',
    content: html,
  };
}

// Helper functions
function serializeItem(item: DiffItem, options: DiffExportOptions): unknown {
  const serialized: Record<string, unknown> = {
    itemId: item.itemId,
    title: item.title,
    type: item.type,
    changeType: item.changeType,
    significance: item.significance,
  };

  if (options.includeFieldChanges && item.fieldChanges) {
    serialized['fieldChanges'] = item.fieldChanges.map((change) => ({
      field: change.field,
      changeType: change.changeType,
      oldValue: change.oldValue,
      newValue: change.newValue,
    }));
  }

  return serialized;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return 'null';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  return String(value);
}

function escapeCSVField(value: unknown): string {
  const str = formatValue(value);
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

export type { DiffExportResult };
