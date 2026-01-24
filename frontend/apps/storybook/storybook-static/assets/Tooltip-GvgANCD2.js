import { r as c, a as ke, R as Tn } from "./iframe-BP6kYN29.js";
import { r as at, R as Ha, j as p, s as za } from "./index-Dj-uACAQ.js";
function Jo(e) {
	var t,
		n,
		o = "";
	if (typeof e == "string" || typeof e == "number") o += e;
	else if (typeof e == "object")
		if (Array.isArray(e)) {
			var r = e.length;
			for (t = 0; t < r; t++)
				e[t] && (n = Jo(e[t])) && (o && (o += " "), (o += n));
		} else for (n in e) e[n] && (o && (o += " "), (o += n));
	return o;
}
function er() {
	for (var e, t, n = 0, o = "", r = arguments.length; n < r; n++)
		(e = arguments[n]) && (t = Jo(e)) && (o && (o += " "), (o += t));
	return o;
}
const go = (e) => (typeof e == "boolean" ? `${e}` : e === 0 ? "0" : e),
	ho = er,
	tr = (e, t) => (n) => {
		var o;
		if (t?.variants == null) return ho(e, n?.class, n?.className);
		const { variants: r, defaultVariants: s } = t,
			i = Object.keys(r).map((u) => {
				const f = n?.[u],
					d = s?.[u];
				if (f === null) return null;
				const g = go(f) || go(d);
				return r[u][g];
			}),
			a =
				n &&
				Object.entries(n).reduce((u, f) => {
					const [d, g] = f;
					return g === void 0 || (u[d] = g), u;
				}, {}),
			l =
				t == null || (o = t.compoundVariants) === null || o === void 0
					? void 0
					: o.reduce((u, f) => {
							const { class: d, className: g, ...v } = f;
							return Object.entries(v).every((h) => {
								const [m, x] = h;
								return Array.isArray(x)
									? x.includes({ ...s, ...a }[m])
									: { ...s, ...a }[m] === x;
							})
								? [...u, d, g]
								: u;
						}, []);
		return ho(e, i, l, n?.class, n?.className);
	},
	Ga = (e, t) => {
		const n = new Array(e.length + t.length);
		for (let o = 0; o < e.length; o++) n[o] = e[o];
		for (let o = 0; o < t.length; o++) n[e.length + o] = t[o];
		return n;
	},
	Ua = (e, t) => ({ classGroupId: e, validator: t }),
	nr = (e = new Map(), t = null, n) => ({
		nextPart: e,
		validators: t,
		classGroupId: n,
	}),
	_t = "-",
	vo = [],
	Ka = "arbitrary..",
	Ya = (e) => {
		const t = qa(e),
			{ conflictingClassGroups: n, conflictingClassGroupModifiers: o } = e;
		return {
			getClassGroupId: (i) => {
				if (i.startsWith("[") && i.endsWith("]")) return Xa(i);
				const a = i.split(_t),
					l = a[0] === "" && a.length > 1 ? 1 : 0;
				return or(a, l, t);
			},
			getConflictingClassGroupIds: (i, a) => {
				if (a) {
					const l = o[i],
						u = n[i];
					return l ? (u ? Ga(u, l) : l) : u || vo;
				}
				return n[i] || vo;
			},
		};
	},
	or = (e, t, n) => {
		if (e.length - t === 0) return n.classGroupId;
		const r = e[t],
			s = n.nextPart.get(r);
		if (s) {
			const u = or(e, t + 1, s);
			if (u) return u;
		}
		const i = n.validators;
		if (i === null) return;
		const a = t === 0 ? e.join(_t) : e.slice(t).join(_t),
			l = i.length;
		for (let u = 0; u < l; u++) {
			const f = i[u];
			if (f.validator(a)) return f.classGroupId;
		}
	},
	Xa = (e) =>
		e.slice(1, -1).indexOf(":") === -1
			? void 0
			: (() => {
					const t = e.slice(1, -1),
						n = t.indexOf(":"),
						o = t.slice(0, n);
					return o ? Ka + o : void 0;
				})(),
	qa = (e) => {
		const { theme: t, classGroups: n } = e;
		return Za(n, t);
	},
	Za = (e, t) => {
		const n = nr();
		for (const o in e) {
			const r = e[o];
			kn(r, n, o, t);
		}
		return n;
	},
	kn = (e, t, n, o) => {
		const r = e.length;
		for (let s = 0; s < r; s++) {
			const i = e[s];
			Qa(i, t, n, o);
		}
	},
	Qa = (e, t, n, o) => {
		if (typeof e == "string") {
			Ja(e, t, n);
			return;
		}
		if (typeof e == "function") {
			ec(e, t, n, o);
			return;
		}
		tc(e, t, n, o);
	},
	Ja = (e, t, n) => {
		const o = e === "" ? t : rr(t, e);
		o.classGroupId = n;
	},
	ec = (e, t, n, o) => {
		if (nc(e)) {
			kn(e(o), t, n, o);
			return;
		}
		t.validators === null && (t.validators = []), t.validators.push(Ua(n, e));
	},
	tc = (e, t, n, o) => {
		const r = Object.entries(e),
			s = r.length;
		for (let i = 0; i < s; i++) {
			const [a, l] = r[i];
			kn(l, rr(t, a), n, o);
		}
	},
	rr = (e, t) => {
		let n = e;
		const o = t.split(_t),
			r = o.length;
		for (let s = 0; s < r; s++) {
			const i = o[s];
			let a = n.nextPart.get(i);
			a || ((a = nr()), n.nextPart.set(i, a)), (n = a);
		}
		return n;
	},
	nc = (e) => "isThemeGetter" in e && e.isThemeGetter === !0,
	oc = (e) => {
		if (e < 1) return { get: () => {}, set: () => {} };
		let t = 0,
			n = Object.create(null),
			o = Object.create(null);
		const r = (s, i) => {
			(n[s] = i), t++, t > e && ((t = 0), (o = n), (n = Object.create(null)));
		};
		return {
			get(s) {
				let i = n[s];
				if (i !== void 0) return i;
				if ((i = o[s]) !== void 0) return r(s, i), i;
			},
			set(s, i) {
				s in n ? (n[s] = i) : r(s, i);
			},
		};
	},
	xn = "!",
	xo = ":",
	rc = [],
	wo = (e, t, n, o, r) => ({
		modifiers: e,
		hasImportantModifier: t,
		baseClassName: n,
		maybePostfixModifierPosition: o,
		isExternal: r,
	}),
	sc = (e) => {
		const { prefix: t, experimentalParseClassName: n } = e;
		let o = (r) => {
			const s = [];
			let i = 0,
				a = 0,
				l = 0,
				u;
			const f = r.length;
			for (let m = 0; m < f; m++) {
				const x = r[m];
				if (i === 0 && a === 0) {
					if (x === xo) {
						s.push(r.slice(l, m)), (l = m + 1);
						continue;
					}
					if (x === "/") {
						u = m;
						continue;
					}
				}
				x === "[" ? i++ : x === "]" ? i-- : x === "(" ? a++ : x === ")" && a--;
			}
			const d = s.length === 0 ? r : r.slice(l);
			let g = d,
				v = !1;
			d.endsWith(xn)
				? ((g = d.slice(0, -1)), (v = !0))
				: d.startsWith(xn) && ((g = d.slice(1)), (v = !0));
			const h = u && u > l ? u - l : void 0;
			return wo(s, v, g, h);
		};
		if (t) {
			const r = t + xo,
				s = o;
			o = (i) =>
				i.startsWith(r) ? s(i.slice(r.length)) : wo(rc, !1, i, void 0, !0);
		}
		if (n) {
			const r = o;
			o = (s) => n({ className: s, parseClassName: r });
		}
		return o;
	},
	ic = (e) => {
		const t = new Map();
		return (
			e.orderSensitiveModifiers.forEach((n, o) => {
				t.set(n, 1e6 + o);
			}),
			(n) => {
				const o = [];
				let r = [];
				for (let s = 0; s < n.length; s++) {
					const i = n[s],
						a = i[0] === "[",
						l = t.has(i);
					a || l
						? (r.length > 0 && (r.sort(), o.push(...r), (r = [])), o.push(i))
						: r.push(i);
				}
				return r.length > 0 && (r.sort(), o.push(...r)), o;
			}
		);
	},
	ac = (e) => ({
		cache: oc(e.cacheSize),
		parseClassName: sc(e),
		sortModifiers: ic(e),
		...Ya(e),
	}),
	cc = /\s+/,
	lc = (e, t) => {
		const {
				parseClassName: n,
				getClassGroupId: o,
				getConflictingClassGroupIds: r,
				sortModifiers: s,
			} = t,
			i = [],
			a = e.trim().split(cc);
		let l = "";
		for (let u = a.length - 1; u >= 0; u -= 1) {
			const f = a[u],
				{
					isExternal: d,
					modifiers: g,
					hasImportantModifier: v,
					baseClassName: h,
					maybePostfixModifierPosition: m,
				} = n(f);
			if (d) {
				l = f + (l.length > 0 ? " " + l : l);
				continue;
			}
			let x = !!m,
				w = o(x ? h.substring(0, m) : h);
			if (!w) {
				if (!x) {
					l = f + (l.length > 0 ? " " + l : l);
					continue;
				}
				if (((w = o(h)), !w)) {
					l = f + (l.length > 0 ? " " + l : l);
					continue;
				}
				x = !1;
			}
			const b = g.length === 0 ? "" : g.length === 1 ? g[0] : s(g).join(":"),
				y = v ? b + xn : b,
				C = y + w;
			if (i.indexOf(C) > -1) continue;
			i.push(C);
			const P = r(w, x);
			for (let T = 0; T < P.length; ++T) {
				const R = P[T];
				i.push(y + R);
			}
			l = f + (l.length > 0 ? " " + l : l);
		}
		return l;
	},
	uc = (...e) => {
		let t = 0,
			n,
			o,
			r = "";
		for (; t < e.length; )
			(n = e[t++]) && (o = sr(n)) && (r && (r += " "), (r += o));
		return r;
	},
	sr = (e) => {
		if (typeof e == "string") return e;
		let t,
			n = "";
		for (let o = 0; o < e.length; o++)
			e[o] && (t = sr(e[o])) && (n && (n += " "), (n += t));
		return n;
	},
	dc = (e, ...t) => {
		let n, o, r, s;
		const i = (l) => {
				const u = t.reduce((f, d) => d(f), e());
				return (n = ac(u)), (o = n.cache.get), (r = n.cache.set), (s = a), a(l);
			},
			a = (l) => {
				const u = o(l);
				if (u) return u;
				const f = lc(l, n);
				return r(l, f), f;
			};
		return (s = i), (...l) => s(uc(...l));
	},
	fc = [],
	J = (e) => {
		const t = (n) => n[e] || fc;
		return (t.isThemeGetter = !0), t;
	},
	ir = /^\[(?:(\w[\w-]*):)?(.+)\]$/i,
	ar = /^\((?:(\w[\w-]*):)?(.+)\)$/i,
	pc = /^\d+\/\d+$/,
	mc = /^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/,
	gc =
		/\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/,
	hc = /^(rgba?|hsla?|hwb|(ok)?(lab|lch)|color-mix)\(.+\)$/,
	vc = /^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/,
	xc =
		/^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/,
	Be = (e) => pc.test(e),
	j = (e) => !!e && !Number.isNaN(Number(e)),
	Re = (e) => !!e && Number.isInteger(Number(e)),
	sn = (e) => e.endsWith("%") && j(e.slice(0, -1)),
	Se = (e) => mc.test(e),
	wc = () => !0,
	bc = (e) => gc.test(e) && !hc.test(e),
	cr = () => !1,
	yc = (e) => vc.test(e),
	Cc = (e) => xc.test(e),
	Sc = (e) => !M(e) && !I(e),
	Ec = (e) => Ye(e, dr, cr),
	M = (e) => ir.test(e),
	Oe = (e) => Ye(e, fr, bc),
	an = (e) => Ye(e, Ac, j),
	bo = (e) => Ye(e, lr, cr),
	Pc = (e) => Ye(e, ur, Cc),
	ht = (e) => Ye(e, pr, yc),
	I = (e) => ar.test(e),
	et = (e) => Xe(e, fr),
	Rc = (e) => Xe(e, Mc),
	yo = (e) => Xe(e, lr),
	_c = (e) => Xe(e, dr),
	Nc = (e) => Xe(e, ur),
	vt = (e) => Xe(e, pr, !0),
	Ye = (e, t, n) => {
		const o = ir.exec(e);
		return o ? (o[1] ? t(o[1]) : n(o[2])) : !1;
	},
	Xe = (e, t, n = !1) => {
		const o = ar.exec(e);
		return o ? (o[1] ? t(o[1]) : n) : !1;
	},
	lr = (e) => e === "position" || e === "percentage",
	ur = (e) => e === "image" || e === "url",
	dr = (e) => e === "length" || e === "size" || e === "bg-size",
	fr = (e) => e === "length",
	Ac = (e) => e === "number",
	Mc = (e) => e === "family-name",
	pr = (e) => e === "shadow",
	Ic = () => {
		const e = J("color"),
			t = J("font"),
			n = J("text"),
			o = J("font-weight"),
			r = J("tracking"),
			s = J("leading"),
			i = J("breakpoint"),
			a = J("container"),
			l = J("spacing"),
			u = J("radius"),
			f = J("shadow"),
			d = J("inset-shadow"),
			g = J("text-shadow"),
			v = J("drop-shadow"),
			h = J("blur"),
			m = J("perspective"),
			x = J("aspect"),
			w = J("ease"),
			b = J("animate"),
			y = () => [
				"auto",
				"avoid",
				"all",
				"avoid-page",
				"page",
				"left",
				"right",
				"column",
			],
			C = () => [
				"center",
				"top",
				"bottom",
				"left",
				"right",
				"top-left",
				"left-top",
				"top-right",
				"right-top",
				"bottom-right",
				"right-bottom",
				"bottom-left",
				"left-bottom",
			],
			P = () => [...C(), I, M],
			T = () => ["auto", "hidden", "clip", "visible", "scroll"],
			R = () => ["auto", "contain", "none"],
			E = () => [I, M, l],
			O = () => [Be, "full", "auto", ...E()],
			D = () => [Re, "none", "subgrid", I, M],
			$ = () => ["auto", { span: ["full", Re, I, M] }, Re, I, M],
			L = () => [Re, "auto", I, M],
			V = () => ["auto", "min", "max", "fr", I, M],
			F = () => [
				"start",
				"end",
				"center",
				"between",
				"around",
				"evenly",
				"stretch",
				"baseline",
				"center-safe",
				"end-safe",
			],
			W = () => [
				"start",
				"end",
				"center",
				"stretch",
				"center-safe",
				"end-safe",
			],
			k = () => ["auto", ...E()],
			B = () => [
				Be,
				"auto",
				"full",
				"dvw",
				"dvh",
				"lvw",
				"lvh",
				"svw",
				"svh",
				"min",
				"max",
				"fit",
				...E(),
			],
			S = () => [e, I, M],
			N = () => [...C(), yo, bo, { position: [I, M] }],
			Z = () => ["no-repeat", { repeat: ["", "x", "y", "space", "round"] }],
			te = () => ["auto", "cover", "contain", _c, Ec, { size: [I, M] }],
			re = () => [sn, et, Oe],
			X = () => ["", "none", "full", u, I, M],
			Y = () => ["", j, et, Oe],
			se = () => ["solid", "dashed", "dotted", "double"],
			oe = () => [
				"normal",
				"multiply",
				"screen",
				"overlay",
				"darken",
				"lighten",
				"color-dodge",
				"color-burn",
				"hard-light",
				"soft-light",
				"difference",
				"exclusion",
				"hue",
				"saturation",
				"color",
				"luminosity",
			],
			_ = () => [j, sn, yo, bo],
			U = () => ["", "none", h, I, M],
			Q = () => ["none", j, I, M],
			H = () => ["none", j, I, M],
			K = () => [j, I, M],
			q = () => [Be, "full", ...E()];
		return {
			cacheSize: 500,
			theme: {
				animate: ["spin", "ping", "pulse", "bounce"],
				aspect: ["video"],
				blur: [Se],
				breakpoint: [Se],
				color: [wc],
				container: [Se],
				"drop-shadow": [Se],
				ease: ["in", "out", "in-out"],
				font: [Sc],
				"font-weight": [
					"thin",
					"extralight",
					"light",
					"normal",
					"medium",
					"semibold",
					"bold",
					"extrabold",
					"black",
				],
				"inset-shadow": [Se],
				leading: ["none", "tight", "snug", "normal", "relaxed", "loose"],
				perspective: [
					"dramatic",
					"near",
					"normal",
					"midrange",
					"distant",
					"none",
				],
				radius: [Se],
				shadow: [Se],
				spacing: ["px", j],
				text: [Se],
				"text-shadow": [Se],
				tracking: ["tighter", "tight", "normal", "wide", "wider", "widest"],
			},
			classGroups: {
				aspect: [{ aspect: ["auto", "square", Be, M, I, x] }],
				container: ["container"],
				columns: [{ columns: [j, M, I, a] }],
				"break-after": [{ "break-after": y() }],
				"break-before": [{ "break-before": y() }],
				"break-inside": [
					{ "break-inside": ["auto", "avoid", "avoid-page", "avoid-column"] },
				],
				"box-decoration": [{ "box-decoration": ["slice", "clone"] }],
				box: [{ box: ["border", "content"] }],
				display: [
					"block",
					"inline-block",
					"inline",
					"flex",
					"inline-flex",
					"table",
					"inline-table",
					"table-caption",
					"table-cell",
					"table-column",
					"table-column-group",
					"table-footer-group",
					"table-header-group",
					"table-row-group",
					"table-row",
					"flow-root",
					"grid",
					"inline-grid",
					"contents",
					"list-item",
					"hidden",
				],
				sr: ["sr-only", "not-sr-only"],
				float: [{ float: ["right", "left", "none", "start", "end"] }],
				clear: [{ clear: ["left", "right", "both", "none", "start", "end"] }],
				isolation: ["isolate", "isolation-auto"],
				"object-fit": [
					{ object: ["contain", "cover", "fill", "none", "scale-down"] },
				],
				"object-position": [{ object: P() }],
				overflow: [{ overflow: T() }],
				"overflow-x": [{ "overflow-x": T() }],
				"overflow-y": [{ "overflow-y": T() }],
				overscroll: [{ overscroll: R() }],
				"overscroll-x": [{ "overscroll-x": R() }],
				"overscroll-y": [{ "overscroll-y": R() }],
				position: ["static", "fixed", "absolute", "relative", "sticky"],
				inset: [{ inset: O() }],
				"inset-x": [{ "inset-x": O() }],
				"inset-y": [{ "inset-y": O() }],
				start: [{ start: O() }],
				end: [{ end: O() }],
				top: [{ top: O() }],
				right: [{ right: O() }],
				bottom: [{ bottom: O() }],
				left: [{ left: O() }],
				visibility: ["visible", "invisible", "collapse"],
				z: [{ z: [Re, "auto", I, M] }],
				basis: [{ basis: [Be, "full", "auto", a, ...E()] }],
				"flex-direction": [
					{ flex: ["row", "row-reverse", "col", "col-reverse"] },
				],
				"flex-wrap": [{ flex: ["nowrap", "wrap", "wrap-reverse"] }],
				flex: [{ flex: [j, Be, "auto", "initial", "none", M] }],
				grow: [{ grow: ["", j, I, M] }],
				shrink: [{ shrink: ["", j, I, M] }],
				order: [{ order: [Re, "first", "last", "none", I, M] }],
				"grid-cols": [{ "grid-cols": D() }],
				"col-start-end": [{ col: $() }],
				"col-start": [{ "col-start": L() }],
				"col-end": [{ "col-end": L() }],
				"grid-rows": [{ "grid-rows": D() }],
				"row-start-end": [{ row: $() }],
				"row-start": [{ "row-start": L() }],
				"row-end": [{ "row-end": L() }],
				"grid-flow": [
					{ "grid-flow": ["row", "col", "dense", "row-dense", "col-dense"] },
				],
				"auto-cols": [{ "auto-cols": V() }],
				"auto-rows": [{ "auto-rows": V() }],
				gap: [{ gap: E() }],
				"gap-x": [{ "gap-x": E() }],
				"gap-y": [{ "gap-y": E() }],
				"justify-content": [{ justify: [...F(), "normal"] }],
				"justify-items": [{ "justify-items": [...W(), "normal"] }],
				"justify-self": [{ "justify-self": ["auto", ...W()] }],
				"align-content": [{ content: ["normal", ...F()] }],
				"align-items": [{ items: [...W(), { baseline: ["", "last"] }] }],
				"align-self": [{ self: ["auto", ...W(), { baseline: ["", "last"] }] }],
				"place-content": [{ "place-content": F() }],
				"place-items": [{ "place-items": [...W(), "baseline"] }],
				"place-self": [{ "place-self": ["auto", ...W()] }],
				p: [{ p: E() }],
				px: [{ px: E() }],
				py: [{ py: E() }],
				ps: [{ ps: E() }],
				pe: [{ pe: E() }],
				pt: [{ pt: E() }],
				pr: [{ pr: E() }],
				pb: [{ pb: E() }],
				pl: [{ pl: E() }],
				m: [{ m: k() }],
				mx: [{ mx: k() }],
				my: [{ my: k() }],
				ms: [{ ms: k() }],
				me: [{ me: k() }],
				mt: [{ mt: k() }],
				mr: [{ mr: k() }],
				mb: [{ mb: k() }],
				ml: [{ ml: k() }],
				"space-x": [{ "space-x": E() }],
				"space-x-reverse": ["space-x-reverse"],
				"space-y": [{ "space-y": E() }],
				"space-y-reverse": ["space-y-reverse"],
				size: [{ size: B() }],
				w: [{ w: [a, "screen", ...B()] }],
				"min-w": [{ "min-w": [a, "screen", "none", ...B()] }],
				"max-w": [
					{ "max-w": [a, "screen", "none", "prose", { screen: [i] }, ...B()] },
				],
				h: [{ h: ["screen", "lh", ...B()] }],
				"min-h": [{ "min-h": ["screen", "lh", "none", ...B()] }],
				"max-h": [{ "max-h": ["screen", "lh", ...B()] }],
				"font-size": [{ text: ["base", n, et, Oe] }],
				"font-smoothing": ["antialiased", "subpixel-antialiased"],
				"font-style": ["italic", "not-italic"],
				"font-weight": [{ font: [o, I, an] }],
				"font-stretch": [
					{
						"font-stretch": [
							"ultra-condensed",
							"extra-condensed",
							"condensed",
							"semi-condensed",
							"normal",
							"semi-expanded",
							"expanded",
							"extra-expanded",
							"ultra-expanded",
							sn,
							M,
						],
					},
				],
				"font-family": [{ font: [Rc, M, t] }],
				"fvn-normal": ["normal-nums"],
				"fvn-ordinal": ["ordinal"],
				"fvn-slashed-zero": ["slashed-zero"],
				"fvn-figure": ["lining-nums", "oldstyle-nums"],
				"fvn-spacing": ["proportional-nums", "tabular-nums"],
				"fvn-fraction": ["diagonal-fractions", "stacked-fractions"],
				tracking: [{ tracking: [r, I, M] }],
				"line-clamp": [{ "line-clamp": [j, "none", I, an] }],
				leading: [{ leading: [s, ...E()] }],
				"list-image": [{ "list-image": ["none", I, M] }],
				"list-style-position": [{ list: ["inside", "outside"] }],
				"list-style-type": [{ list: ["disc", "decimal", "none", I, M] }],
				"text-alignment": [
					{ text: ["left", "center", "right", "justify", "start", "end"] },
				],
				"placeholder-color": [{ placeholder: S() }],
				"text-color": [{ text: S() }],
				"text-decoration": [
					"underline",
					"overline",
					"line-through",
					"no-underline",
				],
				"text-decoration-style": [{ decoration: [...se(), "wavy"] }],
				"text-decoration-thickness": [
					{ decoration: [j, "from-font", "auto", I, Oe] },
				],
				"text-decoration-color": [{ decoration: S() }],
				"underline-offset": [{ "underline-offset": [j, "auto", I, M] }],
				"text-transform": [
					"uppercase",
					"lowercase",
					"capitalize",
					"normal-case",
				],
				"text-overflow": ["truncate", "text-ellipsis", "text-clip"],
				"text-wrap": [{ text: ["wrap", "nowrap", "balance", "pretty"] }],
				indent: [{ indent: E() }],
				"vertical-align": [
					{
						align: [
							"baseline",
							"top",
							"middle",
							"bottom",
							"text-top",
							"text-bottom",
							"sub",
							"super",
							I,
							M,
						],
					},
				],
				whitespace: [
					{
						whitespace: [
							"normal",
							"nowrap",
							"pre",
							"pre-line",
							"pre-wrap",
							"break-spaces",
						],
					},
				],
				break: [{ break: ["normal", "words", "all", "keep"] }],
				wrap: [{ wrap: ["break-word", "anywhere", "normal"] }],
				hyphens: [{ hyphens: ["none", "manual", "auto"] }],
				content: [{ content: ["none", I, M] }],
				"bg-attachment": [{ bg: ["fixed", "local", "scroll"] }],
				"bg-clip": [{ "bg-clip": ["border", "padding", "content", "text"] }],
				"bg-origin": [{ "bg-origin": ["border", "padding", "content"] }],
				"bg-position": [{ bg: N() }],
				"bg-repeat": [{ bg: Z() }],
				"bg-size": [{ bg: te() }],
				"bg-image": [
					{
						bg: [
							"none",
							{
								linear: [
									{ to: ["t", "tr", "r", "br", "b", "bl", "l", "tl"] },
									Re,
									I,
									M,
								],
								radial: ["", I, M],
								conic: [Re, I, M],
							},
							Nc,
							Pc,
						],
					},
				],
				"bg-color": [{ bg: S() }],
				"gradient-from-pos": [{ from: re() }],
				"gradient-via-pos": [{ via: re() }],
				"gradient-to-pos": [{ to: re() }],
				"gradient-from": [{ from: S() }],
				"gradient-via": [{ via: S() }],
				"gradient-to": [{ to: S() }],
				rounded: [{ rounded: X() }],
				"rounded-s": [{ "rounded-s": X() }],
				"rounded-e": [{ "rounded-e": X() }],
				"rounded-t": [{ "rounded-t": X() }],
				"rounded-r": [{ "rounded-r": X() }],
				"rounded-b": [{ "rounded-b": X() }],
				"rounded-l": [{ "rounded-l": X() }],
				"rounded-ss": [{ "rounded-ss": X() }],
				"rounded-se": [{ "rounded-se": X() }],
				"rounded-ee": [{ "rounded-ee": X() }],
				"rounded-es": [{ "rounded-es": X() }],
				"rounded-tl": [{ "rounded-tl": X() }],
				"rounded-tr": [{ "rounded-tr": X() }],
				"rounded-br": [{ "rounded-br": X() }],
				"rounded-bl": [{ "rounded-bl": X() }],
				"border-w": [{ border: Y() }],
				"border-w-x": [{ "border-x": Y() }],
				"border-w-y": [{ "border-y": Y() }],
				"border-w-s": [{ "border-s": Y() }],
				"border-w-e": [{ "border-e": Y() }],
				"border-w-t": [{ "border-t": Y() }],
				"border-w-r": [{ "border-r": Y() }],
				"border-w-b": [{ "border-b": Y() }],
				"border-w-l": [{ "border-l": Y() }],
				"divide-x": [{ "divide-x": Y() }],
				"divide-x-reverse": ["divide-x-reverse"],
				"divide-y": [{ "divide-y": Y() }],
				"divide-y-reverse": ["divide-y-reverse"],
				"border-style": [{ border: [...se(), "hidden", "none"] }],
				"divide-style": [{ divide: [...se(), "hidden", "none"] }],
				"border-color": [{ border: S() }],
				"border-color-x": [{ "border-x": S() }],
				"border-color-y": [{ "border-y": S() }],
				"border-color-s": [{ "border-s": S() }],
				"border-color-e": [{ "border-e": S() }],
				"border-color-t": [{ "border-t": S() }],
				"border-color-r": [{ "border-r": S() }],
				"border-color-b": [{ "border-b": S() }],
				"border-color-l": [{ "border-l": S() }],
				"divide-color": [{ divide: S() }],
				"outline-style": [{ outline: [...se(), "none", "hidden"] }],
				"outline-offset": [{ "outline-offset": [j, I, M] }],
				"outline-w": [{ outline: ["", j, et, Oe] }],
				"outline-color": [{ outline: S() }],
				shadow: [{ shadow: ["", "none", f, vt, ht] }],
				"shadow-color": [{ shadow: S() }],
				"inset-shadow": [{ "inset-shadow": ["none", d, vt, ht] }],
				"inset-shadow-color": [{ "inset-shadow": S() }],
				"ring-w": [{ ring: Y() }],
				"ring-w-inset": ["ring-inset"],
				"ring-color": [{ ring: S() }],
				"ring-offset-w": [{ "ring-offset": [j, Oe] }],
				"ring-offset-color": [{ "ring-offset": S() }],
				"inset-ring-w": [{ "inset-ring": Y() }],
				"inset-ring-color": [{ "inset-ring": S() }],
				"text-shadow": [{ "text-shadow": ["none", g, vt, ht] }],
				"text-shadow-color": [{ "text-shadow": S() }],
				opacity: [{ opacity: [j, I, M] }],
				"mix-blend": [
					{ "mix-blend": [...oe(), "plus-darker", "plus-lighter"] },
				],
				"bg-blend": [{ "bg-blend": oe() }],
				"mask-clip": [
					{
						"mask-clip": [
							"border",
							"padding",
							"content",
							"fill",
							"stroke",
							"view",
						],
					},
					"mask-no-clip",
				],
				"mask-composite": [
					{ mask: ["add", "subtract", "intersect", "exclude"] },
				],
				"mask-image-linear-pos": [{ "mask-linear": [j] }],
				"mask-image-linear-from-pos": [{ "mask-linear-from": _() }],
				"mask-image-linear-to-pos": [{ "mask-linear-to": _() }],
				"mask-image-linear-from-color": [{ "mask-linear-from": S() }],
				"mask-image-linear-to-color": [{ "mask-linear-to": S() }],
				"mask-image-t-from-pos": [{ "mask-t-from": _() }],
				"mask-image-t-to-pos": [{ "mask-t-to": _() }],
				"mask-image-t-from-color": [{ "mask-t-from": S() }],
				"mask-image-t-to-color": [{ "mask-t-to": S() }],
				"mask-image-r-from-pos": [{ "mask-r-from": _() }],
				"mask-image-r-to-pos": [{ "mask-r-to": _() }],
				"mask-image-r-from-color": [{ "mask-r-from": S() }],
				"mask-image-r-to-color": [{ "mask-r-to": S() }],
				"mask-image-b-from-pos": [{ "mask-b-from": _() }],
				"mask-image-b-to-pos": [{ "mask-b-to": _() }],
				"mask-image-b-from-color": [{ "mask-b-from": S() }],
				"mask-image-b-to-color": [{ "mask-b-to": S() }],
				"mask-image-l-from-pos": [{ "mask-l-from": _() }],
				"mask-image-l-to-pos": [{ "mask-l-to": _() }],
				"mask-image-l-from-color": [{ "mask-l-from": S() }],
				"mask-image-l-to-color": [{ "mask-l-to": S() }],
				"mask-image-x-from-pos": [{ "mask-x-from": _() }],
				"mask-image-x-to-pos": [{ "mask-x-to": _() }],
				"mask-image-x-from-color": [{ "mask-x-from": S() }],
				"mask-image-x-to-color": [{ "mask-x-to": S() }],
				"mask-image-y-from-pos": [{ "mask-y-from": _() }],
				"mask-image-y-to-pos": [{ "mask-y-to": _() }],
				"mask-image-y-from-color": [{ "mask-y-from": S() }],
				"mask-image-y-to-color": [{ "mask-y-to": S() }],
				"mask-image-radial": [{ "mask-radial": [I, M] }],
				"mask-image-radial-from-pos": [{ "mask-radial-from": _() }],
				"mask-image-radial-to-pos": [{ "mask-radial-to": _() }],
				"mask-image-radial-from-color": [{ "mask-radial-from": S() }],
				"mask-image-radial-to-color": [{ "mask-radial-to": S() }],
				"mask-image-radial-shape": [{ "mask-radial": ["circle", "ellipse"] }],
				"mask-image-radial-size": [
					{
						"mask-radial": [
							{ closest: ["side", "corner"], farthest: ["side", "corner"] },
						],
					},
				],
				"mask-image-radial-pos": [{ "mask-radial-at": C() }],
				"mask-image-conic-pos": [{ "mask-conic": [j] }],
				"mask-image-conic-from-pos": [{ "mask-conic-from": _() }],
				"mask-image-conic-to-pos": [{ "mask-conic-to": _() }],
				"mask-image-conic-from-color": [{ "mask-conic-from": S() }],
				"mask-image-conic-to-color": [{ "mask-conic-to": S() }],
				"mask-mode": [{ mask: ["alpha", "luminance", "match"] }],
				"mask-origin": [
					{
						"mask-origin": [
							"border",
							"padding",
							"content",
							"fill",
							"stroke",
							"view",
						],
					},
				],
				"mask-position": [{ mask: N() }],
				"mask-repeat": [{ mask: Z() }],
				"mask-size": [{ mask: te() }],
				"mask-type": [{ "mask-type": ["alpha", "luminance"] }],
				"mask-image": [{ mask: ["none", I, M] }],
				filter: [{ filter: ["", "none", I, M] }],
				blur: [{ blur: U() }],
				brightness: [{ brightness: [j, I, M] }],
				contrast: [{ contrast: [j, I, M] }],
				"drop-shadow": [{ "drop-shadow": ["", "none", v, vt, ht] }],
				"drop-shadow-color": [{ "drop-shadow": S() }],
				grayscale: [{ grayscale: ["", j, I, M] }],
				"hue-rotate": [{ "hue-rotate": [j, I, M] }],
				invert: [{ invert: ["", j, I, M] }],
				saturate: [{ saturate: [j, I, M] }],
				sepia: [{ sepia: ["", j, I, M] }],
				"backdrop-filter": [{ "backdrop-filter": ["", "none", I, M] }],
				"backdrop-blur": [{ "backdrop-blur": U() }],
				"backdrop-brightness": [{ "backdrop-brightness": [j, I, M] }],
				"backdrop-contrast": [{ "backdrop-contrast": [j, I, M] }],
				"backdrop-grayscale": [{ "backdrop-grayscale": ["", j, I, M] }],
				"backdrop-hue-rotate": [{ "backdrop-hue-rotate": [j, I, M] }],
				"backdrop-invert": [{ "backdrop-invert": ["", j, I, M] }],
				"backdrop-opacity": [{ "backdrop-opacity": [j, I, M] }],
				"backdrop-saturate": [{ "backdrop-saturate": [j, I, M] }],
				"backdrop-sepia": [{ "backdrop-sepia": ["", j, I, M] }],
				"border-collapse": [{ border: ["collapse", "separate"] }],
				"border-spacing": [{ "border-spacing": E() }],
				"border-spacing-x": [{ "border-spacing-x": E() }],
				"border-spacing-y": [{ "border-spacing-y": E() }],
				"table-layout": [{ table: ["auto", "fixed"] }],
				caption: [{ caption: ["top", "bottom"] }],
				transition: [
					{
						transition: [
							"",
							"all",
							"colors",
							"opacity",
							"shadow",
							"transform",
							"none",
							I,
							M,
						],
					},
				],
				"transition-behavior": [{ transition: ["normal", "discrete"] }],
				duration: [{ duration: [j, "initial", I, M] }],
				ease: [{ ease: ["linear", "initial", w, I, M] }],
				delay: [{ delay: [j, I, M] }],
				animate: [{ animate: ["none", b, I, M] }],
				backface: [{ backface: ["hidden", "visible"] }],
				perspective: [{ perspective: [m, I, M] }],
				"perspective-origin": [{ "perspective-origin": P() }],
				rotate: [{ rotate: Q() }],
				"rotate-x": [{ "rotate-x": Q() }],
				"rotate-y": [{ "rotate-y": Q() }],
				"rotate-z": [{ "rotate-z": Q() }],
				scale: [{ scale: H() }],
				"scale-x": [{ "scale-x": H() }],
				"scale-y": [{ "scale-y": H() }],
				"scale-z": [{ "scale-z": H() }],
				"scale-3d": ["scale-3d"],
				skew: [{ skew: K() }],
				"skew-x": [{ "skew-x": K() }],
				"skew-y": [{ "skew-y": K() }],
				transform: [{ transform: [I, M, "", "none", "gpu", "cpu"] }],
				"transform-origin": [{ origin: P() }],
				"transform-style": [{ transform: ["3d", "flat"] }],
				translate: [{ translate: q() }],
				"translate-x": [{ "translate-x": q() }],
				"translate-y": [{ "translate-y": q() }],
				"translate-z": [{ "translate-z": q() }],
				"translate-none": ["translate-none"],
				accent: [{ accent: S() }],
				appearance: [{ appearance: ["none", "auto"] }],
				"caret-color": [{ caret: S() }],
				"color-scheme": [
					{
						scheme: [
							"normal",
							"dark",
							"light",
							"light-dark",
							"only-dark",
							"only-light",
						],
					},
				],
				cursor: [
					{
						cursor: [
							"auto",
							"default",
							"pointer",
							"wait",
							"text",
							"move",
							"help",
							"not-allowed",
							"none",
							"context-menu",
							"progress",
							"cell",
							"crosshair",
							"vertical-text",
							"alias",
							"copy",
							"no-drop",
							"grab",
							"grabbing",
							"all-scroll",
							"col-resize",
							"row-resize",
							"n-resize",
							"e-resize",
							"s-resize",
							"w-resize",
							"ne-resize",
							"nw-resize",
							"se-resize",
							"sw-resize",
							"ew-resize",
							"ns-resize",
							"nesw-resize",
							"nwse-resize",
							"zoom-in",
							"zoom-out",
							I,
							M,
						],
					},
				],
				"field-sizing": [{ "field-sizing": ["fixed", "content"] }],
				"pointer-events": [{ "pointer-events": ["auto", "none"] }],
				resize: [{ resize: ["none", "", "y", "x"] }],
				"scroll-behavior": [{ scroll: ["auto", "smooth"] }],
				"scroll-m": [{ "scroll-m": E() }],
				"scroll-mx": [{ "scroll-mx": E() }],
				"scroll-my": [{ "scroll-my": E() }],
				"scroll-ms": [{ "scroll-ms": E() }],
				"scroll-me": [{ "scroll-me": E() }],
				"scroll-mt": [{ "scroll-mt": E() }],
				"scroll-mr": [{ "scroll-mr": E() }],
				"scroll-mb": [{ "scroll-mb": E() }],
				"scroll-ml": [{ "scroll-ml": E() }],
				"scroll-p": [{ "scroll-p": E() }],
				"scroll-px": [{ "scroll-px": E() }],
				"scroll-py": [{ "scroll-py": E() }],
				"scroll-ps": [{ "scroll-ps": E() }],
				"scroll-pe": [{ "scroll-pe": E() }],
				"scroll-pt": [{ "scroll-pt": E() }],
				"scroll-pr": [{ "scroll-pr": E() }],
				"scroll-pb": [{ "scroll-pb": E() }],
				"scroll-pl": [{ "scroll-pl": E() }],
				"snap-align": [{ snap: ["start", "end", "center", "align-none"] }],
				"snap-stop": [{ snap: ["normal", "always"] }],
				"snap-type": [{ snap: ["none", "x", "y", "both"] }],
				"snap-strictness": [{ snap: ["mandatory", "proximity"] }],
				touch: [{ touch: ["auto", "none", "manipulation"] }],
				"touch-x": [{ "touch-pan": ["x", "left", "right"] }],
				"touch-y": [{ "touch-pan": ["y", "up", "down"] }],
				"touch-pz": ["touch-pinch-zoom"],
				select: [{ select: ["none", "text", "all", "auto"] }],
				"will-change": [
					{ "will-change": ["auto", "scroll", "contents", "transform", I, M] },
				],
				fill: [{ fill: ["none", ...S()] }],
				"stroke-w": [{ stroke: [j, et, Oe, an] }],
				stroke: [{ stroke: ["none", ...S()] }],
				"forced-color-adjust": [{ "forced-color-adjust": ["auto", "none"] }],
			},
			conflictingClassGroups: {
				overflow: ["overflow-x", "overflow-y"],
				overscroll: ["overscroll-x", "overscroll-y"],
				inset: [
					"inset-x",
					"inset-y",
					"start",
					"end",
					"top",
					"right",
					"bottom",
					"left",
				],
				"inset-x": ["right", "left"],
				"inset-y": ["top", "bottom"],
				flex: ["basis", "grow", "shrink"],
				gap: ["gap-x", "gap-y"],
				p: ["px", "py", "ps", "pe", "pt", "pr", "pb", "pl"],
				px: ["pr", "pl"],
				py: ["pt", "pb"],
				m: ["mx", "my", "ms", "me", "mt", "mr", "mb", "ml"],
				mx: ["mr", "ml"],
				my: ["mt", "mb"],
				size: ["w", "h"],
				"font-size": ["leading"],
				"fvn-normal": [
					"fvn-ordinal",
					"fvn-slashed-zero",
					"fvn-figure",
					"fvn-spacing",
					"fvn-fraction",
				],
				"fvn-ordinal": ["fvn-normal"],
				"fvn-slashed-zero": ["fvn-normal"],
				"fvn-figure": ["fvn-normal"],
				"fvn-spacing": ["fvn-normal"],
				"fvn-fraction": ["fvn-normal"],
				"line-clamp": ["display", "overflow"],
				rounded: [
					"rounded-s",
					"rounded-e",
					"rounded-t",
					"rounded-r",
					"rounded-b",
					"rounded-l",
					"rounded-ss",
					"rounded-se",
					"rounded-ee",
					"rounded-es",
					"rounded-tl",
					"rounded-tr",
					"rounded-br",
					"rounded-bl",
				],
				"rounded-s": ["rounded-ss", "rounded-es"],
				"rounded-e": ["rounded-se", "rounded-ee"],
				"rounded-t": ["rounded-tl", "rounded-tr"],
				"rounded-r": ["rounded-tr", "rounded-br"],
				"rounded-b": ["rounded-br", "rounded-bl"],
				"rounded-l": ["rounded-tl", "rounded-bl"],
				"border-spacing": ["border-spacing-x", "border-spacing-y"],
				"border-w": [
					"border-w-x",
					"border-w-y",
					"border-w-s",
					"border-w-e",
					"border-w-t",
					"border-w-r",
					"border-w-b",
					"border-w-l",
				],
				"border-w-x": ["border-w-r", "border-w-l"],
				"border-w-y": ["border-w-t", "border-w-b"],
				"border-color": [
					"border-color-x",
					"border-color-y",
					"border-color-s",
					"border-color-e",
					"border-color-t",
					"border-color-r",
					"border-color-b",
					"border-color-l",
				],
				"border-color-x": ["border-color-r", "border-color-l"],
				"border-color-y": ["border-color-t", "border-color-b"],
				translate: ["translate-x", "translate-y", "translate-none"],
				"translate-none": [
					"translate",
					"translate-x",
					"translate-y",
					"translate-z",
				],
				"scroll-m": [
					"scroll-mx",
					"scroll-my",
					"scroll-ms",
					"scroll-me",
					"scroll-mt",
					"scroll-mr",
					"scroll-mb",
					"scroll-ml",
				],
				"scroll-mx": ["scroll-mr", "scroll-ml"],
				"scroll-my": ["scroll-mt", "scroll-mb"],
				"scroll-p": [
					"scroll-px",
					"scroll-py",
					"scroll-ps",
					"scroll-pe",
					"scroll-pt",
					"scroll-pr",
					"scroll-pb",
					"scroll-pl",
				],
				"scroll-px": ["scroll-pr", "scroll-pl"],
				"scroll-py": ["scroll-pt", "scroll-pb"],
				touch: ["touch-x", "touch-y", "touch-pz"],
				"touch-x": ["touch"],
				"touch-y": ["touch"],
				"touch-pz": ["touch"],
			},
			conflictingClassGroupModifiers: { "font-size": ["leading"] },
			orderSensitiveModifiers: [
				"*",
				"**",
				"after",
				"backdrop",
				"before",
				"details-content",
				"file",
				"first-letter",
				"first-line",
				"marker",
				"placeholder",
				"selection",
			],
		};
	},
	Tc = dc(Ic);
