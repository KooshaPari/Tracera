System.register(["react", "zustand/traditional"], (a) => {
	var o, s;
	return {
		setters: [
			(r) => {
				o = r.default;
			},
			(r) => {
				s = r.useStoreWithEqualityFn;
			},
		],
		execute: () => {
			a("default", l);
			const {
				createElement: r,
				createContext: c,
				useContext: i,
				useMemo: d,
				useRef: f,
			} = o;
			function l() {
				const n = c(void 0);
				return {
					Provider: ({ createStore: e, children: u }) => {
						const t = f();
						return (
							t.current || (t.current = e()),
							r(n.Provider, { value: t.current }, u)
						);
					},
					useStore: (e, u) => {
						const t = i(n);
						if (!t)
							throw new Error(
								"Seems like you have not used zustand provider as an ancestor.",
							);
						return s(t, e, u);
					},
					useStoreApi: () => {
						const e = i(n);
						if (!e)
							throw new Error(
								"Seems like you have not used zustand provider as an ancestor.",
							);
						return d(() => ({ ...e }), [e]);
					},
				};
			}
		},
	};
});
