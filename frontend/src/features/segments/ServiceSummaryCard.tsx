import React from 'react';
import { Card, Descriptions, Tag } from 'antd';
import type { ServiceSegment } from '@/types';
import { fmt } from '@/lib/formatTime';

const ServiceSummaryCard: React.FC<{ services: ServiceSegment[] }> = ({ services }) => (
  <Card title="Detected Services" style={{ marginBottom: 16 }}>
    {services.map((svc) => (
      <Descriptions
        key={svc.id}
        bordered
        size="small"
        column={2}
        style={{ marginBottom: 12 }}
        title={
          <Tag color={svc.service_number === 2 ? 'blue' : 'default'}>
            Service {svc.service_number}
          </Tag>
        }
      >
        <Descriptions.Item label="Start">{fmt(svc.start_seconds)}</Descriptions.Item>
        <Descriptions.Item label="End">{fmt(svc.end_seconds)}</Descriptions.Item>
        <Descriptions.Item label="Duration">
          {fmt(svc.end_seconds - svc.start_seconds)}
        </Descriptions.Item>
        {svc.confidence != null && (
          <Descriptions.Item label="Confidence">
            {(svc.confidence * 100).toFixed(1)}%
          </Descriptions.Item>
        )}
      </Descriptions>
    ))}
  </Card>
);

export default ServiceSummaryCard;
