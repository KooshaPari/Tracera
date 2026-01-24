import type { Oas2Rule, Oas3Rule } from "../../visitors";
import type { UserContext } from "../../walk";
import { validateResponseCodes } from "../utils";

export const Operation4xxResponse: Oas3Rule | Oas2Rule = ({
	validateWebhooks,
}) => {
	return {
		Paths: {
			Responses(responses: Record<string, object>, { report }: UserContext) {
				const codes = Object.keys(responses || {});

				validateResponseCodes(codes, "4XX", { report } as UserContext);
			},
		},
		WebhooksMap: {
			Responses(responses: Record<string, object>, { report }: UserContext) {
				if (!validateWebhooks) return;

				const codes = Object.keys(responses || {});

				validateResponseCodes(codes, "4XX", { report } as UserContext);
			},
		},
	};
};
