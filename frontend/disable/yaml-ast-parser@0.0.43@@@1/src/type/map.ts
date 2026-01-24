import { Type } from "../type";

export = new Type("tag:yaml.org,2002:map", {
	kind: "mapping",
	construct: (data) => (null !== data ? data : {}),
});