function z(...e) {
	return Tc(er(e));
}
const kc = tr(
		"relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground",
		{
			variants: {
				variant: {
					default: "bg-background text-foreground",
					destructive:
						"border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
					success:
						"border-green-500/50 text-green-700 dark:text-green-400 [&>svg]:text-green-500",
					warning:
						"border-yellow-500/50 text-yellow-700 dark:text-yellow-400 [&>svg]:text-yellow-500",
				},
			},
			defaultVariants: { variant: "default" },
		},
	),
	mr = c.forwardRef(({ className: e, variant: t, ...n }, o) =>
		p.jsx("div", {
			ref: o,
			role: "alert",
			className: z(kc({ variant: t }), e),
			...n,
		}),
	);
mr.displayName = "Alert";
const gr = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("h5", {
		ref: n,
		className: z("mb-1 font-medium leading-none tracking-tight", e),
		...t,
	}),
);
gr.displayName = "AlertTitle";
const hr = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("div", {
		ref: n,
		className: z("text-sm [&_p]:leading-relaxed", e),
		...t,
	}),
);
hr.displayName = "AlertDescription";
mr.__docgenInfo = { description: "", methods: [], displayName: "Alert" };
gr.__docgenInfo = { description: "", methods: [], displayName: "AlertTitle" };
hr.__docgenInfo = {
	description: "",
	methods: [],
	displayName: "AlertDescription",
};
function vr(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i);
		a.displayName = s + "Context";
		const l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Oc(r, ...t)];
}
function Oc(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
function we(e) {
	const t = c.useRef(e);
	return (
		c.useEffect(() => {
			t.current = e;
		}),
		c.useMemo(
			() =>
				(...n) =>
					t.current?.(...n),
			[],
		)
	);
}
var ee = globalThis?.document ? c.useLayoutEffect : () => {};
function Co(e, t) {
	if (typeof e == "function") return e(t);
	e != null && (e.current = t);
}
function ct(...e) {
	return (t) => {
		let n = !1;
		const o = e.map((r) => {
			const s = Co(r, t);
			return !n && typeof s == "function" && (n = !0), s;
		});
		if (n)
			return () => {
				for (let r = 0; r < o.length; r++) {
					const s = o[r];
					typeof s == "function" ? s() : Co(e[r], null);
				}
			};
	};
}
function G(...e) {
	return c.useCallback(ct(...e), e);
}
var Dc = Symbol.for("react.lazy"),
	Nt = Tn[" use ".trim().toString()];
function jc(e) {
	return typeof e == "object" && e !== null && "then" in e;
}
function xr(e) {
	return (
		e != null &&
		typeof e == "object" &&
		"$$typeof" in e &&
		e.$$typeof === Dc &&
		"_payload" in e &&
		jc(e._payload)
	);
}
function $c(e) {
	const t = Lc(e),
		n = c.forwardRef((o, r) => {
			let { children: s, ...i } = o;
			xr(s) && typeof Nt == "function" && (s = Nt(s._payload));
			const a = c.Children.toArray(s),
				l = a.find(Bc);
			if (l) {
				const u = l.props.children,
					f = a.map((d) =>
						d === l
							? c.Children.count(u) > 1
								? c.Children.only(null)
								: c.isValidElement(u)
									? u.props.children
									: null
							: d,
					);
				return p.jsx(t, {
					...i,
					ref: r,
					children: c.isValidElement(u) ? c.cloneElement(u, void 0, f) : null,
				});
			}
			return p.jsx(t, { ...i, ref: r, children: s });
		});
	return (n.displayName = `${e}.Slot`), n;
}
function Lc(e) {
	const t = c.forwardRef((n, o) => {
		let { children: r, ...s } = n;
		if (
			(xr(r) && typeof Nt == "function" && (r = Nt(r._payload)),
			c.isValidElement(r))
		) {
			const i = Wc(r),
				a = Vc(s, r.props);
			return (
				r.type !== c.Fragment && (a.ref = o ? ct(o, i) : i),
				c.cloneElement(r, a)
			);
		}
		return c.Children.count(r) > 1 ? c.Children.only(null) : null;
	});
	return (t.displayName = `${e}.SlotClone`), t;
}
var Fc = Symbol("radix.slottable");
function Bc(e) {
	return (
		c.isValidElement(e) &&
		typeof e.type == "function" &&
		"__radixId" in e.type &&
		e.type.__radixId === Fc
	);
}
function Vc(e, t) {
	const n = { ...t };
	for (const o in t) {
		const r = e[o],
			s = t[o];
		/^on[A-Z]/.test(o)
			? r && s
				? (n[o] = (...a) => {
						const l = s(...a);
						return r(...a), l;
					})
				: r && (n[o] = r)
			: o === "style"
				? (n[o] = { ...r, ...s })
				: o === "className" && (n[o] = [r, s].filter(Boolean).join(" "));
	}
	return { ...e, ...n };
}
function Wc(e) {
	let t = Object.getOwnPropertyDescriptor(e.props, "ref")?.get,
		n = t && "isReactWarning" in t && t.isReactWarning;
	return n
		? e.ref
		: ((t = Object.getOwnPropertyDescriptor(e, "ref")?.get),
			(n = t && "isReactWarning" in t && t.isReactWarning),
			n ? e.props.ref : e.props.ref || e.ref);
}
var zc = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	lt = zc.reduce((e, t) => {
		const n = $c(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {});
function Hc() {
	return za.useSyncExternalStore(
		Gc,
		() => !0,
		() => !1,
	);
}
function Gc() {
	return () => {};
}
var On = "Avatar",
	[Uc] = vr(On),
	[Kc, wr] = Uc(On),
	br = c.forwardRef((e, t) => {
		const { __scopeAvatar: n, ...o } = e,
			[r, s] = c.useState("idle");
		return p.jsx(Kc, {
			scope: n,
			imageLoadingStatus: r,
			onImageLoadingStatusChange: s,
			children: p.jsx(lt.span, { ...o, ref: t }),
		});
	});
br.displayName = On;
var yr = "AvatarImage",
	Cr = c.forwardRef((e, t) => {
		const {
				__scopeAvatar: n,
				src: o,
				onLoadingStatusChange: r = () => {},
				...s
			} = e,
			i = wr(yr, n),
			a = Yc(o, s),
			l = we((u) => {
				r(u), i.onImageLoadingStatusChange(u);
			});
		return (
			ee(() => {
				a !== "idle" && l(a);
			}, [a, l]),
			a === "loaded" ? p.jsx(lt.img, { ...s, ref: t, src: o }) : null
		);
	});
Cr.displayName = yr;
var Sr = "AvatarFallback",
	Er = c.forwardRef((e, t) => {
		const { __scopeAvatar: n, delayMs: o, ...r } = e,
			s = wr(Sr, n),
			[i, a] = c.useState(o === void 0);
		return (
			c.useEffect(() => {
				if (o !== void 0) {
					const l = window.setTimeout(() => a(!0), o);
					return () => window.clearTimeout(l);
				}
			}, [o]),
			i && s.imageLoadingStatus !== "loaded"
				? p.jsx(lt.span, { ...r, ref: t })
				: null
		);
	});
Er.displayName = Sr;
function So(e, t) {
	return e
		? t
			? (e.src !== t && (e.src = t),
				e.complete && e.naturalWidth > 0 ? "loaded" : "loading")
			: "error"
		: "idle";
}
function Yc(e, { referrerPolicy: t, crossOrigin: n }) {
	const o = Hc(),
		r = c.useRef(null),
		s = o ? (r.current || (r.current = new window.Image()), r.current) : null,
		[i, a] = c.useState(() => So(s, e));
	return (
		ee(() => {
			a(So(s, e));
		}, [s, e]),
		ee(() => {
			const l = (d) => () => {
				a(d);
			};
			if (!s) return;
			const u = l("loaded"),
				f = l("error");
			return (
				s.addEventListener("load", u),
				s.addEventListener("error", f),
				t && (s.referrerPolicy = t),
				typeof n == "string" && (s.crossOrigin = n),
				() => {
					s.removeEventListener("load", u), s.removeEventListener("error", f);
				}
			);
		}, [s, n, t]),
		i
	);
}
var Pr = br,
	Rr = Cr,
	_r = Er;
const Nr = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(Pr, {
		ref: n,
		className: z(
			"relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full",
			e,
		),
		...t,
	}),
);
Nr.displayName = Pr.displayName;
const Ar = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(Rr, { ref: n, className: z("aspect-square h-full w-full", e), ...t }),
);
Ar.displayName = Rr.displayName;
const Mr = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(_r, {
		ref: n,
		className: z(
			"flex h-full w-full items-center justify-center rounded-full bg-muted",
			e,
		),
		...t,
	}),
);
Mr.displayName = _r.displayName;
Nr.__docgenInfo = { description: "", methods: [] };
Ar.__docgenInfo = { description: "", methods: [] };
Mr.__docgenInfo = { description: "", methods: [] };
const Xc = tr(
		"inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
		{
			variants: {
				variant: {
					default: "bg-primary text-primary-foreground hover:bg-primary/90",
					destructive:
						"bg-destructive text-destructive-foreground hover:bg-destructive/90",
					outline:
						"border border-input bg-background hover:bg-accent hover:text-accent-foreground",
					secondary:
						"bg-secondary text-secondary-foreground hover:bg-secondary/80",
					ghost: "hover:bg-accent hover:text-accent-foreground",
					link: "text-primary underline-offset-4 hover:underline",
				},
				size: {
					default: "h-10 px-4 py-2",
					sm: "h-9 rounded-md px-3",
					lg: "h-11 rounded-md px-8",
					icon: "h-10 w-10",
				},
			},
			defaultVariants: { variant: "default", size: "default" },
		},
	),
	Ir = c.forwardRef(({ className: e, variant: t, size: n, ...o }, r) =>
		p.jsx("button", {
			className: z(Xc({ variant: t, size: n, className: e })),
			ref: r,
			...o,
		}),
	);
Ir.displayName = "Button";
Ir.__docgenInfo = {
	description: "",
	methods: [],
	displayName: "Button",
	composes: ["ButtonHTMLAttributes", "VariantProps"],
};
const Tr = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("div", {
		ref: n,
		className: z("rounded-xl border bg-card text-card-foreground shadow", e),
		...t,
	}),
);
Tr.displayName = "Card";
const kr = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("div", {
		ref: n,
		className: z("flex flex-col space-y-1.5 p-6", e),
		...t,
	}),
);
kr.displayName = "CardHeader";
const Or = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("h3", {
		ref: n,
		className: z("font-semibold leading-none tracking-tight", e),
		...t,
	}),
);
Or.displayName = "CardTitle";
const Dr = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("div", { ref: n, className: z("p-6 pt-0", e), ...t }),
);
Dr.displayName = "CardContent";
Tr.__docgenInfo = { description: "", methods: [], displayName: "Card" };
kr.__docgenInfo = { description: "", methods: [], displayName: "CardHeader" };
Or.__docgenInfo = { description: "", methods: [], displayName: "CardTitle" };
Dr.__docgenInfo = { description: "", methods: [], displayName: "CardContent" };
function A(e, t, { checkForDefaultPrevented: n = !0 } = {}) {
	return (r) => {
		if ((e?.(r), n === !1 || !r.defaultPrevented)) return t?.(r);
	};
}
function qc(e, t) {
	const n = c.createContext(t),
		o = (s) => {
			const { children: i, ...a } = s,
				l = c.useMemo(() => a, Object.values(a));
			return p.jsx(n.Provider, { value: l, children: i });
		};
	o.displayName = e + "Provider";
	function r(s) {
		const i = c.useContext(n);
		if (i) return i;
		if (t !== void 0) return t;
		throw new Error(`\`${s}\` must be used within \`${e}\``);
	}
	return [o, r];
}
function Zc(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Qc(r, ...t)];
}
function Qc(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var Jc = Tn[" useId ".trim().toString()] || (() => {}),
	el = 0;
function Lt(e) {
	const [t, n] = c.useState(Jc());
	return (
		ee(() => {
			n((o) => o ?? String(el++));
		}, [e]),
		t ? `radix-${t}` : ""
	);
}
var tl = Tn[" useInsertionEffect ".trim().toString()] || ee;
function jr({ prop: e, defaultProp: t, onChange: n = () => {}, caller: o }) {
	const [r, s, i] = nl({ defaultProp: t, onChange: n }),
		a = e !== void 0,
		l = a ? e : r;
	{
		const f = c.useRef(e !== void 0);
		c.useEffect(() => {
			const d = f.current;
			d !== a &&
				console.warn(
					`${o} is changing from ${d ? "controlled" : "uncontrolled"} to ${a ? "controlled" : "uncontrolled"}. Components should not switch from controlled to uncontrolled (or vice versa). Decide between using a controlled or uncontrolled value for the lifetime of the component.`,
				),
				(f.current = a);
		}, [a, o]);
	}
	const u = c.useCallback(
		(f) => {
			if (a) {
				const d = ol(f) ? f(e) : f;
				d !== e && i.current?.(d);
			} else s(f);
		},
		[a, e, s, i],
	);
	return [l, u];
}
function nl({ defaultProp: e, onChange: t }) {
	const [n, o] = c.useState(e),
		r = c.useRef(n),
		s = c.useRef(t);
	return (
		tl(() => {
			s.current = t;
		}, [t]),
		c.useEffect(() => {
			r.current !== n && (s.current?.(n), (r.current = n));
		}, [n, r]),
		[n, o, s]
	);
}
function ol(e) {
	return typeof e == "function";
}
function ne(e) {
	const t = rl(e),
		n = c.forwardRef((o, r) => {
			const { children: s, ...i } = o,
				a = c.Children.toArray(s),
				l = a.find(il);
			if (l) {
				const u = l.props.children,
					f = a.map((d) =>
						d === l
							? c.Children.count(u) > 1
								? c.Children.only(null)
								: c.isValidElement(u)
									? u.props.children
									: null
							: d,
					);
				return p.jsx(t, {
					...i,
					ref: r,
					children: c.isValidElement(u) ? c.cloneElement(u, void 0, f) : null,
				});
			}
			return p.jsx(t, { ...i, ref: r, children: s });
		});
	return (n.displayName = `${e}.Slot`), n;
}
function rl(e) {
	const t = c.forwardRef((n, o) => {
		const { children: r, ...s } = n;
		if (c.isValidElement(r)) {
			const i = cl(r),
				a = al(s, r.props);
			return (
				r.type !== c.Fragment && (a.ref = o ? ct(o, i) : i),
				c.cloneElement(r, a)
			);
		}
		return c.Children.count(r) > 1 ? c.Children.only(null) : null;
	});
	return (t.displayName = `${e}.SlotClone`), t;
}
var $r = Symbol("radix.slottable");
function sl(e) {
	const t = ({ children: n }) => p.jsx(p.Fragment, { children: n });
	return (t.displayName = `${e}.Slottable`), (t.__radixId = $r), t;
}
function il(e) {
	return (
		c.isValidElement(e) &&
		typeof e.type == "function" &&
		"__radixId" in e.type &&
		e.type.__radixId === $r
	);
}
function al(e, t) {
	const n = { ...t };
	for (const o in t) {
		const r = e[o],
			s = t[o];
		/^on[A-Z]/.test(o)
			? r && s
				? (n[o] = (...a) => {
						const l = s(...a);
						return r(...a), l;
					})
				: r && (n[o] = r)
			: o === "style"
				? (n[o] = { ...r, ...s })
				: o === "className" && (n[o] = [r, s].filter(Boolean).join(" "));
	}
	return { ...e, ...n };
}
function cl(e) {
	let t = Object.getOwnPropertyDescriptor(e.props, "ref")?.get,
		n = t && "isReactWarning" in t && t.isReactWarning;
	return n
		? e.ref
		: ((t = Object.getOwnPropertyDescriptor(e, "ref")?.get),
			(n = t && "isReactWarning" in t && t.isReactWarning),
			n ? e.props.ref : e.props.ref || e.ref);
}
var ll = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	Lr = ll.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {});
function ul(e, t) {
	e && at.flushSync(() => e.dispatchEvent(t));
}
function dl(e, t = globalThis?.document) {
	const n = we(e);
	c.useEffect(() => {
		const o = (r) => {
			r.key === "Escape" && n(r);
		};
		return (
			t.addEventListener("keydown", o, { capture: !0 }),
			() => t.removeEventListener("keydown", o, { capture: !0 })
		);
	}, [n, t]);
}
var fl = "DismissableLayer",
	wn = "dismissableLayer.update",
	pl = "dismissableLayer.pointerDownOutside",
	ml = "dismissableLayer.focusOutside",
	Eo,
	Fr = c.createContext({
		layers: new Set(),
		layersWithOutsidePointerEventsDisabled: new Set(),
		branches: new Set(),
	}),
	ut = c.forwardRef((e, t) => {
		const {
				disableOutsidePointerEvents: n = !1,
				onEscapeKeyDown: o,
				onPointerDownOutside: r,
				onFocusOutside: s,
				onInteractOutside: i,
				onDismiss: a,
				...l
			} = e,
			u = c.useContext(Fr),
			[f, d] = c.useState(null),
			g = f?.ownerDocument ?? globalThis?.document,
			[, v] = c.useState({}),
			h = G(t, (R) => d(R)),
			m = Array.from(u.layers),
			[x] = [...u.layersWithOutsidePointerEventsDisabled].slice(-1),
			w = m.indexOf(x),
			b = f ? m.indexOf(f) : -1,
			y = u.layersWithOutsidePointerEventsDisabled.size > 0,
			C = b >= w,
			P = vl((R) => {
				const E = R.target,
					O = [...u.branches].some((D) => D.contains(E));
				!C || O || (r?.(R), i?.(R), R.defaultPrevented || a?.());
			}, g),
			T = xl((R) => {
				const E = R.target;
				[...u.branches].some((D) => D.contains(E)) ||
					(s?.(R), i?.(R), R.defaultPrevented || a?.());
			}, g);
		return (
			dl((R) => {
				b === u.layers.size - 1 &&
					(o?.(R), !R.defaultPrevented && a && (R.preventDefault(), a()));
			}, g),
			c.useEffect(() => {
				if (f)
					return (
						n &&
							(u.layersWithOutsidePointerEventsDisabled.size === 0 &&
								((Eo = g.body.style.pointerEvents),
								(g.body.style.pointerEvents = "none")),
							u.layersWithOutsidePointerEventsDisabled.add(f)),
						u.layers.add(f),
						Po(),
						() => {
							n &&
								u.layersWithOutsidePointerEventsDisabled.size === 1 &&
								(g.body.style.pointerEvents = Eo);
						}
					);
			}, [f, g, n, u]),
			c.useEffect(
				() => () => {
					f &&
						(u.layers.delete(f),
						u.layersWithOutsidePointerEventsDisabled.delete(f),
						Po());
				},
				[f, u],
			),
			c.useEffect(() => {
				const R = () => v({});
				return (
					document.addEventListener(wn, R),
					() => document.removeEventListener(wn, R)
				);
			}, []),
			p.jsx(Lr.div, {
				...l,
				ref: h,
				style: {
					pointerEvents: y ? (C ? "auto" : "none") : void 0,
					...e.style,
				},
				onFocusCapture: A(e.onFocusCapture, T.onFocusCapture),
				onBlurCapture: A(e.onBlurCapture, T.onBlurCapture),
				onPointerDownCapture: A(e.onPointerDownCapture, P.onPointerDownCapture),
			})
		);
	});
