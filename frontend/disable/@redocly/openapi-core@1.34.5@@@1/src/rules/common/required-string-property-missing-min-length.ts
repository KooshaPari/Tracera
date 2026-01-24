import type { Oas2Schema } from "core/src/typings/swagger";
import type { Oas3Rule } from "core/src/visitors";
import type { Oas3_1Schema, Oas3Schema } from "../../typings/openapi";
import type { UserContext } from "../../walk";

export const RequiredStringPropertyMissingMinLength: Oas3Rule = () => {
	let skipSchemaProperties: boolean;
	let requiredPropertiesSet: Set<string>;

	return {
		Schema: {
			enter(schema: Oas3Schema | Oas3_1Schema | Oas2Schema) {
				if (!schema?.required) {
					skipSchemaProperties = true;
					return;
				}
				requiredPropertiesSet = new Set(schema.required);
				skipSchemaProperties = false;
			},

			SchemaProperties: {
				skip() {
					return skipSchemaProperties;
				},

				Schema: {
					enter(
						schema: Oas3Schema | Oas3_1Schema | Oas2Schema,
						{ key, location, report }: UserContext,
					) {
						if (
							requiredPropertiesSet.has(key as string) &&
							schema.type === "string"
						) {
							if (!schema?.minLength) {
								report({
									message: "Property minLength is required.",
									location: location.key(),
								});
							}
						}
					},
				},
			},
		},
	};
};
