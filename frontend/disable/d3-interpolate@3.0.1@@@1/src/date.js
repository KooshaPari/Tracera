export default function (a, b) {
	var d = new Date();
	return (a = +a), (b = +b), (t) => (d.setTime(a * (1 - t) + b * t), d);
}
