import type { FeatureStatus } from '@tracertm/types';

import { asString } from './primitive-decoders';

const asFeatureStatus = (value: unknown): FeatureStatus => {
  const text = asString(value);
  switch (text) {
    case 'draft': {
      return text;
    }
    case 'active': {
      return text;
    }
    case 'deprecated': {
      return text;
    }
    case 'archived': {
      return text;
    }
    default: {
      return 'draft';
    }
  }
};

export { asFeatureStatus };
