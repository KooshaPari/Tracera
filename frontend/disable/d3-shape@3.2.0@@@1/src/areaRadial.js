import area from "./area.js";
import curveRadial, { curveRadialLinear } from "./curve/radial.js";
import { lineRadial } from "./lineRadial.js";

export default function () {
	var a = area().curve(curveRadialLinear),
		c = a.curve,
		x0 = a.lineX0,
		x1 = a.lineX1,
		y0 = a.lineY0,
		y1 = a.lineY1;

	(a.angle = a.x), delete a.x;
	(a.startAngle = a.x0), delete a.x0;
	(a.endAngle = a.x1), delete a.x1;
	(a.radius = a.y), delete a.y;
	(a.innerRadius = a.y0), delete a.y0;
	(a.outerRadius = a.y1), delete a.y1;
	(a.lineStartAngle = () => lineRadial(x0())), delete a.lineX0;
	(a.lineEndAngle = () => lineRadial(x1())), delete a.lineX1;
	(a.lineInnerRadius = () => lineRadial(y0())), delete a.lineY0;
	(a.lineOuterRadius = () => lineRadial(y1())), delete a.lineY1;

	a.curve = function (_) {
		return arguments.length ? c(curveRadial(_)) : c()._curve;
	};

	return a;
}
