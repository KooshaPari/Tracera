import type { Oas2Rule, Oas3Rule } from "../../visitors";
import { validateDefinedAndNonEmpty } from "../utils";

export const InfoLicenseUrl: Oas3Rule | Oas2Rule = () => {
	return {
		License(license, ctx) {
			validateDefinedAndNonEmpty("url", license, ctx);
		},
	};
};
