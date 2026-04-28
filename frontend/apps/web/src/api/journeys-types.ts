type JourneyMetadata = Record<string, string | number | boolean | object | null | undefined>;

interface Journey {
  id: string;
  projectId: string;
  name: string;
  description?: string | undefined;
  type: 'user' | 'system' | 'business' | 'technical';
  itemIds: string[];
  sequence: number[];
  metadata?: JourneyMetadata | undefined;
  detectedAt?: string | undefined;
  createdAt: string;
  updatedAt: string;
}

interface JourneyStep {
  itemId: string;
  order: number;
  duration?: number | undefined;
  description?: string | undefined;
}

interface CreateJourneyInput {
  projectId: string;
  name: string;
  description?: string | undefined;
  type: 'user' | 'system' | 'business' | 'technical';
  itemIds: string[];
  metadata?: JourneyMetadata | undefined;
}

interface UpdateJourneyInput {
  name?: string | undefined;
  description?: string | undefined;
  type?: 'user' | 'system' | 'business' | 'technical' | undefined;
  itemIds?: string[] | undefined;
  metadata?: JourneyMetadata | undefined;
}

interface DetectJourneysInput {
  projectId: string;
  minLength?: number | undefined;
  maxLength?: number | undefined;
  types?: ('user' | 'system' | 'business' | 'technical')[] | undefined;
}

export type {
  CreateJourneyInput,
  DetectJourneysInput,
  Journey,
  JourneyMetadata,
  JourneyStep,
  UpdateJourneyInput,
};
