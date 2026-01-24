var DomUtils = module.exports;

[
	require("./lib/stringify"),
	require("./lib/traversal"),
	require("./lib/manipulation"),
	require("./lib/querying"),
	require("./lib/legacy"),
	require("./lib/helpers"),
].forEach((ext) => {
	Object.keys(ext).forEach((key) => {
		DomUtils[key] = ext[key].bind(DomUtils);
	});
});
