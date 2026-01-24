// populates missing values
module.exports = (dst, src) => {
	Object.keys(src).forEach((prop) => {
		dst[prop] = dst[prop] || src[prop]; // eslint-disable-line no-param-reassign
	});

	return dst;
};
