export default function (a, b) {
	return (a = +a), (b = +b), (t) => a * (1 - t) + b * t;
}
