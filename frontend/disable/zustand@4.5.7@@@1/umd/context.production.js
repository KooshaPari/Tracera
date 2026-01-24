!((e, r) => {
	"object" == typeof exports && "undefined" != typeof module
		? (module.exports = r(require("react"), require("zustand/traditional")))
		: "function" == typeof define && define.amd
			? define(["react", "zustand/traditional"], r)
			: ((e =
					"undefined" != typeof globalThis
						? globalThis
						: e || self).zustandContext = r(e.React, e.traditional));
})(this, (e, r) => {
	function t() {
		return (
			(t = Object.assign
				? Object.assign.bind()
				: function (e) {
						for (var r = 1; r < arguments.length; r++) {
							var t = arguments[r];
							for (var n in t) Object.hasOwn(t, n) && (e[n] = t[n]);
						}
						return e;
					}),
			t.apply(null, arguments)
		);
	}
	var n = e.createElement,
		o = e.createContext,
		u = e.useContext,
		i = e.useMemo,
		a = e.useRef;
	return () => {
		var e = o(void 0);
		return {
			Provider: (r) => {
				var t = r.createStore,
					o = r.children,
					u = a();
				return (
					u.current || (u.current = t()), n(e.Provider, { value: u.current }, o)
				);
			},
			useStore: (t, n) => {
				var o = u(e);
				if (!o)
					throw new Error(
						"Seems like you have not used zustand provider as an ancestor.",
					);
				return r.useStoreWithEqualityFn(o, t, n);
			},
			useStoreApi: () => {
				var r = u(e);
				if (!r)
					throw new Error(
						"Seems like you have not used zustand provider as an ancestor.",
					);
				return i(() => t({}, r), [r]);
			},
		};
	};
});
