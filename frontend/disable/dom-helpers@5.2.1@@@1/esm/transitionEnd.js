import css from "./css";
import listen from "./listen";
import triggerEvent from "./triggerEvent";

function parseDuration(node) {
	var str = css(node, "transitionDuration") || "";
	var mult = str.indexOf("ms") === -1 ? 1000 : 1;
	return parseFloat(str) * mult;
}

function emulateTransitionEnd(element, duration, padding) {
	if (padding === void 0) {
		padding = 5;
	}

	var called = false;
	var handle = setTimeout(() => {
		if (!called) triggerEvent(element, "transitionend", true);
	}, duration + padding);
	var remove = listen(
		element,
		"transitionend",
		() => {
			called = true;
		},
		{
			once: true,
		},
	);
	return () => {
		clearTimeout(handle);
		remove();
	};
}

export default function transitionEnd(element, handler, duration, padding) {
	if (duration == null) duration = parseDuration(element) || 0;
	var removeEmulate = emulateTransitionEnd(element, duration, padding);
	var remove = listen(element, "transitionend", handler);
	return () => {
		removeEmulate();
		remove();
	};
}
