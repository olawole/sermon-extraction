export type JobStage = 
  | 'pending' | 'downloading' | 'audio_extracted' 
  | 'transcribing' | 'transcribed' | 'classifying' | 'classified'
  | 'detecting_services' | 'services_detected'
  | 'detecting_sermon' | 'sermon_detected'
  | 'exporting_sermon' | 'sermon_exported'
  | 'generating_highlights' | 'highlights_generated' | 'completed' | 'failed';

export type AssetType = 
  | 'source_video' | 'source_audio' | 'sermon_video' | 'sermon_audio'
  | 'transcript_txt' | 'subtitle_srt' | 'subtitle_vtt' | 'highlight_clip';

export type SectionLabel = 
  | 'praise_worship' | 'prayer' | 'testimony' | 'announcements' 
  | 'sermon' | 'transition' | 'other';

export type HighlightStatus = 'pending' | 'approved' | 'rejected' | 'rendered';

export interface Job {
  id: number;
  youtube_url: string;
  title: string | null;
  duration_seconds: number | null;
  stage: JobStage;
  progress?: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface TranscriptChunk {
  id: number;
  chunk_index: number;
  start_seconds: number;
  end_seconds: number;
  text: string;
  speaker_id: string | null;
  confidence: number | null;
}

export interface SectionSegment {
  id: number;
  label: SectionLabel;
  start_seconds: number;
  end_seconds: number;
  confidence: number | null;
  dominant_speaker: string | null;
}

export interface ServiceSegment {
  id: number;
  service_number: number;
  start_seconds: number;
  end_seconds: number;
  confidence: number | null;
}

export interface SermonSegment {
  id: number;
  service_number: number;
  start_seconds: number;
  end_seconds: number;
  dominant_speaker: string | null;
  confidence: number | null;
  approved: boolean;
}

export interface HighlightClip {
  id: number;
  start_seconds: number;
  end_seconds: number;
  score: number;
  category: string;
  title: string;
  hook_text: string;
  transcript: string;
  reasons: string[];
  social_caption: string | null;
  hashtags: string | null;
  status: HighlightStatus;
}

export interface MediaAsset {
  id: number;
  job_id: number;
  asset_type: AssetType;
  file_path: string;
  file_name: string;
  format: string | null;
  size_bytes: number | null;
  duration_seconds: number | null;
}

export interface TranscriptResponse {
  job_id: number;
  chunks: TranscriptChunk[];
}

export interface SegmentsResponse {
  job_id: number;
  section_segments: SectionSegment[];
  service_segments: ServiceSegment[];
  sermon_segment: SermonSegment | null;
}

export interface HighlightsResponse {
  job_id: number;
  highlights: HighlightClip[];
}

export interface AssetListResponse {
  job_id: number;
  assets: MediaAsset[];
}

export interface UpdateSermonRequest {
  start_seconds: number;
  end_seconds: number;
}

export interface UpdateHighlightRequest {
  start_seconds: number;
  end_seconds: number;
}
