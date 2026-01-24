System.register(
	["react", "use-sync-external-store/shim/with-selector", "zustand/vanilla"],
	(a) => {
		var c, s, i;
		return {
			setters: [
				(e) => {
					c = e.default;
				},
				(e) => {
					s = e.default;
				},
				(e) => {
					i = e.createStore;
				},
			],
			execute: () => {
				a("useStoreWithEqualityFn", o);
				const { useDebugValue: e } = c,
					{ useSyncExternalStoreWithSelector: S } = s,
					f = (t) => t;
				function o(t, n = f, u) {
					const r = S(
						t.subscribe,
						t.getState,
						t.getServerState || t.getInitialState,
						n,
						u,
					);
					return e(r), r;
				}
				const l = (t, n) => {
						const u = i(t),
							r = (y, h = n) => o(u, y, h);
						return Object.assign(r, u), r;
					},
					g = a("createWithEqualityFn", (t, n) => (t ? l(t, n) : l));
			},
		};
	},
);
