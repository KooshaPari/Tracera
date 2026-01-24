import type { Async3RuleSet } from "../../oas-types";
import type { Async3Rule } from "../../visitors";
import { Assertions } from "../common/assertions";
import { InfoContact } from "../common/info-contact";
import { InfoLicenseStrict } from "../common/info-license-strict";
import { OperationOperationId } from "../common/operation-operationId";
import { Struct } from "../common/struct";
import { TagDescription } from "../common/tag-description";
import { TagsAlphabetical } from "../common/tags-alphabetical";
import { ChannelsKebabCase } from "./channels-kebab-case";
import { NoChannelTrailingSlash } from "./no-channel-trailing-slash";

export const rules: Async3RuleSet<"built-in"> = {
	// eslint-disable-next-line @typescript-eslint/ban-ts-comment
	//@ts-expect-error TODO: This is depricated property `spec` and should be removed in the future
	spec: Struct as Async3Rule,
	struct: Struct as Async3Rule,
	assertions: Assertions as Async3Rule,
	"info-contact": InfoContact as Async3Rule,
	"info-license-strict": InfoLicenseStrict as Async3Rule,
	"operation-operationId": OperationOperationId as Async3Rule,
	"channels-kebab-case": ChannelsKebabCase,
	"no-channel-trailing-slash": NoChannelTrailingSlash,
	"tag-description": TagDescription as Async3Rule,
	"tags-alphabetical": TagsAlphabetical as Async3Rule,
};

export const preprocessors = {};
