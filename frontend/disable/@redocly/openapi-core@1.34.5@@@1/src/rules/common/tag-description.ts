import type { Oas2Rule, Oas3Rule } from "../../visitors";
import { validateDefinedAndNonEmpty } from "../utils";

export const TagDescription: Oas3Rule | Oas2Rule = () => {
	return {
		Tag(tag, ctx) {
			validateDefinedAndNonEmpty("description", tag, ctx);
		},
	};
};
