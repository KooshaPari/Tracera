/**
 * Convert Windows backslash paths to slash paths: foo\\bar ➔ foo/bar
 */
export function slash(path) {
	const isExtendedLengthPath = /^\\\\\?\\/.test(path);
	if (isExtendedLengthPath) {
		return path;
	}
	return path.replace(/\\/g, "/");
}
//# sourceMappingURL=slash.js.map
