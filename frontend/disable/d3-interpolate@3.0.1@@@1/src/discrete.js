export default function (range) {
	var n = range.length;
	return (t) => range[Math.max(0, Math.min(n - 1, Math.floor(t * n)))];
}
