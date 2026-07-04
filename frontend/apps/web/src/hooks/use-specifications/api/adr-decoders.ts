import type { ADRStatus, ADROption } from '@tracertm/types';

import { asBoolean, asOptionalString, asOptionalStringArray, asString } from './primitive-decoders';
import { isApiRecord } from './record-decoders';

const asADROptions = (value: unknown): ADROption[] | undefined => {
  if (!Array.isArray(value)) {
    return;
  }
  const options: ADROption[] = [];
  for (const entry of value) {
    if (isApiRecord(entry)) {
      let chosenValue = entry['is_chosen'];
      if (chosenValue === undefined) {
        chosenValue = entry['isChosen'];
      }
      options.push({
        id: asString(entry['id']),
        title: asString(entry['title']),
        description: asString(entry['description']),
        pros: asOptionalStringArray(entry['pros']),
        cons: asOptionalStringArray(entry['cons']),
        isChosen: asBoolean(chosenValue),
      });
    }
  }
  return options;
};

const asADRStatus = (value: unknown): ADRStatus | undefined => {
  const text = asOptionalString(value);
  if (text === undefined) {
    return;
  }
  switch (text) {
    case 'proposed': {
      return text;
    }
    case 'accepted': {
      return text;
    }
    case 'deprecated': {
      return text;
    }
    case 'superseded': {
      return text;
    }
    case 'rejected': {
      return text;
    }
    default: {
      return undefined;
    }
  }
};

const asADRStatusRequired = (value: unknown): ADRStatus => {
  const status = asADRStatus(value);
  if (status !== undefined) {
    return status;
  }
  return 'proposed';
};

export { asADROptions, asADRStatusRequired };
