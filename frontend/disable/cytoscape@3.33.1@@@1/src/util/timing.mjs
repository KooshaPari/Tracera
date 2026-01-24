import debounce from "lodash/debounce.js";
import window from "../window.mjs";

var performance = window ? window.performance : null;

var pnow =
	performance && performance.now ? () => performance.now() : () => Date.now();

var raf = (() => {
	if (window) {
		if (window.requestAnimationFrame) {
			return (fn) => {
				window.requestAnimationFrame(fn);
			};
		} else if (window.mozRequestAnimationFrame) {
			return (fn) => {
				window.mozRequestAnimationFrame(fn);
			};
		} else if (window.webkitRequestAnimationFrame) {
			return (fn) => {
				window.webkitRequestAnimationFrame(fn);
			};
		} else if (window.msRequestAnimationFrame) {
			return (fn) => {
				window.msRequestAnimationFrame(fn);
			};
		}
	}

	return (fn) => {
		if (fn) {
			setTimeout(() => {
				fn(pnow());
			}, 1000 / 60);
		}
	};
})();

export const requestAnimationFrame = (fn) => raf(fn);

export const performanceNow = pnow;

export const now = () => Date.now();

export { debounce };
