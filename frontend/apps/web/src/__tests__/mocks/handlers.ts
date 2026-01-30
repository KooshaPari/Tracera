import { HttpResponse, http } from "msw";
import { mockItems, mockLinks, mockProjects } from "./data";

const API_BASE = "http://localhost:8000";

export const handlers = [
	http.get(`${API_BASE}/api/v1/projects`, () => {
		return HttpResponse.json({
			total: mockProjects.length,
			projects: mockProjects,
		});
	}),
	http.get(`${API_BASE}/api/v1/items`, () => {
		return HttpResponse.json({
			total: mockItems.length,
			items: mockItems,
		});
	}),
	http.get(`${API_BASE}/api/v1/links`, () => {
		return HttpResponse.json({
			total: mockLinks.length,
			links: mockLinks,
		});
	}),
];
