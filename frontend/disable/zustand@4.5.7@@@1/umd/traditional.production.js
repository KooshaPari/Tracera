!((e, t) => {
	"object" == typeof exports && "undefined" != typeof module
		? t(
				exports,
				require("react"),
				require("use-sync-external-store/shim/with-selector"),
				require("zustand/vanilla"),
			)
		: "function" == typeof define && define.amd
			? define(
					[
						"exports",
						"react",
						"use-sync-external-store/shim/with-selector",
						"zustand/vanilla",
					],
					t,
				)
			: t(
					((e =
						"undefined" != typeof globalThis
							? globalThis
							: e || self).zustandTraditional = {}),
					e.React,
					e.useSyncExternalStoreShimWithSelector,
					e.zustandVanilla,
				);
})(this, (e, t, n, r) => {
	var i = t.useDebugValue,
		a = n.useSyncExternalStoreWithSelector,
		u = (e) => e;
	function o(e, t, n) {
		void 0 === t && (t = u);
		var r = a(
			e.subscribe,
			e.getState,
			e.getServerState || e.getInitialState,
			t,
			n,
		);
		return i(r), r;
	}
	var s = (e, t) => {
		var n = r.createStore(e),
			i = (e, r) => (void 0 === r && (r = t), o(n, e, r));
		return Object.assign(i, n), i;
	};
	(e.createWithEqualityFn = (e, t) => (e ? s(e, t) : s)),
		(e.useStoreWithEqualityFn = o);
});
