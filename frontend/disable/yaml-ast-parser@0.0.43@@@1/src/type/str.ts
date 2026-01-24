import { Type } from "../type";

export = new Type("tag:yaml.org,2002:str", {
	kind: "scalar",
	construct: (data) => (null !== data ? data : ""),
});
