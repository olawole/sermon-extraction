import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import TranscriptViewer from '@/features/transcript/TranscriptViewer';
import type { TranscriptChunk } from '@/types';

const chunks: TranscriptChunk[] = [
  { id: 1, chunk_index: 0, start_seconds: 0, end_seconds: 10, text: 'Hello world', speaker_id: 'Speaker A', confidence: 0.95 },
  { id: 2, chunk_index: 1, start_seconds: 10, end_seconds: 20, text: 'God loves you', speaker_id: null, confidence: 0.9 },
  { id: 3, chunk_index: 2, start_seconds: 3720, end_seconds: 3730, text: 'Final blessing', speaker_id: 'Speaker B', confidence: 0.8 },
];

describe('TranscriptViewer', () => {
  it('renders all transcript chunks', () => {
    render(<TranscriptViewer chunks={chunks} />);
    expect(screen.getByText('Hello world')).toBeInTheDocument();
    expect(screen.getByText('God loves you')).toBeInTheDocument();
    expect(screen.getByText('Final blessing')).toBeInTheDocument();
  });

  it('renders speaker labels when present', () => {
    render(<TranscriptViewer chunks={chunks} />);
    expect(screen.getByText('Speaker A')).toBeInTheDocument();
    expect(screen.getByText('Speaker B')).toBeInTheDocument();
  });

  it('does not render speaker label when speaker_id is null', () => {
    const noSpeaker: TranscriptChunk[] = [
      { id: 1, chunk_index: 0, start_seconds: 0, end_seconds: 5, text: 'No speaker here', speaker_id: null, confidence: null },
    ];
    render(<TranscriptViewer chunks={noSpeaker} />);
    expect(screen.getByText('No speaker here')).toBeInTheDocument();
  });

  it('formats timestamps correctly for sub-hour durations', () => {
    render(<TranscriptViewer chunks={chunks} />);
    expect(screen.getByText('00:00')).toBeInTheDocument();
  });

  it('formats timestamps correctly for over-one-hour durations', () => {
    render(<TranscriptViewer chunks={chunks} />);
    expect(screen.getByText('01:02:00')).toBeInTheDocument();
  });

  it('renders empty container for empty chunk list', () => {
    const { container } = render(<TranscriptViewer chunks={[]} />);
    expect(container.firstChild).toBeInTheDocument();
  });
});
