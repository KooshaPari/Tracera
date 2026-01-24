(() => {
	var _window$dateFns;
	function _typeof(o) {
		"@babel/helpers - typeof";
		return (
			(_typeof =
				"function" == typeof Symbol && "symbol" == typeof Symbol.iterator
					? (o) => typeof o
					: (o) =>
							o &&
							"function" == typeof Symbol &&
							o.constructor === Symbol &&
							o !== Symbol.prototype
								? "symbol"
								: typeof o),
			_typeof(o)
		);
	}
	function ownKeys(e, r) {
		var t = Object.keys(e);
		if (Object.getOwnPropertySymbols) {
			var o = Object.getOwnPropertySymbols(e);
			r &&
				(o = o.filter((r) => Object.getOwnPropertyDescriptor(e, r).enumerable)),
				t.push.apply(t, o);
		}
		return t;
	}
	function _objectSpread(e) {
		for (var r = 1; r < arguments.length; r++) {
			var t = null != arguments[r] ? arguments[r] : {};
			r % 2
				? ownKeys(Object(t), !0).forEach((r) => {
						_defineProperty(e, r, t[r]);
					})
				: Object.getOwnPropertyDescriptors
					? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t))
					: ownKeys(Object(t)).forEach((r) => {
							Object.defineProperty(
								e,
								r,
								Object.getOwnPropertyDescriptor(t, r),
							);
						});
		}
		return e;
	}
	function _defineProperty(obj, key, value) {
		key = _toPropertyKey(key);
		if (key in obj) {
			Object.defineProperty(obj, key, {
				value: value,
				enumerable: true,
				configurable: true,
				writable: true,
			});
		} else {
			obj[key] = value;
		}
		return obj;
	}
	function _toPropertyKey(t) {
		var i = _toPrimitive(t, "string");
		return "symbol" == _typeof(i) ? i : String(i);
	}
	function _toPrimitive(t, r) {
		if ("object" != _typeof(t) || !t) return t;
		var e = t[Symbol.toPrimitive];
		if (void 0 !== e) {
			var i = e.call(t, r || "default");
			if ("object" != _typeof(i)) return i;
			throw new TypeError("@@toPrimitive must return a primitive value.");
		}
		return ("string" === r ? String : Number)(t);
	}
	var __defProp = Object.defineProperty;
	var __export = function __export(target, all) {
		for (var name in all)
			__defProp(target, name, {
				get: all[name],
				enumerable: true,
				configurable: true,
				set: function set(newValue) {
					return (all[name] = () => newValue);
				},
			});
	};

	// lib/locale/he/_lib/formatDistance.js
	var formatDistanceLocale = {
		lessThanXSeconds: {
			one: "\u05E4\u05D7\u05D5\u05EA \u05DE\u05E9\u05E0\u05D9\u05D9\u05D4",
			two: "\u05E4\u05D7\u05D5\u05EA \u05DE\u05E9\u05EA\u05D9 \u05E9\u05E0\u05D9\u05D5\u05EA",
			other:
				"\u05E4\u05D7\u05D5\u05EA \u05DE\u05BE{{count}} \u05E9\u05E0\u05D9\u05D5\u05EA",
		},
		xSeconds: {
			one: "\u05E9\u05E0\u05D9\u05D9\u05D4",
			two: "\u05E9\u05EA\u05D9 \u05E9\u05E0\u05D9\u05D5\u05EA",
			other: "{{count}} \u05E9\u05E0\u05D9\u05D5\u05EA",
		},
		halfAMinute: "\u05D7\u05E6\u05D9 \u05D3\u05E7\u05D4",
		lessThanXMinutes: {
			one: "\u05E4\u05D7\u05D5\u05EA \u05DE\u05D3\u05E7\u05D4",
			two: "\u05E4\u05D7\u05D5\u05EA \u05DE\u05E9\u05EA\u05D9 \u05D3\u05E7\u05D5\u05EA",
			other:
				"\u05E4\u05D7\u05D5\u05EA \u05DE\u05BE{{count}} \u05D3\u05E7\u05D5\u05EA",
		},
		xMinutes: {
			one: "\u05D3\u05E7\u05D4",
			two: "\u05E9\u05EA\u05D9 \u05D3\u05E7\u05D5\u05EA",
			other: "{{count}} \u05D3\u05E7\u05D5\u05EA",
		},
		aboutXHours: {
			one: "\u05DB\u05E9\u05E2\u05D4",
			two: "\u05DB\u05E9\u05E2\u05EA\u05D9\u05D9\u05DD",
			other: "\u05DB\u05BE{{count}} \u05E9\u05E2\u05D5\u05EA",
		},
		xHours: {
			one: "\u05E9\u05E2\u05D4",
			two: "\u05E9\u05E2\u05EA\u05D9\u05D9\u05DD",
			other: "{{count}} \u05E9\u05E2\u05D5\u05EA",
		},
		xDays: {
			one: "\u05D9\u05D5\u05DD",
			two: "\u05D9\u05D5\u05DE\u05D9\u05D9\u05DD",
			other: "{{count}} \u05D9\u05DE\u05D9\u05DD",
		},
		aboutXWeeks: {
			one: "\u05DB\u05E9\u05D1\u05D5\u05E2",
			two: "\u05DB\u05E9\u05D1\u05D5\u05E2\u05D9\u05D9\u05DD",
			other: "\u05DB\u05BE{{count}} \u05E9\u05D1\u05D5\u05E2\u05D5\u05EA",
		},
		xWeeks: {
			one: "\u05E9\u05D1\u05D5\u05E2",
			two: "\u05E9\u05D1\u05D5\u05E2\u05D9\u05D9\u05DD",
			other: "{{count}} \u05E9\u05D1\u05D5\u05E2\u05D5\u05EA",
		},
		aboutXMonths: {
			one: "\u05DB\u05D7\u05D5\u05D3\u05E9",
			two: "\u05DB\u05D7\u05D5\u05D3\u05E9\u05D9\u05D9\u05DD",
			other: "\u05DB\u05BE{{count}} \u05D7\u05D5\u05D3\u05E9\u05D9\u05DD",
		},
		xMonths: {
			one: "\u05D7\u05D5\u05D3\u05E9",
			two: "\u05D7\u05D5\u05D3\u05E9\u05D9\u05D9\u05DD",
			other: "{{count}} \u05D7\u05D5\u05D3\u05E9\u05D9\u05DD",
		},
		aboutXYears: {
			one: "\u05DB\u05E9\u05E0\u05D4",
			two: "\u05DB\u05E9\u05E0\u05EA\u05D9\u05D9\u05DD",
			other: "\u05DB\u05BE{{count}} \u05E9\u05E0\u05D9\u05DD",
		},
		xYears: {
			one: "\u05E9\u05E0\u05D4",
			two: "\u05E9\u05E0\u05EA\u05D9\u05D9\u05DD",
			other: "{{count}} \u05E9\u05E0\u05D9\u05DD",
		},
		overXYears: {
			one: "\u05D9\u05D5\u05EA\u05E8 \u05DE\u05E9\u05E0\u05D4",
			two: "\u05D9\u05D5\u05EA\u05E8 \u05DE\u05E9\u05E0\u05EA\u05D9\u05D9\u05DD",
			other:
				"\u05D9\u05D5\u05EA\u05E8 \u05DE\u05BE{{count}} \u05E9\u05E0\u05D9\u05DD",
		},
		almostXYears: {
			one: "\u05DB\u05DE\u05E2\u05D8 \u05E9\u05E0\u05D4",
			two: "\u05DB\u05DE\u05E2\u05D8 \u05E9\u05E0\u05EA\u05D9\u05D9\u05DD",
			other: "\u05DB\u05DE\u05E2\u05D8 {{count}} \u05E9\u05E0\u05D9\u05DD",
		},
	};
	var formatDistance = function formatDistance(token, count, options) {
		if (
			token === "xDays" &&
			options !== null &&
			options !== void 0 &&
			options.addSuffix &&
			count <= 2
		) {
			if (options.comparison && options.comparison > 0) {
				return count === 1
					? "\u05DE\u05D7\u05E8"
					: "\u05DE\u05D7\u05E8\u05EA\u05D9\u05D9\u05DD";
			}
			return count === 1
				? "\u05D0\u05EA\u05DE\u05D5\u05DC"
				: "\u05E9\u05DC\u05E9\u05D5\u05DD";
		}
		var result;
		var tokenValue = formatDistanceLocale[token];
		if (typeof tokenValue === "string") {
			result = tokenValue;
		} else if (count === 1) {
			result = tokenValue.one;
		} else if (count === 2) {
			result = tokenValue.two;
		} else {
			result = tokenValue.other.replace("{{count}}", String(count));
		}
		if (options !== null && options !== void 0 && options.addSuffix) {
			if (options.comparison && options.comparison > 0) {
				return "\u05D1\u05E2\u05D5\u05D3 " + result;
			} else {
				return "\u05DC\u05E4\u05E0\u05D9 " + result;
			}
		}
		return result;
	};

	// lib/locale/_lib/buildFormatLongFn.js
	function buildFormatLongFn(args) {
		return function () {
			var options =
				arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
			var width = options.width ? String(options.width) : args.defaultWidth;
			var format = args.formats[width] || args.formats[args.defaultWidth];
			return format;
		};
	}

	// lib/locale/he/_lib/formatLong.js
	var dateFormats = {
		full: "EEEE, d \u05D1MMMM y",
		long: "d \u05D1MMMM y",
		medium: "d \u05D1MMM y",
		short: "d.M.y",
	};
	var timeFormats = {
		full: "H:mm:ss zzzz",
		long: "H:mm:ss z",
		medium: "H:mm:ss",
		short: "H:mm",
	};
	var dateTimeFormats = {
		full: "{{date}} '\u05D1\u05E9\u05E2\u05D4' {{time}}",
		long: "{{date}} '\u05D1\u05E9\u05E2\u05D4' {{time}}",
		medium: "{{date}}, {{time}}",
		short: "{{date}}, {{time}}",
	};
	var formatLong = {
		date: buildFormatLongFn({
			formats: dateFormats,
			defaultWidth: "full",
		}),
		time: buildFormatLongFn({
			formats: timeFormats,
			defaultWidth: "full",
		}),
		dateTime: buildFormatLongFn({
			formats: dateTimeFormats,
			defaultWidth: "full",
		}),
	};

	// lib/locale/he/_lib/formatRelative.js
	var formatRelativeLocale = {
		lastWeek: "eeee '\u05E9\u05E2\u05D1\u05E8 \u05D1\u05E9\u05E2\u05D4' p",
		yesterday: "'\u05D0\u05EA\u05DE\u05D5\u05DC \u05D1\u05E9\u05E2\u05D4' p",
		today: "'\u05D4\u05D9\u05D5\u05DD \u05D1\u05E9\u05E2\u05D4' p",
		tomorrow: "'\u05DE\u05D7\u05E8 \u05D1\u05E9\u05E2\u05D4' p",
		nextWeek: "eeee '\u05D1\u05E9\u05E2\u05D4' p",
		other: "P",
	};
	var formatRelative = function formatRelative(
		token,
		_date,
		_baseDate,
		_options,
	) {
		return formatRelativeLocale[token];
	};

	// lib/locale/_lib/buildLocalizeFn.js
	function buildLocalizeFn(args) {
		return (value, options) => {
			var context =
				options !== null && options !== void 0 && options.context
					? String(options.context)
					: "standalone";
			var valuesArray;
			if (context === "formatting" && args.formattingValues) {
				var defaultWidth = args.defaultFormattingWidth || args.defaultWidth;
				var width =
					options !== null && options !== void 0 && options.width
						? String(options.width)
						: defaultWidth;
				valuesArray =
					args.formattingValues[width] || args.formattingValues[defaultWidth];
			} else {
				var _defaultWidth = args.defaultWidth;
				var _width =
					options !== null && options !== void 0 && options.width
						? String(options.width)
						: args.defaultWidth;
				valuesArray = args.values[_width] || args.values[_defaultWidth];
			}
			var index = args.argumentCallback ? args.argumentCallback(value) : value;
			return valuesArray[index];
		};
	}

	// lib/locale/he/_lib/localize.js
	var eraValues = {
		narrow: [
			"\u05DC\u05E4\u05E0\u05D4\u05F4\u05E1",
			"\u05DC\u05E1\u05E4\u05D9\u05E8\u05D4",
		],
		abbreviated: [
			"\u05DC\u05E4\u05E0\u05D4\u05F4\u05E1",
			"\u05DC\u05E1\u05E4\u05D9\u05E8\u05D4",
		],
		wide: [
			"\u05DC\u05E4\u05E0\u05D9 \u05D4\u05E1\u05E4\u05D9\u05E8\u05D4",
			"\u05DC\u05E1\u05E4\u05D9\u05E8\u05D4",
		],
	};
	var quarterValues = {
		narrow: ["1", "2", "3", "4"],
		abbreviated: ["Q1", "Q2", "Q3", "Q4"],
		wide: [
			"\u05E8\u05D1\u05E2\u05D5\u05DF 1",
			"\u05E8\u05D1\u05E2\u05D5\u05DF 2",
			"\u05E8\u05D1\u05E2\u05D5\u05DF 3",
			"\u05E8\u05D1\u05E2\u05D5\u05DF 4",
		],
	};
	var monthValues = {
		narrow: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
		abbreviated: [
			"\u05D9\u05E0\u05D5\u05F3",
			"\u05E4\u05D1\u05E8\u05F3",
			"\u05DE\u05E8\u05E5",
			"\u05D0\u05E4\u05E8\u05F3",
			"\u05DE\u05D0\u05D9",
			"\u05D9\u05D5\u05E0\u05D9",
			"\u05D9\u05D5\u05DC\u05D9",
			"\u05D0\u05D5\u05D2\u05F3",
			"\u05E1\u05E4\u05D8\u05F3",
			"\u05D0\u05D5\u05E7\u05F3",
			"\u05E0\u05D5\u05D1\u05F3",
			"\u05D3\u05E6\u05DE\u05F3",
		],

		wide: [
			"\u05D9\u05E0\u05D5\u05D0\u05E8",
			"\u05E4\u05D1\u05E8\u05D5\u05D0\u05E8",
			"\u05DE\u05E8\u05E5",
			"\u05D0\u05E4\u05E8\u05D9\u05DC",
			"\u05DE\u05D0\u05D9",
			"\u05D9\u05D5\u05E0\u05D9",
			"\u05D9\u05D5\u05DC\u05D9",
			"\u05D0\u05D5\u05D2\u05D5\u05E1\u05D8",
			"\u05E1\u05E4\u05D8\u05DE\u05D1\u05E8",
			"\u05D0\u05D5\u05E7\u05D8\u05D5\u05D1\u05E8",
			"\u05E0\u05D5\u05D1\u05DE\u05D1\u05E8",
			"\u05D3\u05E6\u05DE\u05D1\u05E8",
		],
	};
	var dayValues = {
		narrow: [
			"\u05D0\u05F3",
			"\u05D1\u05F3",
			"\u05D2\u05F3",
			"\u05D3\u05F3",
			"\u05D4\u05F3",
			"\u05D5\u05F3",
			"\u05E9\u05F3",
		],
		short: [
			"\u05D0\u05F3",
			"\u05D1\u05F3",
			"\u05D2\u05F3",
			"\u05D3\u05F3",
			"\u05D4\u05F3",
			"\u05D5\u05F3",
			"\u05E9\u05F3",
		],
		abbreviated: [
			"\u05D9\u05D5\u05DD \u05D0\u05F3",
			"\u05D9\u05D5\u05DD \u05D1\u05F3",
			"\u05D9\u05D5\u05DD \u05D2\u05F3",
			"\u05D9\u05D5\u05DD \u05D3\u05F3",
			"\u05D9\u05D5\u05DD \u05D4\u05F3",
			"\u05D9\u05D5\u05DD \u05D5\u05F3",
			"\u05E9\u05D1\u05EA",
		],

		wide: [
			"\u05D9\u05D5\u05DD \u05E8\u05D0\u05E9\u05D5\u05DF",
			"\u05D9\u05D5\u05DD \u05E9\u05E0\u05D9",
			"\u05D9\u05D5\u05DD \u05E9\u05DC\u05D9\u05E9\u05D9",
			"\u05D9\u05D5\u05DD \u05E8\u05D1\u05D9\u05E2\u05D9",
			"\u05D9\u05D5\u05DD \u05D7\u05DE\u05D9\u05E9\u05D9",
			"\u05D9\u05D5\u05DD \u05E9\u05D9\u05E9\u05D9",
			"\u05D9\u05D5\u05DD \u05E9\u05D1\u05EA",
		],
	};
	var dayPeriodValues = {
		narrow: {
			am: "\u05DC\u05E4\u05E0\u05D4\u05F4\u05E6",
			pm: "\u05D0\u05D7\u05D4\u05F4\u05E6",
			midnight: "\u05D7\u05E6\u05D5\u05EA",
			noon: "\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			morning: "\u05D1\u05D5\u05E7\u05E8",
			afternoon:
				"\u05D0\u05D7\u05E8 \u05D4\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			evening: "\u05E2\u05E8\u05D1",
			night: "\u05DC\u05D9\u05DC\u05D4",
		},
		abbreviated: {
			am: "\u05DC\u05E4\u05E0\u05D4\u05F4\u05E6",
			pm: "\u05D0\u05D7\u05D4\u05F4\u05E6",
			midnight: "\u05D7\u05E6\u05D5\u05EA",
			noon: "\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			morning: "\u05D1\u05D5\u05E7\u05E8",
			afternoon:
				"\u05D0\u05D7\u05E8 \u05D4\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			evening: "\u05E2\u05E8\u05D1",
			night: "\u05DC\u05D9\u05DC\u05D4",
		},
		wide: {
			am: "\u05DC\u05E4\u05E0\u05D4\u05F4\u05E6",
			pm: "\u05D0\u05D7\u05D4\u05F4\u05E6",
			midnight: "\u05D7\u05E6\u05D5\u05EA",
			noon: "\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			morning: "\u05D1\u05D5\u05E7\u05E8",
			afternoon:
				"\u05D0\u05D7\u05E8 \u05D4\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			evening: "\u05E2\u05E8\u05D1",
			night: "\u05DC\u05D9\u05DC\u05D4",
		},
	};
	var formattingDayPeriodValues = {
		narrow: {
			am: "\u05DC\u05E4\u05E0\u05D4\u05F4\u05E6",
			pm: "\u05D0\u05D7\u05D4\u05F4\u05E6",
			midnight: "\u05D7\u05E6\u05D5\u05EA",
			noon: "\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			morning: "\u05D1\u05D1\u05D5\u05E7\u05E8",
			afternoon: "\u05D1\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			evening: "\u05D1\u05E2\u05E8\u05D1",
			night: "\u05D1\u05DC\u05D9\u05DC\u05D4",
		},
		abbreviated: {
			am: "\u05DC\u05E4\u05E0\u05D4\u05F4\u05E6",
			pm: "\u05D0\u05D7\u05D4\u05F4\u05E6",
			midnight: "\u05D7\u05E6\u05D5\u05EA",
			noon: "\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			morning: "\u05D1\u05D1\u05D5\u05E7\u05E8",
			afternoon:
				"\u05D0\u05D7\u05E8 \u05D4\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			evening: "\u05D1\u05E2\u05E8\u05D1",
			night: "\u05D1\u05DC\u05D9\u05DC\u05D4",
		},
		wide: {
			am: "\u05DC\u05E4\u05E0\u05D4\u05F4\u05E6",
			pm: "\u05D0\u05D7\u05D4\u05F4\u05E6",
			midnight: "\u05D7\u05E6\u05D5\u05EA",
			noon: "\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			morning: "\u05D1\u05D1\u05D5\u05E7\u05E8",
			afternoon:
				"\u05D0\u05D7\u05E8 \u05D4\u05E6\u05D4\u05E8\u05D9\u05D9\u05DD",
			evening: "\u05D1\u05E2\u05E8\u05D1",
			night: "\u05D1\u05DC\u05D9\u05DC\u05D4",
		},
	};
	var ordinalNumber = function ordinalNumber(dirtyNumber, options) {
		var number = Number(dirtyNumber);
		if (number <= 0 || number > 10) return String(number);
		var unit = String(
			options === null || options === void 0 ? void 0 : options.unit,
		);
		var isFemale = ["year", "hour", "minute", "second"].indexOf(unit) >= 0;
		var male = [
			"\u05E8\u05D0\u05E9\u05D5\u05DF",
			"\u05E9\u05E0\u05D9",
			"\u05E9\u05DC\u05D9\u05E9\u05D9",
			"\u05E8\u05D1\u05D9\u05E2\u05D9",
			"\u05D7\u05DE\u05D9\u05E9\u05D9",
			"\u05E9\u05D9\u05E9\u05D9",
			"\u05E9\u05D1\u05D9\u05E2\u05D9",
			"\u05E9\u05DE\u05D9\u05E0\u05D9",
			"\u05EA\u05E9\u05D9\u05E2\u05D9",
			"\u05E2\u05E9\u05D9\u05E8\u05D9",
		];

		var female = [
			"\u05E8\u05D0\u05E9\u05D5\u05E0\u05D4",
			"\u05E9\u05E0\u05D9\u05D9\u05D4",
			"\u05E9\u05DC\u05D9\u05E9\u05D9\u05EA",
			"\u05E8\u05D1\u05D9\u05E2\u05D9\u05EA",
			"\u05D7\u05DE\u05D9\u05E9\u05D9\u05EA",
			"\u05E9\u05D9\u05E9\u05D9\u05EA",
			"\u05E9\u05D1\u05D9\u05E2\u05D9\u05EA",
			"\u05E9\u05DE\u05D9\u05E0\u05D9\u05EA",
			"\u05EA\u05E9\u05D9\u05E2\u05D9\u05EA",
			"\u05E2\u05E9\u05D9\u05E8\u05D9\u05EA",
		];

		var index = number - 1;
		return isFemale ? female[index] : male[index];
	};
	var localize = {
		ordinalNumber: ordinalNumber,
		era: buildLocalizeFn({
			values: eraValues,
			defaultWidth: "wide",
		}),
		quarter: buildLocalizeFn({
			values: quarterValues,
			defaultWidth: "wide",
			argumentCallback: function argumentCallback(quarter) {
				return quarter - 1;
			},
		}),
		month: buildLocalizeFn({
			values: monthValues,
			defaultWidth: "wide",
		}),
		day: buildLocalizeFn({
			values: dayValues,
			defaultWidth: "wide",
		}),
		dayPeriod: buildLocalizeFn({
			values: dayPeriodValues,
			defaultWidth: "wide",
			formattingValues: formattingDayPeriodValues,
			defaultFormattingWidth: "wide",
		}),
	};

	// lib/locale/_lib/buildMatchFn.js
	function buildMatchFn(args) {
		return function (string) {
			var options =
				arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
			var width = options.width;
			var matchPattern =
				(width && args.matchPatterns[width]) ||
				args.matchPatterns[args.defaultMatchWidth];
			var matchResult = string.match(matchPattern);
			if (!matchResult) {
				return null;
			}
			var matchedString = matchResult[0];
			var parsePatterns =
				(width && args.parsePatterns[width]) ||
				args.parsePatterns[args.defaultParseWidth];
			var key = Array.isArray(parsePatterns)
				? findIndex(parsePatterns, (pattern) => pattern.test(matchedString))
				: findKey(parsePatterns, (pattern) => pattern.test(matchedString));
			var value;
			value = args.valueCallback ? args.valueCallback(key) : key;
			value = options.valueCallback ? options.valueCallback(value) : value;
			var rest = string.slice(matchedString.length);
			return { value: value, rest: rest };
		};
	}
	function findKey(object, predicate) {
		for (var key in object) {
			if (Object.hasOwn(object, key) && predicate(object[key])) {
				return key;
			}
		}
		return;
	}
	function findIndex(array, predicate) {
		for (var key = 0; key < array.length; key++) {
			if (predicate(array[key])) {
				return key;
			}
		}
		return;
	}

	// lib/locale/_lib/buildMatchPatternFn.js
	function buildMatchPatternFn(args) {
		return function (string) {
			var options =
				arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
			var matchResult = string.match(args.matchPattern);
			if (!matchResult) return null;
			var matchedString = matchResult[0];
			var parseResult = string.match(args.parsePattern);
			if (!parseResult) return null;
			var value = args.valueCallback
				? args.valueCallback(parseResult[0])
				: parseResult[0];
			value = options.valueCallback ? options.valueCallback(value) : value;
			var rest = string.slice(matchedString.length);
			return { value: value, rest: rest };
		};
	}

	// lib/locale/he/_lib/match.js
	var matchOrdinalNumberPattern =
		/^(\d+|(ראשון|שני|שלישי|רביעי|חמישי|שישי|שביעי|שמיני|תשיעי|עשירי|ראשונה|שנייה|שלישית|רביעית|חמישית|שישית|שביעית|שמינית|תשיעית|עשירית))/i;
	var parseOrdinalNumberPattern = /^(\d+|רא|שנ|של|רב|ח|שי|שב|שמ|ת|ע)/i;
	var matchEraPatterns = {
		narrow: /^ל(ספירה|פנה״ס)/i,
		abbreviated: /^ל(ספירה|פנה״ס)/i,
		wide: /^ל(פני ה)?ספירה/i,
	};
	var parseEraPatterns = {
		any: [/^לפ/i, /^לס/i],
	};
	var matchQuarterPatterns = {
		narrow: /^[1234]/i,
		abbreviated: /^q[1234]/i,
		wide: /^רבעון [1234]/i,
	};
	var parseQuarterPatterns = {
		any: [/1/i, /2/i, /3/i, /4/i],
	};
	var matchMonthPatterns = {
		narrow: /^\d+/i,
		abbreviated: /^(ינו|פבר|מרץ|אפר|מאי|יוני|יולי|אוג|ספט|אוק|נוב|דצמ)׳?/i,
		wide: /^(ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)/i,
	};
	var parseMonthPatterns = {
		narrow: [
			/^1$/i,
			/^2/i,
			/^3/i,
			/^4/i,
			/^5/i,
			/^6/i,
			/^7/i,
			/^8/i,
			/^9/i,
			/^10/i,
			/^11/i,
			/^12/i,
		],

		any: [
			/^ינ/i,
			/^פ/i,
			/^מר/i,
			/^אפ/i,
			/^מא/i,
			/^יונ/i,
			/^יול/i,
			/^אוג/i,
			/^ס/i,
			/^אוק/i,
			/^נ/i,
			/^ד/i,
		],
	};
	var matchDayPatterns = {
		narrow: /^[אבגדהוש]׳/i,
		short: /^[אבגדהוש]׳/i,
		abbreviated: /^(שבת|יום (א|ב|ג|ד|ה|ו)׳)/i,
		wide: /^יום (ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)/i,
	};
	var parseDayPatterns = {
		abbreviated: [/א׳$/i, /ב׳$/i, /ג׳$/i, /ד׳$/i, /ה׳$/i, /ו׳$/i, /^ש/i],
		wide: [/ן$/i, /ני$/i, /לישי$/i, /עי$/i, /מישי$/i, /שישי$/i, /ת$/i],
		any: [/^א/i, /^ב/i, /^ג/i, /^ד/i, /^ה/i, /^ו/i, /^ש/i],
	};
	var matchDayPeriodPatterns = {
		any: /^(אחר ה|ב)?(חצות|צהריים|בוקר|ערב|לילה|אחה״צ|לפנה״צ)/i,
	};
	var parseDayPeriodPatterns = {
		any: {
			am: /^לפ/i,
			pm: /^אחה/i,
			midnight: /^ח/i,
			noon: /^צ/i,
			morning: /בוקר/i,
			afternoon: /בצ|אחר/i,
			evening: /ערב/i,
			night: /לילה/i,
		},
	};
	var ordinalName = [
		"\u05E8\u05D0",
		"\u05E9\u05E0",
		"\u05E9\u05DC",
		"\u05E8\u05D1",
		"\u05D7",
		"\u05E9\u05D9",
		"\u05E9\u05D1",
		"\u05E9\u05DE",
		"\u05EA",
		"\u05E2",
	];
	var match = {
		ordinalNumber: buildMatchPatternFn({
			matchPattern: matchOrdinalNumberPattern,
			parsePattern: parseOrdinalNumberPattern,
			valueCallback: function valueCallback(value) {
				var number = parseInt(value, 10);
				return isNaN(number) ? ordinalName.indexOf(value) + 1 : number;
			},
		}),
		era: buildMatchFn({
			matchPatterns: matchEraPatterns,
			defaultMatchWidth: "wide",
			parsePatterns: parseEraPatterns,
			defaultParseWidth: "any",
		}),
		quarter: buildMatchFn({
			matchPatterns: matchQuarterPatterns,
			defaultMatchWidth: "wide",
			parsePatterns: parseQuarterPatterns,
			defaultParseWidth: "any",
			valueCallback: function valueCallback(index) {
				return index + 1;
			},
		}),
		month: buildMatchFn({
			matchPatterns: matchMonthPatterns,
			defaultMatchWidth: "wide",
			parsePatterns: parseMonthPatterns,
			defaultParseWidth: "any",
		}),
		day: buildMatchFn({
			matchPatterns: matchDayPatterns,
			defaultMatchWidth: "wide",
			parsePatterns: parseDayPatterns,
			defaultParseWidth: "any",
		}),
		dayPeriod: buildMatchFn({
			matchPatterns: matchDayPeriodPatterns,
			defaultMatchWidth: "any",
			parsePatterns: parseDayPeriodPatterns,
			defaultParseWidth: "any",
		}),
	};

	// lib/locale/he.js
	var he = {
		code: "he",
		formatDistance: formatDistance,
		formatLong: formatLong,
		formatRelative: formatRelative,
		localize: localize,
		match: match,
		options: {
			weekStartsOn: 0,
			firstWeekContainsDate: 1,
		},
	};

	// lib/locale/he/cdn.js
	window.dateFns = _objectSpread(
		_objectSpread({}, window.dateFns),
		{},
		{
			locale: _objectSpread(
				_objectSpread(
					{},
					(_window$dateFns = window.dateFns) === null ||
						_window$dateFns === void 0
						? void 0
						: _window$dateFns.locale,
				),
				{},
				{
					he: he,
				},
			),
		},
	);

	//# debugId=79737C2841483B4564756E2164756E21

	//# sourceMappingURL=cdn.js.map
})();
