!((e, t) => {
	"object" == typeof exports && "undefined" != typeof module
		? t(
				exports,
				require("zustand/vanilla"),
				require("react"),
				require("use-sync-external-store/shim/with-selector"),
			)
		: "function" == typeof define && define.amd
			? define(
					[
						"exports",
						"zustand/vanilla",
						"react",
						"use-sync-external-store/shim/with-selector",
					],
					t,
				)
			: t(
					((e =
						"undefined" != typeof globalThis ? globalThis : e || self).zustand =
						{}),
					e.zustandVanilla,
					e.React,
					e.useSyncExternalStoreShimWithSelector,
				);
})(this, (e, t, n, r) => {
	var u = n.useDebugValue,
		o = r.useSyncExternalStoreWithSelector,
		i = (e) => e;
	function a(e, t, n) {
		void 0 === t && (t = i);
		var r = o(
			e.subscribe,
			e.getState,
			e.getServerState || e.getInitialState,
			t,
			n,
		);
		return u(r), r;
	}
	var c = (e) => {
			var n = "function" == typeof e ? t.createStore(e) : e,
				r = (e, t) => a(n, e, t);
			return Object.assign(r, n), r;
		},
		s = (e) => (e ? c(e) : c);
	(e.create = s),
		(e.default = (e) => s(e)),
		(e.useStore = a),
		Object.keys(t).forEach((n) => {
			"default" === n ||
				Object.hasOwn(e, n) ||
				Object.defineProperty(e, n, { enumerable: !0, get: () => t[n] });
		}),
		Object.defineProperty(e, "__esModule", { value: !0 });
});
