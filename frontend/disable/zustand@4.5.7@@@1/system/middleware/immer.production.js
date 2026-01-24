System.register(["immer"], (c) => {
	var r;
	return {
		setters: [
			(n) => {
				r = n.produce;
			},
		],
		execute: () => {
			const S = c(
				"immer",
				(s) => (o, u, t) => (
					(t.setState = (e, i, ...m) => {
						const f = typeof e == "function" ? r(e) : e;
						return o(f, i, ...m);
					}),
					s(t.setState, u, t)
				),
			);
		},
	};
});
