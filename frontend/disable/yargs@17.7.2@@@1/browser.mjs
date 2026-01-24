// Bootstrap yargs for browser:

import { YargsFactory } from "./build/lib/yargs-factory.js";
import browserPlatformShim from "./lib/platform-shims/browser.mjs";

const Yargs = YargsFactory(browserPlatformShim);

export default Yargs;
