import type { TypeError } from "../compile/validate/dataType";
import type { ApplicatorKeywordError } from "./applicator";
import type { DiscriminatorError } from "./discriminator";
import type { FormatError } from "./format/format";
import type { UnevaluatedItemsError } from "./unevaluated/unevaluatedItems";
import type { UnevaluatedPropertiesError } from "./unevaluated/unevaluatedProperties";
import type { ValidationKeywordError } from "./validation";
import type { DependentRequiredError } from "./validation/dependentRequired";

export type DefinedError =
	| TypeError
	| ApplicatorKeywordError
	| ValidationKeywordError
	| FormatError
	| UnevaluatedPropertiesError
	| UnevaluatedItemsError
	| DependentRequiredError
	| DiscriminatorError;
