import { matches as queryMatches } from "./query-type-match.mjs";
import Type from "./type.mjs";

// filter an existing collection
const filter = function (collection) {
	// for 1 id #foo queries, just get the element
	if (
		this.length === 1 &&
		this[0].checks.length === 1 &&
		this[0].checks[0].type === Type.ID
	) {
		return collection.getElementById(this[0].checks[0].value).collection();
	}

	let selectorFunction = (element) => {
		for (let j = 0; j < this.length; j++) {
			const query = this[j];

			if (queryMatches(query, element)) {
				return true;
			}
		}

		return false;
	};

	if (this.text() == null) {
		selectorFunction = () => true;
	}

	return collection.filter(selectorFunction);
}; // filter

// does selector match a single element?
const matches = function (ele) {
	for (let j = 0; j < this.length; j++) {
		const query = this[j];

		if (queryMatches(query, ele)) {
			return true;
		}
	}

	return false;
}; // matches

export default { matches, filter };
