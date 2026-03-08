import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as api from '@/services/api';

export const useJobsQuery = () =>
  useQuery({ queryKey: ['jobs'], queryFn: api.listJobs });

export const useJobQuery = (id: number) =>
  useQuery({
    queryKey: ['job', id],
    queryFn: () => api.getJob(id),
    refetchInterval: (query) => {
      const stage = query.state.data?.stage;
      if (!stage || stage === 'completed' || stage === 'failed') return false;
      return 3000;
    },
  });

export const useTranscriptQuery = (id: number) =>
  useQuery({ queryKey: ['transcript', id], queryFn: () => api.getTranscript(id) });

export const useSegmentsQuery = (id: number) =>
  useQuery({ queryKey: ['segments', id], queryFn: () => api.getSegments(id) });

export const useHighlightsQuery = (id: number) =>
  useQuery({ queryKey: ['highlights', id], queryFn: () => api.getHighlights(id) });

export const useAssetsQuery = (id: number) =>
  useQuery({ queryKey: ['assets', id], queryFn: () => api.getAssets(id) });

export const useCreateJobMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (url: string) => api.createJob(url),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  });
};

export const useApproveHighlightMutation = (jobId: number) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (highlightId: number) => api.approveHighlight(jobId, highlightId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['highlights', jobId] }),
  });
};

export const useRejectHighlightMutation = (jobId: number) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (highlightId: number) => api.rejectHighlight(jobId, highlightId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['highlights', jobId] }),
  });
};
