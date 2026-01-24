!((t, e) => {
	"object" == typeof exports && "undefined" != typeof module
		? e(exports)
		: "function" == typeof define && define.amd
			? define(["exports"], e)
			: e(
					((t =
						"undefined" != typeof globalThis
							? globalThis
							: t || self).zustandMiddleware = {}),
				);
})(this, (t) => {
	function e() {
		return (
			(e = Object.assign
				? Object.assign.bind()
				: function (t) {
						for (var e = 1; e < arguments.length; e++) {
							var n = arguments[e];
							for (var r in n) Object.hasOwn(n, r) && (t[r] = n[r]);
						}
						return t;
					}),
			e.apply(null, arguments)
		);
	}
	function n(t, e) {
		if (null == t) return {};
		var n = {};
		for (var r in t)
			if (Object.hasOwn(t, r)) {
				if (e.includes(r)) continue;
				n[r] = t[r];
			}
		return n;
	}
	var r = (t, n) => (r, i, o) => (
			(o.dispatch = (e) => (r((n) => t(n, e), !1, e), e)),
			(o.dispatchFromDevtools = !0),
			e(
				{
					dispatch: function () {
						var t;
						return (t = o).dispatch.apply(t, arguments);
					},
				},
				n,
			)
		),
		i = ["enabled", "anonymousActionType", "store"],
		o = ["connection"],
		a = new Map(),
		u = (t) => {
			var e = a.get(t);
			return e
				? Object.fromEntries(
						Object.entries(e.stores).map((t) => [t[0], t[1].getState()]),
					)
				: {};
		},
		c = (t, r) => (
			void 0 === r && (r = {}),
			(c, f, l) => {
				var d,
					v = r,
					p = v.enabled,
					g = v.anonymousActionType,
					y = v.store,
					m = n(v, i);
				try {
					d = null != p && p && window.__REDUX_DEVTOOLS_EXTENSION__;
				} catch (t) {}
				if (!d) return t(c, f, l);
				var h = ((t, n, r) => {
						if (void 0 === t)
							return { type: "untracked", connection: n.connect(r) };
						var i = a.get(r.name);
						if (i) return e({ type: "tracked", store: t }, i);
						var o = { connection: n.connect(r), stores: {} };
						return a.set(r.name, o), e({ type: "tracked", store: t }, o);
					})(y, d, m),
					S = h.connection,
					b = n(h, o),
					O = !0;
				l.setState = (t, n, r) => {
					var i,
						o = c(t, n);
					if (!O) return o;
					var a =
						void 0 === r
							? { type: g || "anonymous" }
							: "string" == typeof r
								? { type: r }
								: r;
					return void 0 === y
						? (null == S || S.send(a, f()), o)
						: (null == S ||
								S.send(
									e({}, a, { type: y + "/" + a.type }),
									e({}, u(m.name), (((i = {})[y] = l.getState()), i)),
								),
							o);
				};
				var w = function () {
						var t = O;
						(O = !1), c.apply(void 0, arguments), (O = t);
					},
					I = t(l.setState, f, l);
				if (
					("untracked" === b.type
						? null == S || S.init(I)
						: ((b.stores[b.store] = l),
							null == S ||
								S.init(
									Object.fromEntries(
										Object.entries(b.stores).map((t) => {
											var e = t[0],
												n = t[1];
											return [e, e === b.store ? I : n.getState()];
										}),
									),
								)),
					l.dispatchFromDevtools && "function" == typeof l.dispatch)
				) {
					var T = l.dispatch;
					l.dispatch = function () {
						for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
							e[n] = arguments[n];
						T.apply(void 0, e);
					};
				}
				return (
					S.subscribe((t) => {
						switch (t.type) {
							case "ACTION":
								return "string" != typeof t.payload
									? void console.error(
											"[zustand devtools middleware] Unsupported action format",
										)
									: s(t.payload, (t) => {
											if ("__setState" !== t.type)
												l.dispatchFromDevtools &&
													"function" == typeof l.dispatch &&
													l.dispatch(t);
											else {
												if (void 0 === y) return void w(t.state);
												1 !== Object.keys(t.state).length &&
													console.error(
														'\n                    [zustand devtools middleware] Unsupported __setState action format. \n                    When using \'store\' option in devtools(), the \'state\' should have only one key, which is a value of \'store\' that was passed in devtools(),\n                    and value of this only key should be a state object. Example: { "type": "__setState", "state": { "abc123Store": { "foo": "bar" } } }\n                    ',
													);
												var e = t.state[y];
												if (null == e) return;
												JSON.stringify(l.getState()) !== JSON.stringify(e) &&
													w(e);
											}
										});
							case "DISPATCH":
								switch (t.payload.type) {
									case "RESET":
										return (
											w(I),
											void 0 === y
												? null == S
													? void 0
													: S.init(l.getState())
												: null == S
													? void 0
													: S.init(u(m.name))
										);
									case "COMMIT":
										return void 0 === y
											? void (null == S || S.init(l.getState()))
											: null == S
												? void 0
												: S.init(u(m.name));
									case "ROLLBACK":
										return s(t.state, (t) => {
											if (void 0 === y)
												return w(t), void (null == S || S.init(l.getState()));
											w(t[y]), null == S || S.init(u(m.name));
										});
									case "JUMP_TO_STATE":
									case "JUMP_TO_ACTION":
										return s(t.state, (t) => {
											void 0 !== y
												? JSON.stringify(l.getState()) !==
														JSON.stringify(t[y]) && w(t[y])
												: w(t);
										});
									case "IMPORT_STATE": {
										var e,
											n = t.payload.nextLiftedState,
											r =
												null == (e = n.computedStates.slice(-1)[0])
													? void 0
													: e.state;
										if (!r) return;
										return (
											w(void 0 === y ? r : r[y]),
											void (null == S || S.send(null, n))
										);
									}
									case "PAUSE_RECORDING":
										return (O = !O);
								}
								return;
						}
					}),
					I
				);
			}
		),
		s = (t, e) => {
			var n;
			try {
				n = JSON.parse(t);
			} catch (t) {
				console.error(
					"[zustand devtools middleware] Could not parse the received json",
					t,
				);
			}
			void 0 !== n && e(n);
		},
		f = (t) => (e, n, r) => {
			var i = r.subscribe;
			return (
				(r.subscribe = (t, e, n) => {
					var o = t;
					if (e) {
						var a = (null == n ? void 0 : n.equalityFn) || Object.is,
							u = t(r.getState());
						(o = (n) => {
							var r = t(n);
							if (!a(u, r)) {
								var i = u;
								e((u = r), i);
							}
						}),
							null != n && n.fireImmediately && e(u, u);
					}
					return i(o);
				}),
				t(e, n, r)
			);
		};
	function l(t, e) {
		var n;
		try {
			n = t();
		} catch (t) {
			return;
		}
		return {
			getItem: (t) => {
				var r,
					i = (t) =>
						null === t ? null : JSON.parse(t, null == e ? void 0 : e.reviver),
					o = null != (r = n.getItem(t)) ? r : null;
				return o instanceof Promise ? o.then(i) : i(o);
			},
			setItem: (t, r) =>
				n.setItem(t, JSON.stringify(r, null == e ? void 0 : e.replacer)),
			removeItem: (t) => n.removeItem(t),
		};
	}
	var d = (t) => (e) => {
			try {
				var n = t(e);
				return n instanceof Promise
					? n
					: {
							then: (t) => d(t)(n),
							catch: function (t) {
								return this;
							},
						};
			} catch (t) {
				return {
					then: function (t) {
						return this;
					},
					catch: (e) => d(e)(t),
				};
			}
		},
		v = (t, n) =>
			"getStorage" in n || "serialize" in n || "deserialize" in n
				? ((t, n) => (r, i, o) => {
						var a,
							u = e(
								{
									getStorage: () => localStorage,
									serialize: JSON.stringify,
									deserialize: JSON.parse,
									partialize: (t) => t,
									version: 0,
									merge: (t, n) => e({}, n, t),
								},
								n,
							),
							c = !1,
							s = new Set(),
							f = new Set();
						try {
							a = u.getStorage();
						} catch (t) {}
						if (!a)
							return t(
								function () {
									console.warn(
										"[zustand persist middleware] Unable to update item '" +
											u.name +
											"', the given storage is currently unavailable.",
									),
										r.apply(void 0, arguments);
								},
								i,
								o,
							);
						var l = d(u.serialize),
							v = () => {
								var t,
									n = u.partialize(e({}, i())),
									r = l({ state: n, version: u.version })
										.then((t) => a.setItem(u.name, t))
										.catch((e) => {
											t = e;
										});
								if (t) throw t;
								return r;
							},
							p = o.setState;
						o.setState = (t, e) => {
							p(t, e), v();
						};
						var g,
							y = t(
								function () {
									r.apply(void 0, arguments), v();
								},
								i,
								o,
							),
							m = () => {
								if (a) {
									(c = !1), s.forEach((t) => t(i()));
									var t =
										(null == u.onRehydrateStorage
											? void 0
											: u.onRehydrateStorage(i())) || void 0;
									return d(a.getItem.bind(a))(u.name)
										.then((t) => {
											if (t) return u.deserialize(t);
										})
										.then((t) => {
											if (t) {
												if (
													"number" != typeof t.version ||
													t.version === u.version
												)
													return t.state;
												if (u.migrate) return u.migrate(t.state, t.version);
												console.error(
													"State loaded from storage couldn't be migrated since no migrate function was provided",
												);
											}
										})
										.then((t) => {
											var e;
											return (
												(g = u.merge(t, null != (e = i()) ? e : y)),
												r(g, !0),
												v()
											);
										})
										.then(() => {
											null == t || t(g, void 0),
												(c = !0),
												f.forEach((t) => t(g));
										})
										.catch((e) => {
											null == t || t(void 0, e);
										});
								}
							};
						return (
							(o.persist = {
								setOptions: (t) => {
									(u = e({}, u, t)), t.getStorage && (a = t.getStorage());
								},
								clearStorage: () => {
									var t;
									null == (t = a) || t.removeItem(u.name);
								},
								getOptions: () => u,
								rehydrate: () => m(),
								hasHydrated: () => c,
								onHydrate: (t) => (
									s.add(t),
									() => {
										s.delete(t);
									}
								),
								onFinishHydration: (t) => (
									f.add(t),
									() => {
										f.delete(t);
									}
								),
							}),
							m(),
							g || y
						);
					})(t, n)
				: ((t, n) => (r, i, o) => {
						var a = e(
								{
									storage: l(() => localStorage),
									partialize: (t) => t,
									version: 0,
									merge: (t, n) => e({}, n, t),
								},
								n,
							),
							u = !1,
							c = new Set(),
							s = new Set(),
							f = a.storage;
						if (!f)
							return t(
								function () {
									console.warn(
										"[zustand persist middleware] Unable to update item '" +
											a.name +
											"', the given storage is currently unavailable.",
									),
										r.apply(void 0, arguments);
								},
								i,
								o,
							);
						var v = () => {
								var t = a.partialize(e({}, i()));
								return f.setItem(a.name, { state: t, version: a.version });
							},
							p = o.setState;
						o.setState = (t, e) => {
							p(t, e), v();
						};
						var g,
							y = t(
								function () {
									r.apply(void 0, arguments), v();
								},
								i,
								o,
							);
						o.getInitialState = () => y;
						var m = () => {
							var t;
							if (f) {
								(u = !1),
									c.forEach((t) => {
										var e;
										return t(null != (e = i()) ? e : y);
									});
								var e =
									(null == a.onRehydrateStorage
										? void 0
										: a.onRehydrateStorage(null != (t = i()) ? t : y)) ||
									void 0;
								return d(f.getItem.bind(f))(a.name)
									.then((t) => {
										if (t) {
											if (
												"number" != typeof t.version ||
												t.version === a.version
											)
												return [!1, t.state];
											if (a.migrate) return [!0, a.migrate(t.state, t.version)];
											console.error(
												"State loaded from storage couldn't be migrated since no migrate function was provided",
											);
										}
										return [!1, void 0];
									})
									.then((t) => {
										var e,
											n = t[0],
											o = t[1];
										if (
											((g = a.merge(o, null != (e = i()) ? e : y)), r(g, !0), n)
										)
											return v();
									})
									.then(() => {
										null == e || e(g, void 0),
											(g = i()),
											(u = !0),
											s.forEach((t) => t(g));
									})
									.catch((t) => {
										null == e || e(void 0, t);
									});
							}
						};
						return (
							(o.persist = {
								setOptions: (t) => {
									(a = e({}, a, t)), t.storage && (f = t.storage);
								},
								clearStorage: () => {
									var t;
									null == (t = f) || t.removeItem(a.name);
								},
								getOptions: () => a,
								rehydrate: () => m(),
								hasHydrated: () => u,
								onHydrate: (t) => (
									c.add(t),
									() => {
										c.delete(t);
									}
								),
								onFinishHydration: (t) => (
									s.add(t),
									() => {
										s.delete(t);
									}
								),
							}),
							a.skipHydration || m(),
							g || y
						);
					})(t, n);
	(t.combine = (t, e) =>
		function () {
			return Object.assign({}, t, e.apply(void 0, arguments));
		}),
		(t.createJSONStorage = l),
		(t.devtools = c),
		(t.persist = v),
		(t.redux = r),
		(t.subscribeWithSelector = f);
});
