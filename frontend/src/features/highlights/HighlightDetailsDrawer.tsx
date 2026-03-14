import React, { useRef, useState } from 'react';
import { Drawer, Descriptions, Tag, Typography, List, Progress, Space, Divider } from 'antd';
import styled from 'styled-components';
import type { HighlightClip, HighlightStatus } from '@/types';
import { fmt } from '@/lib/formatTime';
import { useAssetsQuery, useTranscriptQuery } from '@/hooks/useJobs';

const { Text, Paragraph, Title } = Typography;

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const statusColor: Record<HighlightStatus, string> = {
  pending: 'default',
  approved: 'success',
  rejected: 'error',
  rendered: 'blue',
};

const TranscriptContainer = styled.div`
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
`;

const Sentence = styled.span<{ $active: boolean }>`
  background-color: ${props => props.$active ? '#fffbe6' : 'transparent'};
  border-bottom: ${props => props.$active ? '2px solid #ffe58f' : 'none'};
  padding: 2px 0;
  transition: all 0.2s;
  cursor: pointer;
  
  &:hover {
    background-color: #f0f0f0;
  }
`;

interface Props {
  jobId: number;
  highlight: HighlightClip;
  onClose: () => void;
}

const HighlightDetailsDrawer: React.FC<Props> = ({ jobId, highlight: h, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [currentTime, setCurrentTime] = useState(0);
  
  const { data: assetsData } = useAssetsQuery(jobId);
  const { data: transcriptData } = useTranscriptQuery(jobId);

  const assets = assetsData?.assets || [];
  const sourceVideo = assets.find((a) => a.asset_type === 'source_video');
  const videoUrl = sourceVideo 
    ? `${BASE_URL}/jobs/${jobId}/assets/${sourceVideo.id}/download`
    : null;

  const chunks = transcriptData?.chunks.filter(
    c => c.start_seconds >= h.start_seconds && c.end_seconds <= h.end_seconds
  ) || [];

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const seekTo = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
  };

  return (
    <Drawer
      title={h.title}
      open={true}
      onClose={onClose}
      width={600}
    >
      <Space direction="vertical" style={{ width: '100%' }} size={16}>
        {videoUrl && (
          <div style={{ width: '100%', background: '#000', borderRadius: 8, overflow: 'hidden' }}>
            <video
              ref={videoRef}
              src={`${videoUrl}#t=${h.start_seconds}`}
              controls
              style={{ width: '100%', maxHeight: '340px' }}
              onTimeUpdate={handleTimeUpdate}
            />
          </div>
        )}

        <Descriptions bordered size="small" column={2}>
          <Descriptions.Item label="Status">
            <Tag color={statusColor[h.status]}>{h.status}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Category">
            <Tag color="geekblue">{h.category}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Start">{fmt(h.start_seconds)}</Descriptions.Item>
          <Descriptions.Item label="End">{fmt(h.end_seconds)}</Descriptions.Item>
          <Descriptions.Item label="Score" span={2}>
            <Progress
              percent={Math.round(h.score * 100)}
              size="small"
              style={{ margin: 0 }}
            />
          </Descriptions.Item>
        </Descriptions>

        <div>
          <Text strong>Interactive Transcript</Text>
          <TranscriptContainer>
            {chunks.length > 0 ? (
              chunks.map((chunk, idx) => (
                <Sentence
                  key={chunk.id || idx}
                  $active={currentTime >= chunk.start_seconds && currentTime <= chunk.end_seconds}
                  onClick={() => seekTo(chunk.start_seconds)}
                >
                  {chunk.text}{' '}
                </Sentence>
              ))
            ) : (
              <Paragraph type="secondary">{h.transcript}</Paragraph>
            )}
          </TranscriptContainer>
        </div>

        {(h.social_caption || h.hashtags) && (
          <>
            <Divider style={{ margin: '8px 0' }} />
            <div>
              <Title level={5}>Social Content</Title>
              {h.social_caption && (
                <div style={{ marginBottom: 12 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>CAPTION</Text>
                  <Paragraph style={{ background: '#f9f9f9', padding: 8, borderRadius: 4 }}>
                    {h.social_caption}
                  </Paragraph>
                </div>
              )}
              {h.hashtags && (
                <div>
                  <Text type="secondary" style={{ fontSize: 12 }}>HASHTAGS</Text>
                  <Paragraph style={{ color: '#1890ff' }}>
                    {h.hashtags}
                  </Paragraph>
                </div>
              )}
            </div>
          </>
        )}

        <Divider style={{ margin: '8px 0' }} />
        
        <div>
          <Text strong>Hook</Text>
          <Paragraph italic style={{ marginTop: 4 }}>"{h.hook_text}"</Paragraph>
        </div>

        <div>
          <Text strong>Scoring Reasons</Text>
          <List
            size="small"
            dataSource={h.reasons}
            renderItem={(reason) => <List.Item>• {reason}</List.Item>}
            style={{ marginTop: 4 }}
          />
        </div>
      </Space>
    </Drawer>
  );
};

export default HighlightDetailsDrawer;
