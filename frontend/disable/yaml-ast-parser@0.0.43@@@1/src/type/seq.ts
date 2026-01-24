import { Type } from "../type";

export = new Type("tag:yaml.org,2002:seq", {
	kind: "sequence",
	construct: (data) => (null !== data ? data : []),
});
