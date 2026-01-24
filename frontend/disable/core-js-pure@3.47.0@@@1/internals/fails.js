"use strict";
module.exports = (exec) => {
	try {
		return !!exec();
	} catch (error) {
		return true;
	}
};
