"use strict";
var $String = String;

module.exports = (argument) => {
	try {
		return $String(argument);
	} catch (error) {
		return "Object";
	}
};
