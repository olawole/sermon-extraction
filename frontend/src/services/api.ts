import axios from 'axios';
import type {
  Job,
  TranscriptResponse,
  SegmentsResponse,
  HighlightsResponse,
  AssetListResponse,
} from '@/types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const client = axios.create({ baseURL: BASE_URL });

export const createJob = async (youtube_url: string): Promise<Job> => {
  const { data } = await client.post<Job>('/jobs/', { youtube_url });
  return data;
};

export const getJob = async (id: number): Promise<Job> => {
  const { data } = await client.get<Job>(`/jobs/${id}`);
  return data;
};

export const listJobs = async (): Promise<Job[]> => {
  const { data } = await client.get<Job[]>('/jobs/');
  return data;
};

export const getTranscript = async (id: number): Promise<TranscriptResponse> => {
  const { data } = await client.get<TranscriptResponse>(`/jobs/${id}/transcript`);
  return data;
};

export const getSegments = async (id: number): Promise<SegmentsResponse> => {
  const { data } = await client.get<SegmentsResponse>(`/jobs/${id}/segments`);
  return data;
};

export const getHighlights = async (id: number): Promise<HighlightsResponse> => {
  const { data } = await client.get<HighlightsResponse>(`/jobs/${id}/highlights`);
  return data;
};

export const getAssets = async (id: number): Promise<AssetListResponse> => {
  const { data } = await client.get<AssetListResponse>(`/jobs/${id}/assets`);
  return data;
};

export const approveHighlight = async (jobId: number, highlightId: number): Promise<void> => {
  await client.post(`/jobs/${jobId}/highlights/${highlightId}/approve`);
};

export const rejectHighlight = async (jobId: number, highlightId: number): Promise<void> => {
  await client.post(`/jobs/${jobId}/highlights/${highlightId}/reject`);
};

export const renderHighlight = async (jobId: number, highlightId: number): Promise<void> => {
  await client.post(`/jobs/${jobId}/highlights/${highlightId}/render`);
};

export const renderAllHighlights = async (jobId: number): Promise<void> => {
  await client.post(`/jobs/${jobId}/render-all`);
};

export const reprocessJob = async (jobId: number): Promise<Job> => {
  const { data } = await client.post<Job>(`/jobs/${jobId}/reprocess`);
  return data;
};
