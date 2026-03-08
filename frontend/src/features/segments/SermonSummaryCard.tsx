import React from 'react';
import { Card, Descriptions, Tag } from 'antd';
import type { SermonSegment } from '@/types';
import { fmt } from '@/lib/formatTime';

const SermonSummaryCard: React.FC<{ sermon: SermonSegment }> = ({ sermon }) => (
  <Card title="Detected Sermon" style={{ marginBottom: 16 }}>
    <Descriptions bordered size="small" column={2}>
      <Descriptions.Item label="Start">{fmt(sermon.start_seconds)}</Descriptions.Item>
      <Descriptions.Item label="End">{fmt(sermon.end_seconds)}</Descriptions.Item>
      <Descriptions.Item label="Duration">
        {fmt(sermon.end_seconds - sermon.start_seconds)}
      </Descriptions.Item>
      <Descriptions.Item label="Service">
        <Tag color="blue">Service {sermon.service_number}</Tag>
      </Descriptions.Item>
      {sermon.dominant_speaker && (
        <Descriptions.Item label="Dominant Speaker">{sermon.dominant_speaker}</Descriptions.Item>
      )}
      {sermon.confidence != null && (
        <Descriptions.Item label="Confidence">
          {(sermon.confidence * 100).toFixed(1)}%
        </Descriptions.Item>
      )}
      <Descriptions.Item label="Approved">
        <Tag color={sermon.approved ? 'green' : 'orange'}>
          {sermon.approved ? 'Approved' : 'Pending'}
        </Tag>
      </Descriptions.Item>
    </Descriptions>
  </Card>
);

export default SermonSummaryCard;
