// Re-export links API from endpoints
import { linksApi } from "./endpoints";

export const fetchLinks = linksApi.list;
export const fetchLink = linksApi.get;
export const createLink = linksApi.create;
export const updateLink = linksApi.update;
export const deleteLink = linksApi.delete;
