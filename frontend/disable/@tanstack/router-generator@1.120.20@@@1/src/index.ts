export type { Config } from "./config";
export { configSchema, getConfig, resolveConfigPath } from "./config";
export type { StartAPIRoutePathSegment } from "./generator";
export {
	CONSTANTS,
	generator,
	startAPIRouteSegmentsFromTSRFilePath,
} from "./generator";
