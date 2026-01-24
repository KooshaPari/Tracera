var isES5 = (function () {
	return this === undefined;
})();

if (isES5) {
	module.exports = {
		freeze: Object.freeze,
		defineProperty: Object.defineProperty,
		getDescriptor: Object.getOwnPropertyDescriptor,
		keys: Object.keys,
		names: Object.getOwnPropertyNames,
		getPrototypeOf: Object.getPrototypeOf,
		isArray: Array.isArray,
		isES5: isES5,
		propertyIsWritable: (obj, prop) => {
			var descriptor = Object.getOwnPropertyDescriptor(obj, prop);
			return !!(!descriptor || descriptor.writable || descriptor.set);
		},
	};
} else {
	var has = {}.hasOwnProperty;
	var str = {}.toString;
	var proto = {}.constructor.prototype;

	var ObjectKeys = (o) => {
		var ret = [];
		for (var key in o) {
			if (has.call(o, key)) {
				ret.push(key);
			}
		}
		return ret;
	};

	var ObjectGetDescriptor = (o, key) => ({ value: o[key] });

	var ObjectDefineProperty = (o, key, desc) => {
		o[key] = desc.value;
		return o;
	};

	var ObjectFreeze = (obj) => obj;

	var ObjectGetPrototypeOf = (obj) => {
		try {
			return Object(obj).constructor.prototype;
		} catch (e) {
			return proto;
		}
	};

	var ArrayIsArray = (obj) => {
		try {
			return str.call(obj) === "[object Array]";
		} catch (e) {
			return false;
		}
	};

	module.exports = {
		isArray: ArrayIsArray,
		keys: ObjectKeys,
		names: ObjectKeys,
		defineProperty: ObjectDefineProperty,
		getDescriptor: ObjectGetDescriptor,
		freeze: ObjectFreeze,
		getPrototypeOf: ObjectGetPrototypeOf,
		isES5: isES5,
		propertyIsWritable: () => true,
	};
}
