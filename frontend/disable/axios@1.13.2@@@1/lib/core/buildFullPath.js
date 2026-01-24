import combineURLs from "../helpers/combineURLs.js";
import isAbsoluteURL from "../helpers/isAbsoluteURL.js";

/**
 * Creates a new URL by combining the baseURL with the requestedURL,
 * only when the requestedURL is not already an absolute URL.
 * If the requestURL is absolute, this function returns the requestedURL untouched.
 *
 * @param {string} baseURL The base URL
 * @param {string} requestedURL Absolute or relative URL to combine
 *
 * @returns {string} The combined full path
 */
export default function buildFullPath(
	baseURL,
	requestedURL,
	allowAbsoluteUrls,
) {
	const isRelativeUrl = !isAbsoluteURL(requestedURL);
	if (baseURL && (isRelativeUrl || allowAbsoluteUrls == false)) {
		return combineURLs(baseURL, requestedURL);
	}
	return requestedURL;
}
