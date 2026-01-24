!((e, t) => {
	"object" == typeof exports && "undefined" != typeof module
		? t(exports)
		: "function" == typeof define && define.amd
			? define(["exports"], t)
			: t(
					((e =
						"undefined" != typeof globalThis
							? globalThis
							: e || self).zustandVanilla = {}),
				);
})(this, (e) => {
	var t = (e) => {
			var t,
				n = new Set(),
				o = (e, o) => {
					var u = "function" == typeof e ? e(t) : e;
					if (!Object.is(u, t)) {
						var r = t;
						(t = (null != o ? o : "object" != typeof u || null === u)
							? u
							: Object.assign({}, t, u)),
							n.forEach((e) => e(t, r));
					}
				},
				u = () => t,
				r = {
					setState: o,
					getState: u,
					getInitialState: () => i,
					subscribe: (e) => (n.add(e), () => n.delete(e)),
					destroy: () => {
						n.clear();
					},
				},
				i = (t = e(o, u, r));
			return r;
		},
		n = (e) => (e ? t(e) : t);
	(e.createStore = n),
		(e.default = (e) => n(e)),
		Object.defineProperty(e, "__esModule", { value: !0 });
});
