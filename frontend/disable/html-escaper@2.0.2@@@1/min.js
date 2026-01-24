var html = ((t) => {
	var n = "".replace,
		u = /[&<>'"]/g,
		r = /&(?:amp|#38|lt|#60|gt|#62|apos|#39|quot|#34);/g,
		a = { "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" },
		e = {
			"&amp;": "&",
			"&#38;": "&",
			"&lt;": "<",
			"&#60;": "<",
			"&gt;": ">",
			"&#62;": ">",
			"&apos;": "'",
			"&#39;": "'",
			"&quot;": '"',
			"&#34;": '"',
		};
	function c(t) {
		return a[t];
	}
	function o(t) {
		return e[t];
	}
	return (
		(t.escape = (t) => n.call(t, u, c)),
		(t.unescape = (t) => n.call(t, r, o)),
		t
	);
})({});