ut.displayName = fl;
var gl = "DismissableLayerBranch",
	hl = c.forwardRef((e, t) => {
		const n = c.useContext(Fr),
			o = c.useRef(null),
			r = G(t, o);
		return (
			c.useEffect(() => {
				const s = o.current;
				if (s)
					return (
						n.branches.add(s),
						() => {
							n.branches.delete(s);
						}
					);
			}, [n.branches]),
			p.jsx(Lr.div, { ...e, ref: r })
		);
	});
hl.displayName = gl;
function vl(e, t = globalThis?.document) {
	const n = we(e),
		o = c.useRef(!1),
		r = c.useRef(() => {});
	return (
		c.useEffect(() => {
			const s = (a) => {
					if (a.target && !o.current) {
						const l = () => {
							Br(pl, n, u, { discrete: !0 });
						};
						const u = { originalEvent: a };
						a.pointerType === "touch"
							? (t.removeEventListener("click", r.current),
								(r.current = l),
								t.addEventListener("click", r.current, { once: !0 }))
							: l();
					} else t.removeEventListener("click", r.current);
					o.current = !1;
				},
				i = window.setTimeout(() => {
					t.addEventListener("pointerdown", s);
				}, 0);
			return () => {
				window.clearTimeout(i),
					t.removeEventListener("pointerdown", s),
					t.removeEventListener("click", r.current);
			};
		}, [t, n]),
		{ onPointerDownCapture: () => (o.current = !0) }
	);
}
function xl(e, t = globalThis?.document) {
	const n = we(e),
		o = c.useRef(!1);
	return (
		c.useEffect(() => {
			const r = (s) => {
				s.target &&
					!o.current &&
					Br(ml, n, { originalEvent: s }, { discrete: !1 });
			};
			return (
				t.addEventListener("focusin", r),
				() => t.removeEventListener("focusin", r)
			);
		}, [t, n]),
		{
			onFocusCapture: () => (o.current = !0),
			onBlurCapture: () => (o.current = !1),
		}
	);
}
function Po() {
	const e = new CustomEvent(wn);
	document.dispatchEvent(e);
}
function Br(e, t, n, { discrete: o }) {
	const r = n.originalEvent.target,
		s = new CustomEvent(e, { bubbles: !1, cancelable: !0, detail: n });
	t && r.addEventListener(e, t, { once: !0 }),
		o ? ul(r, s) : r.dispatchEvent(s);
}
var wl = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	bl = wl.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	cn = "focusScope.autoFocusOnMount",
	ln = "focusScope.autoFocusOnUnmount",
	Ro = { bubbles: !1, cancelable: !0 },
	yl = "FocusScope",
	Ft = c.forwardRef((e, t) => {
		const {
				loop: n = !1,
				trapped: o = !1,
				onMountAutoFocus: r,
				onUnmountAutoFocus: s,
				...i
			} = e,
			[a, l] = c.useState(null),
			u = we(r),
			f = we(s),
			d = c.useRef(null),
			g = G(t, (m) => l(m)),
			v = c.useRef({
				paused: !1,
				pause() {
					this.paused = !0;
				},
				resume() {
					this.paused = !1;
				},
			}).current;
		c.useEffect(() => {
			if (o) {
				const m = (y) => {
						if (v.paused || !a) return;
						const C = y.target;
						a.contains(C) ? (d.current = C) : _e(d.current, { select: !0 });
					},
					x = (y) => {
						if (v.paused || !a) return;
						const C = y.relatedTarget;
						C !== null && (a.contains(C) || _e(d.current, { select: !0 }));
					},
					w = (y) => {
						if (document.activeElement === document.body)
							for (const P of y) P.removedNodes.length > 0 && _e(a);
					};
				document.addEventListener("focusin", m),
					document.addEventListener("focusout", x);
				const b = new MutationObserver(w);
				return (
					a && b.observe(a, { childList: !0, subtree: !0 }),
					() => {
						document.removeEventListener("focusin", m),
							document.removeEventListener("focusout", x),
							b.disconnect();
					}
				);
			}
		}, [o, a, v.paused]),
			c.useEffect(() => {
				if (a) {
					No.add(v);
					const m = document.activeElement;
					if (!a.contains(m)) {
						const w = new CustomEvent(cn, Ro);
						a.addEventListener(cn, u),
							a.dispatchEvent(w),
							w.defaultPrevented ||
								(Cl(_l(Vr(a)), { select: !0 }),
								document.activeElement === m && _e(a));
					}
					return () => {
						a.removeEventListener(cn, u),
							setTimeout(() => {
								const w = new CustomEvent(ln, Ro);
								a.addEventListener(ln, f),
									a.dispatchEvent(w),
									w.defaultPrevented || _e(m ?? document.body, { select: !0 }),
									a.removeEventListener(ln, f),
									No.remove(v);
							}, 0);
					};
				}
			}, [a, u, f, v]);
		const h = c.useCallback(
			(m) => {
				if ((!n && !o) || v.paused) return;
				const x = m.key === "Tab" && !m.altKey && !m.ctrlKey && !m.metaKey,
					w = document.activeElement;
				if (x && w) {
					const b = m.currentTarget,
						[y, C] = Sl(b);
					y && C
						? !m.shiftKey && w === C
							? (m.preventDefault(), n && _e(y, { select: !0 }))
							: m.shiftKey &&
								w === y &&
								(m.preventDefault(), n && _e(C, { select: !0 }))
						: w === b && m.preventDefault();
				}
			},
			[n, o, v.paused],
		);
		return p.jsx(bl.div, { tabIndex: -1, ...i, ref: g, onKeyDown: h });
	});
Ft.displayName = yl;
function Cl(e, { select: t = !1 } = {}) {
	const n = document.activeElement;
	for (const o of e)
		if ((_e(o, { select: t }), document.activeElement !== n)) return;
}
function Sl(e) {
	const t = Vr(e),
		n = _o(t, e),
		o = _o(t.reverse(), e);
	return [n, o];
}
function Vr(e) {
	const t = [],
		n = document.createTreeWalker(e, NodeFilter.SHOW_ELEMENT, {
			acceptNode: (o) => {
				const r = o.tagName === "INPUT" && o.type === "hidden";
				return o.disabled || o.hidden || r
					? NodeFilter.FILTER_SKIP
					: o.tabIndex >= 0
						? NodeFilter.FILTER_ACCEPT
						: NodeFilter.FILTER_SKIP;
			},
		});
	for (; n.nextNode(); ) t.push(n.currentNode);
	return t;
}
function _o(e, t) {
	for (const n of e) if (!El(n, { upTo: t })) return n;
}
function El(e, { upTo: t }) {
	if (getComputedStyle(e).visibility === "hidden") return !0;
	for (; e; ) {
		if (t !== void 0 && e === t) return !1;
		if (getComputedStyle(e).display === "none") return !0;
		e = e.parentElement;
	}
	return !1;
}
function Pl(e) {
	return e instanceof HTMLInputElement && "select" in e;
}
function _e(e, { select: t = !1 } = {}) {
	if (e && e.focus) {
		const n = document.activeElement;
		e.focus({ preventScroll: !0 }), e !== n && Pl(e) && t && e.select();
	}
}
var No = Rl();
function Rl() {
	let e = [];
	return {
		add(t) {
			const n = e[0];
			t !== n && n?.pause(), (e = Ao(e, t)), e.unshift(t);
		},
		remove(t) {
			(e = Ao(e, t)), e[0]?.resume();
		},
	};
}
function Ao(e, t) {
	const n = [...e],
		o = n.indexOf(t);
	return o !== -1 && n.splice(o, 1), n;
}
function _l(e) {
	return e.filter((t) => t.tagName !== "A");
}
var Nl = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	Al = Nl.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	Ml = "Portal",
	Bt = c.forwardRef((e, t) => {
		const { container: n, ...o } = e,
			[r, s] = c.useState(!1);
		ee(() => s(!0), []);
		const i = n || (r && globalThis?.document?.body);
		return i ? Ha.createPortal(p.jsx(Al.div, { ...o, ref: t }), i) : null;
	});
Bt.displayName = Ml;
function Il(e, t) {
	return c.useReducer((n, o) => t[n][o] ?? n, e);
}
var ye = (e) => {
	const { present: t, children: n } = e,
		o = Tl(t),
		r =
			typeof n == "function" ? n({ present: o.isPresent }) : c.Children.only(n),
		s = G(o.ref, kl(r));
	return typeof n == "function" || o.isPresent
		? c.cloneElement(r, { ref: s })
		: null;
};
ye.displayName = "Presence";
function Tl(e) {
	const [t, n] = c.useState(),
		o = c.useRef(null),
		r = c.useRef(e),
		s = c.useRef("none"),
		i = e ? "mounted" : "unmounted",
		[a, l] = Il(i, {
			mounted: { UNMOUNT: "unmounted", ANIMATION_OUT: "unmountSuspended" },
			unmountSuspended: { MOUNT: "mounted", ANIMATION_END: "unmounted" },
			unmounted: { MOUNT: "mounted" },
		});
	return (
		c.useEffect(() => {
			const u = xt(o.current);
			s.current = a === "mounted" ? u : "none";
		}, [a]),
		ee(() => {
			const u = o.current,
				f = r.current;
			if (f !== e) {
				const g = s.current,
					v = xt(u);
				e
					? l("MOUNT")
					: v === "none" || u?.display === "none"
						? l("UNMOUNT")
						: l(f && g !== v ? "ANIMATION_OUT" : "UNMOUNT"),
					(r.current = e);
			}
		}, [e, l]),
		ee(() => {
			if (t) {
				let u;
				const f = t.ownerDocument.defaultView ?? window,
					d = (v) => {
						const m = xt(o.current).includes(CSS.escape(v.animationName));
						if (v.target === t && m && (l("ANIMATION_END"), !r.current)) {
							const x = t.style.animationFillMode;
							(t.style.animationFillMode = "forwards"),
								(u = f.setTimeout(() => {
									t.style.animationFillMode === "forwards" &&
										(t.style.animationFillMode = x);
								}));
						}
					},
					g = (v) => {
						v.target === t && (s.current = xt(o.current));
					};
				return (
					t.addEventListener("animationstart", g),
					t.addEventListener("animationcancel", d),
					t.addEventListener("animationend", d),
					() => {
						f.clearTimeout(u),
							t.removeEventListener("animationstart", g),
							t.removeEventListener("animationcancel", d),
							t.removeEventListener("animationend", d);
					}
				);
			} else l("ANIMATION_END");
		}, [t, l]),
		{
			isPresent: ["mounted", "unmountSuspended"].includes(a),
			ref: c.useCallback((u) => {
				(o.current = u ? getComputedStyle(u) : null), n(u);
			}, []),
		}
	);
}
function xt(e) {
	return e?.animationName || "none";
}
function kl(e) {
	let t = Object.getOwnPropertyDescriptor(e.props, "ref")?.get,
		n = t && "isReactWarning" in t && t.isReactWarning;
	return n
		? e.ref
		: ((t = Object.getOwnPropertyDescriptor(e, "ref")?.get),
			(n = t && "isReactWarning" in t && t.isReactWarning),
			n ? e.props.ref : e.props.ref || e.ref);
}
var Ol = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	dt = Ol.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	un = 0;
function Dn() {
	c.useEffect(() => {
		const e = document.querySelectorAll("[data-radix-focus-guard]");
		return (
			document.body.insertAdjacentElement("afterbegin", e[0] ?? Mo()),
			document.body.insertAdjacentElement("beforeend", e[1] ?? Mo()),
			un++,
			() => {
				un === 1 &&
					document
						.querySelectorAll("[data-radix-focus-guard]")
						.forEach((t) => t.remove()),
					un--;
			}
		);
	}, []);
}
function Mo() {
	const e = document.createElement("span");
	return (
		e.setAttribute("data-radix-focus-guard", ""),
		(e.tabIndex = 0),
		(e.style.outline = "none"),
		(e.style.opacity = "0"),
		(e.style.position = "fixed"),
		(e.style.pointerEvents = "none"),
		e
	);
}
var he = function () {
	return (
		(he =
			Object.assign ||
			function (t) {
				for (var n, o = 1, r = arguments.length; o < r; o++) {
					n = arguments[o];
					for (var s in n) Object.hasOwn(n, s) && (t[s] = n[s]);
				}
				return t;
			}),
		he.apply(this, arguments)
	);
};
function Wr(e, t) {
	var n = {};
	for (var o in e) Object.hasOwn(e, o) && t.indexOf(o) < 0 && (n[o] = e[o]);
	if (e != null && typeof Object.getOwnPropertySymbols == "function")
		for (var r = 0, o = Object.getOwnPropertySymbols(e); r < o.length; r++)
			t.indexOf(o[r]) < 0 &&
				Object.prototype.propertyIsEnumerable.call(e, o[r]) &&
				(n[o[r]] = e[o[r]]);
	return n;
}
function Dl(e, t, n) {
	if (n || arguments.length === 2)
		for (var o = 0, r = t.length, s; o < r; o++)
			(s || !(o in t)) &&
				(s || (s = Array.prototype.slice.call(t, 0, o)), (s[o] = t[o]));
	return e.concat(s || Array.prototype.slice.call(t));
}
var Et = "right-scroll-bar-position",
	Pt = "width-before-scroll-bar",
	jl = "with-scroll-bars-hidden",
	$l = "--removed-body-scroll-bar-size";
function dn(e, t) {
	return typeof e == "function" ? e(t) : e && (e.current = t), e;
}
function Ll(e, t) {
	var n = c.useState(() => ({
		value: e,
		callback: t,
		facade: {
			get current() {
				return n.value;
			},
			set current(o) {
				var r = n.value;
				r !== o && ((n.value = o), n.callback(o, r));
			},
		},
	}))[0];
	return (n.callback = t), n.facade;
}
var Fl = typeof window < "u" ? c.useLayoutEffect : c.useEffect,
	Io = new WeakMap();
function Bl(e, t) {
	var n = Ll(null, (o) => e.forEach((r) => dn(r, o)));
	return (
		Fl(() => {
			var o = Io.get(n);
			if (o) {
				var r = new Set(o),
					s = new Set(e),
					i = n.current;
				r.forEach((a) => {
					s.has(a) || dn(a, null);
				}),
					s.forEach((a) => {
						r.has(a) || dn(a, i);
					});
			}
			Io.set(n, e);
		}, [e]),
		n
	);
}
function Vl(e) {
	return e;
}
function Wl(e, t) {
	t === void 0 && (t = Vl);
	var n = [],
		o = !1,
		r = {
			read: () => {
				if (o)
					throw new Error(
						"Sidecar: could not `read` from an `assigned` medium. `read` could be used only with `useMedium`.",
					);
				return n.length ? n[n.length - 1] : e;
			},
			useMedium: (s) => {
				var i = t(s, o);
				return (
					n.push(i),
					() => {
						n = n.filter((a) => a !== i);
					}
				);
			},
			assignSyncMedium: (s) => {
				for (o = !0; n.length; ) {
					var i = n;
					(n = []), i.forEach(s);
				}
				n = { push: (a) => s(a), filter: () => n };
			},
			assignMedium: (s) => {
				o = !0;
				var i = [];
				if (n.length) {
					var a = n;
					(n = []), a.forEach(s), (i = n);
				}
				var l = () => {
						var f = i;
						(i = []), f.forEach(s);
					},
					u = () => Promise.resolve().then(l);
				u(),
					(n = {
						push: (f) => {
							i.push(f), u();
						},
						filter: (f) => ((i = i.filter(f)), n),
					});
			},
		};
	return r;
}
function zl(e) {
	e === void 0 && (e = {});
	var t = Wl(null);
	return (t.options = he({ async: !0, ssr: !1 }, e)), t;
}
var zr = (e) => {
	var t = e.sideCar,
		n = Wr(e, ["sideCar"]);
	if (!t)
		throw new Error(
			"Sidecar: please provide `sideCar` property to import the right car",
		);
	var o = t.read();
	if (!o) throw new Error("Sidecar medium not found");
	return c.createElement(o, he({}, n));
};
zr.isSideCarExport = !0;
function Hl(e, t) {
	return e.useMedium(t), zr;
}
var Hr = zl(),
	fn = () => {},
	Vt = c.forwardRef((e, t) => {
		var n = c.useRef(null),
			o = c.useState({
				onScrollCapture: fn,
				onWheelCapture: fn,
				onTouchMoveCapture: fn,
			}),
			r = o[0],
			s = o[1],
			i = e.forwardProps,
			a = e.children,
			l = e.className,
			u = e.removeScrollBar,
			f = e.enabled,
			d = e.shards,
			g = e.sideCar,
			v = e.noRelative,
			h = e.noIsolation,
			m = e.inert,
			x = e.allowPinchZoom,
			w = e.as,
			b = w === void 0 ? "div" : w,
			y = e.gapMode,
			C = Wr(e, [
				"forwardProps",
				"children",
				"className",
				"removeScrollBar",
				"enabled",
				"shards",
				"sideCar",
				"noRelative",
				"noIsolation",
				"inert",
				"allowPinchZoom",
				"as",
				"gapMode",
			]),
			P = g,
			T = Bl([n, t]),
			R = he(he({}, C), r);
		return c.createElement(
			c.Fragment,
			null,
			f &&
				c.createElement(P, {
					sideCar: Hr,
					removeScrollBar: u,
					shards: d,
					noRelative: v,
					noIsolation: h,
					inert: m,
					setCallbacks: s,
					allowPinchZoom: !!x,
					lockRef: n,
					gapMode: y,
				}),
			i
				? c.cloneElement(c.Children.only(a), he(he({}, R), { ref: T }))
				: c.createElement(b, he({}, R, { className: l, ref: T }), a),
		);
	});
Vt.defaultProps = { enabled: !0, removeScrollBar: !0, inert: !1 };
Vt.classNames = { fullWidth: Pt, zeroRight: Et };
var Gl = () => {
	if (typeof __webpack_nonce__ < "u") return __webpack_nonce__;
};
function Ul() {
	if (!document) return null;
	var e = document.createElement("style");
	e.type = "text/css";
	var t = Gl();
	return t && e.setAttribute("nonce", t), e;
}
function Kl(e, t) {
	e.styleSheet
		? (e.styleSheet.cssText = t)
		: e.appendChild(document.createTextNode(t));
}
function Yl(e) {
	var t = document.head || document.getElementsByTagName("head")[0];
	t.appendChild(e);
}
var Xl = () => {
		var e = 0,
			t = null;
		return {
			add: (n) => {
				e == 0 && (t = Ul()) && (Kl(t, n), Yl(t)), e++;
			},
			remove: () => {
				e--,
					!e && t && (t.parentNode && t.parentNode.removeChild(t), (t = null));
			},
		};
	},
	ql = () => {
		var e = Xl();
		return (t, n) => {
			c.useEffect(
				() => (
					e.add(t),
					() => {
						e.remove();
					}
				),
				[t && n],
			);
		};
	},
	Gr = () => {
		var e = ql(),
			t = (n) => {
				var o = n.styles,
					r = n.dynamic;
				return e(o, r), null;
			};
		return t;
	},
	Zl = { left: 0, top: 0, right: 0, gap: 0 },
	pn = (e) => parseInt(e || "", 10) || 0,
	Ql = (e) => {
		var t = window.getComputedStyle(document.body),
			n = t[e === "padding" ? "paddingLeft" : "marginLeft"],
			o = t[e === "padding" ? "paddingTop" : "marginTop"],
			r = t[e === "padding" ? "paddingRight" : "marginRight"];
		return [pn(n), pn(o), pn(r)];
	},
	Jl = (e) => {
		if ((e === void 0 && (e = "margin"), typeof window > "u")) return Zl;
		var t = Ql(e),
			n = document.documentElement.clientWidth,
			o = window.innerWidth;
		return {
			left: t[0],
			top: t[1],
			right: t[2],
			gap: Math.max(0, o - n + t[2] - t[0]),
		};
	},
	eu = Gr(),
	He = "data-scroll-locked",
	tu = (e, t, n, o) => {
		var r = e.left,
			s = e.top,
			i = e.right,
			a = e.gap;
		return (
			n === void 0 && (n = "margin"),
			`
  .`
				.concat(
					jl,
					` {
   overflow: hidden `,
				)
				.concat(
					o,
					`;
   padding-right: `,
				)
				.concat(a, "px ")
				.concat(
					o,
					`;
  }
  body[`,
				)
				.concat(
					He,
					`] {
    overflow: hidden `,
				)
				.concat(
					o,
					`;
    overscroll-behavior: contain;
    `,
				)
				.concat(
					[
						t && "position: relative ".concat(o, ";"),
						n === "margin" &&
							`
    padding-left: `
								.concat(
									r,
									`px;
    padding-top: `,
								)
								.concat(
									s,
									`px;
    padding-right: `,
								)
								.concat(
									i,
									`px;
    margin-left:0;
    margin-top:0;
    margin-right: `,
								)
								.concat(a, "px ")
								.concat(
									o,
									`;
    `,
								),
						n === "padding" &&
							"padding-right: ".concat(a, "px ").concat(o, ";"),
					]
						.filter(Boolean)
						.join(""),
					`
  }
  
  .`,
				)
				.concat(
					Et,
					` {
    right: `,
				)
				.concat(a, "px ")
				.concat(
					o,
					`;
  }
  
  .`,
				)
				.concat(
					Pt,
					` {
    margin-right: `,
				)
				.concat(a, "px ")
				.concat(
					o,
					`;
  }
  
  .`,
				)
				.concat(Et, " .")
				.concat(
					Et,
					` {
    right: 0 `,
				)
				.concat(
					o,
					`;
  }
  
  .`,
				)
				.concat(Pt, " .")
				.concat(
					Pt,
					` {
    margin-right: 0 `,
				)
				.concat(
					o,
					`;
  }
  
  body[`,
				)
				.concat(
					He,
					`] {
    `,
				)
				.concat($l, ": ")
				.concat(
					a,
					`px;
  }
`,
				)
		);
	},
	To = () => {
		var e = parseInt(document.body.getAttribute(He) || "0", 10);
		return isFinite(e) ? e : 0;
	},
	nu = () => {
		c.useEffect(
			() => (
				document.body.setAttribute(He, (To() + 1).toString()),
				() => {
					var e = To() - 1;
					e <= 0
						? document.body.removeAttribute(He)
						: document.body.setAttribute(He, e.toString());
				}
			),
			[],
		);
	},
	ou = (e) => {
		var t = e.noRelative,
			n = e.noImportant,
			o = e.gapMode,
			r = o === void 0 ? "margin" : o;
		nu();
		var s = c.useMemo(() => Jl(r), [r]);
		return c.createElement(eu, { styles: tu(s, !t, r, n ? "" : "!important") });
	},
	bn = !1;
if (typeof window < "u")
	try {
		var wt = Object.defineProperty({}, "passive", {
			get: () => ((bn = !0), !0),
		});
		window.addEventListener("test", wt, wt),
			window.removeEventListener("test", wt, wt);
	} catch {
		bn = !1;
	}
var Ve = bn ? { passive: !1 } : !1,
	ru = (e) => e.tagName === "TEXTAREA",
	Ur = (e, t) => {
		if (!(e instanceof Element)) return !1;
		var n = window.getComputedStyle(e);
		return (
			n[t] !== "hidden" &&
			!(n.overflowY === n.overflowX && !ru(e) && n[t] === "visible")
		);
	},
	su = (e) => Ur(e, "overflowY"),
	iu = (e) => Ur(e, "overflowX"),
	ko = (e, t) => {
		var n = t.ownerDocument,
			o = t;
		do {
			typeof ShadowRoot < "u" && o instanceof ShadowRoot && (o = o.host);
			var r = Kr(e, o);
			if (r) {
				var s = Yr(e, o),
					i = s[1],
					a = s[2];
				if (i > a) return !0;
			}
			o = o.parentNode;
		} while (o && o !== n.body);
		return !1;
	},
	au = (e) => {
		var t = e.scrollTop,
			n = e.scrollHeight,
			o = e.clientHeight;
		return [t, n, o];
	},
	cu = (e) => {
		var t = e.scrollLeft,
			n = e.scrollWidth,
			o = e.clientWidth;
		return [t, n, o];
	},
	Kr = (e, t) => (e === "v" ? su(t) : iu(t)),
	Yr = (e, t) => (e === "v" ? au(t) : cu(t)),
	lu = (e, t) => (e === "h" && t === "rtl" ? -1 : 1),
	uu = (e, t, n, o, r) => {
		var s = lu(e, window.getComputedStyle(t).direction),
			i = s * o,
			a = n.target,
			l = t.contains(a),
			u = !1,
			f = i > 0,
			d = 0,
			g = 0;
		do {
			if (!a) break;
			var v = Yr(e, a),
				h = v[0],
				m = v[1],
				x = v[2],
				w = m - x - s * h;
			(h || w) && Kr(e, a) && ((d += w), (g += h));
			var b = a.parentNode;
			a = b && b.nodeType === Node.DOCUMENT_FRAGMENT_NODE ? b.host : b;
		} while ((!l && a !== document.body) || (l && (t.contains(a) || t === a)));
		return ((f && Math.abs(d) < 1) || (!f && Math.abs(g) < 1)) && (u = !0), u;
	},
	bt = (e) =>
		"changedTouches" in e
			? [e.changedTouches[0].clientX, e.changedTouches[0].clientY]
			: [0, 0],
	Oo = (e) => [e.deltaX, e.deltaY],
	Do = (e) => (e && "current" in e ? e.current : e),
	du = (e, t) => e[0] === t[0] && e[1] === t[1],
	fu = (e) =>
		`
  .block-interactivity-`
			.concat(
				e,
				` {pointer-events: none;}
  .allow-interactivity-`,
			)
			.concat(
				e,
				` {pointer-events: all;}
`,
			),
	pu = 0,
	We = [];
