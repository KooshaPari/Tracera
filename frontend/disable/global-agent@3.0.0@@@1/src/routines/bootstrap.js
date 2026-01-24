// @flow

import {
  createGlobalProxyAgent,
} from '../factories';
import Logger from '../Logger';

import type {
  ProxyAgentConfigurationInputType,
} from '../types';

const log = Logger.child({
  namespace: 'bootstrap',
});

export default (configurationInput?: ProxyAgentConfigurationInputType): boolean => {
  if (global.GLOBAL_AGENT) {
    log.warn('found global.GLOBAL_AGENT; second attempt to bootstrap global-agent was ignored');

    return false;
  }

  global.GLOBAL_AGENT = createGlobalProxyAgent(configurationInput);

  return true;
};
