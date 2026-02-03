type JourneyMetadata = Record<
	string,
	string | number | boolean | object | null | undefined
>;

interface Journey {
	id: string;
	projectId: string;
	name: string;
	description?: string;
	type: "user" | "system" | "business" | "technical";
	itemIds: string[];
	sequence: number[];
	metadata?: JourneyMetadata;
	detectedAt?: string;
	createdAt: string;
	updatedAt: string;
}

interface JourneyStep {
	itemId: string;
	order: number;
	duration?: number;
	description?: string;
}

interface CreateJourneyInput {
	projectId: string;
	name: string;
	description?: string;
	type: "user" | "system" | "business" | "technical";
	itemIds: string[];
	metadata?: JourneyMetadata;
}

interface UpdateJourneyInput {
	name?: string;
	description?: string;
	type?: "user" | "system" | "business" | "technical";
	itemIds?: string[];
	metadata?: JourneyMetadata;
}

interface DetectJourneysInput {
	projectId: string;
	minLength?: number;
	maxLength?: number;
	types?: ("user" | "system" | "business" | "technical")[];
}

export type {
	CreateJourneyInput,
	DetectJourneysInput,
	Journey,
	JourneyMetadata,
	JourneyStep,
	UpdateJourneyInput,
};
