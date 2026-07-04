import type {
  Contract,
  ContractCondition,
  ContractStatus,
  ContractTransition,
  ContractType,
} from '@tracertm/types';

import {
  asBoolean,
  asNumber,
  asOptionalString,
  asOptionalStringArray,
  asString,
} from './primitive-decoders';
import { isApiRecord } from './record-decoders';

const asContractConditionResult = (value: unknown): ContractCondition['lastVerifiedResult'] => {
  const text = asOptionalString(value);
  switch (text) {
    case 'pass': {
      return text;
    }
    case 'fail': {
      return text;
    }
    case 'skip': {
      return text;
    }
    default: {
      return undefined;
    }
  }
};

const asContractConditions = (value: unknown): ContractCondition[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  const conditions: ContractCondition[] = [];
  for (const entry of value) {
    if (isApiRecord(entry)) {
      let requiredValue = entry['is_required'];
      if (requiredValue === undefined) {
        requiredValue = entry['isRequired'];
      }
      let lastResultValue = entry['last_verified_result'];
      if (lastResultValue === undefined) {
        lastResultValue = entry['lastVerifiedResult'];
      }
      conditions.push({
        id: asString(entry['id']),
        description: asString(entry['description']),
        expression: asOptionalString(entry['expression']),
        isRequired: asBoolean(requiredValue),
        lastVerifiedResult: asContractConditionResult(lastResultValue),
      });
    }
  }
  return conditions;
};

const asContractTransitions = (value: unknown): ContractTransition[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const transitions: ContractTransition[] = [];
  for (const entry of value) {
    if (isApiRecord(entry)) {
      let fromStateValue = entry['from_state'];
      if (fromStateValue === undefined) {
        fromStateValue = entry['fromState'];
      }
      let toStateValue = entry['to_state'];
      if (toStateValue === undefined) {
        toStateValue = entry['toState'];
      }
      transitions.push({
        id: asString(entry['id']),
        fromState: asString(fromStateValue),
        toState: asString(toStateValue),
        trigger: asString(entry['trigger']),
        guards: asOptionalStringArray(entry['guards']),
        actions: asOptionalStringArray(entry['actions']),
      });
    }
  }
  return transitions;
};

const asSpecLanguage = (value: unknown): Contract['specLanguage'] => {
  const text = asOptionalString(value);
  if (text === 'typescript' || text === 'python' || text === 'gherkin') {
    return text;
  }
  return undefined;
};

const asContractType = (value: unknown): ContractType => {
  const text = asString(value);
  switch (text) {
    case 'api': {
      return text;
    }
    case 'function': {
      return text;
    }
    case 'invariant': {
      return text;
    }
    case 'data': {
      return text;
    }
    case 'integration': {
      return text;
    }
    default: {
      return 'api';
    }
  }
};

const asContractStatus = (value: unknown): ContractStatus => {
  const text = asString(value);
  switch (text) {
    case 'draft': {
      return text;
    }
    case 'active': {
      return text;
    }
    case 'verified': {
      return text;
    }
    case 'violated': {
      return text;
    }
    case 'deprecated': {
      return text;
    }
    default: {
      return 'draft';
    }
  }
};

const asVerificationStatus = (value: unknown): 'pass' | 'fail' | 'error' => {
  const text = asString(value);
  switch (text) {
    case 'pass': {
      return text;
    }
    case 'fail': {
      return text;
    }
    case 'error': {
      return text;
    }
    default: {
      return 'error';
    }
  }
};

function buildVerificationResult(value: unknown): Contract['verificationResult'] {
  if (!isApiRecord(value)) {
    return;
  }

  let passedValue = value['passed_conditions'];
  if (passedValue === undefined) {
    passedValue = value['passedConditions'];
  }

  let failedValue = value['failed_conditions'];
  if (failedValue === undefined) {
    failedValue = value['failedConditions'];
  }

  const detailsValue = value['details'];

  return {
    status: asVerificationStatus(value['status']),
    passedConditions: asNumber(passedValue),
    failedConditions: asNumber(failedValue),
    details: asOptionalString(detailsValue),
  };
}

export {
  asContractConditions,
  asContractStatus,
  asContractTransitions,
  asContractType,
  asSpecLanguage,
  asVerificationStatus,
  buildVerificationResult,
};