function mu(e) {
	var t = c.useRef([]),
		n = c.useRef([0, 0]),
		o = c.useRef(),
		r = c.useState(pu++)[0],
		s = c.useState(Gr)[0],
		i = c.useRef(e);
	c.useEffect(() => {
		i.current = e;
	}, [e]),
		c.useEffect(() => {
			if (e.inert) {
				document.body.classList.add("block-interactivity-".concat(r));
				var m = Dl([e.lockRef.current], (e.shards || []).map(Do), !0).filter(
					Boolean,
				);
				return (
					m.forEach((x) => x.classList.add("allow-interactivity-".concat(r))),
					() => {
						document.body.classList.remove("block-interactivity-".concat(r)),
							m.forEach((x) =>
								x.classList.remove("allow-interactivity-".concat(r)),
							);
					}
				);
			}
		}, [e.inert, e.lockRef.current, e.shards]);
	var a = c.useCallback((m, x) => {
			if (
				("touches" in m && m.touches.length === 2) ||
				(m.type === "wheel" && m.ctrlKey)
			)
				return !i.current.allowPinchZoom;
			var w = bt(m),
				b = n.current,
				y = "deltaX" in m ? m.deltaX : b[0] - w[0],
				C = "deltaY" in m ? m.deltaY : b[1] - w[1],
				P,
				T = m.target,
				R = Math.abs(y) > Math.abs(C) ? "h" : "v";
			if ("touches" in m && R === "h" && T.type === "range") return !1;
			var E = window.getSelection(),
				O = E && E.anchorNode,
				D = O ? O === T || O.contains(T) : !1;
			if (D) return !1;
			var $ = ko(R, T);
			if (!$) return !0;
			if (($ ? (P = R) : ((P = R === "v" ? "h" : "v"), ($ = ko(R, T))), !$))
				return !1;
			if (
				(!o.current && "changedTouches" in m && (y || C) && (o.current = P), !P)
			)
				return !0;
			var L = o.current || P;
			return uu(L, x, m, L === "h" ? y : C);
		}, []),
		l = c.useCallback((m) => {
			var x = m;
			if (!(!We.length || We[We.length - 1] !== s)) {
				var w = "deltaY" in x ? Oo(x) : bt(x),
					b = t.current.filter(
						(P) =>
							P.name === x.type &&
							(P.target === x.target || x.target === P.shadowParent) &&
							du(P.delta, w),
					)[0];
				if (b && b.should) {
					x.cancelable && x.preventDefault();
					return;
				}
				if (!b) {
					var y = (i.current.shards || [])
							.map(Do)
							.filter(Boolean)
							.filter((P) => P.contains(x.target)),
						C = y.length > 0 ? a(x, y[0]) : !i.current.noIsolation;
					C && x.cancelable && x.preventDefault();
				}
			}
		}, []),
		u = c.useCallback((m, x, w, b) => {
			var y = { name: m, delta: x, target: w, should: b, shadowParent: gu(w) };
			t.current.push(y),
				setTimeout(() => {
					t.current = t.current.filter((C) => C !== y);
				}, 1);
		}, []),
		f = c.useCallback((m) => {
			(n.current = bt(m)), (o.current = void 0);
		}, []),
		d = c.useCallback((m) => {
			u(m.type, Oo(m), m.target, a(m, e.lockRef.current));
		}, []),
		g = c.useCallback((m) => {
			u(m.type, bt(m), m.target, a(m, e.lockRef.current));
		}, []);
	c.useEffect(
		() => (
			We.push(s),
			e.setCallbacks({
				onScrollCapture: d,
				onWheelCapture: d,
				onTouchMoveCapture: g,
			}),
			document.addEventListener("wheel", l, Ve),
			document.addEventListener("touchmove", l, Ve),
			document.addEventListener("touchstart", f, Ve),
			() => {
				(We = We.filter((m) => m !== s)),
					document.removeEventListener("wheel", l, Ve),
					document.removeEventListener("touchmove", l, Ve),
					document.removeEventListener("touchstart", f, Ve);
			}
		),
		[],
	);
	var v = e.removeScrollBar,
		h = e.inert;
	return c.createElement(
		c.Fragment,
		null,
		h ? c.createElement(s, { styles: fu(r) }) : null,
		v
			? c.createElement(ou, { noRelative: e.noRelative, gapMode: e.gapMode })
			: null,
	);
}
function gu(e) {
	for (var t = null; e !== null; )
		e instanceof ShadowRoot && ((t = e.host), (e = e.host)), (e = e.parentNode);
	return t;
}
const hu = Hl(Hr, mu);
var Wt = c.forwardRef((e, t) =>
	c.createElement(Vt, he({}, e, { ref: t, sideCar: hu })),
);
Wt.classNames = Vt.classNames;
var vu = (e) => {
		if (typeof document > "u") return null;
		var t = Array.isArray(e) ? e[0] : e;
		return t.ownerDocument.body;
	},
	ze = new WeakMap(),
	yt = new WeakMap(),
	Ct = {},
	mn = 0,
	Xr = (e) => e && (e.host || Xr(e.parentNode)),
	xu = (e, t) =>
		t
			.map((n) => {
				if (e.contains(n)) return n;
				var o = Xr(n);
				return o && e.contains(o)
					? o
					: (console.error(
							"aria-hidden",
							n,
							"in not contained inside",
							e,
							". Doing nothing",
						),
						null);
			})
			.filter((n) => !!n),
	wu = (e, t, n, o) => {
		var r = xu(t, Array.isArray(e) ? e : [e]);
		Ct[n] || (Ct[n] = new WeakMap());
		var s = Ct[n],
			i = [],
			a = new Set(),
			l = new Set(r),
			u = (d) => {
				!d || a.has(d) || (a.add(d), u(d.parentNode));
			};
		r.forEach(u);
		var f = (d) => {
			!d ||
				l.has(d) ||
				Array.prototype.forEach.call(d.children, (g) => {
					if (a.has(g)) f(g);
					else
						try {
							var v = g.getAttribute(o),
								h = v !== null && v !== "false",
								m = (ze.get(g) || 0) + 1,
								x = (s.get(g) || 0) + 1;
							ze.set(g, m),
								s.set(g, x),
								i.push(g),
								m === 1 && h && yt.set(g, !0),
								x === 1 && g.setAttribute(n, "true"),
								h || g.setAttribute(o, "true");
						} catch (w) {
							console.error("aria-hidden: cannot operate on ", g, w);
						}
				});
		};
		return (
			f(t),
			a.clear(),
			mn++,
			() => {
				i.forEach((d) => {
					var g = ze.get(d) - 1,
						v = s.get(d) - 1;
					ze.set(d, g),
						s.set(d, v),
						g || (yt.has(d) || d.removeAttribute(o), yt.delete(d)),
						v || d.removeAttribute(n);
				}),
					mn--,
					mn ||
						((ze = new WeakMap()),
						(ze = new WeakMap()),
						(yt = new WeakMap()),
						(Ct = {}));
			}
		);
	},
	jn = (e, t, n) => {
		n === void 0 && (n = "data-aria-hidden");
		var o = Array.from(Array.isArray(e) ? e : [e]),
			r = vu(e);
		return r
			? (o.push.apply(o, Array.from(r.querySelectorAll("[aria-live], script"))),
				wu(o, r, n, "aria-hidden"))
			: () => null;
	},
	qr = "Dialog",
	[Zr] = Zc(qr),
	[ug, ge] = Zr(qr),
	Qr = "DialogTrigger",
	bu = c.forwardRef((e, t) => {
		const { __scopeDialog: n, ...o } = e,
			r = ge(Qr, n),
			s = G(t, r.triggerRef);
		return p.jsx(dt.button, {
			type: "button",
			"aria-haspopup": "dialog",
			"aria-expanded": r.open,
			"aria-controls": r.contentId,
			"data-state": Fn(r.open),
			...o,
			ref: s,
			onClick: A(e.onClick, r.onOpenToggle),
		});
	});
bu.displayName = Qr;
var $n = "DialogPortal",
	[yu, Jr] = Zr($n, { forceMount: void 0 }),
	es = (e) => {
		const { __scopeDialog: t, forceMount: n, children: o, container: r } = e,
			s = ge($n, t);
		return p.jsx(yu, {
			scope: t,
			forceMount: n,
			children: c.Children.map(o, (i) =>
				p.jsx(ye, {
					present: n || s.open,
					children: p.jsx(Bt, { asChild: !0, container: r, children: i }),
				}),
			),
		});
	};
es.displayName = $n;
var At = "DialogOverlay",
	ts = c.forwardRef((e, t) => {
		const n = Jr(At, e.__scopeDialog),
			{ forceMount: o = n.forceMount, ...r } = e,
			s = ge(At, e.__scopeDialog);
		return s.modal
			? p.jsx(ye, {
					present: o || s.open,
					children: p.jsx(Su, { ...r, ref: t }),
				})
			: null;
	});
ts.displayName = At;
var Cu = ne("DialogOverlay.RemoveScroll"),
	Su = c.forwardRef((e, t) => {
		const { __scopeDialog: n, ...o } = e,
			r = ge(At, n);
		return p.jsx(Wt, {
			as: Cu,
			allowPinchZoom: !0,
			shards: [r.contentRef],
			children: p.jsx(dt.div, {
				"data-state": Fn(r.open),
				...o,
				ref: t,
				style: { pointerEvents: "auto", ...o.style },
			}),
		});
	}),
	De = "DialogContent",
	ns = c.forwardRef((e, t) => {
		const n = Jr(De, e.__scopeDialog),
			{ forceMount: o = n.forceMount, ...r } = e,
			s = ge(De, e.__scopeDialog);
		return p.jsx(ye, {
			present: o || s.open,
			children: s.modal
				? p.jsx(Eu, { ...r, ref: t })
				: p.jsx(Pu, { ...r, ref: t }),
		});
	});
ns.displayName = De;
var Eu = c.forwardRef((e, t) => {
		const n = ge(De, e.__scopeDialog),
			o = c.useRef(null),
			r = G(t, n.contentRef, o);
		return (
			c.useEffect(() => {
				const s = o.current;
				if (s) return jn(s);
			}, []),
			p.jsx(os, {
				...e,
				ref: r,
				trapFocus: n.open,
				disableOutsidePointerEvents: !0,
				onCloseAutoFocus: A(e.onCloseAutoFocus, (s) => {
					s.preventDefault(), n.triggerRef.current?.focus();
				}),
				onPointerDownOutside: A(e.onPointerDownOutside, (s) => {
					const i = s.detail.originalEvent,
						a = i.button === 0 && i.ctrlKey === !0;
					(i.button === 2 || a) && s.preventDefault();
				}),
				onFocusOutside: A(e.onFocusOutside, (s) => s.preventDefault()),
			})
		);
	}),
	Pu = c.forwardRef((e, t) => {
		const n = ge(De, e.__scopeDialog),
			o = c.useRef(!1),
			r = c.useRef(!1);
		return p.jsx(os, {
			...e,
			ref: t,
			trapFocus: !1,
			disableOutsidePointerEvents: !1,
			onCloseAutoFocus: (s) => {
				e.onCloseAutoFocus?.(s),
					s.defaultPrevented ||
						(o.current || n.triggerRef.current?.focus(), s.preventDefault()),
					(o.current = !1),
					(r.current = !1);
			},
			onInteractOutside: (s) => {
				e.onInteractOutside?.(s),
					s.defaultPrevented ||
						((o.current = !0),
						s.detail.originalEvent.type === "pointerdown" && (r.current = !0));
				const i = s.target;
				n.triggerRef.current?.contains(i) && s.preventDefault(),
					s.detail.originalEvent.type === "focusin" &&
						r.current &&
						s.preventDefault();
			},
		});
	}),
	os = c.forwardRef((e, t) => {
		const {
				__scopeDialog: n,
				trapFocus: o,
				onOpenAutoFocus: r,
				onCloseAutoFocus: s,
				...i
			} = e,
			a = ge(De, n),
			l = c.useRef(null),
			u = G(t, l);
		return (
			Dn(),
			p.jsxs(p.Fragment, {
				children: [
					p.jsx(Ft, {
						asChild: !0,
						loop: !0,
						trapped: o,
						onMountAutoFocus: r,
						onUnmountAutoFocus: s,
						children: p.jsx(ut, {
							role: "dialog",
							id: a.contentId,
							"aria-describedby": a.descriptionId,
							"aria-labelledby": a.titleId,
							"data-state": Fn(a.open),
							...i,
							ref: u,
							onDismiss: () => a.onOpenChange(!1),
						}),
					}),
					p.jsxs(p.Fragment, {
						children: [
							p.jsx(_u, { titleId: a.titleId }),
							p.jsx(Au, { contentRef: l, descriptionId: a.descriptionId }),
						],
					}),
				],
			})
		);
	}),
	Ln = "DialogTitle",
	rs = c.forwardRef((e, t) => {
		const { __scopeDialog: n, ...o } = e,
			r = ge(Ln, n);
		return p.jsx(dt.h2, { id: r.titleId, ...o, ref: t });
	});
rs.displayName = Ln;
var ss = "DialogDescription",
	Ru = c.forwardRef((e, t) => {
		const { __scopeDialog: n, ...o } = e,
			r = ge(ss, n);
		return p.jsx(dt.p, { id: r.descriptionId, ...o, ref: t });
	});
Ru.displayName = ss;
var is = "DialogClose",
	as = c.forwardRef((e, t) => {
		const { __scopeDialog: n, ...o } = e,
			r = ge(is, n);
		return p.jsx(dt.button, {
			type: "button",
			...o,
			ref: t,
			onClick: A(e.onClick, () => r.onOpenChange(!1)),
		});
	});
as.displayName = is;
function Fn(e) {
	return e ? "open" : "closed";
}
var cs = "DialogTitleWarning",
	[dg, ls] = qc(cs, { contentName: De, titleName: Ln, docsSlug: "dialog" }),
	_u = ({ titleId: e }) => {
		const t = ls(cs),
			n = `\`${t.contentName}\` requires a \`${t.titleName}\` for the component to be accessible for screen reader users.

If you want to hide the \`${t.titleName}\`, you can wrap it with our VisuallyHidden component.

For more information, see https://radix-ui.com/primitives/docs/components/${t.docsSlug}`;
		return (
			c.useEffect(() => {
				e && (document.getElementById(e) || console.error(n));
			}, [n, e]),
			null
		);
	},
	Nu = "DialogDescriptionWarning",
	Au = ({ contentRef: e, descriptionId: t }) => {
		const o = `Warning: Missing \`Description\` or \`aria-describedby={undefined}\` for {${ls(Nu).contentName}}.`;
		return (
			c.useEffect(() => {
				const r = e.current?.getAttribute("aria-describedby");
				t && r && (document.getElementById(t) || console.warn(o));
			}, [o, e, t]),
			null
		);
	},
	Mu = es,
	us = ts,
	ds = ns,
	fs = rs,
	Iu = as;
const Tu = (e) => e.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase(),
	ku = (e) =>
		e.replace(/^([A-Z])|[\s-_]+(\w)/g, (t, n, o) =>
			o ? o.toUpperCase() : n.toLowerCase(),
		),
	jo = (e) => {
		const t = ku(e);
		return t.charAt(0).toUpperCase() + t.slice(1);
	},
	ps = (...e) =>
		e
			.filter((t, n, o) => !!t && t.trim() !== "" && o.indexOf(t) === n)
			.join(" ")
			.trim(),
	Ou = (e) => {
		for (const t in e)
			if (t.startsWith("aria-") || t === "role" || t === "title") return !0;
	};
var Du = {
	xmlns: "http://www.w3.org/2000/svg",
	width: 24,
	height: 24,
	viewBox: "0 0 24 24",
	fill: "none",
	stroke: "currentColor",
	strokeWidth: 2,
	strokeLinecap: "round",
	strokeLinejoin: "round",
};
const ju = c.forwardRef(
	(
		{
			color: e = "currentColor",
			size: t = 24,
			strokeWidth: n = 2,
			absoluteStrokeWidth: o,
			className: r = "",
			children: s,
			iconNode: i,
			...a
		},
		l,
	) =>
		c.createElement(
			"svg",
			{
				ref: l,
				...Du,
				width: t,
				height: t,
				stroke: e,
				strokeWidth: o ? (Number(n) * 24) / Number(t) : n,
				className: ps("lucide", r),
				...(!s && !Ou(a) && { "aria-hidden": "true" }),
				...a,
			},
			[
				...i.map(([u, f]) => c.createElement(u, f)),
				...(Array.isArray(s) ? s : [s]),
			],
		),
);
const Bn = (e, t) => {
	const n = c.forwardRef(({ className: o, ...r }, s) =>
		c.createElement(ju, {
			ref: s,
			iconNode: t,
			className: ps(`lucide-${Tu(jo(e))}`, `lucide-${e}`, o),
			...r,
		}),
	);
	return (n.displayName = jo(e)), n;
};
const $u = [["path", { d: "M20 6 9 17l-5-5", key: "1gmf2c" }]],
	Lu = Bn("check", $u);
const Fu = [["path", { d: "m6 9 6 6 6-6", key: "qrunsl" }]],
	Bu = Bn("chevron-down", Fu);
const Vu = [
		["path", { d: "M18 6 6 18", key: "1bl5f8" }],
		["path", { d: "m6 6 12 12", key: "d8bk6v" }],
	],
	Wu = Bn("x", Vu),
	zu = Mu,
	Vn = c.forwardRef(({ className: e, ...t }, n) =>
		p.jsx(us, {
			ref: n,
			className: z(
				"fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out",
				e,
			),
			...t,
		}),
	);
