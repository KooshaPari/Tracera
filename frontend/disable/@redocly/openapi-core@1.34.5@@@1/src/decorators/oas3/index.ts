import type { Oas3Decorator } from "../../visitors";
import { FilterIn } from "../common/filters/filter-in";
import { FilterOut } from "../common/filters/filter-out";
import { InfoDescriptionOverride } from "../common/info-description-override";
import { InfoOverride } from "../common/info-override";
import { MediaTypeExamplesOverride } from "../common/media-type-examples-override";
import { OperationDescriptionOverride } from "../common/operation-description-override";
import { RegistryDependencies } from "../common/registry-dependencies";
import { RemoveXInternal } from "../common/remove-x-internal";
import { TagDescriptionOverride } from "../common/tag-description-override";

export const decorators = {
	"registry-dependencies": RegistryDependencies as Oas3Decorator,
	"operation-description-override":
		OperationDescriptionOverride as Oas3Decorator,
	"tag-description-override": TagDescriptionOverride as Oas3Decorator,
	"info-description-override": InfoDescriptionOverride as Oas3Decorator,
	"info-override": InfoOverride as Oas3Decorator,
	"remove-x-internal": RemoveXInternal as Oas3Decorator,
	"filter-in": FilterIn as Oas3Decorator,
	"filter-out": FilterOut as Oas3Decorator,
	"media-type-examples-override": MediaTypeExamplesOverride as Oas3Decorator,
};
