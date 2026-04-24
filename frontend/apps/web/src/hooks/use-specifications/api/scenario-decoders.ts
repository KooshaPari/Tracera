import type { Scenario, ScenarioStatus, ScenarioStep } from '@tracertm/types';

import { asNumber, asOptionalString, asString, asStringArray } from './primitive-decoders';
import { isApiRecord } from './record-decoders';

const asStringTable = (value: unknown): string[][] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const rows: string[][] = [];
  for (const row of value) {
    if (Array.isArray(row)) {
      const rowValues: string[] = [];
      for (const cell of row) {
        if (typeof cell === 'string') {
          rowValues.push(cell);
        }
      }
      rows.push(rowValues);
    }
  }
  return rows;
};

const asScenarioStepKeyword = (value: unknown): ScenarioStep['keyword'] => {
  const text = asString(value);
  switch (text) {
    case 'Given': {
      return text;
    }
    case 'When': {
      return text;
    }
    case 'Then': {
      return text;
    }
    case 'And': {
      return text;
    }
    case 'But': {
      return text;
    }
    default: {
      return 'Given';
    }
  }
};

const asScenarioSteps = (value: unknown): ScenarioStep[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  const steps: ScenarioStep[] = [];
  for (const entry of value) {
    if (isApiRecord(entry) && typeof entry['text'] === 'string') {
      let stepNumberValue = entry['step_number'];
      if (stepNumberValue === undefined) {
        stepNumberValue = entry['stepNumber'];
      }
      let dataTableValue = entry['data_table'];
      if (dataTableValue === undefined) {
        dataTableValue = entry['dataTable'];
      }
      steps.push({
        stepNumber: asNumber(stepNumberValue),
        keyword: asScenarioStepKeyword(entry['keyword']),
        text: asString(entry['text']),
        dataTable: asStringTable(dataTableValue),
        docString: asOptionalString(entry['doc_string']),
        stepDefinitionId: asOptionalString(entry['step_definition_id']),
      });
    }
  }
  return steps;
};

const asOptionalScenarioSteps = (value: unknown): ScenarioStep[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  return asScenarioSteps(value);
};

const asExamples = (value: unknown): Record<string, string[]> | undefined => {
  if (!isApiRecord(value)) {
    return;
  }
  const result: Record<string, string[]> = {};
  for (const [key, entry] of Object.entries(value)) {
    if (Array.isArray(entry)) {
      result[key] = asStringArray(entry);
    }
  }
  return result;
};

const asScenarioStatus = (value: unknown): ScenarioStatus => {
  const text = asString(value);
  switch (text) {
    case 'draft': {
      return text;
    }
    case 'pending': {
      return text;
    }
    case 'passed': {
      return 'passing';
    }
    case 'failed': {
      return 'failing';
    }
    case 'passing': {
      return text;
    }
    case 'failing': {
      return text;
    }
    case 'skipped': {
      return text;
    }
    default: {
      return 'draft';
    }
  }
};

const asRunResult = (value: unknown): Scenario['lastRunResult'] => {
  const text = asOptionalString(value);
  switch (text) {
    case 'pass': {
      return text;
    }
    case 'fail': {
      return text;
    }
    case 'pending': {
      return text;
    }
    case 'error': {
      return text;
    }
    default: {
      return undefined;
    }
  }
};

export { asExamples, asOptionalScenarioSteps, asRunResult, asScenarioStatus, asScenarioSteps };
