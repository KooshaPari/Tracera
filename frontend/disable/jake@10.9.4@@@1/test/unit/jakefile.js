task("foo", () => {
	console.log("ran top-level foo");
});

task("bar", () => {
	console.log("ran top-level bar");
});

task("zerb", () => {
	console.log("ran zerb");
});

namespace("zooby", () => {
	task("zerp", () => {});

	task("derp", ["zerp"], () => {});

	namespace("frang", () => {
		namespace("w00t", () => {
			task("bar", () => {
				console.log("ran zooby:frang:w00t:bar");
			});
		});

		task("asdf", () => {});
	});
});

namespace("hurr", () => {
	namespace("durr");
});
