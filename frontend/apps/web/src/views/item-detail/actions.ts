import { toast } from 'sonner';

function reportDeleteFailure(): void {
  toast.error('Failed to delete item');
}

function reportSaveFailure(): void {
  toast.error('Failed to update item');
}

function reportNoRelationships(): void {
  toast.info('No relationships to analyze');
}

function reportAnalysisComplete(total: number): void {
  toast.success(`Analyzed ${String(total)} relationships`);
}

function reportNoImpact(): void {
  toast.info('No impact relationships detected');
}

function reportImpactComplete(count: number): void {
  toast.success(`Impact analysis: ${String(count)} affected items`);
}

export {
  reportAnalysisComplete,
  reportDeleteFailure,
  reportImpactComplete,
  reportNoImpact,
  reportNoRelationships,
  reportSaveFailure,
};
