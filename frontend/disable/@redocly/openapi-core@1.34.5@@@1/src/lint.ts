import { rootRedoclyConfigSchema } from "@redocly/config";
import type { Config, StyleguideConfig } from "./config";
import { initRules } from "./config";
import {
	detectSpec,
	getMajorSpecVersion,
	getTypes,
	SpecVersion,
} from "./oas-types";
import type { Document, ResolvedRefMap } from "./resolve";
import {
	BaseResolver,
	makeDocumentFromString,
	resolveDocument,
} from "./resolve";
import { releaseAjvInstance } from "./rules/ajv";
import { Struct } from "./rules/common/struct";
import { NoUnresolvedRefs } from "./rules/no-unresolved-refs";
import type { NodeType } from "./types";
import { normalizeTypes } from "./types";
import { createConfigTypes } from "./types/redocly-yaml";
import type { CollectFn } from "./utils";
import type {
	Arazzo1Visitor,
	Async2Visitor,
	Async3Visitor,
	NestedVisitObject,
	Oas2Visitor,
	Oas3Visitor,
	Overlay1Visitor,
	RuleInstanceConfig,
} from "./visitors";
import { normalizeVisitors } from "./visitors";
import type { ProblemSeverity, WalkContext } from "./walk";
import { walkDocument } from "./walk";

export async function lint(opts: {
	ref: string;
	config: Config;
	externalRefResolver?: BaseResolver;
	collectSpecData?: CollectFn;
}) {
	const { ref, externalRefResolver = new BaseResolver(opts.config.resolve) } =
		opts;
	const document = (await externalRefResolver.resolveDocument(
		null,
		ref,
		true,
	)) as Document;
	opts.collectSpecData?.(document.parsed);

	return lintDocument({
		document,
		...opts,
		externalRefResolver,
		config: opts.config.styleguide,
	});
}

export async function lintFromString(opts: {
	source: string;
	absoluteRef?: string;
	config: Config;
	externalRefResolver?: BaseResolver;
}) {
	const {
		source,
		absoluteRef,
		externalRefResolver = new BaseResolver(opts.config.resolve),
	} = opts;
	const document = makeDocumentFromString(source, absoluteRef || "/");

	return lintDocument({
		document,
		...opts,
		externalRefResolver,
		config: opts.config.styleguide,
	});
}

export async function lintDocument(opts: {
	document: Document;
	config: StyleguideConfig;
	customTypes?: Record<string, NodeType>;
	externalRefResolver: BaseResolver;
}) {
	releaseAjvInstance(); // FIXME: preprocessors can modify nodes which are then cached to ajv-instance by absolute path

	const { document, customTypes, externalRefResolver, config } = opts;
	const specVersion = detectSpec(document.parsed);
	const specMajorVersion = getMajorSpecVersion(specVersion);
	const rules = config.getRulesForSpecVersion(specMajorVersion);
	const types = normalizeTypes(
		config.extendTypes(customTypes ?? getTypes(specVersion), specVersion),
		config,
	);

	const ctx: WalkContext = {
		problems: [],
		oasVersion: specVersion,
		visitorsData: {},
	};

	const preprocessors = initRules(rules, config, "preprocessors", specVersion);
	const regularRules = initRules(rules, config, "rules", specVersion);

	let resolvedRefMap = await resolveDocument({
		rootDocument: document,
		rootType: types.Root,
		externalRefResolver,
	});

	if (preprocessors.length > 0) {
		// Make additional pass to resolve refs defined in preprocessors.
		walkDocument({
			document,
			rootType: types.Root,
			normalizedVisitors: normalizeVisitors(preprocessors, types),
			resolvedRefMap,
			ctx,
		});
		resolvedRefMap = await resolveDocument({
			rootDocument: document,
			rootType: types.Root,
			externalRefResolver,
		});
	}

	const normalizedVisitors = normalizeVisitors(regularRules, types);

	walkDocument({
		document,
		rootType: types.Root,
		normalizedVisitors,
		resolvedRefMap,
		ctx,
	});
	return ctx.problems.map((problem) => config.addProblemToIgnore(problem));
}

export async function lintConfig(opts: {
	document: Document;
	config: Config;
	resolvedRefMap?: ResolvedRefMap;
	severity?: ProblemSeverity;
	externalRefResolver?: BaseResolver;
	externalConfigTypes?: Record<string, NodeType>;
}) {
	const {
		document,
		severity,
		externalRefResolver = new BaseResolver(),
		config,
	} = opts;

	const ctx: WalkContext = {
		problems: [],
		oasVersion: SpecVersion.OAS3_0,
		visitorsData: {},
	};

	const types = normalizeTypes(
		opts.externalConfigTypes ||
			createConfigTypes(rootRedoclyConfigSchema, config),
		{ doNotResolveExamples: config.styleguide.doNotResolveExamples },
	);

	const rules: (RuleInstanceConfig & {
		visitor: NestedVisitObject<
			unknown,
			| Oas3Visitor
			| Oas3Visitor[]
			| Oas2Visitor
			| Oas2Visitor[]
			| Async2Visitor
			| Async2Visitor[]
			| Async3Visitor
			| Async3Visitor[]
			| Arazzo1Visitor
			| Arazzo1Visitor[]
			| Overlay1Visitor
			| Overlay1Visitor[]
		>;
	})[] = [
		{
			severity: severity || "error",
			ruleId: "configuration spec",
			visitor: Struct({ severity: "error" }),
		},
		{
			severity: severity || "error",
			ruleId: "configuration no-unresolved-refs",
			visitor: NoUnresolvedRefs({ severity: "error" }),
		},
	];
	const normalizedVisitors = normalizeVisitors(rules, types);
	const resolvedRefMap =
		opts.resolvedRefMap ||
		(await resolveDocument({
			rootDocument: document,
			rootType: types.ConfigRoot,
			externalRefResolver,
		}));
	walkDocument({
		document,
		rootType: types.ConfigRoot,
		normalizedVisitors,
		resolvedRefMap,
		ctx,
	});

	return ctx.problems;
}
