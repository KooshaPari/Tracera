import addEventListener from "./addEventListener";
import removeEventListener from "./removeEventListener";

function listen(node, eventName, handler, options) {
	addEventListener(node, eventName, handler, options);
	return () => {
		removeEventListener(node, eventName, handler, options);
	};
}

export default listen;
