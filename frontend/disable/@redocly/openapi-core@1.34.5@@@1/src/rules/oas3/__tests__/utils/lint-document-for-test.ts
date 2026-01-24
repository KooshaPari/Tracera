import {
	makeConfig,
	parseYamlToDocument,
} from "../../../../../__tests__/utils";
import type { RuleConfig } from "../../../../config";
import { lintDocument } from "../../../../lint";
import { BaseResolver, type Document } from "../../../../resolve";

export async function lintDocumentForTest(
	rules: Record<string, RuleConfig>,
	document: Document,
	additionalDocuments: { absoluteRef: string; body: string }[],
) {
	const baseResolver = new BaseResolver();
	additionalDocuments.forEach((item) =>
		baseResolver.cache.set(
			item.absoluteRef,
			Promise.resolve(parseYamlToDocument(item.body, item.absoluteRef)),
		),
	);
	return await lintDocument({
		externalRefResolver: baseResolver,
		document,
		config: await makeConfig({ rules }),
	});
}
