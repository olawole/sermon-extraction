import React from 'react';
import { List, Button, Tag, Space, Typography } from 'antd';
import {
  DownloadOutlined,
  FileTextOutlined,
  VideoCameraOutlined,
  SoundOutlined,
} from '@ant-design/icons';
import type { MediaAsset, AssetType } from '@/types';
import { fmt } from '@/lib/formatTime';

const { Text } = Typography;

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const assetIcon: Record<AssetType, React.ReactNode> = {
  source_video: <VideoCameraOutlined />,
  source_audio: <SoundOutlined />,
  sermon_video: <VideoCameraOutlined />,
  sermon_audio: <SoundOutlined />,
  transcript_txt: <FileTextOutlined />,
  subtitle_srt: <FileTextOutlined />,
  subtitle_vtt: <FileTextOutlined />,
  highlight_clip: <VideoCameraOutlined />,
};

const assetColor: Record<AssetType, string> = {
  source_video: 'default',
  source_audio: 'default',
  sermon_video: 'blue',
  sermon_audio: 'blue',
  transcript_txt: 'green',
  subtitle_srt: 'green',
  subtitle_vtt: 'green',
  highlight_clip: 'purple',
};

function formatBytes(b: number) {
  if (b < 1024) return `${b} B`;
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  if (b < 1024 * 1024 * 1024) return `${(b / (1024 * 1024)).toFixed(1)} MB`;
  return `${(b / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

const AssetListPanel: React.FC<{ assets: MediaAsset[] }> = ({ assets }) => (
  <List
    dataSource={assets}
    rowKey="id"
    renderItem={(asset) => (
      <List.Item
        actions={[
          <Button
            key="dl"
            icon={<DownloadOutlined />}
            size="small"
            href={`${BASE_URL}/files/${encodeURIComponent(asset.file_name)}`}
            target="_blank"
            rel="noreferrer"
          >
            Download
          </Button>,
        ]}
      >
        <List.Item.Meta
          avatar={assetIcon[asset.asset_type]}
          title={
            <Space>
              <Text>{asset.file_name}</Text>
              <Tag color={assetColor[asset.asset_type]}>
                {asset.asset_type.replace(/_/g, ' ')}
              </Tag>
              {asset.format && <Tag>{asset.format}</Tag>}
            </Space>
          }
          description={
            <Space>
              {asset.size_bytes != null && (
                <Text type="secondary">{formatBytes(asset.size_bytes)}</Text>
              )}
              {asset.duration_seconds != null && (
                <Text type="secondary">{fmt(asset.duration_seconds)}</Text>
              )}
            </Space>
          }
        />
      </List.Item>
    )}
  />
);

export default AssetListPanel;
