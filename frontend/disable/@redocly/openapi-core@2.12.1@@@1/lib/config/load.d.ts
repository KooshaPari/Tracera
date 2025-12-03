import { Config } from './config.js';
import { BaseResolver, type ResolvedRefMap } from '../resolve.js';
import type { RawUniversalConfig } from './types.js';
export declare function loadConfig(options?: {
    configPath?: string;
    customExtends?: string[];
    externalRefResolver?: BaseResolver;
}): Promise<Config>;
export declare function findConfig(dir?: string): string | undefined;
type CreateConfigOptions = {
    configPath?: string;
    externalRefResolver?: BaseResolver;
    resolvedRefMap?: ResolvedRefMap;
};
export declare function createConfig(config?: string | RawUniversalConfig, { configPath, externalRefResolver }?: CreateConfigOptions): Promise<Config>;
export {};
//# sourceMappingURL=load.d.ts.map