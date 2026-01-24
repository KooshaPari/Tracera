import { YargsFactory } from "./build/lib/yargs-factory.js";
// Bootstraps yargs for ESM:
import esmPlatformShim from "./lib/platform-shims/esm.mjs";

const Yargs = YargsFactory(esmPlatformShim);
export default Yargs;
