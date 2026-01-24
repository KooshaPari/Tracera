/**
 * GraphQL.js provides a reference implementation for the GraphQL specification
 * but is also a useful utility for operating on GraphQL files and building
 * sophisticated tools.
 *
 * This primary module exports a general purpose function for fulfilling all
 * steps of the GraphQL specification in a single operation, but also includes
 * utilities for every part of the GraphQL specification:
 *
 *   - Parsing the GraphQL language.
 *   - Building a GraphQL type schema.
 *   - Validating a GraphQL request against a type schema.
 *   - Executing a GraphQL request against a type schema.
 *
 * This also includes utility functions for operating on GraphQL types and
 * GraphQL documents to facilitate building tools.
 *
 * You may also import from each sub-directory directly. For example, the
 * following two import statements are equivalent:
 *
 * ```ts
 * import { parse } from 'graphql';
 * import { parse } from 'graphql/language';
 * ```
 *
 * @packageDocumentation
 */
// The GraphQL.js version info.

// Create, format, and print GraphQL errors.
export {
	formatError,
	GraphQLError,
	locatedError,
	printError,
	syntaxError,
} from "./error/index.mjs";
// Execute GraphQL queries.
export {
	createSourceEventStream,
	defaultFieldResolver,
	defaultTypeResolver,
	execute,
	executeSync,
	getArgumentValues,
	getDirectiveValues,
	getVariableValues,
	responsePathAsArray,
	subscribe,
} from "./execution/index.mjs";
export { graphql, graphqlSync } from "./graphql.mjs"; // Create and operate on GraphQL type definitions and schema.
// Parse and operate on GraphQL language source files.
export {
	BREAK,
	DirectiveLocation, // Predicates
	getEnterLeaveForKind,
	getLocation, // Print source location.
	getVisitFn,
	isConstValueNode,
	isDefinitionNode,
	isExecutableDefinitionNode,
	isSchemaCoordinateNode,
	isSelectionNode,
	isTypeDefinitionNode,
	isTypeExtensionNode,
	isTypeNode,
	isTypeSystemDefinitionNode,
	isTypeSystemExtensionNode,
	isValueNode,
	Kind,
	Lexer,
	Location,
	OperationTypeNode,
	parse,
	parseConstValue,
	parseSchemaCoordinate, // Print
	parseType,
	parseValue,
	print, // Visit
	printLocation,
	printSourceLocation, // Lex
	Source,
	Token,
	TokenKind, // Parse
	visit,
	visitInParallel,
} from "./language/index.mjs";
export {
	__Directive,
	__DirectiveLocation,
	__EnumValue,
	__Field,
	__InputValue,
	__Schema,
	__Type,
	__TypeKind, // Meta-field definitions.
	assertAbstractType,
	assertCompositeType,
	assertDirective,
	assertEnumType,
	assertEnumValueName,
	assertInputObjectType,
	assertInputType,
	assertInterfaceType,
	assertLeafType,
	assertListType,
	assertName,
	assertNamedType, // Un-modifiers
	assertNonNullType,
	assertNullableType,
	assertObjectType,
	assertOutputType,
	assertScalarType,
	assertSchema,
	assertType,
	assertUnionType,
	assertValidSchema, // Upholds the spec rules about naming.
	assertWrappingType,
	DEFAULT_DEPRECATION_REASON, // GraphQL Types for introspection.
	GRAPHQL_MAX_INT,
	GRAPHQL_MIN_INT, // Built-in Directives defined by the Spec
	GraphQLBoolean,
	GraphQLDeprecatedDirective,
	GraphQLDirective,
	GraphQLEnumType,
	GraphQLFloat,
	GraphQLID, // Int boundaries constants
	GraphQLIncludeDirective,
	GraphQLInputObjectType,
	GraphQLInt,
	GraphQLInterfaceType,
	GraphQLList,
	GraphQLNonNull, // Standard GraphQL Scalars
	GraphQLObjectType,
	GraphQLOneOfDirective, // "Enum" of Type Kinds
	GraphQLScalarType,
	GraphQLSchema,
	GraphQLSkipDirective,
	GraphQLSpecifiedByDirective,
	GraphQLString,
	GraphQLUnionType,
	getNamedType, // Validate GraphQL schema.
	getNullableType,
	introspectionTypes,
	isAbstractType,
	isCompositeType,
	isDirective,
	isEnumType,
	isInputObjectType,
	isInputType,
	isInterfaceType,
	isIntrospectionType,
	isLeafType,
	isListType,
	isNamedType,
	isNonNullType,
	isNullableType,
	isObjectType,
	isOutputType,
	isRequiredArgument,
	isRequiredInputField,
	isScalarType,
	isSchema,
	isSpecifiedDirective, // Assertions
	isSpecifiedScalarType,
	isType,
	isUnionType,
	isWrappingType,
	resolveObjMapThunk,
	resolveReadonlyArrayThunk, // Definitions
	SchemaMetaFieldDef,
	specifiedDirectives,
	specifiedScalarTypes,
	TypeKind, // Constant Deprecation Reason
	TypeMetaFieldDef,
	TypeNameMetaFieldDef, // Predicates
	validateSchema,
} from "./type/index.mjs";
// Utilities for operating on GraphQL type schema and parsed sources.
export {
	assertValidName, // Determine if a string is a valid GraphQL name.
	astFromValue, // A helper to use within recursive-descent visitors which need to be aware of the GraphQL type system.
	BreakingChangeType,
	buildASTSchema, // Build a GraphQLSchema from a GraphQL schema language document.
	buildClientSchema, // Build a GraphQLSchema from a parsed GraphQL Schema language AST.
	buildSchema, // Extends an existing GraphQLSchema from a parsed GraphQL Schema language AST.
	coerceInputValue, // Concatenates multiple AST together.
	concatAST, // Separates an AST into an AST per Operation.
	DangerousChangeType,
	doTypesOverlap, // Asserts a string is a valid GraphQL name.
	extendSchema, // Sort a GraphQLSchema.
	findBreakingChanges,
	findDangerousChanges, // Schema Coordinates
	// Produce the GraphQL query recommended for a full schema introspection.
	// Accepts optional IntrospectionOptions.
	getIntrospectionQuery, // Gets the target Operation from a Document.
	getOperationAST, // Gets the Type for the target Operation AST.
	getOperationRootType, // Convert a GraphQLSchema to an IntrospectionQuery.
	introspectionFromSchema, // Build a GraphQLSchema from an introspection result.
	isEqualType,
	isTypeSubTypeOf,
	isValidNameError, // Compares two GraphQLSchemas and detects breaking changes.
	lexicographicSortSchema, // Print a GraphQLSchema to GraphQL Schema language.
	printIntrospectionSchema, // Create a GraphQLType from a GraphQL language AST.
	printSchema, // Print a GraphQLType to GraphQL Schema language.
	printType, // Prints the built-in introspection schema in the Schema Language format.
	resolveASTSchemaCoordinate,
	resolveSchemaCoordinate,
	separateOperations, // Strips characters that are not significant to the validity or execution of a GraphQL document.
	stripIgnoredCharacters, // Comparators for types
	TypeInfo,
	typeFromAST, // Create a JavaScript value from a GraphQL language AST with a Type.
	valueFromAST, // Create a JavaScript value from a GraphQL language AST without a Type.
	valueFromASTUntyped, // Create a GraphQL language AST from a JavaScript value.
	visitWithTypeInfo, // Coerces a JavaScript value to a GraphQL type, or produces errors.
} from "./utilities/index.mjs";
// Validate GraphQL documents.
export {
	ExecutableDefinitionsRule,
	FieldsOnCorrectTypeRule,
	FragmentsOnCompositeTypesRule,
	KnownArgumentNamesRule,
	KnownDirectivesRule,
	KnownFragmentNamesRule,
	KnownTypeNamesRule,
	LoneAnonymousOperationRule,
	LoneSchemaDefinitionRule,
	MaxIntrospectionDepthRule, // SDL-specific validation rules
	NoDeprecatedCustomRule,
	NoFragmentCyclesRule,
	NoSchemaIntrospectionCustomRule,
	NoUndefinedVariablesRule,
	NoUnusedFragmentsRule,
	NoUnusedVariablesRule,
	OverlappingFieldsCanBeMergedRule,
	PossibleFragmentSpreadsRule,
	PossibleTypeExtensionsRule, // Custom validation rules
	ProvidedRequiredArgumentsRule,
	recommendedRules, // Individual validation rules.
	ScalarLeafsRule,
	SingleFieldSubscriptionsRule,
	specifiedRules,
	UniqueArgumentDefinitionNamesRule,
	UniqueArgumentNamesRule,
	UniqueDirectiveNamesRule,
	UniqueDirectivesPerLocationRule,
	UniqueEnumValueNamesRule,
	UniqueFieldDefinitionNamesRule,
	UniqueFragmentNamesRule,
	UniqueInputFieldNamesRule,
	UniqueOperationNamesRule,
	UniqueOperationTypesRule,
	UniqueTypeNamesRule,
	UniqueVariableNamesRule,
	ValidationContext, // All validation rules in the GraphQL Specification.
	ValuesOfCorrectTypeRule,
	VariablesAreInputTypesRule,
	VariablesInAllowedPositionRule,
	validate,
} from "./validation/index.mjs";
export { version, versionInfo } from "./version.mjs"; // The primary entry point into fulfilling a GraphQL request.
