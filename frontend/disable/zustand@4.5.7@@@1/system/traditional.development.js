System.register(
	["react", "use-sync-external-store/shim/with-selector", "zustand/vanilla"],
	(exports) => {
		var ReactExports, useSyncExternalStoreExports, createStore;
		return {
			setters: [
				(module) => {
					ReactExports = module.default;
				},
				(module) => {
					useSyncExternalStoreExports = module.default;
				},
				(module) => {
					createStore = module.createStore;
				},
			],
			execute: () => {
				exports("useStoreWithEqualityFn", useStoreWithEqualityFn);

				const { useDebugValue } = ReactExports;
				const { useSyncExternalStoreWithSelector } =
					useSyncExternalStoreExports;
				const identity = (arg) => arg;
				function useStoreWithEqualityFn(api, selector = identity, equalityFn) {
					const slice = useSyncExternalStoreWithSelector(
						api.subscribe,
						api.getState,
						api.getServerState || api.getInitialState,
						selector,
						equalityFn,
					);
					useDebugValue(slice);
					return slice;
				}
				const createWithEqualityFnImpl = (createState, defaultEqualityFn) => {
					const api = createStore(createState);
					const useBoundStoreWithEqualityFn = (
						selector,
						equalityFn = defaultEqualityFn,
					) => useStoreWithEqualityFn(api, selector, equalityFn);
					Object.assign(useBoundStoreWithEqualityFn, api);
					return useBoundStoreWithEqualityFn;
				};
				const createWithEqualityFn = exports(
					"createWithEqualityFn",
					(createState, defaultEqualityFn) =>
						createState
							? createWithEqualityFnImpl(createState, defaultEqualityFn)
							: createWithEqualityFnImpl,
				);
			},
		};
	},
);
