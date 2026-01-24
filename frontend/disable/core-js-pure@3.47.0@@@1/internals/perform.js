"use strict";
module.exports = (exec) => {
	try {
		return { error: false, value: exec() };
	} catch (error) {
		return { error: true, value: error };
	}
};
