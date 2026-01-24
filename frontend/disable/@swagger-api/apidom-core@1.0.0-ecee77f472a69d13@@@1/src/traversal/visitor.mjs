import {
	visit as astVisit,
	BREAK,
	cloneNode as cloneNodeDefault,
	mergeAllVisitors,
} from "@swagger-api/apidom-ast";
import { pipe, F as stubFalse } from "ramda";
import { isString } from "ramda-adjunct";
import { cloneShallow } from "../clone/index.mjs";
import {
	isArrayElement,
	isBooleanElement,
	isElement,
	isLinkElement,
	isMemberElement,
	isNullElement,
	isNumberElement,
	isObjectElement,
	isRefElement,
	isStringElement,
} from "../predicates/index.mjs";
export { BREAK, mergeAllVisitors };

/**
 * @public
 */
export const getNodeType = (element) => {
	/*
	 * We're translating every possible higher element type to primitive minim type here.
	 * We're using polymorphism to recognize any higher element type as ObjectElement or ArrayElement.
	 * Using polymorphism allows us to assume any namespace.
	 *
	 * There is a problem with naming visitor methods described here: https://github.com/babel/babel/discussions/12874
	 */
	return isObjectElement(element)
		? "ObjectElement"
		: isArrayElement(element)
			? "ArrayElement"
			: isMemberElement(element)
				? "MemberElement"
				: isStringElement(element)
					? "StringElement"
					: isBooleanElement(element)
						? "BooleanElement"
						: isNumberElement(element)
							? "NumberElement"
							: isNullElement(element)
								? "NullElement"
								: isLinkElement(element)
									? "LinkElement"
									: isRefElement(element)
										? "RefElement"
										: undefined;
};

/**
 * @public
 */
export const cloneNode = (node) => {
	if (isElement(node)) {
		return cloneShallow(node);
	}
	return cloneNodeDefault(node);
};

// isNode :: Node -> Boolean
export const isNode = pipe(getNodeType, isString);

/**
 * @public
 */
export const keyMapDefault = {
	ObjectElement: ["content"],
	ArrayElement: ["content"],
	MemberElement: ["key", "value"],
	StringElement: [],
	BooleanElement: [],
	NumberElement: [],
	NullElement: [],
	RefElement: [],
	LinkElement: [],
	Annotation: [],
	Comment: [],
	ParseResultElement: ["content"],
};
export class PredicateVisitor {
	result;
	predicate;
	returnOnTrue;
	returnOnFalse;
	constructor({ predicate = stubFalse, returnOnTrue, returnOnFalse } = {}) {
		this.result = [];
		this.predicate = predicate;
		this.returnOnTrue = returnOnTrue;
		this.returnOnFalse = returnOnFalse;
	}
	enter(element) {
		if (this.predicate(element)) {
			this.result.push(element);
			return this.returnOnTrue;
		}
		return this.returnOnFalse;
	}
}

/**
 * @public
 */
export const visit = (
	root,
	// @ts-expect-error
	visitor,
	{ keyMap = keyMapDefault, ...rest } = {},
) => {
	// @ts-expect-error
	return astVisit(root, visitor, {
		// @ts-expect-error
		keyMap,
		// @ts-expect-error
		nodeTypeGetter: getNodeType,
		nodePredicate: isNode,
		nodeCloneFn: cloneNode,
		...rest,
	});
};

// @ts-expect-error
visit[Symbol.for("nodejs.util.promisify.custom")] = async (
	root,
	// @ts-expect-error
	visitor,
	{ keyMap = keyMapDefault, ...rest } = {},
) => {
	// @ts-expect-error
	return astVisit[Symbol.for("nodejs.util.promisify.custom")](root, visitor, {
		// @ts-expect-error
		keyMap,
		// @ts-expect-error
		nodeTypeGetter: getNodeType,
		nodePredicate: isNode,
		nodeCloneFn: cloneNode,
		...rest,
	});
};
