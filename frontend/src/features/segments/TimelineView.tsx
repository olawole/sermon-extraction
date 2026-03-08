import React from 'react';
import { Tooltip, Typography } from 'antd';
import styled from 'styled-components';
import type { SectionSegment, ServiceSegment, SermonSegment, HighlightClip } from '@/types';
import { fmt } from '@/lib/formatTime';

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
  margin-bottom: 8px;
  gap: 8px;
`;

const TrackBar = styled.div`
  position: relative;
  flex: 1;
  height: 24px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
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
}

const SegmentBlock = styled.div<SegmentBlockProps>`
  position: absolute;
  top: 0;
  bottom: 0;
  left: ${({ left }) => left}%;
  width: ${({ width }) => Math.max(width, 0.3)}%;
  background: ${({ color }) => color};
  opacity: 0.85;
  border-radius: 2px;
`;

interface Props {
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
  totalDuration,
  sectionSegments = [],
  serviceSegments = [],
  sermonSegment,
  highlights = [],
}) => {
  if (totalDuration <= 0) return null;

  return (
    <Wrapper>
      <Text strong style={{ display: 'block', marginBottom: 12 }}>
        Timeline
      </Text>

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

      {serviceSegments.length > 0 && (
        <TrackRow>
          <TrackLabel>Services</TrackLabel>
          <TrackBar>
            {serviceSegments.map((svc) => (
              <Tooltip
                key={svc.id}
                title={`Service ${svc.service_number} · ${fmt(svc.start_seconds)} – ${fmt(svc.end_seconds)}`}
              >
                <SegmentBlock
                  left={toPercent(svc.start_seconds, totalDuration)}
                  width={toPercent(svc.end_seconds - svc.start_seconds, totalDuration)}
                  color={svc.service_number === 1 ? '#adc6ff' : '#b5f5ec'}
                />
              </Tooltip>
            ))}
          </TrackBar>
        </TrackRow>
      )}

      {sermonSegment && (
        <TrackRow>
          <TrackLabel>Sermon</TrackLabel>
          <TrackBar>
            <Tooltip
              title={`Sermon · ${fmt(sermonSegment.start_seconds)} – ${fmt(sermonSegment.end_seconds)}`}
            >
              <SegmentBlock
                left={toPercent(sermonSegment.start_seconds, totalDuration)}
                width={toPercent(sermonSegment.end_seconds - sermonSegment.start_seconds, totalDuration)}
                color="#722ed1"
              />
            </Tooltip>
          </TrackBar>
        </TrackRow>
      )}

      {highlights.length > 0 && (
        <TrackRow>
          <TrackLabel>Highlights</TrackLabel>
          <TrackBar>
            {highlights.map((h) => (
              <Tooltip
                key={h.id}
                title={`${h.title} · ${fmt(h.start_seconds)} – ${fmt(h.end_seconds)} · score ${Math.round(h.score * 100)}%`}
              >
                <SegmentBlock
                  left={toPercent(h.start_seconds, totalDuration)}
                  width={toPercent(h.end_seconds - h.start_seconds, totalDuration)}
                  color="#ff7a45"
                />
              </Tooltip>
            ))}
          </TrackBar>
        </TrackRow>
      )}
    </Wrapper>
  );
};

export default TimelineView;