Vn.displayName = us.displayName;
const ms = c.forwardRef(({ className: e, children: t, ...n }, o) =>
	p.jsxs(zu, {
		children: [
			p.jsx(Vn, {}),
			p.jsxs(ds, {
				ref: o,
				className: z(
					"fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] rounded-lg border bg-background p-6 shadow-lg",
					e,
				),
				...n,
				children: [
					t,
					p.jsx(Iu, {
						className:
							"absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100",
						children: p.jsx(Wu, { className: "h-4 w-4" }),
					}),
				],
			}),
		],
	}),
);
ms.displayName = ds.displayName;
const gs = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(fs, { ref: n, className: z("text-lg font-semibold", e), ...t }),
);
gs.displayName = fs.displayName;
Vn.__docgenInfo = { description: "", methods: [] };
ms.__docgenInfo = { description: "", methods: [] };
gs.__docgenInfo = { description: "", methods: [] };
function Hu(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Gu(r, ...t)];
}
function Gu(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var Uu = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	Ku = Uu.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {});
function Yu(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Xu(r, ...t)];
}
function Xu(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
function Wn(e) {
	const t = e + "CollectionProvider",
		[n, o] = Yu(t),
		[r, s] = n(t, { collectionRef: { current: null }, itemMap: new Map() }),
		i = (m) => {
			const { scope: x, children: w } = m,
				b = ke.useRef(null),
				y = ke.useRef(new Map()).current;
			return p.jsx(r, { scope: x, itemMap: y, collectionRef: b, children: w });
		};
	i.displayName = t;
	const a = e + "CollectionSlot",
		l = ne(a),
		u = ke.forwardRef((m, x) => {
			const { scope: w, children: b } = m,
				y = s(a, w),
				C = G(x, y.collectionRef);
			return p.jsx(l, { ref: C, children: b });
		});
	u.displayName = a;
	const f = e + "CollectionItemSlot",
		d = "data-radix-collection-item",
		g = ne(f),
		v = ke.forwardRef((m, x) => {
			const { scope: w, children: b, ...y } = m,
				C = ke.useRef(null),
				P = G(x, C),
				T = s(f, w);
			return (
				ke.useEffect(
					() => (
						T.itemMap.set(C, { ref: C, ...y }), () => void T.itemMap.delete(C)
					),
				),
				p.jsx(g, { [d]: "", ref: P, children: b })
			);
		});
	v.displayName = f;
	function h(m) {
		const x = s(e + "CollectionConsumer", m);
		return ke.useCallback(() => {
			const b = x.collectionRef.current;
			if (!b) return [];
			const y = Array.from(b.querySelectorAll(`[${d}]`));
			return Array.from(x.itemMap.values()).sort(
				(T, R) => y.indexOf(T.ref.current) - y.indexOf(R.ref.current),
			);
		}, [x.collectionRef, x.itemMap]);
	}
	return [{ Provider: i, Slot: u, ItemSlot: v }, h, o];
}
function qu(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Zu(r, ...t)];
}
function Zu(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var Qu = c.createContext(void 0);
function hs(e) {
	const t = c.useContext(Qu);
	return e || t || "ltr";
}
const Ju = ["top", "right", "bottom", "left"],
	Ne = Math.min,
	ae = Math.max,
	Mt = Math.round,
	St = Math.floor,
	xe = (e) => ({ x: e, y: e }),
	ed = { left: "right", right: "left", bottom: "top", top: "bottom" },
	td = { start: "end", end: "start" };
function yn(e, t, n) {
	return ae(e, Ne(t, n));
}
function Ee(e, t) {
	return typeof e == "function" ? e(t) : e;
}
function Pe(e) {
	return e.split("-")[0];
}
function qe(e) {
	return e.split("-")[1];
}
function zn(e) {
	return e === "x" ? "y" : "x";
}
function Hn(e) {
	return e === "y" ? "height" : "width";
}
const nd = new Set(["top", "bottom"]);
function ve(e) {
	return nd.has(Pe(e)) ? "y" : "x";
}
function Gn(e) {
	return zn(ve(e));
}
function od(e, t, n) {
	n === void 0 && (n = !1);
	const o = qe(e),
		r = Gn(e),
		s = Hn(r);
	let i =
		r === "x"
			? o === (n ? "end" : "start")
				? "right"
				: "left"
			: o === "start"
				? "bottom"
				: "top";
	return t.reference[s] > t.floating[s] && (i = It(i)), [i, It(i)];
}
function rd(e) {
	const t = It(e);
	return [Cn(e), t, Cn(t)];
}
function Cn(e) {
	return e.replace(/start|end/g, (t) => td[t]);
}
const $o = ["left", "right"],
	Lo = ["right", "left"],
	sd = ["top", "bottom"],
	id = ["bottom", "top"];
function ad(e, t, n) {
	switch (e) {
		case "top":
		case "bottom":
			return n ? (t ? Lo : $o) : t ? $o : Lo;
		case "left":
		case "right":
			return t ? sd : id;
		default:
			return [];
	}
}
function cd(e, t, n, o) {
	const r = qe(e);
	let s = ad(Pe(e), n === "start", o);
	return (
		r && ((s = s.map((i) => i + "-" + r)), t && (s = s.concat(s.map(Cn)))), s
	);
}
function It(e) {
	return e.replace(/left|right|bottom|top/g, (t) => ed[t]);
}
function ld(e) {
	return { top: 0, right: 0, bottom: 0, left: 0, ...e };
}
function vs(e) {
	return typeof e != "number"
		? ld(e)
		: { top: e, right: e, bottom: e, left: e };
}
function Tt(e) {
	const { x: t, y: n, width: o, height: r } = e;
	return {
		width: o,
		height: r,
		top: n,
		left: t,
		right: t + o,
		bottom: n + r,
		x: t,
		y: n,
	};
}
function Fo(e, t, n) {
	const { reference: o, floating: r } = e;
	const s = ve(t),
		i = Gn(t),
		a = Hn(i),
		l = Pe(t),
		u = s === "y",
		f = o.x + o.width / 2 - r.width / 2,
		d = o.y + o.height / 2 - r.height / 2,
		g = o[a] / 2 - r[a] / 2;
	let v;
	switch (l) {
		case "top":
			v = { x: f, y: o.y - r.height };
			break;
		case "bottom":
			v = { x: f, y: o.y + o.height };
			break;
		case "right":
			v = { x: o.x + o.width, y: d };
			break;
		case "left":
			v = { x: o.x - r.width, y: d };
			break;
		default:
			v = { x: o.x, y: o.y };
	}
	switch (qe(t)) {
		case "start":
			v[i] -= g * (n && u ? -1 : 1);
			break;
		case "end":
			v[i] += g * (n && u ? -1 : 1);
			break;
	}
	return v;
}
const ud = async (e, t, n) => {
	const {
			placement: o = "bottom",
			strategy: r = "absolute",
			middleware: s = [],
			platform: i,
		} = n,
		a = s.filter(Boolean),
		l = await (i.isRTL == null ? void 0 : i.isRTL(t));
	let u = await i.getElementRects({ reference: e, floating: t, strategy: r }),
		{ x: f, y: d } = Fo(u, o, l),
		g = o,
		v = {},
		h = 0;
	for (let m = 0; m < a.length; m++) {
		const { name: x, fn: w } = a[m],
			{
				x: b,
				y,
				data: C,
				reset: P,
			} = await w({
				x: f,
				y: d,
				initialPlacement: o,
				placement: g,
				strategy: r,
				middlewareData: v,
				rects: u,
				platform: i,
				elements: { reference: e, floating: t },
			});
		(f = b ?? f),
			(d = y ?? d),
			(v = { ...v, [x]: { ...v[x], ...C } }),
			P &&
				h <= 50 &&
				(h++,
				typeof P == "object" &&
					(P.placement && (g = P.placement),
					P.rects &&
						(u =
							P.rects === !0
								? await i.getElementRects({
										reference: e,
										floating: t,
										strategy: r,
									})
								: P.rects),
					({ x: f, y: d } = Fo(u, g, l))),
				(m = -1));
	}
	return { x: f, y: d, placement: g, strategy: r, middlewareData: v };
};
async function ot(e, t) {
	var n;
	t === void 0 && (t = {});
	const { x: o, y: r, platform: s, rects: i, elements: a, strategy: l } = e,
		{
			boundary: u = "clippingAncestors",
			rootBoundary: f = "viewport",
			elementContext: d = "floating",
			altBoundary: g = !1,
			padding: v = 0,
		} = Ee(t, e),
		h = vs(v),
		x = a[g ? (d === "floating" ? "reference" : "floating") : d],
		w = Tt(
			await s.getClippingRect({
				element:
					(n = await (s.isElement == null ? void 0 : s.isElement(x))) == null ||
					n
						? x
						: x.contextElement ||
							(await (s.getDocumentElement == null
								? void 0
								: s.getDocumentElement(a.floating))),
				boundary: u,
				rootBoundary: f,
				strategy: l,
			}),
		),
		b =
			d === "floating"
				? { x: o, y: r, width: i.floating.width, height: i.floating.height }
				: i.reference,
		y = await (s.getOffsetParent == null
			? void 0
			: s.getOffsetParent(a.floating)),
		C = (await (s.isElement == null ? void 0 : s.isElement(y)))
			? (await (s.getScale == null ? void 0 : s.getScale(y))) || { x: 1, y: 1 }
			: { x: 1, y: 1 },
		P = Tt(
			s.convertOffsetParentRelativeRectToViewportRelativeRect
				? await s.convertOffsetParentRelativeRectToViewportRelativeRect({
						elements: a,
						rect: b,
						offsetParent: y,
						strategy: l,
					})
				: b,
		);
	return {
		top: (w.top - P.top + h.top) / C.y,
		bottom: (P.bottom - w.bottom + h.bottom) / C.y,
		left: (w.left - P.left + h.left) / C.x,
		right: (P.right - w.right + h.right) / C.x,
	};
}
const dd = (e) => ({
		name: "arrow",
		options: e,
		async fn(t) {
			const {
					x: n,
					y: o,
					placement: r,
					rects: s,
					platform: i,
					elements: a,
					middlewareData: l,
				} = t,
				{ element: u, padding: f = 0 } = Ee(e, t) || {};
			if (u == null) return {};
			const d = vs(f),
				g = { x: n, y: o },
				v = Gn(r),
				h = Hn(v),
				m = await i.getDimensions(u),
				x = v === "y",
				w = x ? "top" : "left",
				b = x ? "bottom" : "right",
				y = x ? "clientHeight" : "clientWidth",
				C = s.reference[h] + s.reference[v] - g[v] - s.floating[h],
				P = g[v] - s.reference[v],
				T = await (i.getOffsetParent == null ? void 0 : i.getOffsetParent(u));
			let R = T ? T[y] : 0;
			(!R || !(await (i.isElement == null ? void 0 : i.isElement(T)))) &&
				(R = a.floating[y] || s.floating[h]);
			const E = C / 2 - P / 2,
				O = R / 2 - m[h] / 2 - 1,
				D = Ne(d[w], O),
				$ = Ne(d[b], O),
				L = D,
				V = R - m[h] - $,
				F = R / 2 - m[h] / 2 + E,
				W = yn(L, F, V),
				k =
					!l.arrow &&
					qe(r) != null &&
					F !== W &&
					s.reference[h] / 2 - (F < L ? D : $) - m[h] / 2 < 0,
				B = k ? (F < L ? F - L : F - V) : 0;
			return {
				[v]: g[v] + B,
				data: {
					[v]: W,
					centerOffset: F - W - B,
					...(k && { alignmentOffset: B }),
				},
				reset: k,
			};
		},
	}),
	fd = (e) => (
		e === void 0 && (e = {}),
		{
			name: "flip",
			options: e,
			async fn(t) {
				var n, o;
				const {
						placement: r,
						middlewareData: s,
						rects: i,
						initialPlacement: a,
						platform: l,
						elements: u,
					} = t,
					{
						mainAxis: f = !0,
						crossAxis: d = !0,
						fallbackPlacements: g,
						fallbackStrategy: v = "bestFit",
						fallbackAxisSideDirection: h = "none",
						flipAlignment: m = !0,
						...x
					} = Ee(e, t);
				if ((n = s.arrow) != null && n.alignmentOffset) return {};
				const w = Pe(r),
					b = ve(a),
					y = Pe(a) === a,
					C = await (l.isRTL == null ? void 0 : l.isRTL(u.floating)),
					P = g || (y || !m ? [It(a)] : rd(a)),
					T = h !== "none";
				!g && T && P.push(...cd(a, m, h, C));
				const R = [a, ...P],
					E = await ot(t, x),
					O = [];
				let D = ((o = s.flip) == null ? void 0 : o.overflows) || [];
				if ((f && O.push(E[w]), d)) {
					const F = od(r, i, C);
					O.push(E[F[0]], E[F[1]]);
				}
				if (
					((D = [...D, { placement: r, overflows: O }]),
					!O.every((F) => F <= 0))
				) {
					var $, L;
					const F = ((($ = s.flip) == null ? void 0 : $.index) || 0) + 1,
						W = R[F];
					if (
						W &&
						(!(d === "alignment" ? b !== ve(W) : !1) ||
							D.every((S) => (ve(S.placement) === b ? S.overflows[0] > 0 : !0)))
					)
						return {
							data: { index: F, overflows: D },
							reset: { placement: W },
						};
					let k =
						(L = D.filter((B) => B.overflows[0] <= 0).sort(
							(B, S) => B.overflows[1] - S.overflows[1],
						)[0]) == null
							? void 0
							: L.placement;
					if (!k)
						switch (v) {
							case "bestFit": {
								var V;
								const B =
									(V = D.filter((S) => {
										if (T) {
											const N = ve(S.placement);
											return N === b || N === "y";
										}
										return !0;
									})
										.map((S) => [
											S.placement,
											S.overflows
												.filter((N) => N > 0)
												.reduce((N, Z) => N + Z, 0),
										])
										.sort((S, N) => S[1] - N[1])[0]) == null
										? void 0
										: V[0];
								B && (k = B);
								break;
							}
							case "initialPlacement":
								k = a;
								break;
						}
					if (r !== k) return { reset: { placement: k } };
				}
				return {};
			},
		}
	);
function Bo(e, t) {
	return {
		top: e.top - t.height,
		right: e.right - t.width,
		bottom: e.bottom - t.height,
		left: e.left - t.width,
	};
}
function Vo(e) {
	return Ju.some((t) => e[t] >= 0);
}
const pd = (e) => (
		e === void 0 && (e = {}),
		{
			name: "hide",
			options: e,
			async fn(t) {
				const { rects: n } = t,
					{ strategy: o = "referenceHidden", ...r } = Ee(e, t);
				switch (o) {
					case "referenceHidden": {
						const s = await ot(t, { ...r, elementContext: "reference" }),
							i = Bo(s, n.reference);
						return {
							data: { referenceHiddenOffsets: i, referenceHidden: Vo(i) },
						};
					}
					case "escaped": {
						const s = await ot(t, { ...r, altBoundary: !0 }),
							i = Bo(s, n.floating);
						return { data: { escapedOffsets: i, escaped: Vo(i) } };
					}
					default:
						return {};
				}
			},
		}
	),
	xs = new Set(["left", "top"]);
async function md(e, t) {
	const { placement: n, platform: o, elements: r } = e,
		s = await (o.isRTL == null ? void 0 : o.isRTL(r.floating)),
		i = Pe(n),
		a = qe(n),
		l = ve(n) === "y",
		u = xs.has(i) ? -1 : 1,
		f = s && l ? -1 : 1,
		d = Ee(t, e);
	let {
		mainAxis: g,
		crossAxis: v,
		alignmentAxis: h,
	} = typeof d == "number"
		? { mainAxis: d, crossAxis: 0, alignmentAxis: null }
		: {
				mainAxis: d.mainAxis || 0,
				crossAxis: d.crossAxis || 0,
				alignmentAxis: d.alignmentAxis,
			};
	return (
		a && typeof h == "number" && (v = a === "end" ? h * -1 : h),
		l ? { x: v * f, y: g * u } : { x: g * u, y: v * f }
	);
}
const gd = (e) => (
		e === void 0 && (e = 0),
		{
			name: "offset",
			options: e,
			async fn(t) {
				var n, o;
				const { x: r, y: s, placement: i, middlewareData: a } = t,
					l = await md(t, e);
				return i === ((n = a.offset) == null ? void 0 : n.placement) &&
					(o = a.arrow) != null &&
					o.alignmentOffset
					? {}
					: { x: r + l.x, y: s + l.y, data: { ...l, placement: i } };
			},
		}
	),
	hd = (e) => (
		e === void 0 && (e = {}),
		{
			name: "shift",
			options: e,
			async fn(t) {
				const { x: n, y: o, placement: r } = t,
					{
						mainAxis: s = !0,
						crossAxis: i = !1,
						limiter: a = {
							fn: (x) => {
								const { x: w, y: b } = x;
								return { x: w, y: b };
							},
						},
						...l
					} = Ee(e, t),
					u = { x: n, y: o },
					f = await ot(t, l),
					d = ve(Pe(r)),
					g = zn(d);
				let v = u[g],
					h = u[d];
				if (s) {
					const x = g === "y" ? "top" : "left",
						w = g === "y" ? "bottom" : "right",
						b = v + f[x],
						y = v - f[w];
					v = yn(b, v, y);
				}
				if (i) {
					const x = d === "y" ? "top" : "left",
						w = d === "y" ? "bottom" : "right",
						b = h + f[x],
						y = h - f[w];
					h = yn(b, h, y);
				}
				const m = a.fn({ ...t, [g]: v, [d]: h });
				return {
					...m,
					data: { x: m.x - n, y: m.y - o, enabled: { [g]: s, [d]: i } },
				};
			},
		}
	),
	vd = (e) => (
		e === void 0 && (e = {}),
		{
			options: e,
			fn(t) {
				const { x: n, y: o, placement: r, rects: s, middlewareData: i } = t,
					{ offset: a = 0, mainAxis: l = !0, crossAxis: u = !0 } = Ee(e, t),
					f = { x: n, y: o },
					d = ve(r),
					g = zn(d);
				let v = f[g],
					h = f[d];
				const m = Ee(a, t),
					x =
						typeof m == "number"
							? { mainAxis: m, crossAxis: 0 }
							: { mainAxis: 0, crossAxis: 0, ...m };
				if (l) {
					const y = g === "y" ? "height" : "width",
						C = s.reference[g] - s.floating[y] + x.mainAxis,
						P = s.reference[g] + s.reference[y] - x.mainAxis;
					v < C ? (v = C) : v > P && (v = P);
				}
				if (u) {
					var w, b;
					const y = g === "y" ? "width" : "height",
						C = xs.has(Pe(r)),
						P =
							s.reference[d] -
							s.floating[y] +
							((C && ((w = i.offset) == null ? void 0 : w[d])) || 0) +
							(C ? 0 : x.crossAxis),
						T =
							s.reference[d] +
							s.reference[y] +
							(C ? 0 : ((b = i.offset) == null ? void 0 : b[d]) || 0) -
							(C ? x.crossAxis : 0);
					h < P ? (h = P) : h > T && (h = T);
				}
				return { [g]: v, [d]: h };
			},
		}
	),
	xd = (e) => (
		e === void 0 && (e = {}),
		{
			name: "size",
			options: e,
			async fn(t) {
				var n, o;
				const { placement: r, rects: s, platform: i, elements: a } = t,
					{ apply: l = () => {}, ...u } = Ee(e, t),
					f = await ot(t, u),
					d = Pe(r),
					g = qe(r),
					v = ve(r) === "y",
					{ width: h, height: m } = s.floating;
				let x, w;
				d === "top" || d === "bottom"
					? ((x = d),
						(w =
							g ===
							((await (i.isRTL == null ? void 0 : i.isRTL(a.floating)))
								? "start"
								: "end")
								? "left"
								: "right"))
					: ((w = d), (x = g === "end" ? "top" : "bottom"));
				const b = m - f.top - f.bottom,
					y = h - f.left - f.right,
					C = Ne(m - f[x], b),
					P = Ne(h - f[w], y),
					T = !t.middlewareData.shift;
				let R = C,
					E = P;
				if (
					((n = t.middlewareData.shift) != null && n.enabled.x && (E = y),
					(o = t.middlewareData.shift) != null && o.enabled.y && (R = b),
					T && !g)
				) {
					const D = ae(f.left, 0),
						$ = ae(f.right, 0),
						L = ae(f.top, 0),
						V = ae(f.bottom, 0);
					v
						? (E = h - 2 * (D !== 0 || $ !== 0 ? D + $ : ae(f.left, f.right)))
						: (R = m - 2 * (L !== 0 || V !== 0 ? L + V : ae(f.top, f.bottom)));
				}
				await l({ ...t, availableWidth: E, availableHeight: R });
				const O = await i.getDimensions(a.floating);
				return h !== O.width || m !== O.height ? { reset: { rects: !0 } } : {};
			},
		}
	);
function zt() {
	return typeof window < "u";
}
function Ze(e) {
	return ws(e) ? (e.nodeName || "").toLowerCase() : "#document";
}
function ce(e) {
	var t;
	return (
		(e == null || (t = e.ownerDocument) == null ? void 0 : t.defaultView) ||
		window
	);
}
function Ce(e) {
	var t;
	return (t = (ws(e) ? e.ownerDocument : e.document) || window.document) == null
		? void 0
		: t.documentElement;
}
function ws(e) {
	return zt() ? e instanceof Node || e instanceof ce(e).Node : !1;
}
function pe(e) {
	return zt() ? e instanceof Element || e instanceof ce(e).Element : !1;
}
function be(e) {
	return zt() ? e instanceof HTMLElement || e instanceof ce(e).HTMLElement : !1;
}
function Wo(e) {
	return !zt() || typeof ShadowRoot > "u"
		? !1
		: e instanceof ShadowRoot || e instanceof ce(e).ShadowRoot;
}
const wd = new Set(["inline", "contents"]);
function ft(e) {
	const { overflow: t, overflowX: n, overflowY: o, display: r } = me(e);
	return /auto|scroll|overlay|hidden|clip/.test(t + o + n) && !wd.has(r);
}
const bd = new Set(["table", "td", "th"]);
function yd(e) {
	return bd.has(Ze(e));
}
const Cd = [":popover-open", ":modal"];
function Ht(e) {
	return Cd.some((t) => {
		try {
			return e.matches(t);
		} catch {
			return !1;
		}
	});
}
const Sd = ["transform", "translate", "scale", "rotate", "perspective"],
	Ed = ["transform", "translate", "scale", "rotate", "perspective", "filter"],
	Pd = ["paint", "layout", "strict", "content"];
function Un(e) {
	const t = Kn(),
		n = pe(e) ? me(e) : e;
	return (
		Sd.some((o) => (n[o] ? n[o] !== "none" : !1)) ||
		(n.containerType ? n.containerType !== "normal" : !1) ||
		(!t && (n.backdropFilter ? n.backdropFilter !== "none" : !1)) ||
		(!t && (n.filter ? n.filter !== "none" : !1)) ||
		Ed.some((o) => (n.willChange || "").includes(o)) ||
		Pd.some((o) => (n.contain || "").includes(o))
	);
}
function Rd(e) {
	let t = Ae(e);
	for (; be(t) && !Ue(t); ) {
		if (Un(t)) return t;
		if (Ht(t)) return null;
		t = Ae(t);
	}
	return null;
}
function Kn() {
	return typeof CSS > "u" || !CSS.supports
		? !1
		: CSS.supports("-webkit-backdrop-filter", "none");
}
const _d = new Set(["html", "body", "#document"]);
function Ue(e) {
	return _d.has(Ze(e));
}
function me(e) {
	return ce(e).getComputedStyle(e);
}
function Gt(e) {
	return pe(e)
		? { scrollLeft: e.scrollLeft, scrollTop: e.scrollTop }
		: { scrollLeft: e.scrollX, scrollTop: e.scrollY };
}
function Ae(e) {
	if (Ze(e) === "html") return e;
	const t = e.assignedSlot || e.parentNode || (Wo(e) && e.host) || Ce(e);
	return Wo(t) ? t.host : t;
}
function bs(e) {
	const t = Ae(e);
	return Ue(t)
		? e.ownerDocument
			? e.ownerDocument.body
			: e.body
		: be(t) && ft(t)
			? t
			: bs(t);
}
function rt(e, t, n) {
	var o;
	t === void 0 && (t = []), n === void 0 && (n = !0);
	const r = bs(e),
		s = r === ((o = e.ownerDocument) == null ? void 0 : o.body),
		i = ce(r);
	if (s) {
		const a = Sn(i);
		return t.concat(
			i,
			i.visualViewport || [],
			ft(r) ? r : [],
			a && n ? rt(a) : [],
		);
	}
	return t.concat(r, rt(r, [], n));
}
function Sn(e) {
	return e.parent && Object.getPrototypeOf(e.parent) ? e.frameElement : null;
}
function ys(e) {
	const t = me(e);
	let n = parseFloat(t.width) || 0,
		o = parseFloat(t.height) || 0;
	const r = be(e),
		s = r ? e.offsetWidth : n,
		i = r ? e.offsetHeight : o,
		a = Mt(n) !== s || Mt(o) !== i;
	return a && ((n = s), (o = i)), { width: n, height: o, $: a };
}
function Yn(e) {
	return pe(e) ? e : e.contextElement;
}
function Ge(e) {
	const t = Yn(e);
	if (!be(t)) return xe(1);
	const n = t.getBoundingClientRect(),
		{ width: o, height: r, $: s } = ys(t);
	let i = (s ? Mt(n.width) : n.width) / o,
		a = (s ? Mt(n.height) : n.height) / r;
	return (
		(!i || !Number.isFinite(i)) && (i = 1),
		(!a || !Number.isFinite(a)) && (a = 1),
		{ x: i, y: a }
	);
}
const Nd = xe(0);
function Cs(e) {
	const t = ce(e);
	return !Kn() || !t.visualViewport
		? Nd
		: { x: t.visualViewport.offsetLeft, y: t.visualViewport.offsetTop };
}
function Ad(e, t, n) {
	return t === void 0 && (t = !1), !n || (t && n !== ce(e)) ? !1 : t;
}
function je(e, t, n, o) {
	t === void 0 && (t = !1), n === void 0 && (n = !1);
	const r = e.getBoundingClientRect(),
		s = Yn(e);
	let i = xe(1);
	t && (o ? pe(o) && (i = Ge(o)) : (i = Ge(e)));
	const a = Ad(s, n, o) ? Cs(s) : xe(0);
	let l = (r.left + a.x) / i.x,
		u = (r.top + a.y) / i.y,
		f = r.width / i.x,
		d = r.height / i.y;
	if (s) {
		const g = ce(s),
			v = o && pe(o) ? ce(o) : o;
		let h = g,
			m = Sn(h);
		for (; m && o && v !== h; ) {
			const x = Ge(m),
				w = m.getBoundingClientRect(),
				b = me(m),
				y = w.left + (m.clientLeft + parseFloat(b.paddingLeft)) * x.x,
				C = w.top + (m.clientTop + parseFloat(b.paddingTop)) * x.y;
			(l *= x.x),
				(u *= x.y),
				(f *= x.x),
				(d *= x.y),
				(l += y),
				(u += C),
				(h = ce(m)),
				(m = Sn(h));
		}
	}
	return Tt({ width: f, height: d, x: l, y: u });
}
function Ut(e, t) {
	const n = Gt(e).scrollLeft;
	return t ? t.left + n : je(Ce(e)).left + n;
}
function Ss(e, t) {
	const n = e.getBoundingClientRect(),
		o = n.left + t.scrollLeft - Ut(e, n),
		r = n.top + t.scrollTop;
	return { x: o, y: r };
}
function Md(e) {
	const { elements: t, rect: n, offsetParent: o, strategy: r } = e;
	const s = r === "fixed",
		i = Ce(o),
		a = t ? Ht(t.floating) : !1;
	if (o === i || (a && s)) return n;
	let l = { scrollLeft: 0, scrollTop: 0 },
		u = xe(1);
	const f = xe(0),
		d = be(o);
	if (
		(d || (!d && !s)) &&
		((Ze(o) !== "body" || ft(i)) && (l = Gt(o)), be(o))
	) {
		const v = je(o);
		(u = Ge(o)), (f.x = v.x + o.clientLeft), (f.y = v.y + o.clientTop);
	}
	const g = i && !d && !s ? Ss(i, l) : xe(0);
	return {
		width: n.width * u.x,
		height: n.height * u.y,
		x: n.x * u.x - l.scrollLeft * u.x + f.x + g.x,
		y: n.y * u.y - l.scrollTop * u.y + f.y + g.y,
	};
}
function Id(e) {
	return Array.from(e.getClientRects());
}
function Td(e) {
	const t = Ce(e),
		n = Gt(e),
		o = e.ownerDocument.body,
		r = ae(t.scrollWidth, t.clientWidth, o.scrollWidth, o.clientWidth),
		s = ae(t.scrollHeight, t.clientHeight, o.scrollHeight, o.clientHeight);
	let i = -n.scrollLeft + Ut(e);
	const a = -n.scrollTop;
	return (
		me(o).direction === "rtl" && (i += ae(t.clientWidth, o.clientWidth) - r),
		{ width: r, height: s, x: i, y: a }
	);
}
const zo = 25;
function kd(e, t) {
	const n = ce(e),
		o = Ce(e),
		r = n.visualViewport;
	let s = o.clientWidth,
		i = o.clientHeight,
		a = 0,
		l = 0;
	if (r) {
		(s = r.width), (i = r.height);
		const f = Kn();
		(!f || (f && t === "fixed")) && ((a = r.offsetLeft), (l = r.offsetTop));
	}
	const u = Ut(o);
	if (u <= 0) {
		const f = o.ownerDocument,
			d = f.body,
			g = getComputedStyle(d),
			v =
				(f.compatMode === "CSS1Compat" &&
					parseFloat(g.marginLeft) + parseFloat(g.marginRight)) ||
				0,
			h = Math.abs(o.clientWidth - d.clientWidth - v);
		h <= zo && (s -= h);
	} else u <= zo && (s += u);
	return { width: s, height: i, x: a, y: l };
}
const Od = new Set(["absolute", "fixed"]);
function Dd(e, t) {
	const n = je(e, !0, t === "fixed"),
		o = n.top + e.clientTop,
		r = n.left + e.clientLeft,
		s = be(e) ? Ge(e) : xe(1),
		i = e.clientWidth * s.x,
		a = e.clientHeight * s.y,
		l = r * s.x,
		u = o * s.y;
	return { width: i, height: a, x: l, y: u };
}
function Ho(e, t, n) {
	let o;
	if (t === "viewport") o = kd(e, n);
	else if (t === "document") o = Td(Ce(e));
	else if (pe(t)) o = Dd(t, n);
	else {
		const r = Cs(e);
		o = { x: t.x - r.x, y: t.y - r.y, width: t.width, height: t.height };
	}
	return Tt(o);
}
function Es(e, t) {
	const n = Ae(e);
	return n === t || !pe(n) || Ue(n)
		? !1
		: me(n).position === "fixed" || Es(n, t);
}
function jd(e, t) {
	const n = t.get(e);
	if (n) return n;
	let o = rt(e, [], !1).filter((a) => pe(a) && Ze(a) !== "body"),
		r = null;
	const s = me(e).position === "fixed";
	let i = s ? Ae(e) : e;
	for (; pe(i) && !Ue(i); ) {
		const a = me(i),
			l = Un(i);
		!l && a.position === "fixed" && (r = null),
			(
				s
					? !l && !r
					: (!l && a.position === "static" && !!r && Od.has(r.position)) ||
						(ft(i) && !l && Es(e, i))
			)
				? (o = o.filter((f) => f !== i))
				: (r = a),
			(i = Ae(i));
	}
	return t.set(e, o), o;
}
function $d(e) {
	const { element: t, boundary: n, rootBoundary: o, strategy: r } = e;
	const i = [
			...(n === "clippingAncestors"
				? Ht(t)
					? []
					: jd(t, this._c)
				: [].concat(n)),
			o,
		],
		a = i[0],
		l = i.reduce(
			(u, f) => {
				const d = Ho(t, f, r);
				return (
					(u.top = ae(d.top, u.top)),
					(u.right = Ne(d.right, u.right)),
					(u.bottom = Ne(d.bottom, u.bottom)),
					(u.left = ae(d.left, u.left)),
					u
				);
			},
			Ho(t, a, r),
		);
	return {
		width: l.right - l.left,
		height: l.bottom - l.top,
		x: l.left,
		y: l.top,
	};
}
function Ld(e) {
	const { width: t, height: n } = ys(e);
	return { width: t, height: n };
}
function Fd(e, t, n) {
	const o = be(t),
		r = Ce(t),
		s = n === "fixed",
		i = je(e, !0, s, t);
	let a = { scrollLeft: 0, scrollTop: 0 };
	const l = xe(0);
	function u() {
		l.x = Ut(r);
	}
	if (o || (!o && !s))
		if (((Ze(t) !== "body" || ft(r)) && (a = Gt(t)), o)) {
			const v = je(t, !0, s, t);
			(l.x = v.x + t.clientLeft), (l.y = v.y + t.clientTop);
		} else r && u();
	s && !o && r && u();
	const f = r && !o && !s ? Ss(r, a) : xe(0),
		d = i.left + a.scrollLeft - l.x - f.x,
		g = i.top + a.scrollTop - l.y - f.y;
	return { x: d, y: g, width: i.width, height: i.height };
}
function gn(e) {
	return me(e).position === "static";
}
function Go(e, t) {
	if (!be(e) || me(e).position === "fixed") return null;
	if (t) return t(e);
	let n = e.offsetParent;
	return Ce(e) === n && (n = n.ownerDocument.body), n;
}
function Ps(e, t) {
	const n = ce(e);
	if (Ht(e)) return n;
	if (!be(e)) {
		let r = Ae(e);
		for (; r && !Ue(r); ) {
			if (pe(r) && !gn(r)) return r;
			r = Ae(r);
		}
		return n;
	}
	let o = Go(e, t);
	for (; o && yd(o) && gn(o); ) o = Go(o, t);
	return o && Ue(o) && gn(o) && !Un(o) ? n : o || Rd(e) || n;
}
const Bd = async function (e) {
	const t = this.getOffsetParent || Ps,
		n = this.getDimensions,
		o = await n(e.floating);
	return {
		reference: Fd(e.reference, await t(e.floating), e.strategy),
		floating: { x: 0, y: 0, width: o.width, height: o.height },
	};
};
function Vd(e) {
	return me(e).direction === "rtl";
}
const Wd = {
	convertOffsetParentRelativeRectToViewportRelativeRect: Md,
	getDocumentElement: Ce,
	getClippingRect: $d,
	getOffsetParent: Ps,
	getElementRects: Bd,
	getClientRects: Id,
	getDimensions: Ld,
	getScale: Ge,
	isElement: pe,
	isRTL: Vd,
};
function Rs(e, t) {
	return (
		e.x === t.x && e.y === t.y && e.width === t.width && e.height === t.height
	);
}
function zd(e, t) {
	let n = null,
		o;
	const r = Ce(e);
	function s() {
		var a;
		clearTimeout(o), (a = n) == null || a.disconnect(), (n = null);
	}
	function i(a, l) {
		a === void 0 && (a = !1), l === void 0 && (l = 1), s();
		const u = e.getBoundingClientRect(),
			{ left: f, top: d, width: g, height: v } = u;
		if ((a || t(), !g || !v)) return;
		const h = St(d),
			m = St(r.clientWidth - (f + g)),
			x = St(r.clientHeight - (d + v)),
			w = St(f),
			y = {
				rootMargin: -h + "px " + -m + "px " + -x + "px " + -w + "px",
				threshold: ae(0, Ne(1, l)) || 1,
			};
		let C = !0;
		function P(T) {
			const R = T[0].intersectionRatio;
			if (R !== l) {
				if (!C) return i();
				R
					? i(!1, R)
					: (o = setTimeout(() => {
							i(!1, 1e-7);
						}, 1e3));
			}
			R === 1 && !Rs(u, e.getBoundingClientRect()) && i(), (C = !1);
		}
		try {
			n = new IntersectionObserver(P, { ...y, root: r.ownerDocument });
		} catch {
			n = new IntersectionObserver(P, y);
		}
		n.observe(e);
	}
	return i(!0), s;
}
function Hd(e, t, n, o) {
	o === void 0 && (o = {});
	const {
			ancestorScroll: r = !0,
			ancestorResize: s = !0,
			elementResize: i = typeof ResizeObserver == "function",
			layoutShift: a = typeof IntersectionObserver == "function",
			animationFrame: l = !1,
		} = o,
		u = Yn(e),
		f = r || s ? [...(u ? rt(u) : []), ...rt(t)] : [];
	f.forEach((w) => {
		r && w.addEventListener("scroll", n, { passive: !0 }),
			s && w.addEventListener("resize", n);
	});
	const d = u && a ? zd(u, n) : null;
	let g = -1,
		v = null;
	i &&
		((v = new ResizeObserver((w) => {
			const [b] = w;
			b &&
				b.target === u &&
				v &&
				(v.unobserve(t),
				cancelAnimationFrame(g),
				(g = requestAnimationFrame(() => {
					var y;
					(y = v) == null || y.observe(t);
				}))),
				n();
		})),
		u && !l && v.observe(u),
		v.observe(t));
	let h,
		m = l ? je(e) : null;
	l && x();
	function x() {
		const w = je(e);
		m && !Rs(m, w) && n(), (m = w), (h = requestAnimationFrame(x));
	}
	return (
		n(),
		() => {
			var w;
			f.forEach((b) => {
				r && b.removeEventListener("scroll", n),
					s && b.removeEventListener("resize", n);
			}),
				d?.(),
				(w = v) == null || w.disconnect(),
				(v = null),
				l && cancelAnimationFrame(h);
		}
	);
}
const Gd = gd,
	Ud = hd,
	Kd = fd,
	Yd = xd,
	Xd = pd,
	Uo = dd,
	qd = vd,
	Zd = (e, t, n) => {
		const o = new Map(),
			r = { platform: Wd, ...n },
			s = { ...r.platform, _c: o };
		return ud(e, t, { ...r, platform: s });
	};
var Qd = typeof document < "u",
	Jd = () => {},
	Rt = Qd ? c.useLayoutEffect : Jd;
function kt(e, t) {
	if (e === t) return !0;
	if (typeof e != typeof t) return !1;
	if (typeof e == "function" && e.toString() === t.toString()) return !0;
	let n, o, r;
	if (e && t && typeof e == "object") {
		if (Array.isArray(e)) {
			if (((n = e.length), n !== t.length)) return !1;
			for (o = n; o-- !== 0; ) if (!kt(e[o], t[o])) return !1;
			return !0;
		}
		if (((r = Object.keys(e)), (n = r.length), n !== Object.keys(t).length))
			return !1;
		for (o = n; o-- !== 0; ) if (!Object.hasOwn(t, r[o])) return !1;
		for (o = n; o-- !== 0; ) {
			const s = r[o];
			if (!(s === "_owner" && e.$$typeof) && !kt(e[s], t[s])) return !1;
		}
		return !0;
	}
	return e !== e && t !== t;
}
function _s(e) {
	return typeof window > "u"
		? 1
		: (e.ownerDocument.defaultView || window).devicePixelRatio || 1;
}
function Ko(e, t) {
	const n = _s(e);
	return Math.round(t * n) / n;
}
function hn(e) {
	const t = c.useRef(e);
	return (
		Rt(() => {
			t.current = e;
		}),
		t
	);
}
function ef(e) {
	e === void 0 && (e = {});
	const {
			placement: t = "bottom",
			strategy: n = "absolute",
			middleware: o = [],
			platform: r,
			elements: { reference: s, floating: i } = {},
			transform: a = !0,
			whileElementsMounted: l,
			open: u,
		} = e,
		[f, d] = c.useState({
			x: 0,
			y: 0,
			strategy: n,
			placement: t,
			middlewareData: {},
			isPositioned: !1,
		}),
		[g, v] = c.useState(o);
	kt(g, o) || v(o);
	const [h, m] = c.useState(null),
		[x, w] = c.useState(null),
		b = c.useCallback((S) => {
			S !== T.current && ((T.current = S), m(S));
		}, []),
		y = c.useCallback((S) => {
			S !== R.current && ((R.current = S), w(S));
		}, []),
		C = s || h,
		P = i || x,
		T = c.useRef(null),
		R = c.useRef(null),
		E = c.useRef(f),
		O = l != null,
		D = hn(l),
		$ = hn(r),
		L = hn(u),
		V = c.useCallback(() => {
			if (!T.current || !R.current) return;
			const S = { placement: t, strategy: n, middleware: g };
			$.current && (S.platform = $.current),
				Zd(T.current, R.current, S).then((N) => {
					const Z = { ...N, isPositioned: L.current !== !1 };
					F.current &&
						!kt(E.current, Z) &&
						((E.current = Z),
						at.flushSync(() => {
							d(Z);
						}));
				});
		}, [g, t, n, $, L]);
	Rt(() => {
		u === !1 &&
			E.current.isPositioned &&
			((E.current.isPositioned = !1), d((S) => ({ ...S, isPositioned: !1 })));
	}, [u]);
	const F = c.useRef(!1);
	Rt(
		() => (
			(F.current = !0),
			() => {
				F.current = !1;
			}
		),
		[],
	),
		Rt(() => {
			if ((C && (T.current = C), P && (R.current = P), C && P)) {
				if (D.current) return D.current(C, P, V);
				V();
			}
		}, [C, P, V, D, O]);
	const W = c.useMemo(
			() => ({ reference: T, floating: R, setReference: b, setFloating: y }),
			[b, y],
		),
		k = c.useMemo(() => ({ reference: C, floating: P }), [C, P]),
		B = c.useMemo(() => {
			const S = { position: n, left: 0, top: 0 };
			if (!k.floating) return S;
			const N = Ko(k.floating, f.x),
				Z = Ko(k.floating, f.y);
			return a
				? {
						...S,
						transform: "translate(" + N + "px, " + Z + "px)",
						...(_s(k.floating) >= 1.5 && { willChange: "transform" }),
					}
				: { position: n, left: N, top: Z };
		}, [n, a, k.floating, f.x, f.y]);
	return c.useMemo(
		() => ({ ...f, update: V, refs: W, elements: k, floatingStyles: B }),
		[f, V, W, k, B],
	);
}
const tf = (e) => {
		function t(n) {
			return Object.hasOwn(n, "current");
		}
		return {
			name: "arrow",
			options: e,
			fn(n) {
				const { element: o, padding: r } = typeof e == "function" ? e(n) : e;
				return o && t(o)
					? o.current != null
						? Uo({ element: o.current, padding: r }).fn(n)
						: {}
					: o
						? Uo({ element: o, padding: r }).fn(n)
						: {};
			},
		};
	},
	nf = (e, t) => ({ ...Gd(e), options: [e, t] }),
	of = (e, t) => ({ ...Ud(e), options: [e, t] }),
	rf = (e, t) => ({ ...qd(e), options: [e, t] }),
	sf = (e, t) => ({ ...Kd(e), options: [e, t] }),
	af = (e, t) => ({ ...Yd(e), options: [e, t] }),
	cf = (e, t) => ({ ...Xd(e), options: [e, t] }),
	lf = (e, t) => ({ ...tf(e), options: [e, t] });
var uf = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	df = uf.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	ff = "Arrow",
	Ns = c.forwardRef((e, t) => {
		const { children: n, width: o = 10, height: r = 5, ...s } = e;
		return p.jsx(df.svg, {
			...s,
			ref: t,
			width: o,
			height: r,
			viewBox: "0 0 30 10",
			preserveAspectRatio: "none",
			children: e.asChild ? n : p.jsx("polygon", { points: "0,0 30,0 15,10" }),
		});
	});
Ns.displayName = ff;
var pf = Ns;
function mf(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, gf(r, ...t)];
}
function gf(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var hf = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	As = hf.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {});
function vf(e) {
	const [t, n] = c.useState(void 0);
	return (
		ee(() => {
			if (e) {
				n({ width: e.offsetWidth, height: e.offsetHeight });
				const o = new ResizeObserver((r) => {
					if (!Array.isArray(r) || !r.length) return;
					const s = r[0];
					let i, a;
					if ("borderBoxSize" in s) {
						const l = s.borderBoxSize,
							u = Array.isArray(l) ? l[0] : l;
						(i = u.inlineSize), (a = u.blockSize);
					} else (i = e.offsetWidth), (a = e.offsetHeight);
					n({ width: i, height: a });
				});
				return o.observe(e, { box: "border-box" }), () => o.unobserve(e);
			} else n(void 0);
		}, [e]),
		t
	);
}
var Ms = "Popper",
	[Is, Qe] = mf(Ms),
	[fg, Ts] = Is(Ms),
	ks = "PopperAnchor",
	Os = c.forwardRef((e, t) => {
		const { __scopePopper: n, virtualRef: o, ...r } = e,
			s = Ts(ks, n),
			i = c.useRef(null),
			a = G(t, i),
			l = c.useRef(null);
		return (
			c.useEffect(() => {
				const u = l.current;
				(l.current = o?.current || i.current),
					u !== l.current && s.onAnchorChange(l.current);
			}),
			o ? null : p.jsx(As.div, { ...r, ref: a })
		);
	});
