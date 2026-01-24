module.exports = function defFunc(ajv) {
	defFunc.definition = {
		type: "object",
		macro: (schema) => {
			if (schema.length == 0) return true;
			if (schema.length == 1) return { required: schema };
			var schemas = schema.map((prop) => ({ required: [prop] }));
			return { anyOf: schemas };
		},
		metaSchema: {
			type: "array",
			items: {
				type: "string",
			},
		},
	};

	ajv.addKeyword("anyRequired", defFunc.definition);
	return ajv;
};
