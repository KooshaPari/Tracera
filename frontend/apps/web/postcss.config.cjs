// Use CommonJS require to bypass jiti's ESM processing
const tailwindcss = require("@tailwindcss/postcss");
const autoprefixer = require("autoprefixer");

module.exports = {
	plugins: [
		tailwindcss({}),
		autoprefixer({}),
	],
};
