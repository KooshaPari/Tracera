import { type expect } from "@jest/globals";
import { type TestingLibraryMatchers } from "./matchers";
declare module "@jest/expect" {
	export interface Matchers<R extends void | Promise<void>>
		extends TestingLibraryMatchers<
			ReturnType<typeof expect.stringContaining>,
			R
		> {}
}