Os.displayName = ks;
var Xn = "PopperContent",
	[xf, wf] = Is(Xn),
	Ds = c.forwardRef((e, t) => {
		const {
				__scopePopper: n,
				side: o = "bottom",
				sideOffset: r = 0,
				align: s = "center",
				alignOffset: i = 0,
				arrowPadding: a = 0,
				avoidCollisions: l = !0,
				collisionBoundary: u = [],
				collisionPadding: f = 0,
				sticky: d = "partial",
				hideWhenDetached: g = !1,
				updatePositionStrategy: v = "optimized",
				onPlaced: h,
				...m
			} = e,
			x = Ts(Xn, n),
			[w, b] = c.useState(null),
			y = G(t, (_) => b(_)),
			[C, P] = c.useState(null),
			T = vf(C),
			R = T?.width ?? 0,
			E = T?.height ?? 0,
			O = o + (s !== "center" ? "-" + s : ""),
			D =
				typeof f == "number"
					? f
					: { top: 0, right: 0, bottom: 0, left: 0, ...f },
			$ = Array.isArray(u) ? u : [u],
			L = $.length > 0,
			V = { padding: D, boundary: $.filter(yf), altBoundary: L },
			{
				refs: F,
				floatingStyles: W,
				placement: k,
				isPositioned: B,
				middlewareData: S,
			} = ef({
				strategy: "fixed",
				placement: O,
				whileElementsMounted: (..._) =>
					Hd(..._, { animationFrame: v === "always" }),
				elements: { reference: x.anchor },
				middleware: [
					nf({ mainAxis: r + E, alignmentAxis: i }),
					l &&
						of({
							mainAxis: !0,
							crossAxis: !1,
							limiter: d === "partial" ? rf() : void 0,
							...V,
						}),
					l && sf({ ...V }),
					af({
						...V,
						apply: ({
							elements: _,
							rects: U,
							availableWidth: Q,
							availableHeight: H,
						}) => {
							const { width: K, height: q } = U.reference,
								ue = _.floating.style;
							ue.setProperty("--radix-popper-available-width", `${Q}px`),
								ue.setProperty("--radix-popper-available-height", `${H}px`),
								ue.setProperty("--radix-popper-anchor-width", `${K}px`),
								ue.setProperty("--radix-popper-anchor-height", `${q}px`);
						},
					}),
					C && lf({ element: C, padding: a }),
					Cf({ arrowWidth: R, arrowHeight: E }),
					g && cf({ strategy: "referenceHidden", ...V }),
				],
			}),
			[N, Z] = Ls(k),
			te = we(h);
		ee(() => {
			B && te?.();
		}, [B, te]);
		const re = S.arrow?.x,
			X = S.arrow?.y,
			Y = S.arrow?.centerOffset !== 0,
			[se, oe] = c.useState();
		return (
			ee(() => {
				w && oe(window.getComputedStyle(w).zIndex);
			}, [w]),
			p.jsx("div", {
				ref: F.setFloating,
				"data-radix-popper-content-wrapper": "",
				style: {
					...W,
					transform: B ? W.transform : "translate(0, -200%)",
					minWidth: "max-content",
					zIndex: se,
					"--radix-popper-transform-origin": [
						S.transformOrigin?.x,
						S.transformOrigin?.y,
					].join(" "),
					...(S.hide?.referenceHidden && {
						visibility: "hidden",
						pointerEvents: "none",
					}),
				},
				dir: e.dir,
				children: p.jsx(xf, {
					scope: n,
					placedSide: N,
					onArrowChange: P,
					arrowX: re,
					arrowY: X,
					shouldHideArrow: Y,
					children: p.jsx(As.div, {
						"data-side": N,
						"data-align": Z,
						...m,
						ref: y,
						style: { ...m.style, animation: B ? void 0 : "none" },
					}),
				}),
			})
		);
	});
Ds.displayName = Xn;
var js = "PopperArrow",
	bf = { top: "bottom", right: "left", bottom: "top", left: "right" },
	$s = c.forwardRef((t, n) => {
		const { __scopePopper: o, ...r } = t,
			s = wf(js, o),
			i = bf[s.placedSide];
		return p.jsx("span", {
			ref: s.onArrowChange,
			style: {
				position: "absolute",
				left: s.arrowX,
				top: s.arrowY,
				[i]: 0,
				transformOrigin: {
					top: "",
					right: "0 0",
					bottom: "center 0",
					left: "100% 0",
				}[s.placedSide],
				transform: {
					top: "translateY(100%)",
					right: "translateY(50%) rotate(90deg) translateX(-50%)",
					bottom: "rotate(180deg)",
					left: "translateY(50%) rotate(-90deg) translateX(50%)",
				}[s.placedSide],
				visibility: s.shouldHideArrow ? "hidden" : void 0,
			},
			children: p.jsx(pf, {
				...r,
				ref: n,
				style: { ...r.style, display: "block" },
			}),
		});
	});
$s.displayName = js;
function yf(e) {
	return e !== null;
}
var Cf = (e) => ({
	name: "transformOrigin",
	options: e,
	fn(t) {
		const { placement: n, rects: o, middlewareData: r } = t,
			i = r.arrow?.centerOffset !== 0,
			a = i ? 0 : e.arrowWidth,
			l = i ? 0 : e.arrowHeight,
			[u, f] = Ls(n),
			d = { start: "0%", center: "50%", end: "100%" }[f],
			g = (r.arrow?.x ?? 0) + a / 2,
			v = (r.arrow?.y ?? 0) + l / 2;
		let h = "",
			m = "";
		return (
			u === "bottom"
				? ((h = i ? d : `${g}px`), (m = `${-l}px`))
				: u === "top"
					? ((h = i ? d : `${g}px`), (m = `${o.floating.height + l}px`))
					: u === "right"
						? ((h = `${-l}px`), (m = i ? d : `${v}px`))
						: u === "left" &&
							((h = `${o.floating.width + l}px`), (m = i ? d : `${v}px`)),
			{ data: { x: h, y: m } }
		);
	},
});
function Ls(e) {
	const [t, n = "center"] = e.split("-");
	return [t, n];
}
var qn = Os,
	Zn = Ds,
	Qn = $s,
	Sf = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	pt = Sf.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {});
function Ef(e, t) {
	e && at.flushSync(() => e.dispatchEvent(t));
}
function Pf(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Rf(r, ...t)];
}
function Rf(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var _f = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	Fs = _f.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	vn = "rovingFocusGroup.onEntryFocus",
	Nf = { bubbles: !1, cancelable: !0 },
	mt = "RovingFocusGroup",
	[En, Bs, Af] = Wn(mt),
	[Mf, Kt] = Pf(mt, [Af]),
	[If, Tf] = Mf(mt),
	Vs = c.forwardRef((e, t) =>
		p.jsx(En.Provider, {
			scope: e.__scopeRovingFocusGroup,
			children: p.jsx(En.Slot, {
				scope: e.__scopeRovingFocusGroup,
				children: p.jsx(kf, { ...e, ref: t }),
			}),
		}),
	);
Vs.displayName = mt;
var kf = c.forwardRef((e, t) => {
		const {
				__scopeRovingFocusGroup: n,
				orientation: o,
				loop: r = !1,
				dir: s,
				currentTabStopId: i,
				defaultCurrentTabStopId: a,
				onCurrentTabStopIdChange: l,
				onEntryFocus: u,
				preventScrollOnEntryFocus: f = !1,
				...d
			} = e,
			g = c.useRef(null),
			v = G(t, g),
			h = hs(s),
			[m, x] = jr({ prop: i, defaultProp: a ?? null, onChange: l, caller: mt }),
			[w, b] = c.useState(!1),
			y = we(u),
			C = Bs(n),
			P = c.useRef(!1),
			[T, R] = c.useState(0);
		return (
			c.useEffect(() => {
				const E = g.current;
				if (E)
					return E.addEventListener(vn, y), () => E.removeEventListener(vn, y);
			}, [y]),
			p.jsx(If, {
				scope: n,
				orientation: o,
				dir: h,
				loop: r,
				currentTabStopId: m,
				onItemFocus: c.useCallback((E) => x(E), [x]),
				onItemShiftTab: c.useCallback(() => b(!0), []),
				onFocusableItemAdd: c.useCallback(() => R((E) => E + 1), []),
				onFocusableItemRemove: c.useCallback(() => R((E) => E - 1), []),
				children: p.jsx(Fs.div, {
					tabIndex: w || T === 0 ? -1 : 0,
					"data-orientation": o,
					...d,
					ref: v,
					style: { outline: "none", ...e.style },
					onMouseDown: A(e.onMouseDown, () => {
						P.current = !0;
					}),
					onFocus: A(e.onFocus, (E) => {
						const O = !P.current;
						if (E.target === E.currentTarget && O && !w) {
							const D = new CustomEvent(vn, Nf);
							if ((E.currentTarget.dispatchEvent(D), !D.defaultPrevented)) {
								const $ = C().filter((k) => k.focusable),
									L = $.find((k) => k.active),
									V = $.find((k) => k.id === m),
									W = [L, V, ...$].filter(Boolean).map((k) => k.ref.current);
								Hs(W, f);
							}
						}
						P.current = !1;
					}),
					onBlur: A(e.onBlur, () => b(!1)),
				}),
			})
		);
	}),
	Ws = "RovingFocusGroupItem",
	zs = c.forwardRef((e, t) => {
		const {
				__scopeRovingFocusGroup: n,
				focusable: o = !0,
				active: r = !1,
				tabStopId: s,
				children: i,
				...a
			} = e,
			l = Lt(),
			u = s || l,
			f = Tf(Ws, n),
			d = f.currentTabStopId === u,
			g = Bs(n),
			{
				onFocusableItemAdd: v,
				onFocusableItemRemove: h,
				currentTabStopId: m,
			} = f;
		return (
			c.useEffect(() => {
				if (o) return v(), () => h();
			}, [o, v, h]),
			p.jsx(En.ItemSlot, {
				scope: n,
				id: u,
				focusable: o,
				active: r,
				children: p.jsx(Fs.span, {
					tabIndex: d ? 0 : -1,
					"data-orientation": f.orientation,
					...a,
					ref: t,
					onMouseDown: A(e.onMouseDown, (x) => {
						o ? f.onItemFocus(u) : x.preventDefault();
					}),
					onFocus: A(e.onFocus, () => f.onItemFocus(u)),
					onKeyDown: A(e.onKeyDown, (x) => {
						if (x.key === "Tab" && x.shiftKey) {
							f.onItemShiftTab();
							return;
						}
						if (x.target !== x.currentTarget) return;
						const w = jf(x, f.orientation, f.dir);
						if (w !== void 0) {
							if (x.metaKey || x.ctrlKey || x.altKey || x.shiftKey) return;
							x.preventDefault();
							let y = g()
								.filter((C) => C.focusable)
								.map((C) => C.ref.current);
							if (w === "last") y.reverse();
							else if (w === "prev" || w === "next") {
								w === "prev" && y.reverse();
								const C = y.indexOf(x.currentTarget);
								y = f.loop ? $f(y, C + 1) : y.slice(C + 1);
							}
							setTimeout(() => Hs(y));
						}
					}),
					children:
						typeof i == "function"
							? i({ isCurrentTabStop: d, hasTabStop: m != null })
							: i,
				}),
			})
		);
	});
zs.displayName = Ws;
var Of = {
	ArrowLeft: "prev",
	ArrowUp: "prev",
	ArrowRight: "next",
	ArrowDown: "next",
	PageUp: "first",
	Home: "first",
	PageDown: "last",
	End: "last",
};
function Df(e, t) {
	return t !== "rtl"
		? e
		: e === "ArrowLeft"
			? "ArrowRight"
			: e === "ArrowRight"
				? "ArrowLeft"
				: e;
}
function jf(e, t, n) {
	const o = Df(e.key, n);
	if (
		!(t === "vertical" && ["ArrowLeft", "ArrowRight"].includes(o)) &&
		!(t === "horizontal" && ["ArrowUp", "ArrowDown"].includes(o))
	)
		return Of[o];
}
function Hs(e, t = !1) {
	const n = document.activeElement;
	for (const o of e)
		if (
			o === n ||
			(o.focus({ preventScroll: t }), document.activeElement !== n)
		)
			return;
}
function $f(e, t) {
	return e.map((n, o) => e[(t + o) % e.length]);
}
var Gs = Vs,
	Us = zs,
	Pn = ["Enter", " "],
	Lf = ["ArrowDown", "PageUp", "Home"],
	Ks = ["ArrowUp", "PageDown", "End"],
	Ff = [...Lf, ...Ks],
	Bf = { ltr: [...Pn, "ArrowRight"], rtl: [...Pn, "ArrowLeft"] },
	Vf = { ltr: ["ArrowLeft"], rtl: ["ArrowRight"] },
	Yt = "Menu",
	[st, Wf, zf] = Wn(Yt),
	[Le, Ys] = qu(Yt, [zf, Qe, Kt]),
	Jn = Qe(),
	Xs = Kt(),
	[pg, Fe] = Le(Yt),
	[mg, gt] = Le(Yt),
	Hf = "MenuAnchor",
	eo = c.forwardRef((e, t) => {
		const { __scopeMenu: n, ...o } = e,
			r = Jn(n);
		return p.jsx(qn, { ...r, ...o, ref: t });
	});
eo.displayName = Hf;
var to = "MenuPortal",
	[Gf, qs] = Le(to, { forceMount: void 0 }),
	Zs = (e) => {
		const { __scopeMenu: t, forceMount: n, children: o, container: r } = e,
			s = Fe(to, t);
		return p.jsx(Gf, {
			scope: t,
			forceMount: n,
			children: p.jsx(ye, {
				present: n || s.open,
				children: p.jsx(Bt, { asChild: !0, container: r, children: o }),
			}),
		});
	};
Zs.displayName = to;
var de = "MenuContent",
	[Uf, no] = Le(de),
	Qs = c.forwardRef((e, t) => {
		const n = qs(de, e.__scopeMenu),
			{ forceMount: o = n.forceMount, ...r } = e,
			s = Fe(de, e.__scopeMenu),
			i = gt(de, e.__scopeMenu);
		return p.jsx(st.Provider, {
			scope: e.__scopeMenu,
			children: p.jsx(ye, {
				present: o || s.open,
				children: p.jsx(st.Slot, {
					scope: e.__scopeMenu,
					children: i.modal
						? p.jsx(Kf, { ...r, ref: t })
						: p.jsx(Yf, { ...r, ref: t }),
				}),
			}),
		});
	}),
	Kf = c.forwardRef((e, t) => {
		const n = Fe(de, e.__scopeMenu),
			o = c.useRef(null),
			r = G(t, o);
		return (
			c.useEffect(() => {
				const s = o.current;
				if (s) return jn(s);
			}, []),
			p.jsx(oo, {
				...e,
				ref: r,
				trapFocus: n.open,
				disableOutsidePointerEvents: n.open,
				disableOutsideScroll: !0,
				onFocusOutside: A(e.onFocusOutside, (s) => s.preventDefault(), {
					checkForDefaultPrevented: !1,
				}),
				onDismiss: () => n.onOpenChange(!1),
			})
		);
	}),
	Yf = c.forwardRef((e, t) => {
		const n = Fe(de, e.__scopeMenu);
		return p.jsx(oo, {
			...e,
			ref: t,
			trapFocus: !1,
			disableOutsidePointerEvents: !1,
			disableOutsideScroll: !1,
			onDismiss: () => n.onOpenChange(!1),
		});
	}),
	Xf = ne("MenuContent.ScrollLock"),
	oo = c.forwardRef((e, t) => {
		const {
				__scopeMenu: n,
				loop: o = !1,
				trapFocus: r,
				onOpenAutoFocus: s,
				onCloseAutoFocus: i,
				disableOutsidePointerEvents: a,
				onEntryFocus: l,
				onEscapeKeyDown: u,
				onPointerDownOutside: f,
				onFocusOutside: d,
				onInteractOutside: g,
				onDismiss: v,
				disableOutsideScroll: h,
				...m
			} = e,
			x = Fe(de, n),
			w = gt(de, n),
			b = Jn(n),
			y = Xs(n),
			C = Wf(n),
			[P, T] = c.useState(null),
			R = c.useRef(null),
			E = G(t, R, x.onContentChange),
			O = c.useRef(0),
			D = c.useRef(""),
			$ = c.useRef(0),
			L = c.useRef(null),
			V = c.useRef("right"),
			F = c.useRef(0),
			W = h ? Wt : c.Fragment,
			k = h ? { as: Xf, allowPinchZoom: !0 } : void 0,
			B = (N) => {
				const Z = D.current + N,
					te = C().filter((_) => !_.disabled),
					re = document.activeElement,
					X = te.find((_) => _.ref.current === re)?.textValue,
					Y = te.map((_) => _.textValue),
					se = ap(Y, Z, X),
					oe = te.find((_) => _.textValue === se)?.ref.current;
				(function _(U) {
					(D.current = U),
						window.clearTimeout(O.current),
						U !== "" && (O.current = window.setTimeout(() => _(""), 1e3));
				})(Z),
					oe && setTimeout(() => oe.focus());
			};
		c.useEffect(() => () => window.clearTimeout(O.current), []), Dn();
		const S = c.useCallback(
			(N) => V.current === L.current?.side && lp(N, L.current?.area),
			[],
		);
		return p.jsx(Uf, {
			scope: n,
			searchRef: D,
			onItemEnter: c.useCallback(
				(N) => {
					S(N) && N.preventDefault();
				},
				[S],
			),
			onItemLeave: c.useCallback(
				(N) => {
					S(N) || (R.current?.focus(), T(null));
				},
				[S],
			),
			onTriggerLeave: c.useCallback(
				(N) => {
					S(N) && N.preventDefault();
				},
				[S],
			),
			pointerGraceTimerRef: $,
			onPointerGraceIntentChange: c.useCallback((N) => {
				L.current = N;
			}, []),
			children: p.jsx(W, {
				...k,
				children: p.jsx(Ft, {
					asChild: !0,
					trapped: r,
					onMountAutoFocus: A(s, (N) => {
						N.preventDefault(), R.current?.focus({ preventScroll: !0 });
					}),
					onUnmountAutoFocus: i,
					children: p.jsx(ut, {
						asChild: !0,
						disableOutsidePointerEvents: a,
						onEscapeKeyDown: u,
						onPointerDownOutside: f,
						onFocusOutside: d,
						onInteractOutside: g,
						onDismiss: v,
						children: p.jsx(Gs, {
							asChild: !0,
							...y,
							dir: w.dir,
							orientation: "vertical",
							loop: o,
							currentTabStopId: P,
							onCurrentTabStopIdChange: T,
							onEntryFocus: A(l, (N) => {
								w.isUsingKeyboardRef.current || N.preventDefault();
							}),
							preventScrollOnEntryFocus: !0,
							children: p.jsx(Zn, {
								role: "menu",
								"aria-orientation": "vertical",
								"data-state": mi(x.open),
								"data-radix-menu-content": "",
								dir: w.dir,
								...b,
								...m,
								ref: E,
								style: { outline: "none", ...m.style },
								onKeyDown: A(m.onKeyDown, (N) => {
									const te =
											N.target.closest("[data-radix-menu-content]") ===
											N.currentTarget,
										re = N.ctrlKey || N.altKey || N.metaKey,
										X = N.key.length === 1;
									te &&
										(N.key === "Tab" && N.preventDefault(),
										!re && X && B(N.key));
									const Y = R.current;
									if (N.target !== Y || !Ff.includes(N.key)) return;
									N.preventDefault();
									const oe = C()
										.filter((_) => !_.disabled)
										.map((_) => _.ref.current);
									Ks.includes(N.key) && oe.reverse(), sp(oe);
								}),
								onBlur: A(e.onBlur, (N) => {
									N.currentTarget.contains(N.target) ||
										(window.clearTimeout(O.current), (D.current = ""));
								}),
								onPointerMove: A(
									e.onPointerMove,
									it((N) => {
										const Z = N.target,
											te = F.current !== N.clientX;
										if (N.currentTarget.contains(Z) && te) {
											const re = N.clientX > F.current ? "right" : "left";
											(V.current = re), (F.current = N.clientX);
										}
									}),
								),
							}),
						}),
					}),
				}),
			}),
		});
	});
Qs.displayName = de;
var qf = "MenuGroup",
	ro = c.forwardRef((e, t) => {
		const { __scopeMenu: n, ...o } = e;
		return p.jsx(pt.div, { role: "group", ...o, ref: t });
	});
ro.displayName = qf;
var Zf = "MenuLabel",
	Js = c.forwardRef((e, t) => {
		const { __scopeMenu: n, ...o } = e;
		return p.jsx(pt.div, { ...o, ref: t });
	});
Js.displayName = Zf;
var Ot = "MenuItem",
	Yo = "menu.itemSelect",
	Xt = c.forwardRef((e, t) => {
		const { disabled: n = !1, onSelect: o, ...r } = e,
			s = c.useRef(null),
			i = gt(Ot, e.__scopeMenu),
			a = no(Ot, e.__scopeMenu),
			l = G(t, s),
			u = c.useRef(!1),
			f = () => {
				const d = s.current;
				if (!n && d) {
					const g = new CustomEvent(Yo, { bubbles: !0, cancelable: !0 });
					d.addEventListener(Yo, (v) => o?.(v), { once: !0 }),
						Ef(d, g),
						g.defaultPrevented ? (u.current = !1) : i.onClose();
				}
			};
		return p.jsx(ei, {
			...r,
			ref: l,
			disabled: n,
			onClick: A(e.onClick, f),
			onPointerDown: (d) => {
				e.onPointerDown?.(d), (u.current = !0);
			},
			onPointerUp: A(e.onPointerUp, (d) => {
				u.current || d.currentTarget?.click();
			}),
			onKeyDown: A(e.onKeyDown, (d) => {
				const g = a.searchRef.current !== "";
				n ||
					(g && d.key === " ") ||
					(Pn.includes(d.key) && (d.currentTarget.click(), d.preventDefault()));
			}),
		});
	});
Xt.displayName = Ot;
var ei = c.forwardRef((e, t) => {
		const { __scopeMenu: n, disabled: o = !1, textValue: r, ...s } = e,
			i = no(Ot, n),
			a = Xs(n),
			l = c.useRef(null),
			u = G(t, l),
			[f, d] = c.useState(!1),
			[g, v] = c.useState("");
		return (
			c.useEffect(() => {
				const h = l.current;
				h && v((h.textContent ?? "").trim());
			}, [s.children]),
			p.jsx(st.ItemSlot, {
				scope: n,
				disabled: o,
				textValue: r ?? g,
				children: p.jsx(Us, {
					asChild: !0,
					...a,
					focusable: !o,
					children: p.jsx(pt.div, {
						role: "menuitem",
						"data-highlighted": f ? "" : void 0,
						"aria-disabled": o || void 0,
						"data-disabled": o ? "" : void 0,
						...s,
						ref: u,
						onPointerMove: A(
							e.onPointerMove,
							it((h) => {
								o
									? i.onItemLeave(h)
									: (i.onItemEnter(h),
										h.defaultPrevented ||
											h.currentTarget.focus({ preventScroll: !0 }));
							}),
						),
						onPointerLeave: A(
							e.onPointerLeave,
							it((h) => i.onItemLeave(h)),
						),
						onFocus: A(e.onFocus, () => d(!0)),
						onBlur: A(e.onBlur, () => d(!1)),
					}),
				}),
			})
		);
	}),
	Qf = "MenuCheckboxItem",
	ti = c.forwardRef((e, t) => {
		const { checked: n = !1, onCheckedChange: o, ...r } = e;
		return p.jsx(ii, {
			scope: e.__scopeMenu,
			checked: n,
			children: p.jsx(Xt, {
				role: "menuitemcheckbox",
				"aria-checked": Dt(n) ? "mixed" : n,
				...r,
				ref: t,
				"data-state": io(n),
				onSelect: A(r.onSelect, () => o?.(Dt(n) ? !0 : !n), {
					checkForDefaultPrevented: !1,
				}),
			}),
		});
	});
ti.displayName = Qf;
var ni = "MenuRadioGroup",
	[Jf, ep] = Le(ni, { value: void 0, onValueChange: () => {} }),
	oi = c.forwardRef((e, t) => {
		const { value: n, onValueChange: o, ...r } = e,
			s = we(o);
		return p.jsx(Jf, {
			scope: e.__scopeMenu,
			value: n,
			onValueChange: s,
			children: p.jsx(ro, { ...r, ref: t }),
		});
	});
oi.displayName = ni;
var ri = "MenuRadioItem",
	si = c.forwardRef((e, t) => {
		const { value: n, ...o } = e,
			r = ep(ri, e.__scopeMenu),
			s = n === r.value;
		return p.jsx(ii, {
			scope: e.__scopeMenu,
			checked: s,
			children: p.jsx(Xt, {
				role: "menuitemradio",
				"aria-checked": s,
				...o,
				ref: t,
				"data-state": io(s),
				onSelect: A(o.onSelect, () => r.onValueChange?.(n), {
					checkForDefaultPrevented: !1,
				}),
			}),
		});
	});
si.displayName = ri;
var so = "MenuItemIndicator",
	[ii, tp] = Le(so, { checked: !1 }),
	ai = c.forwardRef((e, t) => {
		const { __scopeMenu: n, forceMount: o, ...r } = e,
			s = tp(so, n);
		return p.jsx(ye, {
			present: o || Dt(s.checked) || s.checked === !0,
			children: p.jsx(pt.span, { ...r, ref: t, "data-state": io(s.checked) }),
		});
	});
ai.displayName = so;
var np = "MenuSeparator",
	ci = c.forwardRef((e, t) => {
		const { __scopeMenu: n, ...o } = e;
		return p.jsx(pt.div, {
			role: "separator",
			"aria-orientation": "horizontal",
			...o,
			ref: t,
		});
	});
ci.displayName = np;
var op = "MenuArrow",
	li = c.forwardRef((e, t) => {
		const { __scopeMenu: n, ...o } = e,
			r = Jn(n);
		return p.jsx(Qn, { ...r, ...o, ref: t });
	});
li.displayName = op;
var rp = "MenuSub",
	[gg, ui] = Le(rp),
	tt = "MenuSubTrigger",
	di = c.forwardRef((e, t) => {
		const n = Fe(tt, e.__scopeMenu),
			o = gt(tt, e.__scopeMenu),
			r = ui(tt, e.__scopeMenu),
			s = no(tt, e.__scopeMenu),
			i = c.useRef(null),
			{ pointerGraceTimerRef: a, onPointerGraceIntentChange: l } = s,
			u = { __scopeMenu: e.__scopeMenu },
			f = c.useCallback(() => {
				i.current && window.clearTimeout(i.current), (i.current = null);
			}, []);
		return (
			c.useEffect(() => f, [f]),
			c.useEffect(() => {
				const d = a.current;
				return () => {
					window.clearTimeout(d), l(null);
				};
			}, [a, l]),
			p.jsx(eo, {
				asChild: !0,
				...u,
				children: p.jsx(ei, {
					id: r.triggerId,
					"aria-haspopup": "menu",
					"aria-expanded": n.open,
					"aria-controls": r.contentId,
					"data-state": mi(n.open),
					...e,
					ref: ct(t, r.onTriggerChange),
					onClick: (d) => {
						e.onClick?.(d),
							!(e.disabled || d.defaultPrevented) &&
								(d.currentTarget.focus(), n.open || n.onOpenChange(!0));
					},
					onPointerMove: A(
						e.onPointerMove,
						it((d) => {
							s.onItemEnter(d),
								!d.defaultPrevented &&
									!e.disabled &&
									!n.open &&
									!i.current &&
									(s.onPointerGraceIntentChange(null),
									(i.current = window.setTimeout(() => {
										n.onOpenChange(!0), f();
									}, 100)));
						}),
					),
					onPointerLeave: A(
						e.onPointerLeave,
						it((d) => {
							f();
							const g = n.content?.getBoundingClientRect();
							if (g) {
								const v = n.content?.dataset.side,
									h = v === "right",
									m = h ? -5 : 5,
									x = g[h ? "left" : "right"],
									w = g[h ? "right" : "left"];
								s.onPointerGraceIntentChange({
									area: [
										{ x: d.clientX + m, y: d.clientY },
										{ x, y: g.top },
										{ x: w, y: g.top },
										{ x: w, y: g.bottom },
										{ x, y: g.bottom },
									],
									side: v,
								}),
									window.clearTimeout(a.current),
									(a.current = window.setTimeout(
										() => s.onPointerGraceIntentChange(null),
										300,
									));
							} else {
								if ((s.onTriggerLeave(d), d.defaultPrevented)) return;
								s.onPointerGraceIntentChange(null);
							}
						}),
					),
					onKeyDown: A(e.onKeyDown, (d) => {
						const g = s.searchRef.current !== "";
						e.disabled ||
							(g && d.key === " ") ||
							(Bf[o.dir].includes(d.key) &&
								(n.onOpenChange(!0), n.content?.focus(), d.preventDefault()));
					}),
				}),
			})
		);
	});
di.displayName = tt;
var fi = "MenuSubContent",
	pi = c.forwardRef((e, t) => {
		const n = qs(de, e.__scopeMenu),
			{ forceMount: o = n.forceMount, ...r } = e,
			s = Fe(de, e.__scopeMenu),
			i = gt(de, e.__scopeMenu),
			a = ui(fi, e.__scopeMenu),
			l = c.useRef(null),
			u = G(t, l);
		return p.jsx(st.Provider, {
			scope: e.__scopeMenu,
			children: p.jsx(ye, {
				present: o || s.open,
				children: p.jsx(st.Slot, {
					scope: e.__scopeMenu,
					children: p.jsx(oo, {
						id: a.contentId,
						"aria-labelledby": a.triggerId,
						...r,
						ref: u,
						align: "start",
						side: i.dir === "rtl" ? "left" : "right",
						disableOutsidePointerEvents: !1,
						disableOutsideScroll: !1,
						trapFocus: !1,
						onOpenAutoFocus: (f) => {
							i.isUsingKeyboardRef.current && l.current?.focus(),
								f.preventDefault();
						},
						onCloseAutoFocus: (f) => f.preventDefault(),
						onFocusOutside: A(e.onFocusOutside, (f) => {
							f.target !== a.trigger && s.onOpenChange(!1);
						}),
						onEscapeKeyDown: A(e.onEscapeKeyDown, (f) => {
							i.onClose(), f.preventDefault();
						}),
						onKeyDown: A(e.onKeyDown, (f) => {
							const d = f.currentTarget.contains(f.target),
								g = Vf[i.dir].includes(f.key);
							d &&
								g &&
								(s.onOpenChange(!1), a.trigger?.focus(), f.preventDefault());
						}),
					}),
				}),
			}),
		});
	});
pi.displayName = fi;
function mi(e) {
	return e ? "open" : "closed";
}
function Dt(e) {
	return e === "indeterminate";
}
function io(e) {
	return Dt(e) ? "indeterminate" : e ? "checked" : "unchecked";
}
function sp(e) {
	const t = document.activeElement;
	for (const n of e)
		if (n === t || (n.focus(), document.activeElement !== t)) return;
}
function ip(e, t) {
	return e.map((n, o) => e[(t + o) % e.length]);
}
function ap(e, t, n) {
	const r = t.length > 1 && Array.from(t).every((u) => u === t[0]) ? t[0] : t,
		s = n ? e.indexOf(n) : -1;
	let i = ip(e, Math.max(s, 0));
	r.length === 1 && (i = i.filter((u) => u !== n));
	const l = i.find((u) => u.toLowerCase().startsWith(r.toLowerCase()));
	return l !== n ? l : void 0;
}
function cp(e, t) {
	const { x: n, y: o } = e;
	let r = !1;
	for (let s = 0, i = t.length - 1; s < t.length; i = s++) {
		const a = t[s],
			l = t[i],
			u = a.x,
			f = a.y,
			d = l.x,
			g = l.y;
		f > o != g > o && n < ((d - u) * (o - f)) / (g - f) + u && (r = !r);
	}
	return r;
}
function lp(e, t) {
	if (!t) return !1;
	const n = { x: e.clientX, y: e.clientY };
	return cp(n, t);
}
function it(e) {
	return (t) => (t.pointerType === "mouse" ? e(t) : void 0);
}
var up = eo,
	dp = Zs,
	fp = Qs,
	pp = ro,
	mp = Js,
	gp = Xt,
	hp = ti,
	vp = oi,
	xp = si,
	wp = ai,
	bp = ci,
	yp = li,
	Cp = di,
	Sp = pi,
	gi = "DropdownMenu",
	[Ep] = Hu(gi, [Ys]),
	ie = Ys(),
	[hg, hi] = Ep(gi),
	vi = "DropdownMenuTrigger",
	Pp = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, disabled: o = !1, ...r } = e,
			s = hi(vi, n),
			i = ie(n);
		return p.jsx(up, {
			asChild: !0,
			...i,
			children: p.jsx(Ku.button, {
				type: "button",
				id: s.triggerId,
				"aria-haspopup": "menu",
				"aria-expanded": s.open,
				"aria-controls": s.open ? s.contentId : void 0,
				"data-state": s.open ? "open" : "closed",
				"data-disabled": o ? "" : void 0,
				disabled: o,
				...r,
				ref: ct(t, s.triggerRef),
				onPointerDown: A(e.onPointerDown, (a) => {
					!o &&
						a.button === 0 &&
						a.ctrlKey === !1 &&
						(s.onOpenToggle(), s.open || a.preventDefault());
				}),
				onKeyDown: A(e.onKeyDown, (a) => {
					o ||
						(["Enter", " "].includes(a.key) && s.onOpenToggle(),
						a.key === "ArrowDown" && s.onOpenChange(!0),
						["Enter", " ", "ArrowDown"].includes(a.key) && a.preventDefault());
				}),
			}),
		});
	});
