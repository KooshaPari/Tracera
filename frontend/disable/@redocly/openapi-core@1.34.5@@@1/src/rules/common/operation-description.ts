import type { Oas3Operation } from "../../typings/openapi";
import type { Oas2Operation } from "../../typings/swagger";
import type { Oas2Rule, Oas3Rule } from "../../visitors";
import type { UserContext } from "../../walk";
import { validateDefinedAndNonEmpty } from "../utils";

export const OperationDescription: Oas3Rule | Oas2Rule = () => {
	return {
		Operation(operation: Oas2Operation | Oas3Operation, ctx: UserContext) {
			validateDefinedAndNonEmpty("description", operation, ctx);
		},
	};
};
