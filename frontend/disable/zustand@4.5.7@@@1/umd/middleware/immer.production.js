!((e, t) => {
	"object" == typeof exports && "undefined" != typeof module
		? t(exports, require("immer"))
		: "function" == typeof define && define.amd
			? define(["exports", "immer"], t)
			: t(
					((e =
						"undefined" != typeof globalThis
							? globalThis
							: e || self).zustandMiddlewareImmer = {}),
					e.immer,
				);
})(this, (e, t) => {
	var n = (e) => (n, r, i) => (
		(i.setState = function (e, r) {
			for (
				var i = "function" == typeof e ? t.produce(e) : e,
					o = arguments.length,
					f = new Array(o > 2 ? o - 2 : 0),
					u = 2;
				u < o;
				u++
			)
				f[u - 2] = arguments[u];
			return n.apply(void 0, [i, r].concat(f));
		}),
		e(i.setState, r, i)
	);
	e.immer = n;
});
