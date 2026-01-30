import { describe, it, expect, beforeEach, vi } from "vitest";
import {
	journeyQueryKeys,
	type Journey,
	type JourneyStep,
	type CreateJourneyInput,
	type UpdateJourneyInput,
	type DetectJourneysInput,
} from "../../api/journeys";

describe("journey API hooks", () => {
	describe("queryKeys", () => {
		it("should generate correct query key for all journeys", () => {
			const key = journeyQueryKeys.all;
			expect(key).toEqual(["journeys"]);
		});

		it("should generate correct query key for list with projectId and type", () => {
			const key = journeyQueryKeys.list("project-1", "user");
			expect(key).toEqual(["journeys", "list", "project-1", "user"]);
		});

		it("should generate correct query key for list with projectId only", () => {
			const key = journeyQueryKeys.list("project-1");
			expect(key).toEqual(["journeys", "list", "project-1", undefined]);
		});

		it("should generate correct query key for detail", () => {
			const key = journeyQueryKeys.detail("journey-1");
			expect(key).toEqual(["journeys", "detail", "journey-1"]);
		});

		it("should generate correct query key for steps", () => {
			const key = journeyQueryKeys.steps("journey-1");
			expect(key).toEqual(["journeys", "steps", "journey-1"]);
		});
	});

	describe("Journey type", () => {
		it("should validate journey structure", () => {
			const journey: Journey = {
				id: "journey-1",
				projectId: "project-1",
				name: "User Onboarding",
				description: "New user signup and setup flow",
				type: "user",
				itemIds: ["item-1", "item-2", "item-3"],
				sequence: [0, 1, 2],
				metadata: { personas: ["newUser"] },
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-02T00:00:00Z",
			};

			expect(journey.id).toBeDefined();
			expect(journey.projectId).toBeDefined();
			expect(journey.name).toBeDefined();
			expect(["user", "system", "business", "technical"]).toContain(
				journey.type,
			);
			expect(journey.itemIds).toHaveLength(3);
			expect(journey.sequence).toHaveLength(3);
		});

		it("should allow optional detectedAt field", () => {
			const journey: Journey = {
				id: "journey-1",
				projectId: "project-1",
				name: "System Flow",
				type: "system",
				itemIds: ["item-1"],
				sequence: [0],
				detectedAt: "2024-01-01T00:00:00Z",
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			expect(journey.detectedAt).toBeDefined();
		});
	});

	describe("JourneyStep type", () => {
		it("should validate journey step structure", () => {
			const step: JourneyStep = {
				itemId: "item-1",
				order: 0,
				duration: 300,
				description: "First step",
			};

			expect(step.itemId).toBeDefined();
			expect(step.order).toBeGreaterThanOrEqual(0);
		});

		it("should allow optional duration and description", () => {
			const step: JourneyStep = {
				itemId: "item-1",
				order: 0,
			};

			expect(step.duration).toBeUndefined();
			expect(step.description).toBeUndefined();
		});
	});

	describe("Input types", () => {
		it("should validate CreateJourneyInput", () => {
			const input: CreateJourneyInput = {
				projectId: "project-1",
				name: "New Journey",
				description: "A new journey",
				type: "business",
				itemIds: ["item-1", "item-2"],
				metadata: { owner: "team-a" },
			};

			expect(input.projectId).toBeDefined();
			expect(input.name).toBeDefined();
			expect(input.type).toBeDefined();
			expect(input.itemIds).toBeDefined();
		});

		it("should validate UpdateJourneyInput", () => {
			const input: UpdateJourneyInput = {
				name: "Updated Journey",
				itemIds: ["item-1", "item-2", "item-3"],
			};

			expect(input.name).toBeDefined();
		});

		it("should validate DetectJourneysInput", () => {
			const input: DetectJourneysInput = {
				projectId: "project-1",
				minLength: 2,
				maxLength: 10,
				types: ["user", "system"],
			};

			expect(input.projectId).toBeDefined();
		});
	});

	describe("Journey types validation", () => {
		it("should accept all valid journey types", () => {
			const validTypes: Array<"user" | "system" | "business" | "technical"> = [
				"user",
				"system",
				"business",
				"technical",
			];

			validTypes.forEach((type) => {
				const journey: Journey = {
					id: "journey-1",
					projectId: "project-1",
					name: "Test",
					type: type,
					itemIds: [],
					sequence: [],
					createdAt: "2024-01-01T00:00:00Z",
					updatedAt: "2024-01-01T00:00:00Z",
				};

				expect(journey.type).toBe(type);
			});
		});
	});

	describe("Query key hierarchies", () => {
		it("should create consistent list query keys", () => {
			const key1 = journeyQueryKeys.list("project-1", "user");
			const key2 = journeyQueryKeys.list("project-1", "system");

			expect(key1).not.toEqual(key2);
			expect(key1.slice(0, 2)).toEqual(key2.slice(0, 2)); // Same prefix
		});

		it("should create consistent detail and steps keys", () => {
			const detailKey = journeyQueryKeys.detail("journey-1");
			const stepsKey = journeyQueryKeys.steps("journey-1");

			expect(detailKey).not.toEqual(stepsKey);
			expect(detailKey[2]).toEqual(stepsKey[2]); // Same journey ID
		});
	});
});
