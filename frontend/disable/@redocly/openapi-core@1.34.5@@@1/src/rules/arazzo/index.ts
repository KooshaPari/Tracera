import type { Arazzo1RuleSet } from "../../oas-types";
import type { Arazzo1Rule } from "../../visitors";
import { SourceDescriptionType } from "../arazzo/sourceDescription-type";
import { Assertions } from "../common/assertions";
import { Struct } from "../common/struct";
import { NoCriteriaXpath } from "../respect/no-criteria-xpath";
import { RespectSupportedVersions } from "../respect/respect-supported-versions";
import { CriteriaUnique } from "./criteria-unique";
import { ParametersUnique } from "./parameters-unique";
import { RequestBodyReplacementsUnique } from "./requestBody-replacements-unique";
import { SourceDescriptionsNameUnique } from "./sourceDescriptions-name-unique";
import { SourceDescriptionsNotEmpty } from "./sourceDescriptions-not-empty";
import { StepOnFailureUnique } from "./step-onFailure-unique";
import { StepOnSuccessUnique } from "./step-onSuccess-unique";
import { StepIdUnique } from "./stepId-unique";
import { WorkflowDependsOn } from "./workflow-dependsOn";
import { WorkflowIdUnique } from "./workflowId-unique";

export const rules: Arazzo1RuleSet<"built-in"> = {
	struct: Struct as Arazzo1Rule,
	assertions: Assertions as Arazzo1Rule,
	"sourceDescription-type": SourceDescriptionType,
	"respect-supported-versions": RespectSupportedVersions,
	"workflowId-unique": WorkflowIdUnique,
	"stepId-unique": StepIdUnique,
	"sourceDescription-name-unique": SourceDescriptionsNameUnique,
	"sourceDescriptions-not-empty": SourceDescriptionsNotEmpty,
	"workflow-dependsOn": WorkflowDependsOn,
	"parameters-unique": ParametersUnique,
	"step-onSuccess-unique": StepOnSuccessUnique,
	"step-onFailure-unique": StepOnFailureUnique,
	"requestBody-replacements-unique": RequestBodyReplacementsUnique,
	"no-criteria-xpath": NoCriteriaXpath,
	"criteria-unique": CriteriaUnique,
};

export const preprocessors = {};
