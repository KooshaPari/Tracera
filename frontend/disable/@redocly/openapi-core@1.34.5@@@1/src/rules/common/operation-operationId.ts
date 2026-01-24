import type { Oas3Operation } from "../../typings/openapi";
import type { Oas2Operation } from "../../typings/swagger";
import type { Oas2Rule, Oas3Rule } from "../../visitors";
import type { UserContext } from "../../walk";
import { validateDefinedAndNonEmpty } from "../utils";

export const OperationOperationId: Oas3Rule | Oas2Rule = () => {
	return {
		Root: {
			PathItem: {
				Operation(operation: Oas2Operation | Oas3Operation, ctx: UserContext) {
					validateDefinedAndNonEmpty("operationId", operation, ctx);
				},
			},
		},
	};
};
