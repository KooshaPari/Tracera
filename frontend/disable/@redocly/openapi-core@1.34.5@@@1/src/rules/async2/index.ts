import type { Async2RuleSet } from "../../oas-types";
import type { Async2Rule } from "../../visitors";
import { Assertions } from "../common/assertions";
import { InfoContact } from "../common/info-contact";
import { InfoLicenseStrict } from "../common/info-license-strict";
import { OperationOperationId } from "../common/operation-operationId";
import { Struct } from "../common/struct";
import { TagDescription } from "../common/tag-description";
import { TagsAlphabetical } from "../common/tags-alphabetical";
import { ChannelsKebabCase } from "./channels-kebab-case";
import { NoChannelTrailingSlash } from "./no-channel-trailing-slash";

export const rules: Async2RuleSet<"built-in"> = {
	// eslint-disable-next-line @typescript-eslint/ban-ts-comment
	//@ts-expect-error TODO: This is depricated property `spec` and should be removed in the future
	spec: Struct as Async2Rule,
	struct: Struct as Async2Rule,
	assertions: Assertions as Async2Rule,
	"info-contact": InfoContact as Async2Rule,
	"info-license-strict": InfoLicenseStrict as Async2Rule,
	"operation-operationId": OperationOperationId as Async2Rule,
	"channels-kebab-case": ChannelsKebabCase,
	"no-channel-trailing-slash": NoChannelTrailingSlash,
	"tag-description": TagDescription as Async2Rule,
	"tags-alphabetical": TagsAlphabetical as Async2Rule,
};

export const preprocessors = {};
