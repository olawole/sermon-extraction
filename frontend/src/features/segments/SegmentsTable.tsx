import React from 'react';
import { Table, Tag } from 'antd';
import type { SectionSegment, SectionLabel } from '@/types';
import { fmt } from '@/lib/formatTime';

const labelColor: Record<SectionLabel, string> = {
  praise_worship: 'purple',
  prayer: 'blue',
  testimony: 'cyan',
  announcements: 'orange',
  sermon: 'green',
  transition: 'default',
  other: 'default',
};

const columns = [
  {
    title: 'Label',
    dataIndex: 'label',
    key: 'label',
    render: (label: SectionLabel) => (
      <Tag color={labelColor[label]}>{label.replace(/_/g, ' ')}</Tag>
    ),
  },
  {
    title: 'Start',
    dataIndex: 'start_seconds',
    key: 'start',
    render: (v: number) => fmt(v),
  },
  {
    title: 'End',
    dataIndex: 'end_seconds',
    key: 'end',
    render: (v: number) => fmt(v),
  },
  {
    title: 'Duration',
    key: 'duration',
    render: (_: unknown, row: SectionSegment) =>
      fmt(row.end_seconds - row.start_seconds),
  },
  {
    title: 'Confidence',
    dataIndex: 'confidence',
    key: 'confidence',
    render: (v: number | null) => (v != null ? `${(v * 100).toFixed(1)}%` : '—'),
  },
  {
    title: 'Dominant Speaker',
    dataIndex: 'dominant_speaker',
    key: 'speaker',
    render: (v: string | null) => v ?? '—',
  },
];

const SegmentsTable: React.FC<{ segments: SectionSegment[] }> = ({ segments }) => (
  <Table
    dataSource={segments}
    columns={columns}
    rowKey="id"
    size="small"
    pagination={{ pageSize: 20 }}
    scroll={{ x: true }}
  />
);

export default SegmentsTable;
