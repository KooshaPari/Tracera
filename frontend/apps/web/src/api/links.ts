/* oxlint-disable oxc/no-async-await */
// Re-export links API from endpoints
import { linksApi } from "./endpoints";

const fetchLinks = linksApi.list;
const fetchLink = linksApi.get;
const createLink = linksApi.create;
const updateLink = linksApi.update;
const deleteLink = linksApi.delete;

const linksApiExports = {
	createLink,
	deleteLink,
	fetchLink,
	fetchLinks,
	updateLink,
};

// eslint-disable-next-line import/no-default-export
export default linksApiExports;
