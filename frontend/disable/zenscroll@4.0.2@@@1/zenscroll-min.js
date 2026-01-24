!((t, e) => {
	"function" == typeof define && define.amd
		? define([], e())
		: "object" == typeof module && module.exports
			? (module.exports = e())
			: (function n() {
					document && document.body ? (t.zenscroll = e()) : setTimeout(n, 9);
				})();
})(this, () => {
	var t = (t) =>
		t &&
		"getComputedStyle" in window &&
		"smooth" === window.getComputedStyle(t)["scroll-behavior"];
	if ("undefined" == typeof window || !("document" in window)) return {};
	var e = (e, n, o) => {
			(n = n || 999), o || 0 === o || (o = 9);
			var i,
				r = (t) => {
					i = t;
				},
				u = () => {
					clearTimeout(i), r(0);
				},
				c = (t) => Math.max(0, e.getTopOf(t) - o),
				a = (o, i, c) => {
					if ((u(), 0 === i || (i && i < 0) || t(e.body))) e.toY(o), c && c();
					else {
						var a = e.getY(),
							f = Math.max(0, o) - a,
							s = new Date().getTime();
						(i = i || Math.min(Math.abs(f), n)),
							(function t() {
								r(
									setTimeout(() => {
										var n = Math.min(1, (new Date().getTime() - s) / i),
											o = Math.max(
												0,
												Math.floor(
													a + f * (n < 0.5 ? 2 * n * n : n * (4 - 2 * n) - 1),
												),
											);
										e.toY(o),
											n < 1 && e.getHeight() + o < e.body.scrollHeight
												? t()
												: (setTimeout(u, 99), c && c());
									}, 9),
								);
							})();
					}
				},
				f = (t, e, n) => {
					a(c(t), e, n);
				},
				s = (t, n, i) => {
					var r = t.getBoundingClientRect().height,
						u = e.getTopOf(t) + r,
						s = e.getHeight(),
						l = e.getY(),
						d = l + s;
					c(t) < l || r + o > s
						? f(t, n, i)
						: u + o > d
							? a(u - s + o, n, i)
							: i && i();
				},
				l = (t, n, o, i) => {
					a(
						Math.max(
							0,
							e.getTopOf(t) -
								e.getHeight() / 2 +
								(o || t.getBoundingClientRect().height / 2),
						),
						n,
						i,
					);
				};
			return {
				setup: (t, e) => (
					(0 === t || t) && (n = t),
					(0 === e || e) && (o = e),
					{ defaultDuration: n, edgeOffset: o }
				),
				to: f,
				toY: a,
				intoView: s,
				center: l,
				stop: u,
				moving: () => !!i,
				getY: e.getY,
				getTopOf: e.getTopOf,
			};
		},
		n = document.documentElement,
		o = () => window.scrollY || n.scrollTop,
		i = e({
			body: document.scrollingElement || document.body,
			toY: (t) => {
				window.scrollTo(0, t);
			},
			getY: o,
			getHeight: () => window.innerHeight || n.clientHeight,
			getTopOf: (t) => t.getBoundingClientRect().top + o() - n.offsetTop,
		});
	if (
		((i.createScroller = (t, o, i) =>
			e(
				{
					body: t,
					toY: (e) => {
						t.scrollTop = e;
					},
					getY: () => t.scrollTop,
					getHeight: () =>
						Math.min(t.clientHeight, window.innerHeight || n.clientHeight),
					getTopOf: (t) => t.offsetTop,
				},
				o,
				i,
			)),
		"addEventListener" in window && !window.noZensmooth && !t(document.body))
	) {
		var r = "history" in window && "pushState" in history,
			u = r && "scrollRestoration" in history;
		u && (history.scrollRestoration = "auto"),
			window.addEventListener(
				"load",
				() => {
					u &&
						(setTimeout(() => {
							history.scrollRestoration = "manual";
						}, 9),
						window.addEventListener(
							"popstate",
							(t) => {
								t.state && "zenscrollY" in t.state && i.toY(t.state.zenscrollY);
							},
							!1,
						)),
						window.location.hash &&
							setTimeout(() => {
								var t = i.setup().edgeOffset;
								if (t) {
									var e = document.getElementById(
										window.location.href.split("#")[1],
									);
									if (e) {
										var n = Math.max(0, i.getTopOf(e) - t),
											o = i.getY() - n;
										0 <= o && o < 9 && window.scrollTo(0, n);
									}
								}
							}, 9);
				},
				!1,
			);
		var c = /(^|\s)noZensmooth(\s|$)/;
		window.addEventListener(
			"click",
			(t) => {
				for (var e = t.target; e && "A" !== e.tagName; ) e = e.parentNode;
				if (
					!(
						!e ||
						1 !== t.which ||
						t.shiftKey ||
						t.metaKey ||
						t.ctrlKey ||
						t.altKey
					)
				) {
					if (u) {
						var n =
							history.state && "object" == typeof history.state
								? history.state
								: {};
						n.zenscrollY = i.getY();
						try {
							history.replaceState(n, "");
						} catch (t) {}
					}
					var o = e.getAttribute("href") || "";
					if (0 === o.indexOf("#") && !c.test(e.className)) {
						var a = 0,
							f = document.getElementById(o.substring(1));
						if ("#" !== o) {
							if (!f) return;
							a = i.getTopOf(f);
						}
						t.preventDefault();
						var s = () => {
								window.location = o;
							},
							l = i.setup().edgeOffset;
						l &&
							((a = Math.max(0, a - l)),
							r &&
								(s = () => {
									history.pushState({}, "", o);
								})),
							i.toY(a, null, s);
					}
				}
			},
			!1,
		);
	}
	return i;
});