Pp.displayName = vi;
var Rp = "DropdownMenuPortal",
	xi = (e) => {
		const { __scopeDropdownMenu: t, ...n } = e,
			o = ie(t);
		return p.jsx(dp, { ...o, ...n });
	};
xi.displayName = Rp;
var wi = "DropdownMenuContent",
	bi = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = hi(wi, n),
			s = ie(n),
			i = c.useRef(!1);
		return p.jsx(fp, {
			id: r.contentId,
			"aria-labelledby": r.triggerId,
			...s,
			...o,
			ref: t,
			onCloseAutoFocus: A(e.onCloseAutoFocus, (a) => {
				i.current || r.triggerRef.current?.focus(),
					(i.current = !1),
					a.preventDefault();
			}),
			onInteractOutside: A(e.onInteractOutside, (a) => {
				const l = a.detail.originalEvent,
					u = l.button === 0 && l.ctrlKey === !0,
					f = l.button === 2 || u;
				(!r.modal || f) && (i.current = !0);
			}),
			style: {
				...e.style,
				"--radix-dropdown-menu-content-transform-origin":
					"var(--radix-popper-transform-origin)",
				"--radix-dropdown-menu-content-available-width":
					"var(--radix-popper-available-width)",
				"--radix-dropdown-menu-content-available-height":
					"var(--radix-popper-available-height)",
				"--radix-dropdown-menu-trigger-width":
					"var(--radix-popper-anchor-width)",
				"--radix-dropdown-menu-trigger-height":
					"var(--radix-popper-anchor-height)",
			},
		});
	});
bi.displayName = wi;
var _p = "DropdownMenuGroup",
	Np = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(pp, { ...r, ...o, ref: t });
	});
Np.displayName = _p;
var Ap = "DropdownMenuLabel",
	yi = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(mp, { ...r, ...o, ref: t });
	});
yi.displayName = Ap;
var Mp = "DropdownMenuItem",
	Ci = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(gp, { ...r, ...o, ref: t });
	});
Ci.displayName = Mp;
var Ip = "DropdownMenuCheckboxItem",
	Si = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(hp, { ...r, ...o, ref: t });
	});
Si.displayName = Ip;
var Tp = "DropdownMenuRadioGroup",
	kp = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(vp, { ...r, ...o, ref: t });
	});
kp.displayName = Tp;
var Op = "DropdownMenuRadioItem",
	Dp = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(xp, { ...r, ...o, ref: t });
	});
Dp.displayName = Op;
var jp = "DropdownMenuItemIndicator",
	Ei = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(wp, { ...r, ...o, ref: t });
	});
Ei.displayName = jp;
var $p = "DropdownMenuSeparator",
	Pi = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(bp, { ...r, ...o, ref: t });
	});
Pi.displayName = $p;
var Lp = "DropdownMenuArrow",
	Fp = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(yp, { ...r, ...o, ref: t });
	});
Fp.displayName = Lp;
var Bp = "DropdownMenuSubTrigger",
	Vp = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(Cp, { ...r, ...o, ref: t });
	});
Vp.displayName = Bp;
var Wp = "DropdownMenuSubContent",
	zp = c.forwardRef((e, t) => {
		const { __scopeDropdownMenu: n, ...o } = e,
			r = ie(n);
		return p.jsx(Sp, {
			...r,
			...o,
			ref: t,
			style: {
				...e.style,
				"--radix-dropdown-menu-content-transform-origin":
					"var(--radix-popper-transform-origin)",
				"--radix-dropdown-menu-content-available-width":
					"var(--radix-popper-available-width)",
				"--radix-dropdown-menu-content-available-height":
					"var(--radix-popper-available-height)",
				"--radix-dropdown-menu-trigger-width":
					"var(--radix-popper-anchor-width)",
				"--radix-dropdown-menu-trigger-height":
					"var(--radix-popper-anchor-height)",
			},
		});
	});
zp.displayName = Wp;
var Hp = xi,
	Ri = bi,
	_i = yi,
	Ni = Ci,
	Ai = Si,
	Gp = Ei,
	Mi = Pi;
const Ii = c.forwardRef(({ className: e, sideOffset: t = 4, ...n }, o) =>
	p.jsx(Hp, {
		children: p.jsx(Ri, {
			ref: o,
			sideOffset: t,
			className: z(
				"z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
				"data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
				e,
			),
			...n,
		}),
	}),
);
Ii.displayName = Ri.displayName;
const Ti = c.forwardRef(({ className: e, inset: t, ...n }, o) =>
	p.jsx(Ni, {
		ref: o,
		className: z(
			"relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
			"focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
			t && "pl-8",
			e,
		),
		...n,
	}),
);
Ti.displayName = Ni.displayName;
const ki = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(Mi, { ref: n, className: z("-mx-1 my-1 h-px bg-muted", e), ...t }),
);
ki.displayName = Mi.displayName;
const Oi = c.forwardRef(({ className: e, inset: t, ...n }, o) =>
	p.jsx(_i, {
		ref: o,
		className: z("px-2 py-1.5 text-sm font-semibold", t && "pl-8", e),
		...n,
	}),
);
Oi.displayName = _i.displayName;
const Di = c.forwardRef(
	({ className: e, children: t, checked: n = !1, ...o }, r) =>
		p.jsxs(Ai, {
			ref: r,
			className: z(
				"relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors",
				"focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
				e,
			),
			checked: n,
			...o,
			children: [
				p.jsx("span", {
					className:
						"absolute left-2 flex h-3.5 w-3.5 items-center justify-center",
					children: p.jsx(Gp, {
						children: p.jsx("svg", {
							className: "h-4 w-4",
							fill: "none",
							stroke: "currentColor",
							viewBox: "0 0 24 24",
							xmlns: "http://www.w3.org/2000/svg",
							children: p.jsx("path", {
								strokeLinecap: "round",
								strokeLinejoin: "round",
								strokeWidth: 2,
								d: "M5 13l4 4L19 7",
							}),
						}),
					}),
				}),
				t,
			],
		}),
);
Di.displayName = Ai.displayName;
Ii.__docgenInfo = {
	description: "",
	methods: [],
	props: {
		sideOffset: { defaultValue: { value: "4", computed: !1 }, required: !1 },
	},
};
Ti.__docgenInfo = {
	description: "",
	methods: [],
	props: {
		inset: { required: !1, tsType: { name: "boolean" }, description: "" },
	},
};
ki.__docgenInfo = { description: "", methods: [] };
Oi.__docgenInfo = {
	description: "",
	methods: [],
	props: {
		inset: { required: !1, tsType: { name: "boolean" }, description: "" },
	},
};
Di.__docgenInfo = {
	description: "",
	methods: [],
	props: {
		checked: { defaultValue: { value: "false", computed: !1 }, required: !1 },
	},
};
const ji = c.forwardRef(({ className: e, type: t, ...n }, o) =>
	p.jsx("input", {
		type: t,
		className: z(
			"flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
			"file:border-0 file:bg-transparent file:text-sm file:font-medium",
			"placeholder:text-muted-foreground",
			"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
			"disabled:cursor-not-allowed disabled:opacity-50",
			e,
		),
		ref: o,
		...n,
	}),
);
ji.displayName = "Input";
ji.__docgenInfo = { description: "", methods: [], displayName: "Input" };
const $i = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("label", {
		ref: n,
		className: z(
			"text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
			e,
		),
		...t,
	}),
);
$i.displayName = "Label";
$i.__docgenInfo = { description: "", methods: [], displayName: "Label" };
var ao = "Progress",
	co = 100,
	[Up] = vr(ao),
	[Kp, Yp] = Up(ao),
	Li = c.forwardRef((e, t) => {
		const {
			__scopeProgress: n,
			value: o = null,
			max: r,
			getValueLabel: s = Xp,
			...i
		} = e;
		(r || r === 0) && !Xo(r) && console.error(qp(`${r}`, "Progress"));
		const a = Xo(r) ? r : co;
		o !== null && !qo(o, a) && console.error(Zp(`${o}`, "Progress"));
		const l = qo(o, a) ? o : null,
			u = jt(l) ? s(l, a) : void 0;
		return p.jsx(Kp, {
			scope: n,
			value: l,
			max: a,
			children: p.jsx(lt.div, {
				"aria-valuemax": a,
				"aria-valuemin": 0,
				"aria-valuenow": jt(l) ? l : void 0,
				"aria-valuetext": u,
				role: "progressbar",
				"data-state": Vi(l, a),
				"data-value": l ?? void 0,
				"data-max": a,
				...i,
				ref: t,
			}),
		});
	});
Li.displayName = ao;
var Fi = "ProgressIndicator",
	Bi = c.forwardRef((e, t) => {
		const { __scopeProgress: n, ...o } = e,
			r = Yp(Fi, n);
		return p.jsx(lt.div, {
			"data-state": Vi(r.value, r.max),
			"data-value": r.value ?? void 0,
			"data-max": r.max,
			...o,
			ref: t,
		});
	});
Bi.displayName = Fi;
function Xp(e, t) {
	return `${Math.round((e / t) * 100)}%`;
}
function Vi(e, t) {
	return e == null ? "indeterminate" : e === t ? "complete" : "loading";
}
function jt(e) {
	return typeof e == "number";
}
function Xo(e) {
	return jt(e) && !isNaN(e) && e > 0;
}
function qo(e, t) {
	return jt(e) && !isNaN(e) && e <= t && e >= 0;
}
function qp(e, t) {
	return `Invalid prop \`max\` of value \`${e}\` supplied to \`${t}\`. Only numbers greater than 0 are valid max values. Defaulting to \`${co}\`.`;
}
function Zp(e, t) {
	return `Invalid prop \`value\` of value \`${e}\` supplied to \`${t}\`. The \`value\` prop must be:
  - a positive number
  - less than the value passed to \`max\` (or ${co} if no \`max\` prop is set)
  - \`null\` or \`undefined\` if the progress is indeterminate.

Defaulting to \`null\`.`;
}
var Wi = Li,
	Qp = Bi;
const zi = c.forwardRef(({ className: e, value: t, ...n }, o) =>
	p.jsx(Wi, {
		ref: o,
		className: z(
			"relative h-4 w-full overflow-hidden rounded-full bg-secondary",
			e,
		),
		...n,
		children: p.jsx(Qp, {
			className: "h-full w-full flex-1 bg-primary transition-all",
			style: { transform: `translateX(-${100 - (t || 0)}%)` },
		}),
	}),
);
zi.displayName = Wi.displayName;
zi.__docgenInfo = { description: "", methods: [] };
function Zo(e, [t, n]) {
	return Math.min(n, Math.max(t, e));
}
function Jp(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, em(r, ...t)];
}
function em(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var tm = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	le = tm.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {});
function nm(e) {
	const t = c.useRef({ value: e, previous: e });
	return c.useMemo(
		() => (
			t.current.value !== e &&
				((t.current.previous = t.current.value), (t.current.value = e)),
			t.current.previous
		),
		[e],
	);
}
var om = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	rm = om.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	Hi = Object.freeze({
		position: "absolute",
		border: 0,
		width: 1,
		height: 1,
		padding: 0,
		margin: -1,
		overflow: "hidden",
		clip: "rect(0, 0, 0, 0)",
		whiteSpace: "nowrap",
		wordWrap: "normal",
	}),
	sm = "VisuallyHidden",
	Gi = c.forwardRef((e, t) =>
		p.jsx(rm.span, { ...e, ref: t, style: { ...Hi, ...e.style } }),
	);
Gi.displayName = sm;
var im = Gi,
	am = [" ", "Enter", "ArrowUp", "ArrowDown"],
	cm = [" ", "Enter"],
	qt = "Select",
	[lo, Zt, lm] = Wn(qt),
	[Je] = Jp(qt, [lm, Qe]),
	uo = Qe(),
	[vg, Me] = Je(qt),
	[xg, um] = Je(qt),
	Ui = "SelectTrigger",
	Ki = c.forwardRef((e, t) => {
		const { __scopeSelect: n, disabled: o = !1, ...r } = e,
			s = uo(n),
			i = Me(Ui, n),
			a = i.disabled || o,
			l = G(t, i.onTriggerChange),
			u = Zt(n),
			f = c.useRef("touch"),
			[d, g, v] = da((m) => {
				const x = u().filter((y) => !y.disabled),
					w = x.find((y) => y.value === i.value),
					b = fa(x, m, w);
				b !== void 0 && i.onValueChange(b.value);
			}),
			h = (m) => {
				a || (i.onOpenChange(!0), v()),
					m &&
						(i.triggerPointerDownPosRef.current = {
							x: Math.round(m.pageX),
							y: Math.round(m.pageY),
						});
			};
		return p.jsx(qn, {
			asChild: !0,
			...s,
			children: p.jsx(le.button, {
				type: "button",
				role: "combobox",
				"aria-controls": i.contentId,
				"aria-expanded": i.open,
				"aria-required": i.required,
				"aria-autocomplete": "none",
				dir: i.dir,
				"data-state": i.open ? "open" : "closed",
				disabled: a,
				"data-disabled": a ? "" : void 0,
				"data-placeholder": ua(i.value) ? "" : void 0,
				...r,
				ref: l,
				onClick: A(r.onClick, (m) => {
					m.currentTarget.focus(), f.current !== "mouse" && h(m);
				}),
				onPointerDown: A(r.onPointerDown, (m) => {
					f.current = m.pointerType;
					const x = m.target;
					x.hasPointerCapture(m.pointerId) &&
						x.releasePointerCapture(m.pointerId),
						m.button === 0 &&
							m.ctrlKey === !1 &&
							m.pointerType === "mouse" &&
							(h(m), m.preventDefault());
				}),
				onKeyDown: A(r.onKeyDown, (m) => {
					const x = d.current !== "";
					!(m.ctrlKey || m.altKey || m.metaKey) &&
						m.key.length === 1 &&
						g(m.key),
						!(x && m.key === " ") &&
							am.includes(m.key) &&
							(h(), m.preventDefault());
				}),
			}),
		});
	});
Ki.displayName = Ui;
var Yi = "SelectValue",
	dm = c.forwardRef((e, t) => {
		const {
				__scopeSelect: n,
				className: o,
				style: r,
				children: s,
				placeholder: i = "",
				...a
			} = e,
			l = Me(Yi, n),
			{ onValueNodeHasChildrenChange: u } = l,
			f = s !== void 0,
			d = G(t, l.onValueNodeChange);
		return (
			ee(() => {
				u(f);
			}, [u, f]),
			p.jsx(le.span, {
				...a,
				ref: d,
				style: { pointerEvents: "none" },
				children: ua(l.value) ? p.jsx(p.Fragment, { children: i }) : s,
			})
		);
	});
dm.displayName = Yi;
var fm = "SelectIcon",
	Xi = c.forwardRef((e, t) => {
		const { __scopeSelect: n, children: o, ...r } = e;
		return p.jsx(le.span, {
			"aria-hidden": !0,
			...r,
			ref: t,
			children: o || "▼",
		});
	});
Xi.displayName = fm;
var pm = "SelectPortal",
	qi = (e) => p.jsx(Bt, { asChild: !0, ...e });
qi.displayName = pm;
var $e = "SelectContent",
	Zi = c.forwardRef((e, t) => {
		const n = Me($e, e.__scopeSelect),
			[o, r] = c.useState();
		if (
			(ee(() => {
				r(new DocumentFragment());
			}, []),
			!n.open)
		) {
			const s = o;
			return s
				? at.createPortal(
						p.jsx(Qi, {
							scope: e.__scopeSelect,
							children: p.jsx(lo.Slot, {
								scope: e.__scopeSelect,
								children: p.jsx("div", { children: e.children }),
							}),
						}),
						s,
					)
				: null;
		}
		return p.jsx(Ji, { ...e, ref: t });
	});
Zi.displayName = $e;
var fe = 10,
	[Qi, Ie] = Je($e),
	mm = "SelectContentImpl",
	gm = ne("SelectContent.RemoveScroll"),
	Ji = c.forwardRef((e, t) => {
		const {
				__scopeSelect: n,
				position: o = "item-aligned",
				onCloseAutoFocus: r,
				onEscapeKeyDown: s,
				onPointerDownOutside: i,
				side: a,
				sideOffset: l,
				align: u,
				alignOffset: f,
				arrowPadding: d,
				collisionBoundary: g,
				collisionPadding: v,
				sticky: h,
				hideWhenDetached: m,
				avoidCollisions: x,
				...w
			} = e,
			b = Me($e, n),
			[y, C] = c.useState(null),
			[P, T] = c.useState(null),
			R = G(t, (_) => C(_)),
			[E, O] = c.useState(null),
			[D, $] = c.useState(null),
			L = Zt(n),
			[V, F] = c.useState(!1),
			W = c.useRef(!1);
		c.useEffect(() => {
			if (y) return jn(y);
		}, [y]),
			Dn();
		const k = c.useCallback(
				(_) => {
					const [U, ...Q] = L().map((q) => q.ref.current),
						[H] = Q.slice(-1),
						K = document.activeElement;
					for (const q of _)
						if (
							q === K ||
							(q?.scrollIntoView({ block: "nearest" }),
							q === U && P && (P.scrollTop = 0),
							q === H && P && (P.scrollTop = P.scrollHeight),
							q?.focus(),
							document.activeElement !== K)
						)
							return;
				},
				[L, P],
			),
			B = c.useCallback(() => k([E, y]), [k, E, y]);
		c.useEffect(() => {
			V && B();
		}, [V, B]);
		const { onOpenChange: S, triggerPointerDownPosRef: N } = b;
		c.useEffect(() => {
			if (y) {
				let _ = { x: 0, y: 0 };
				const U = (H) => {
						_ = {
							x: Math.abs(Math.round(H.pageX) - (N.current?.x ?? 0)),
							y: Math.abs(Math.round(H.pageY) - (N.current?.y ?? 0)),
						};
					},
					Q = (H) => {
						_.x <= 10 && _.y <= 10
							? H.preventDefault()
							: y.contains(H.target) || S(!1),
							document.removeEventListener("pointermove", U),
							(N.current = null);
					};
				return (
					N.current !== null &&
						(document.addEventListener("pointermove", U),
						document.addEventListener("pointerup", Q, {
							capture: !0,
							once: !0,
						})),
					() => {
						document.removeEventListener("pointermove", U),
							document.removeEventListener("pointerup", Q, { capture: !0 });
					}
				);
			}
		}, [y, S, N]),
			c.useEffect(() => {
				const _ = () => S(!1);
				return (
					window.addEventListener("blur", _),
					window.addEventListener("resize", _),
					() => {
						window.removeEventListener("blur", _),
							window.removeEventListener("resize", _);
					}
				);
			}, [S]);
		const [Z, te] = da((_) => {
				const U = L().filter((K) => !K.disabled),
					Q = U.find((K) => K.ref.current === document.activeElement),
					H = fa(U, _, Q);
				H && setTimeout(() => H.ref.current.focus());
			}),
			re = c.useCallback(
				(_, U, Q) => {
					const H = !W.current && !Q;
					((b.value !== void 0 && b.value === U) || H) &&
						(O(_), H && (W.current = !0));
				},
				[b.value],
			),
			X = c.useCallback(() => y?.focus(), [y]),
			Y = c.useCallback(
				(_, U, Q) => {
					const H = !W.current && !Q;
					((b.value !== void 0 && b.value === U) || H) && $(_);
				},
				[b.value],
			),
			se = o === "popper" ? Rn : ea,
			oe =
				se === Rn
					? {
							side: a,
							sideOffset: l,
							align: u,
							alignOffset: f,
							arrowPadding: d,
							collisionBoundary: g,
							collisionPadding: v,
							sticky: h,
							hideWhenDetached: m,
							avoidCollisions: x,
						}
					: {};
		return p.jsx(Qi, {
			scope: n,
			content: y,
			viewport: P,
			onViewportChange: T,
			itemRefCallback: re,
			selectedItem: E,
			onItemLeave: X,
			itemTextRefCallback: Y,
			focusSelectedItem: B,
			selectedItemText: D,
			position: o,
			isPositioned: V,
			searchRef: Z,
			children: p.jsx(Wt, {
				as: gm,
				allowPinchZoom: !0,
				children: p.jsx(Ft, {
					asChild: !0,
					trapped: b.open,
					onMountAutoFocus: (_) => {
						_.preventDefault();
					},
					onUnmountAutoFocus: A(r, (_) => {
						b.trigger?.focus({ preventScroll: !0 }), _.preventDefault();
					}),
					children: p.jsx(ut, {
						asChild: !0,
						disableOutsidePointerEvents: !0,
						onEscapeKeyDown: s,
						onPointerDownOutside: i,
						onFocusOutside: (_) => _.preventDefault(),
						onDismiss: () => b.onOpenChange(!1),
						children: p.jsx(se, {
							role: "listbox",
							id: b.contentId,
							"data-state": b.open ? "open" : "closed",
							dir: b.dir,
							onContextMenu: (_) => _.preventDefault(),
							...w,
							...oe,
							onPlaced: () => F(!0),
							ref: R,
							style: {
								display: "flex",
								flexDirection: "column",
								outline: "none",
								...w.style,
							},
							onKeyDown: A(w.onKeyDown, (_) => {
								const U = _.ctrlKey || _.altKey || _.metaKey;
								if (
									(_.key === "Tab" && _.preventDefault(),
									!U && _.key.length === 1 && te(_.key),
									["ArrowUp", "ArrowDown", "Home", "End"].includes(_.key))
								) {
									let H = L()
										.filter((K) => !K.disabled)
										.map((K) => K.ref.current);
									if (
										(["ArrowUp", "End"].includes(_.key) &&
											(H = H.slice().reverse()),
										["ArrowUp", "ArrowDown"].includes(_.key))
									) {
										const K = _.target,
											q = H.indexOf(K);
										H = H.slice(q + 1);
									}
									setTimeout(() => k(H)), _.preventDefault();
								}
							}),
						}),
					}),
				}),
			}),
		});
	});
Ji.displayName = mm;
var hm = "SelectItemAlignedPosition",
	ea = c.forwardRef((e, t) => {
		const { __scopeSelect: n, onPlaced: o, ...r } = e,
			s = Me($e, n),
			i = Ie($e, n),
			[a, l] = c.useState(null),
			[u, f] = c.useState(null),
			d = G(t, (R) => f(R)),
			g = Zt(n),
			v = c.useRef(!1),
			h = c.useRef(!0),
			{
				viewport: m,
				selectedItem: x,
				selectedItemText: w,
				focusSelectedItem: b,
			} = i,
			y = c.useCallback(() => {
				if (s.trigger && s.valueNode && a && u && m && x && w) {
					const R = s.trigger.getBoundingClientRect(),
						E = u.getBoundingClientRect(),
						O = s.valueNode.getBoundingClientRect(),
						D = w.getBoundingClientRect();
					if (s.dir !== "rtl") {
						const K = D.left - E.left,
							q = O.left - K,
							ue = R.left - q,
							Te = R.width + ue,
							nn = Math.max(Te, E.width),
							on = window.innerWidth - fe,
							rn = Zo(q, [fe, Math.max(fe, on - nn)]);
						(a.style.minWidth = Te + "px"), (a.style.left = rn + "px");
					} else {
						const K = E.right - D.right,
							q = window.innerWidth - O.right - K,
							ue = window.innerWidth - R.right - q,
							Te = R.width + ue,
							nn = Math.max(Te, E.width),
							on = window.innerWidth - fe,
							rn = Zo(q, [fe, Math.max(fe, on - nn)]);
						(a.style.minWidth = Te + "px"), (a.style.right = rn + "px");
					}
					const $ = g(),
						L = window.innerHeight - fe * 2,
						V = m.scrollHeight,
						F = window.getComputedStyle(u),
						W = parseInt(F.borderTopWidth, 10),
						k = parseInt(F.paddingTop, 10),
						B = parseInt(F.borderBottomWidth, 10),
						S = parseInt(F.paddingBottom, 10),
						N = W + k + V + S + B,
						Z = Math.min(x.offsetHeight * 5, N),
						te = window.getComputedStyle(m),
						re = parseInt(te.paddingTop, 10),
						X = parseInt(te.paddingBottom, 10),
						Y = R.top + R.height / 2 - fe,
						se = L - Y,
						oe = x.offsetHeight / 2,
						_ = x.offsetTop + oe,
						U = W + k + _,
						Q = N - U;
					if (U <= Y) {
						const K = $.length > 0 && x === $[$.length - 1].ref.current;
						a.style.bottom = "0px";
						const q = u.clientHeight - m.offsetTop - m.offsetHeight,
							ue = Math.max(se, oe + (K ? X : 0) + q + B),
							Te = U + ue;
						a.style.height = Te + "px";
					} else {
						const K = $.length > 0 && x === $[0].ref.current;
						a.style.top = "0px";
						const ue = Math.max(Y, W + m.offsetTop + (K ? re : 0) + oe) + Q;
						(a.style.height = ue + "px"), (m.scrollTop = U - Y + m.offsetTop);
					}
					(a.style.margin = `${fe}px 0`),
						(a.style.minHeight = Z + "px"),
						(a.style.maxHeight = L + "px"),
						o?.(),
						requestAnimationFrame(() => (v.current = !0));
				}
			}, [g, s.trigger, s.valueNode, a, u, m, x, w, s.dir, o]);
		ee(() => y(), [y]);
		const [C, P] = c.useState();
		ee(() => {
			u && P(window.getComputedStyle(u).zIndex);
		}, [u]);
		const T = c.useCallback(
			(R) => {
				R && h.current === !0 && (y(), b?.(), (h.current = !1));
			},
			[y, b],
		);
		return p.jsx(xm, {
			scope: n,
			contentWrapper: a,
			shouldExpandOnScrollRef: v,
			onScrollButtonChange: T,
			children: p.jsx("div", {
				ref: l,
				style: {
					display: "flex",
					flexDirection: "column",
					position: "fixed",
					zIndex: C,
				},
				children: p.jsx(le.div, {
					...r,
					ref: d,
					style: { boxSizing: "border-box", maxHeight: "100%", ...r.style },
				}),
			}),
		});
	});
ea.displayName = hm;
var vm = "SelectPopperPosition",
	Rn = c.forwardRef((e, t) => {
		const {
				__scopeSelect: n,
				align: o = "start",
				collisionPadding: r = fe,
				...s
			} = e,
			i = uo(n);
		return p.jsx(Zn, {
			...i,
			...s,
			ref: t,
			align: o,
			collisionPadding: r,
			style: {
				boxSizing: "border-box",
				...s.style,
				"--radix-select-content-transform-origin":
					"var(--radix-popper-transform-origin)",
				"--radix-select-content-available-width":
					"var(--radix-popper-available-width)",
				"--radix-select-content-available-height":
					"var(--radix-popper-available-height)",
				"--radix-select-trigger-width": "var(--radix-popper-anchor-width)",
				"--radix-select-trigger-height": "var(--radix-popper-anchor-height)",
			},
		});
	});
Rn.displayName = vm;
var [xm, fo] = Je($e, {}),
	_n = "SelectViewport",
	ta = c.forwardRef((e, t) => {
		const { __scopeSelect: n, nonce: o, ...r } = e,
			s = Ie(_n, n),
			i = fo(_n, n),
			a = G(t, s.onViewportChange),
			l = c.useRef(0);
		return p.jsxs(p.Fragment, {
			children: [
				p.jsx("style", {
					dangerouslySetInnerHTML: {
						__html:
							"[data-radix-select-viewport]{scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;}[data-radix-select-viewport]::-webkit-scrollbar{display:none}",
					},
					nonce: o,
				}),
				p.jsx(lo.Slot, {
					scope: n,
					children: p.jsx(le.div, {
						"data-radix-select-viewport": "",
						role: "presentation",
						...r,
						ref: a,
						style: {
							position: "relative",
							flex: 1,
							overflow: "hidden auto",
							...r.style,
						},
						onScroll: A(r.onScroll, (u) => {
							const f = u.currentTarget,
								{ contentWrapper: d, shouldExpandOnScrollRef: g } = i;
							if (g?.current && d) {
								const v = Math.abs(l.current - f.scrollTop);
								if (v > 0) {
									const h = window.innerHeight - fe * 2,
										m = parseFloat(d.style.minHeight),
										x = parseFloat(d.style.height),
										w = Math.max(m, x);
									if (w < h) {
										const b = w + v,
											y = Math.min(h, b),
											C = b - y;
										(d.style.height = y + "px"),
											d.style.bottom === "0px" &&
												((f.scrollTop = C > 0 ? C : 0),
												(d.style.justifyContent = "flex-end"));
									}
								}
							}
							l.current = f.scrollTop;
						}),
					}),
				}),
			],
		});
	});
