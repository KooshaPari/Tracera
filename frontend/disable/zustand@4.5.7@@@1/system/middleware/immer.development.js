System.register(["immer"], (exports) => {
	var produce;
	return {
		setters: [
			(module) => {
				produce = module.produce;
			},
		],
		execute: () => {
			const immerImpl = (initializer) => (set, get, store) => {
				store.setState = (updater, replace, ...a) => {
					const nextState =
						typeof updater === "function" ? produce(updater) : updater;
					return set(nextState, replace, ...a);
				};
				return initializer(store.setState, get, store);
			};
			const immer = exports("immer", immerImpl);
		},
	};
});
