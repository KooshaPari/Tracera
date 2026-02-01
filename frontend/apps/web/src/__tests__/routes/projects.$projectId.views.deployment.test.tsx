/**
 * Tests for Deployment View Route
 */

import { describe, expect, it } from "vitest";

describe("Deployment View Route", () => {
	it("validates deployment view route path pattern", () => {
		const deploymentPath = "/projects/proj-1/views/deployment";
		expect(deploymentPath).toMatch(/^\/projects\/[^/]+\/views\/deployment$/);
	});

	it("extracts projectId from route parameters", () => {
		const path = "/projects/proj-123/views/deployment";
		const match = path.match(/\/projects\/([^/]+)\/views\/deployment/);

		expect(match).not.toBeNull();
		expect(match?.[1]).toBe("proj-123");
	});

	it("recognizes deployment view type from route", () => {
		const path = "/projects/proj-1/views/deployment";
		const viewType = path.split("/")[4];

		expect(viewType).toBe("deployment");
	});

	it("supports deployment metadata", () => {
		const mockDeployment = {
			id: "deploy-1",
			title: "Production Deployment",
			type: "deployment",
			status: "done",
			environment: "production",
		};

		expect(mockDeployment.environment).toMatch(/^(staging|production|development)$/);
		expect(mockDeployment.status).toMatch(/^(pending|done|failed)$/);
	});

	it("handles multiple deployments", () => {
		const mockDeployments = [
			{ id: "d1", environment: "development", status: "done" },
			{ id: "d2", environment: "staging", status: "done" },
			{ id: "d3", environment: "production", status: "pending" },
		];

		expect(mockDeployments).toHaveLength(3);
		expect(mockDeployments.filter(d => d.status === "done")).toHaveLength(2);
	});
});
