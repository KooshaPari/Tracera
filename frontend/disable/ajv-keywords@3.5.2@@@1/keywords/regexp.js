module.exports = function defFunc(ajv) {
	defFunc.definition = {
		type: "string",
		inline: (it, keyword, schema) =>
			getRegExp() + ".test(data" + (it.dataLevel || "") + ")",
		metaSchema: {
			type: ["string", "object"],
			properties: {
				pattern: { type: "string" },
				flags: { type: "string" },
			},
			required: ["pattern"],
			additionalProperties: false,
		},
	};

	ajv.addKeyword("regexp", defFunc.definition);
	return ajv;
};
