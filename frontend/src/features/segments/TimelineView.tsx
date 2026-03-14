import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Tooltip, Typography, Button, Space, message } from 'antd';
import { SaveOutlined, UndoOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import type { SectionSegment, ServiceSegment, SermonSegment, HighlightClip } from '@/types';
import { fmt } from '@/lib/formatTime';
import { useUpdateSermonMutation, useUpdateHighlightMutation } from '@/hooks/useJobs';

const { Text } = Typography;

const Wrapper = styled.div`
  padding: 16px 0;
`;

const TrackLabel = styled.div`
  font-size: 12px;
  color: #888;
  width: 80px;
  flex-shrink: 0;
`;

const TrackRow = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
`;

const TrackBar = styled.div`
  position: relative;
  flex: 1;
  height: 32px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: visible; /* Changed to visible to see handles better */
`;

const Handle = styled.div<{ position: 'left' | 'right' }>`
  position: absolute;
  top: -4px;
  bottom: -4px;
  width: 8px;
  background: rgba(0, 0, 0, 0.4);
  cursor: col-resize;
  ${({ position }) => position}: -4px;
  border-radius: 4px;
  z-index: 10;
  transition: background 0.2s;
  &:hover {
    background: rgba(0, 0, 0, 0.7);
  }
`;

const sectionColors: Record<string, string> = {
  praise_worship: '#52c41a',
  prayer: '#1677ff',
  testimony: '#faad14',
  announcements: '#fa8c16',
  sermon: '#722ed1',
  transition: '#bfbfbf',
  other: '#d9d9d9',
};

interface SegmentBlockProps {
  left: number;
  width: number;
  color: string;
  active?: boolean;
}

const SegmentBlock = styled.div<SegmentBlockProps>`
  position: absolute;
  top: 0;
  bottom: 0;
  left: ${({ left }) => left}%;
  width: ${({ width }) => Math.max(width, 0.3)}%;
  background: ${({ color }) => color};
  opacity: ${({ active }) => (active ? 0.95 : 0.75)};
  border-radius: 2px;
  border: ${({ active }) => (active ? '2px solid #333' : 'none')};
  cursor: ${({ active }) => (active ? 'default' : 'pointer')};
  transition: opacity 0.2s;
`;

interface Props {
  jobId: number;
  totalDuration: number;
  sectionSegments?: SectionSegment[];
  serviceSegments?: ServiceSegment[];
  sermonSegment?: SermonSegment | null;
  highlights?: HighlightClip[];
}

function toPercent(seconds: number, total: number): number {
  if (total <= 0) return 0;
  return (seconds / total) * 100;
}

const TimelineView: React.FC<Props> = ({
  jobId,
  totalDuration,
  sectionSegments = [],
  serviceSegments = [],
  sermonSegment,
  highlights = [],
}) => {
  const [selectedHighlightId, setSelectedHighlightId] = useState<number | null>(null);
  
  // Local state for edits
  const [editedSermon, setEditedSermon] = useState<{ start: number; end: number } | null>(null);
  const [editedHighlights, setEditedHighlights] = useState<Record<number, { start: number; end: number }>>({});

  const trackRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef<{ type: 'sermon' | 'highlight'; id?: number; handle: 'left' | 'right' } | null>(null);

  const updateSermonMutation = useUpdateSermonMutation(jobId);
  const updateHighlightMutation = useUpdateHighlightMutation(jobId);

  useEffect(() => {
    if (sermonSegment && !editedSermon) {
      setEditedSermon({ start: sermonSegment.start_seconds, end: sermonSegment.end_seconds });
    }
  }, [sermonSegment]);

  const handleMouseDown = (type: 'sermon' | 'highlight', handle: 'left' | 'right', id?: number) => {
    draggingRef.current = { type, handle, id };
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!draggingRef.current || !trackRef.current) return;

    const rect = trackRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const newSeconds = (x / rect.width) * totalDuration;

    const { type, handle, id } = draggingRef.current;

    if (type === 'sermon') {
      setEditedSermon(prev => {
        if (!prev) return prev;
        if (handle === 'left') {
          return { ...prev, start: Math.min(newSeconds, prev.end - 1) };
        } else {
          return { ...prev, end: Math.max(newSeconds, prev.start + 1) };
        }
      });
    } else if (type === 'highlight' && id !== undefined) {
      setEditedHighlights(prev => {
        const current = prev[id] || highlights.find(h => h.id === id) || { start: 0, end: 0 };
        if (handle === 'left') {
          return { ...prev, [id]: { ...current, start: Math.min(newSeconds, current.end - 1) } };
        } else {
          return { ...prev, [id]: { ...current, end: Math.max(newSeconds, current.start + 1) } };
        }
      });
    }
  }, [totalDuration, highlights]);

  const handleMouseUp = useCallback(() => {
    draggingRef.current = null;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  const saveSermon = () => {
    if (!editedSermon) return;
    updateSermonMutation.mutate(
      { start_seconds: editedSermon.start, end_seconds: editedSermon.end },
      { onSuccess: () => message.success('Sermon boundaries updated') }
    );
  };

  const saveHighlight = (id: number) => {
    const edited = editedHighlights[id];
    if (!edited) return;
    updateHighlightMutation.mutate(
      { highlightId: id, payload: { start_seconds: edited.start, end_seconds: edited.end } },
      { onSuccess: () => message.success('Highlight boundaries updated') }
    );
  };

  if (totalDuration <= 0) return null;

  const currentSermon = editedSermon || (sermonSegment ? { start: sermonSegment.start_seconds, end: sermonSegment.end_seconds } : null);

  return (
    <Wrapper>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <Text strong>Timeline (Drag handles to adjust)</Text>
        <Space>
          {editedSermon && sermonSegment && (editedSermon.start !== sermonSegment.start_seconds || editedSermon.end !== sermonSegment.end_seconds) && (
            <Button 
              size="small" 
              type="primary" 
              icon={<SaveOutlined />} 
              onClick={saveSermon}
              loading={updateSermonMutation.isPending}
            >
              Save Sermon
            </Button>
          )}
        </Space>
      </div>

      {sectionSegments.length > 0 && (
        <TrackRow>
          <TrackLabel>Sections</TrackLabel>
          <TrackBar>
            {sectionSegments.map((seg) => (
              <Tooltip
                key={seg.id}
                title={`${seg.label} · ${fmt(seg.start_seconds)} – ${fmt(seg.end_seconds)}`}
              >
                <SegmentBlock
                  left={toPercent(seg.start_seconds, totalDuration)}
                  width={toPercent(seg.end_seconds - seg.start_seconds, totalDuration)}
                  color={sectionColors[seg.label] ?? '#bfbfbf'}
                />
              </Tooltip>
            ))}
          </TrackBar>
        </TrackRow>
      )}

      {currentSermon && (
        <TrackRow>
          <TrackLabel>Sermon</TrackLabel>
          <TrackBar ref={trackRef}>
            <SegmentBlock
              left={toPercent(currentSermon.start, totalDuration)}
              width={toPercent(currentSermon.end - currentSermon.start, totalDuration)}
              color="#722ed1"
              active
            >
              <Handle position="left" onMouseDown={(e) => { e.stopPropagation(); handleMouseDown('sermon', 'left'); }} />
              <Handle position="right" onMouseDown={(e) => { e.stopPropagation(); handleMouseDown('sermon', 'right'); }} />
              <div style={{ color: 'white', fontSize: '10px', padding: '0 8px', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                {fmt(currentSermon.start)} - {fmt(currentSermon.end)}
              </div>
            </SegmentBlock>
          </TrackBar>
        </TrackRow>
      )}

      {highlights.length > 0 && (
        <TrackRow>
          <TrackLabel>Highlights</TrackLabel>
          <TrackBar>
            {highlights.map((h) => {
              const edited = editedHighlights[h.id];
              const start = edited?.start ?? h.start_seconds;
              const end = edited?.end ?? h.end_seconds;
              const isSelected = selectedHighlightId === h.id;
              const isModified = edited && (edited.start !== h.start_seconds || edited.end !== h.end_seconds);

              return (
                <div key={h.id}>
                  <Tooltip
                    title={`${h.title} · ${fmt(start)} – ${fmt(end)}`}
                    open={isSelected ? false : undefined}
                  >
                    <SegmentBlock
                      left={toPercent(start, totalDuration)}
                      width={toPercent(end - start, totalDuration)}
                      color={isModified ? '#ff4d4f' : '#ff7a45'}
                      active={isSelected}
                      onClick={() => setSelectedHighlightId(h.id)}
                    >
                      {isSelected && (
                        <>
                          <Handle position="left" onMouseDown={(e) => { e.stopPropagation(); handleMouseDown('highlight', 'left', h.id); }} />
                          <Handle position="right" onMouseDown={(e) => { e.stopPropagation(); handleMouseDown('highlight', 'right', h.id); }} />
                        </>
                      )}
                    </SegmentBlock>
                  </Tooltip>
                  {isSelected && isModified && (
                    <div style={{ position: 'absolute', top: 32, left: `${toPercent(start, totalDuration)}%`, zIndex: 20 }}>
                       <Button 
                        size="small" 
                        type="primary" 
                        icon={<SaveOutlined />} 
                        onClick={() => saveHighlight(h.id)}
                        loading={updateHighlightMutation.isPending}
                        style={{ fontSize: '10px', height: '20px' }}
                      >
                        Save
                      </Button>
                    </div>
                  )}
                </div>
              );
            })}
          </TrackBar>
        </TrackRow>
      )}
    </Wrapper>
  );
};

export default TimelineView;
