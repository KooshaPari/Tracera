import { color } from "d3-color";
import { genericArray } from "./array.js";
import constant from "./constant.js";
import date from "./date.js";
import number from "./number.js";
import numberArray, { isNumberArray } from "./numberArray.js";
import object from "./object.js";
import rgb from "./rgb.js";
import string from "./string.js";

export default function (a, b) {
	var t = typeof b,
		c;
	return b == null || t === "boolean"
		? constant(b)
		: (t === "number"
				? number
				: t === "string"
					? (c = color(b))
						? ((b = c), rgb)
						: string
					: b instanceof color
						? rgb
						: b instanceof Date
							? date
							: isNumberArray(b)
								? numberArray
								: Array.isArray(b)
									? genericArray
									: (typeof b.valueOf !== "function" &&
												typeof b.toString !== "function") ||
											isNaN(b)
										? object
										: number)(a, b);
}
