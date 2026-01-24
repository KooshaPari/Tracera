export default function (a, b) {
	return (a = +a), (b = +b), (t) => Math.round(a * (1 - t) + b * t);
}
