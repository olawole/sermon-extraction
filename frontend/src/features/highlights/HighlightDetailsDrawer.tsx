import React from 'react';
import { Drawer, Descriptions, Tag, Typography, List, Progress, Space } from 'antd';
import type { HighlightClip, HighlightStatus } from '@/types';
import { fmt } from '@/lib/formatTime';

const { Text, Paragraph } = Typography;

const statusColor: Record<HighlightStatus, string> = {
  pending: 'default',
  approved: 'success',
  rejected: 'error',
  rendered: 'blue',
};

interface Props {
  highlight: HighlightClip;
  onClose: () => void;
}

const HighlightDetailsDrawer: React.FC<Props> = ({ highlight: h, onClose }) => (
  <Drawer
    title={h.title}
    open={true}
    onClose={onClose}
    width={480}
  >
    <Space direction="vertical" style={{ width: '100%' }} size={16}>
      <Descriptions bordered size="small" column={1}>
        <Descriptions.Item label="Status">
          <Tag color={statusColor[h.status]}>{h.status}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Category">
          <Tag color="geekblue">{h.category}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Start">{fmt(h.start_seconds)}</Descriptions.Item>
        <Descriptions.Item label="End">{fmt(h.end_seconds)}</Descriptions.Item>
        <Descriptions.Item label="Duration">
          {fmt(h.end_seconds - h.start_seconds)}
        </Descriptions.Item>
        <Descriptions.Item label="Score">
          <Progress
            percent={Math.round(h.score * 100)}
            size="small"
            style={{ margin: 0 }}
          />
        </Descriptions.Item>
      </Descriptions>

      <div>
        <Text strong>Hook</Text>
        <Paragraph italic style={{ marginTop: 4 }}>"{h.hook_text}"</Paragraph>
      </div>

      <div>
        <Text strong>Transcript</Text>
        <Paragraph style={{ marginTop: 4, fontSize: 13 }}>{h.transcript}</Paragraph>
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

export default HighlightDetailsDrawer;