ta.displayName = _n;
var na = "SelectGroup",
	[wm, bm] = Je(na),
	ym = c.forwardRef((e, t) => {
		const { __scopeSelect: n, ...o } = e,
			r = Lt();
		return p.jsx(wm, {
			scope: n,
			id: r,
			children: p.jsx(le.div, {
				role: "group",
				"aria-labelledby": r,
				...o,
				ref: t,
			}),
		});
	});
ym.displayName = na;
var oa = "SelectLabel",
	Cm = c.forwardRef((e, t) => {
		const { __scopeSelect: n, ...o } = e,
			r = bm(oa, n);
		return p.jsx(le.div, { id: r.id, ...o, ref: t });
	});
Cm.displayName = oa;
var $t = "SelectItem",
	[Sm, ra] = Je($t),
	sa = c.forwardRef((e, t) => {
		const {
				__scopeSelect: n,
				value: o,
				disabled: r = !1,
				textValue: s,
				...i
			} = e,
			a = Me($t, n),
			l = Ie($t, n),
			u = a.value === o,
			[f, d] = c.useState(s ?? ""),
			[g, v] = c.useState(!1),
			h = G(t, (b) => l.itemRefCallback?.(b, o, r)),
			m = Lt(),
			x = c.useRef("touch"),
			w = () => {
				r || (a.onValueChange(o), a.onOpenChange(!1));
			};
		if (o === "")
			throw new Error(
				"A <Select.Item /> must have a value prop that is not an empty string. This is because the Select value can be set to an empty string to clear the selection and show the placeholder.",
			);
		return p.jsx(Sm, {
			scope: n,
			value: o,
			disabled: r,
			textId: m,
			isSelected: u,
			onItemTextChange: c.useCallback((b) => {
				d((y) => y || (b?.textContent ?? "").trim());
			}, []),
			children: p.jsx(lo.ItemSlot, {
				scope: n,
				value: o,
				disabled: r,
				textValue: f,
				children: p.jsx(le.div, {
					role: "option",
					"aria-labelledby": m,
					"data-highlighted": g ? "" : void 0,
					"aria-selected": u && g,
					"data-state": u ? "checked" : "unchecked",
					"aria-disabled": r || void 0,
					"data-disabled": r ? "" : void 0,
					tabIndex: r ? void 0 : -1,
					...i,
					ref: h,
					onFocus: A(i.onFocus, () => v(!0)),
					onBlur: A(i.onBlur, () => v(!1)),
					onClick: A(i.onClick, () => {
						x.current !== "mouse" && w();
					}),
					onPointerUp: A(i.onPointerUp, () => {
						x.current === "mouse" && w();
					}),
					onPointerDown: A(i.onPointerDown, (b) => {
						x.current = b.pointerType;
					}),
					onPointerMove: A(i.onPointerMove, (b) => {
						(x.current = b.pointerType),
							r
								? l.onItemLeave?.()
								: x.current === "mouse" &&
									b.currentTarget.focus({ preventScroll: !0 });
					}),
					onPointerLeave: A(i.onPointerLeave, (b) => {
						b.currentTarget === document.activeElement && l.onItemLeave?.();
					}),
					onKeyDown: A(i.onKeyDown, (b) => {
						(l.searchRef?.current !== "" && b.key === " ") ||
							(cm.includes(b.key) && w(), b.key === " " && b.preventDefault());
					}),
				}),
			}),
		});
	});
sa.displayName = $t;
var nt = "SelectItemText",
	ia = c.forwardRef((e, t) => {
		const { __scopeSelect: n, className: o, style: r, ...s } = e,
			i = Me(nt, n),
			a = Ie(nt, n),
			l = ra(nt, n),
			u = um(nt, n),
			[f, d] = c.useState(null),
			g = G(
				t,
				(w) => d(w),
				l.onItemTextChange,
				(w) => a.itemTextRefCallback?.(w, l.value, l.disabled),
			),
			v = f?.textContent,
			h = c.useMemo(
				() =>
					p.jsx(
						"option",
						{ value: l.value, disabled: l.disabled, children: v },
						l.value,
					),
				[l.disabled, l.value, v],
			),
			{ onNativeOptionAdd: m, onNativeOptionRemove: x } = u;
		return (
			ee(() => (m(h), () => x(h)), [m, x, h]),
			p.jsxs(p.Fragment, {
				children: [
					p.jsx(le.span, { id: l.textId, ...s, ref: g }),
					l.isSelected && i.valueNode && !i.valueNodeHasChildren
						? at.createPortal(s.children, i.valueNode)
						: null,
				],
			})
		);
	});
ia.displayName = nt;
var aa = "SelectItemIndicator",
	ca = c.forwardRef((e, t) => {
		const { __scopeSelect: n, ...o } = e;
		return ra(aa, n).isSelected
			? p.jsx(le.span, { "aria-hidden": !0, ...o, ref: t })
			: null;
	});
ca.displayName = aa;
var Nn = "SelectScrollUpButton",
	Em = c.forwardRef((e, t) => {
		const n = Ie(Nn, e.__scopeSelect),
			o = fo(Nn, e.__scopeSelect),
			[r, s] = c.useState(!1),
			i = G(t, o.onScrollButtonChange);
		return (
			ee(() => {
				if (n.viewport && n.isPositioned) {
					const a = () => {
						const u = l.scrollTop > 0;
						s(u);
					};
					const l = n.viewport;
					return (
						a(),
						l.addEventListener("scroll", a),
						() => l.removeEventListener("scroll", a)
					);
				}
			}, [n.viewport, n.isPositioned]),
			r
				? p.jsx(la, {
						...e,
						ref: i,
						onAutoScroll: () => {
							const { viewport: a, selectedItem: l } = n;
							a && l && (a.scrollTop = a.scrollTop - l.offsetHeight);
						},
					})
				: null
		);
	});
Em.displayName = Nn;
var An = "SelectScrollDownButton",
	Pm = c.forwardRef((e, t) => {
		const n = Ie(An, e.__scopeSelect),
			o = fo(An, e.__scopeSelect),
			[r, s] = c.useState(!1),
			i = G(t, o.onScrollButtonChange);
		return (
			ee(() => {
				if (n.viewport && n.isPositioned) {
					const a = () => {
						const u = l.scrollHeight - l.clientHeight,
							f = Math.ceil(l.scrollTop) < u;
						s(f);
					};
					const l = n.viewport;
					return (
						a(),
						l.addEventListener("scroll", a),
						() => l.removeEventListener("scroll", a)
					);
				}
			}, [n.viewport, n.isPositioned]),
			r
				? p.jsx(la, {
						...e,
						ref: i,
						onAutoScroll: () => {
							const { viewport: a, selectedItem: l } = n;
							a && l && (a.scrollTop = a.scrollTop + l.offsetHeight);
						},
					})
				: null
		);
	});
Pm.displayName = An;
var la = c.forwardRef((e, t) => {
		const { __scopeSelect: n, onAutoScroll: o, ...r } = e,
			s = Ie("SelectScrollButton", n),
			i = c.useRef(null),
			a = Zt(n),
			l = c.useCallback(() => {
				i.current !== null &&
					(window.clearInterval(i.current), (i.current = null));
			}, []);
		return (
			c.useEffect(() => () => l(), [l]),
			ee(() => {
				a()
					.find((f) => f.ref.current === document.activeElement)
					?.ref.current?.scrollIntoView({ block: "nearest" });
			}, [a]),
			p.jsx(le.div, {
				"aria-hidden": !0,
				...r,
				ref: t,
				style: { flexShrink: 0, ...r.style },
				onPointerDown: A(r.onPointerDown, () => {
					i.current === null && (i.current = window.setInterval(o, 50));
				}),
				onPointerMove: A(r.onPointerMove, () => {
					s.onItemLeave?.(),
						i.current === null && (i.current = window.setInterval(o, 50));
				}),
				onPointerLeave: A(r.onPointerLeave, () => {
					l();
				}),
			})
		);
	}),
	Rm = "SelectSeparator",
	_m = c.forwardRef((e, t) => {
		const { __scopeSelect: n, ...o } = e;
		return p.jsx(le.div, { "aria-hidden": !0, ...o, ref: t });
	});
_m.displayName = Rm;
var Mn = "SelectArrow",
	Nm = c.forwardRef((e, t) => {
		const { __scopeSelect: n, ...o } = e,
			r = uo(n),
			s = Me(Mn, n),
			i = Ie(Mn, n);
		return s.open && i.position === "popper"
			? p.jsx(Qn, { ...r, ...o, ref: t })
			: null;
	});
Nm.displayName = Mn;
var Am = "SelectBubbleInput",
	Mm = c.forwardRef(({ __scopeSelect: e, value: t, ...n }, o) => {
		const r = c.useRef(null),
			s = G(o, r),
			i = nm(t);
		return (
			c.useEffect(() => {
				const a = r.current;
				if (!a) return;
				const l = window.HTMLSelectElement.prototype,
					f = Object.getOwnPropertyDescriptor(l, "value").set;
				if (i !== t && f) {
					const d = new Event("change", { bubbles: !0 });
					f.call(a, t), a.dispatchEvent(d);
				}
			}, [i, t]),
			p.jsx(le.select, {
				...n,
				style: { ...Hi, ...n.style },
				ref: s,
				defaultValue: t,
			})
		);
	});
Mm.displayName = Am;
function ua(e) {
	return e === "" || e === void 0;
}
function da(e) {
	const t = we(e),
		n = c.useRef(""),
		o = c.useRef(0),
		r = c.useCallback(
			(i) => {
				const a = n.current + i;
				t(a),
					(function l(u) {
						(n.current = u),
							window.clearTimeout(o.current),
							u !== "" && (o.current = window.setTimeout(() => l(""), 1e3));
					})(a);
			},
			[t],
		),
		s = c.useCallback(() => {
			(n.current = ""), window.clearTimeout(o.current);
		}, []);
	return c.useEffect(() => () => window.clearTimeout(o.current), []), [n, r, s];
}
function fa(e, t, n) {
	const r = t.length > 1 && Array.from(t).every((u) => u === t[0]) ? t[0] : t,
		s = n ? e.indexOf(n) : -1;
	let i = Im(e, Math.max(s, 0));
	r.length === 1 && (i = i.filter((u) => u !== n));
	const l = i.find((u) =>
		u.textValue.toLowerCase().startsWith(r.toLowerCase()),
	);
	return l !== n ? l : void 0;
}
function Im(e, t) {
	return e.map((n, o) => e[(t + o) % e.length]);
}
var pa = Ki,
	Tm = Xi,
	km = qi,
	ma = Zi,
	Om = ta,
	ga = sa,
	Dm = ia,
	jm = ca;
const ha = c.forwardRef(({ className: e, children: t, ...n }, o) =>
	p.jsxs(pa, {
		ref: o,
		className: z(
			"flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background",
			"placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
			"disabled:cursor-not-allowed disabled:opacity-50",
			e,
		),
		...n,
		children: [
			t,
			p.jsx(Tm, {
				asChild: !0,
				children: p.jsx(Bu, { className: "h-4 w-4 opacity-50" }),
			}),
		],
	}),
);
ha.displayName = pa.displayName;
const va = c.forwardRef(
	({ className: e, children: t, position: n = "popper", ...o }, r) =>
		p.jsx(km, {
			children: p.jsx(ma, {
				ref: r,
				className: z(
					"relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md",
					"data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
					n === "popper" &&
						"data-[side=bottom]:translate-y-1 data-[side=top]:-translate-y-1",
					e,
				),
				position: n,
				...o,
				children: p.jsx(Om, {
					className: z(
						"p-1",
						n === "popper" &&
							"h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]",
					),
					children: t,
				}),
			}),
		}),
);
va.displayName = ma.displayName;
const xa = c.forwardRef(({ className: e, children: t, ...n }, o) =>
	p.jsxs(ga, {
		ref: o,
		className: z(
			"relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none",
			"focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
			e,
		),
		...n,
		children: [
			p.jsx("span", {
				className:
					"absolute left-2 flex h-3.5 w-3.5 items-center justify-center",
				children: p.jsx(jm, { children: p.jsx(Lu, { className: "h-4 w-4" }) }),
			}),
			p.jsx(Dm, { children: t }),
		],
	}),
);
xa.displayName = ga.displayName;
ha.__docgenInfo = { description: "", methods: [] };
va.__docgenInfo = {
	description: "",
	methods: [],
	props: {
		position: {
			defaultValue: { value: "'popper'", computed: !1 },
			required: !1,
		},
	},
};
xa.__docgenInfo = { description: "", methods: [] };
const wa = c.forwardRef(
	({ className: e, orientation: t = "horizontal", ...n }, o) =>
		p.jsx("div", {
			ref: o,
			role: "separator",
			"aria-orientation": t,
			className: z(
				"shrink-0 bg-border",
				t === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
				e,
			),
			...n,
		}),
);
wa.displayName = "Separator";
wa.__docgenInfo = {
	description: "",
	methods: [],
	displayName: "Separator",
	props: {
		orientation: {
			required: !1,
			tsType: {
				name: "union",
				raw: '"horizontal" | "vertical"',
				elements: [
					{ name: "literal", value: '"horizontal"' },
					{ name: "literal", value: '"vertical"' },
				],
			},
			description: "",
			defaultValue: { value: '"horizontal"', computed: !1 },
		},
	},
};
function $m(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Lm(r, ...t)];
}
function Lm(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var Fm = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	Qt = Fm.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	Jt = "Tabs",
	[Bm] = $m(Jt, [Kt]),
	ba = Kt(),
	[Vm, po] = Bm(Jt),
	Wm = c.forwardRef((e, t) => {
		const {
				__scopeTabs: n,
				value: o,
				onValueChange: r,
				defaultValue: s,
				orientation: i = "horizontal",
				dir: a,
				activationMode: l = "automatic",
				...u
			} = e,
			f = hs(a),
			[d, g] = jr({ prop: o, onChange: r, defaultProp: s ?? "", caller: Jt });
		return p.jsx(Vm, {
			scope: n,
			baseId: Lt(),
			value: d,
			onValueChange: g,
			orientation: i,
			dir: f,
			activationMode: l,
			children: p.jsx(Qt.div, { dir: f, "data-orientation": i, ...u, ref: t }),
		});
	});
Wm.displayName = Jt;
var ya = "TabsList",
	Ca = c.forwardRef((e, t) => {
		const { __scopeTabs: n, loop: o = !0, ...r } = e,
			s = po(ya, n),
			i = ba(n);
		return p.jsx(Gs, {
			asChild: !0,
			...i,
			orientation: s.orientation,
			dir: s.dir,
			loop: o,
			children: p.jsx(Qt.div, {
				role: "tablist",
				"aria-orientation": s.orientation,
				...r,
				ref: t,
			}),
		});
	});
Ca.displayName = ya;
var Sa = "TabsTrigger",
	Ea = c.forwardRef((e, t) => {
		const { __scopeTabs: n, value: o, disabled: r = !1, ...s } = e,
			i = po(Sa, n),
			a = ba(n),
			l = _a(i.baseId, o),
			u = Na(i.baseId, o),
			f = o === i.value;
		return p.jsx(Us, {
			asChild: !0,
			...a,
			focusable: !r,
			active: f,
			children: p.jsx(Qt.button, {
				type: "button",
				role: "tab",
				"aria-selected": f,
				"aria-controls": u,
				"data-state": f ? "active" : "inactive",
				"data-disabled": r ? "" : void 0,
				disabled: r,
				id: l,
				...s,
				ref: t,
				onMouseDown: A(e.onMouseDown, (d) => {
					!r && d.button === 0 && d.ctrlKey === !1
						? i.onValueChange(o)
						: d.preventDefault();
				}),
				onKeyDown: A(e.onKeyDown, (d) => {
					[" ", "Enter"].includes(d.key) && i.onValueChange(o);
				}),
				onFocus: A(e.onFocus, () => {
					const d = i.activationMode !== "manual";
					!f && !r && d && i.onValueChange(o);
				}),
			}),
		});
	});
Ea.displayName = Sa;
var Pa = "TabsContent",
	Ra = c.forwardRef((e, t) => {
		const { __scopeTabs: n, value: o, forceMount: r, children: s, ...i } = e,
			a = po(Pa, n),
			l = _a(a.baseId, o),
			u = Na(a.baseId, o),
			f = o === a.value,
			d = c.useRef(f);
		return (
			c.useEffect(() => {
				const g = requestAnimationFrame(() => (d.current = !1));
				return () => cancelAnimationFrame(g);
			}, []),
			p.jsx(ye, {
				present: r || f,
				children: ({ present: g }) =>
					p.jsx(Qt.div, {
						"data-state": f ? "active" : "inactive",
						"data-orientation": a.orientation,
						role: "tabpanel",
						"aria-labelledby": l,
						hidden: !g,
						id: u,
						tabIndex: 0,
						...i,
						ref: t,
						style: { ...e.style, animationDuration: d.current ? "0s" : void 0 },
						children: g && s,
					}),
			})
		);
	});
Ra.displayName = Pa;
function _a(e, t) {
	return `${e}-trigger-${t}`;
}
function Na(e, t) {
	return `${e}-content-${t}`;
}
var Aa = Ca,
	Ma = Ea,
	Ia = Ra;
const Ta = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(Aa, {
		ref: n,
		className: z(
			"inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground",
			e,
		),
		...t,
	}),
);
Ta.displayName = Aa.displayName;
const ka = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(Ma, {
		ref: n,
		className: z(
			"inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all",
			"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
			"disabled:pointer-events-none disabled:opacity-50",
			"data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm",
			e,
		),
		...t,
	}),
);
ka.displayName = Ma.displayName;
const Oa = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx(Ia, {
		ref: n,
		className: z(
			"mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
			e,
		),
		...t,
	}),
);
Oa.displayName = Ia.displayName;
Ta.__docgenInfo = { description: "", methods: [] };
ka.__docgenInfo = { description: "", methods: [] };
Oa.__docgenInfo = { description: "", methods: [] };
const Da = c.forwardRef(({ className: e, ...t }, n) =>
	p.jsx("textarea", {
		className: z(
			"flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
			e,
		),
		ref: n,
		...t,
	}),
);
Da.displayName = "Textarea";
Da.__docgenInfo = { description: "", methods: [], displayName: "Textarea" };
function zm(e, t = []) {
	let n = [];
	function o(s, i) {
		const a = c.createContext(i),
			l = n.length;
		n = [...n, i];
		const u = (d) => {
			const { scope: g, children: v, ...h } = d,
				m = g?.[e]?.[l] || a,
				x = c.useMemo(() => h, Object.values(h));
			return p.jsx(m.Provider, { value: x, children: v });
		};
		u.displayName = s + "Provider";
		function f(d, g) {
			const v = g?.[e]?.[l] || a,
				h = c.useContext(v);
			if (h) return h;
			if (i !== void 0) return i;
			throw new Error(`\`${d}\` must be used within \`${s}\``);
		}
		return [u, f];
	}
	const r = () => {
		const s = n.map((i) => c.createContext(i));
		return (a) => {
			const l = a?.[e] || s;
			return c.useMemo(() => ({ [`__scope${e}`]: { ...a, [e]: l } }), [a, l]);
		};
	};
	return (r.scopeName = e), [o, Hm(r, ...t)];
}
function Hm(...e) {
	const t = e[0];
	if (e.length === 1) return t;
	const n = () => {
		const o = e.map((r) => ({ useScope: r(), scopeName: r.scopeName }));
		return (s) => {
			const i = o.reduce((a, { useScope: l, scopeName: u }) => {
				const d = l(s)[`__scope${u}`];
				return { ...a, ...d };
			}, {});
			return c.useMemo(() => ({ [`__scope${t.scopeName}`]: i }), [i]);
		};
	};
	return (n.scopeName = t.scopeName), n;
}
var Gm = [
		"a",
		"button",
		"div",
		"form",
		"h2",
		"h3",
		"img",
		"input",
		"label",
		"li",
		"nav",
		"ol",
		"p",
		"select",
		"span",
		"svg",
		"ul",
	],
	Um = Gm.reduce((e, t) => {
		const n = ne(`Primitive.${t}`),
			o = c.forwardRef((r, s) => {
				const { asChild: i, ...a } = r,
					l = i ? n : t;
				return (
					typeof window < "u" && (window[Symbol.for("radix-ui")] = !0),
					p.jsx(l, { ...a, ref: s })
				);
			});
		return (o.displayName = `Primitive.${t}`), { ...e, [t]: o };
	}, {}),
	[en] = zm("Tooltip", [Qe]),
	mo = Qe(),
	Km = "TooltipProvider",
	Qo = "tooltip.open",
	[wg, ja] = en(Km),
	$a = "Tooltip",
	[bg, tn] = en($a),
	In = "TooltipTrigger",
	Ym = c.forwardRef((e, t) => {
		const { __scopeTooltip: n, ...o } = e,
			r = tn(In, n),
			s = ja(In, n),
			i = mo(n),
			a = c.useRef(null),
			l = G(t, a, r.onTriggerChange),
			u = c.useRef(!1),
			f = c.useRef(!1),
			d = c.useCallback(() => (u.current = !1), []);
		return (
			c.useEffect(
				() => () => document.removeEventListener("pointerup", d),
				[d],
			),
			p.jsx(qn, {
				asChild: !0,
				...i,
				children: p.jsx(Um.button, {
					"aria-describedby": r.open ? r.contentId : void 0,
					"data-state": r.stateAttribute,
					...o,
					ref: l,
					onPointerMove: A(e.onPointerMove, (g) => {
						g.pointerType !== "touch" &&
							!f.current &&
							!s.isPointerInTransitRef.current &&
							(r.onTriggerEnter(), (f.current = !0));
					}),
					onPointerLeave: A(e.onPointerLeave, () => {
						r.onTriggerLeave(), (f.current = !1);
					}),
					onPointerDown: A(e.onPointerDown, () => {
						r.open && r.onClose(),
							(u.current = !0),
							document.addEventListener("pointerup", d, { once: !0 });
					}),
					onFocus: A(e.onFocus, () => {
						u.current || r.onOpen();
					}),
					onBlur: A(e.onBlur, r.onClose),
					onClick: A(e.onClick, r.onClose),
				}),
			})
		);
	});
Ym.displayName = In;
var Xm = "TooltipPortal",
	[yg, qm] = en(Xm, { forceMount: void 0 }),
	Ke = "TooltipContent",
	La = c.forwardRef((e, t) => {
		const n = qm(Ke, e.__scopeTooltip),
			{ forceMount: o = n.forceMount, side: r = "top", ...s } = e,
			i = tn(Ke, e.__scopeTooltip);
		return p.jsx(ye, {
			present: o || i.open,
			children: i.disableHoverableContent
				? p.jsx(Fa, { side: r, ...s, ref: t })
				: p.jsx(Zm, { side: r, ...s, ref: t }),
		});
	}),
	Zm = c.forwardRef((e, t) => {
		const n = tn(Ke, e.__scopeTooltip),
			o = ja(Ke, e.__scopeTooltip),
			r = c.useRef(null),
			s = G(t, r),
			[i, a] = c.useState(null),
			{ trigger: l, onClose: u } = n,
			f = r.current,
			{ onPointerInTransitChange: d } = o,
			g = c.useCallback(() => {
				a(null), d(!1);
			}, [d]),
			v = c.useCallback(
				(h, m) => {
					const x = h.currentTarget,
						w = { x: h.clientX, y: h.clientY },
						b = ng(w, x.getBoundingClientRect()),
						y = og(w, b),
						C = rg(m.getBoundingClientRect()),
						P = ig([...y, ...C]);
					a(P), d(!0);
				},
				[d],
			);
		return (
			c.useEffect(() => () => g(), [g]),
			c.useEffect(() => {
				if (l && f) {
					const h = (x) => v(x, f),
						m = (x) => v(x, l);
					return (
						l.addEventListener("pointerleave", h),
						f.addEventListener("pointerleave", m),
						() => {
							l.removeEventListener("pointerleave", h),
								f.removeEventListener("pointerleave", m);
						}
					);
				}
			}, [l, f, v, g]),
			c.useEffect(() => {
				if (i) {
					const h = (m) => {
						const x = m.target,
							w = { x: m.clientX, y: m.clientY },
							b = l?.contains(x) || f?.contains(x),
							y = !sg(w, i);
						b ? g() : y && (g(), u());
					};
					return (
						document.addEventListener("pointermove", h),
						() => document.removeEventListener("pointermove", h)
					);
				}
			}, [l, f, i, u, g]),
			p.jsx(Fa, { ...e, ref: s })
		);
	}),
	[Qm, Jm] = en($a, { isInside: !1 }),
	eg = sl("TooltipContent"),
	Fa = c.forwardRef((e, t) => {
		const {
				__scopeTooltip: n,
				children: o,
				"aria-label": r,
				onEscapeKeyDown: s,
				onPointerDownOutside: i,
				...a
			} = e,
			l = tn(Ke, n),
			u = mo(n),
			{ onClose: f } = l;
		return (
			c.useEffect(
				() => (
					document.addEventListener(Qo, f),
					() => document.removeEventListener(Qo, f)
				),
				[f],
			),
			c.useEffect(() => {
				if (l.trigger) {
					const d = (g) => {
						g.target?.contains(l.trigger) && f();
					};
					return (
						window.addEventListener("scroll", d, { capture: !0 }),
						() => window.removeEventListener("scroll", d, { capture: !0 })
					);
				}
			}, [l.trigger, f]),
			p.jsx(ut, {
				asChild: !0,
				disableOutsidePointerEvents: !1,
				onEscapeKeyDown: s,
				onPointerDownOutside: i,
				onFocusOutside: (d) => d.preventDefault(),
				onDismiss: f,
				children: p.jsxs(Zn, {
					"data-state": l.stateAttribute,
					...u,
					...a,
					ref: t,
					style: {
						...a.style,
						"--radix-tooltip-content-transform-origin":
							"var(--radix-popper-transform-origin)",
						"--radix-tooltip-content-available-width":
							"var(--radix-popper-available-width)",
						"--radix-tooltip-content-available-height":
							"var(--radix-popper-available-height)",
						"--radix-tooltip-trigger-width": "var(--radix-popper-anchor-width)",
						"--radix-tooltip-trigger-height":
							"var(--radix-popper-anchor-height)",
					},
					children: [
						p.jsx(eg, { children: o }),
						p.jsx(Qm, {
							scope: n,
							isInside: !0,
							children: p.jsx(im, {
								id: l.contentId,
								role: "tooltip",
								children: r || o,
							}),
						}),
					],
				}),
			})
		);
	});
La.displayName = Ke;
var Ba = "TooltipArrow",
	tg = c.forwardRef((e, t) => {
		const { __scopeTooltip: n, ...o } = e,
			r = mo(n);
		return Jm(Ba, n).isInside ? null : p.jsx(Qn, { ...r, ...o, ref: t });
	});
tg.displayName = Ba;
function ng(e, t) {
	const n = Math.abs(t.top - e.y),
		o = Math.abs(t.bottom - e.y),
		r = Math.abs(t.right - e.x),
		s = Math.abs(t.left - e.x);
	switch (Math.min(n, o, r, s)) {
		case s:
			return "left";
		case r:
			return "right";
		case n:
			return "top";
		case o:
			return "bottom";
		default:
			throw new Error("unreachable");
	}
}
function og(e, t, n = 5) {
	const o = [];
	switch (t) {
		case "top":
			o.push({ x: e.x - n, y: e.y + n }, { x: e.x + n, y: e.y + n });
			break;
		case "bottom":
			o.push({ x: e.x - n, y: e.y - n }, { x: e.x + n, y: e.y - n });
			break;
		case "left":
			o.push({ x: e.x + n, y: e.y - n }, { x: e.x + n, y: e.y + n });
			break;
		case "right":
			o.push({ x: e.x - n, y: e.y - n }, { x: e.x - n, y: e.y + n });
			break;
	}
	return o;
}
function rg(e) {
	const { top: t, right: n, bottom: o, left: r } = e;
	return [
		{ x: r, y: t },
		{ x: n, y: t },
		{ x: n, y: o },
		{ x: r, y: o },
	];
}
function sg(e, t) {
	const { x: n, y: o } = e;
	let r = !1;
	for (let s = 0, i = t.length - 1; s < t.length; i = s++) {
		const a = t[s],
			l = t[i],
			u = a.x,
			f = a.y,
			d = l.x,
			g = l.y;
		f > o != g > o && n < ((d - u) * (o - f)) / (g - f) + u && (r = !r);
	}
	return r;
}
function ig(e) {
	const t = e.slice();
	return (
		t.sort((n, o) =>
			n.x < o.x ? -1 : n.x > o.x ? 1 : n.y < o.y ? -1 : n.y > o.y ? 1 : 0,
		),
		ag(t)
	);
}
function ag(e) {
	if (e.length <= 1) return e.slice();
	const t = [];
	for (let o = 0; o < e.length; o++) {
		const r = e[o];
		for (; t.length >= 2; ) {
			const s = t[t.length - 1],
				i = t[t.length - 2];
			if ((s.x - i.x) * (r.y - i.y) >= (s.y - i.y) * (r.x - i.x)) t.pop();
			else break;
		}
		t.push(r);
	}
	t.pop();
	const n = [];
	for (let o = e.length - 1; o >= 0; o--) {
		const r = e[o];
		for (; n.length >= 2; ) {
			const s = n[n.length - 1],
				i = n[n.length - 2];
			if ((s.x - i.x) * (r.y - i.y) >= (s.y - i.y) * (r.x - i.x)) n.pop();
			else break;
		}
		n.push(r);
	}
	return (
		n.pop(),
		t.length === 1 && n.length === 1 && t[0].x === n[0].x && t[0].y === n[0].y
			? t
			: t.concat(n)
	);
}
var Va = La;
const Wa = c.forwardRef(({ className: e, sideOffset: t = 4, ...n }, o) =>
	p.jsx(Va, {
		ref: o,
		sideOffset: t,
		className: z(
			"z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md",
			"animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
			"data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
			e,
		),
		...n,
	}),
);
Wa.displayName = Va.displayName;
Wa.__docgenInfo = {
	description: "",
	methods: [],
	props: {
		sideOffset: { defaultValue: { value: "4", computed: !1 }, required: !1 },
	},
};
export {
	mr as A,
	Ir as B,
	Tr as C,
	Vn as D,
	ji as I,
	zi as P,
	ha as S,
	Ta as T,
	Nr as a,
	kr as b,
	Or as c,
	Dr as d,
	Ii as e,
	Wa as f,
};
