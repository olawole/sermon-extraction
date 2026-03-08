import React, { useState } from 'react';
import { Card, Tag, Button, Space, Typography, Progress } from 'antd';
import styled from 'styled-components';
import type { HighlightClip, HighlightStatus } from '@/types';
import { fmt } from '@/lib/formatTime';
import HighlightDetailsDrawer from './HighlightDetailsDrawer';

const { Text } = Typography;

const statusColor: Record<HighlightStatus, string> = {
  pending: 'default',
  approved: 'success',
  rejected: 'error',
  rendered: 'blue',
};

const HookText = styled.div`
  font-style: italic;
  color: #555;
  margin-bottom: 8px;
`;

const TranscriptPreview = styled.div`
  font-size: 12px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

interface Props {
  highlights: HighlightClip[];
  onApprove?: (id: number) => void;
  onReject?: (id: number) => void;
  onRender?: (id: number) => void;
}

const HighlightsList: React.FC<Props> = ({ highlights, onApprove, onReject, onRender }) => {
  const [selected, setSelected] = useState<HighlightClip | null>(null);

  return (
    <>
      {highlights.map((h) => (
        <Card
          key={h.id}
          size="small"
          style={{ marginBottom: 12 }}
          title={
            <Space>
              <Text strong>{h.title}</Text>
              <Tag color={statusColor[h.status]}>{h.status}</Tag>
              <Tag color="geekblue">{h.category}</Tag>
            </Space>
          }
          extra={
            <Space>
              <Button size="small" onClick={() => setSelected(h)}>
                Details
              </Button>
              {h.status === 'pending' && (
                <>
                  <Button
                    size="small"
                    type="primary"
                    onClick={() => onApprove?.(h.id)}
                  >
                    Approve
                  </Button>
                  <Button
                    size="small"
                    danger
                    onClick={() => onReject?.(h.id)}
                  >
                    Reject
                  </Button>
                </>
              )}
              {h.status === 'approved' && (
                <Button
                  size="small"
                  type="dashed"
                  onClick={() => onRender?.(h.id)}
                >
                  Render
                </Button>
              )}
            </Space>
          }
        >
          <Space direction="vertical" style={{ width: '100%' }} size={4}>
            <Space>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {fmt(h.start_seconds)} – {fmt(h.end_seconds)}
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                ({fmt(h.end_seconds - h.start_seconds)})
              </Text>
            </Space>
            <Progress
              percent={Math.round(h.score * 100)}
              size="small"
              format={(p) => `Score: ${p}%`}
            />
            <HookText>"{h.hook_text}"</HookText>
            <TranscriptPreview>{h.transcript}</TranscriptPreview>
          </Space>
        </Card>
      ))}
      {selected && (
        <HighlightDetailsDrawer
          highlight={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
};

export default HighlightsList;
