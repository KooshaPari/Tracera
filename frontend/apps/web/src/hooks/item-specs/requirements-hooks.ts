import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  RequirementSpecCreate,
  RequirementSpecUpdate,
  RequirementType,
  RiskLevel,
  VerificationStatus,
} from './types';

import { itemSpecKeys } from './keys';
import {
  analyzeRequirementImpact,
  analyzeRequirementQuality,
  createRequirementSpec,
  deleteRequirementSpec,
  fetchHighRiskRequirements,
  fetchRequirementSpec,
  fetchRequirementSpecByItem,
  fetchRequirementSpecs,
  fetchUnverifiedRequirements,
  updateRequirementSpec,
  verifyRequirement,
} from './requirements-api';

function useRequirementSpecs(
  projectId: string,
  options?: {
    requirementType?: RequirementType;
    riskLevel?: RiskLevel;
    verificationStatus?: VerificationStatus;
    limit?: number;
    offset?: number;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchRequirementSpecs(projectId, options);
      return data;
    },
    queryKey: [...itemSpecKeys.requirements(projectId), options],
  });
}

function useRequirementSpec(projectId: string, specId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(specId),
    queryFn: async () => {
      const data = await fetchRequirementSpec(projectId, specId);
      return data;
    },
    queryKey: itemSpecKeys.requirement(projectId, specId),
  });
}

function useRequirementSpecByItem(projectId: string, itemId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(itemId),
    queryFn: async () => {
      const data = await fetchRequirementSpecByItem(projectId, itemId);
      return data;
    },
    queryKey: itemSpecKeys.requirementByItem(projectId, itemId),
  });
}

function useUnverifiedRequirements(projectId: string, limit?: number) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchUnverifiedRequirements(projectId, limit);
      return data;
    },
    queryKey: itemSpecKeys.unverifiedRequirements(projectId),
  });
}

function useHighRiskRequirements(projectId: string, limit?: number) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchHighRiskRequirements(projectId, limit);
      return data;
    },
    queryKey: itemSpecKeys.highRiskRequirements(projectId),
  });
}

function useCreateRequirementSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: RequirementSpecCreate) => {
      const result = await createRequirementSpec(projectId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.requirement(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.requirements(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.unverifiedRequirements(projectId),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.highRiskRequirements(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useUpdateRequirementSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, data }: { specId: string; data: RequirementSpecUpdate }) => {
      const result = await updateRequirementSpec(projectId, specId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.requirement(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.requirements(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.unverifiedRequirements(projectId),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.highRiskRequirements(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useDeleteRequirementSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      await deleteRequirementSpec(projectId, specId);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.requirements(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.unverifiedRequirements(projectId),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.highRiskRequirements(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useAnalyzeRequirementQuality(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      const result = await analyzeRequirementQuality(projectId, specId);
      return result;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(itemSpecKeys.requirement(projectId, data['id']), data);
    },
  });
}

function useAnalyzeRequirementImpact(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      const result = await analyzeRequirementImpact(projectId, specId);
      return result;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(itemSpecKeys.requirement(projectId, data['id']), data);
    },
  });
}

function useVerifyRequirement(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      specId,
      evidenceType,
      evidenceReference,
      description,
    }: {
      specId: string;
      evidenceType: string;
      evidenceReference: string;
      description: string;
    }) => {
      const result = await verifyRequirement(
        projectId,
        specId,
        evidenceType,
        evidenceReference,
        description,
      );
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.requirement(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.requirements(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.unverifiedRequirements(projectId),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.highRiskRequirements(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

export {
  useRequirementSpecs,
  useRequirementSpec,
  useRequirementSpecByItem,
  useUnverifiedRequirements,
  useHighRiskRequirements,
  useCreateRequirementSpec,
  useUpdateRequirementSpec,
  useDeleteRequirementSpec,
  useAnalyzeRequirementQuality,
  useAnalyzeRequirementImpact,
  useVerifyRequirement,
};
