var toString = {}.toString;

module.exports =
	Array.isArray || ((arr) => toString.call(arr) == "[object Array]");
