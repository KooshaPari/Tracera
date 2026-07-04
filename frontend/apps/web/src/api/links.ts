// Re-export links API from endpoints
import { linksApi } from './endpoints';

const fetchLinks = linksApi.list;
const fetchLink = linksApi.get;
const createLink = linksApi.create;
const updateLink = linksApi.update;
const deleteLink = linksApi.delete;

export { createLink, deleteLink, fetchLink, fetchLinks, updateLink };

const linksApiExports = {
  createLink,
  deleteLink,
  fetchLink,
  fetchLinks,
  updateLink,
};

export default linksApiExports;
