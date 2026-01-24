import { ObjectElement } from "@swagger-api/apidom-core";
import {
	FallbackVisitor,
	MapVisitor,
	ParentSchemaAwareVisitor,
} from "@swagger-api/apidom-ns-json-schema-draft-7";
import { always } from "ramda";
import { Mixin } from "ts-mixer";

/**
 * @public
 */

/**
 * @public
 */
class $defsVisitor extends Mixin(
	MapVisitor,
	ParentSchemaAwareVisitor,
	FallbackVisitor,
) {
	constructor(options) {
		super(options);
		this.element = new ObjectElement();
		this.element.classes.push("json-schema-$defs");
		this.specPath = always(["document", "objects", "JSONSchema"]);
	}
}
export default $defsVisitor;
