import React from 'react';
import styled from 'styled-components';
import type { TranscriptChunk } from '@/types';

const Container = styled.div`
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
`;

const ChunkRow = styled.div`
  display: flex;
  gap: 12px;
  padding: 6px 4px;
  border-bottom: 1px solid #f9f9f9;
  &:last-child { border-bottom: none; }
`;

const Timestamp = styled.span`
  color: #1677ff;
  font-size: 12px;
  min-width: 64px;
  font-family: monospace;
`;

const Speaker = styled.span`
  background: #e6f4ff;
  color: #0958d9;
  border-radius: 4px;
  padding: 0 6px;
  font-size: 11px;
`;

const Text = styled.span`
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
`;

function fmt(s: number) {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  return h > 0
    ? `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
    : `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
}

const TranscriptViewer: React.FC<{ chunks: TranscriptChunk[] }> = ({ chunks }) => (
  <Container>
    {chunks.map((c) => (
      <ChunkRow key={c.id}>
        <Timestamp>{fmt(c.start_seconds)}</Timestamp>
        {c.speaker_id && <Speaker>{c.speaker_id}</Speaker>}
        <Text>{c.text}</Text>
      </ChunkRow>
    ))}
  </Container>
);

export default TranscriptViewer;
