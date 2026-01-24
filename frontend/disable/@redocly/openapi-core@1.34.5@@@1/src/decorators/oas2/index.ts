import type { Oas2Decorator } from "../../visitors";
import { FilterIn } from "../common/filters/filter-in";
import { FilterOut } from "../common/filters/filter-out";
import { InfoDescriptionOverride } from "../common/info-description-override";
import { InfoOverride } from "../common/info-override";
import { OperationDescriptionOverride } from "../common/operation-description-override";
import { RegistryDependencies } from "../common/registry-dependencies";
import { RemoveXInternal } from "../common/remove-x-internal";
import { TagDescriptionOverride } from "../common/tag-description-override";

export const decorators = {
	"registry-dependencies": RegistryDependencies as Oas2Decorator,
	"operation-description-override":
		OperationDescriptionOverride as Oas2Decorator,
	"tag-description-override": TagDescriptionOverride as Oas2Decorator,
	"info-description-override": InfoDescriptionOverride as Oas2Decorator,
	"info-override": InfoOverride as Oas2Decorator,
	"remove-x-internal": RemoveXInternal as Oas2Decorator,
	"filter-in": FilterIn as Oas2Decorator,
	"filter-out": FilterOut as Oas2Decorator,
};
