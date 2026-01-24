import { parseYamlToDocument } from "../../../../../__tests__/utils";
import {
	type RuleConfig,
	resolveStyleguideConfig,
	StyleguideConfig,
} from "../../../../config";
import { lintDocument } from "../../../../lint";
import { BaseResolver } from "../../../../resolve";

export async function validateDoc(
	source: string,
	rules: Record<string, RuleConfig> = { spec: "error" },
) {
	const document = parseYamlToDocument(source, "foobar.yaml");

	const results = await lintDocument({
		externalRefResolver: new BaseResolver(),
		document,
		config: new StyleguideConfig(
			await resolveStyleguideConfig({
				styleguideConfig: {
					plugins: [],
					extends: [],
					rules,
				},
			}),
		),
	});

	return results.map((res) => {
		return {
			message: res.message,
			location: res.location[0].pointer || "",
		};
	});
}
