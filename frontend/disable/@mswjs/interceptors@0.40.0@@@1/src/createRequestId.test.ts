import { expect, it } from "vitest";
import { REQUEST_ID_REGEXP } from "../test/helpers";
import { createRequestId } from "./createRequestId";

it("returns a request ID", () => {
	expect(createRequestId()).toMatch(REQUEST_ID_REGEXP);
});
