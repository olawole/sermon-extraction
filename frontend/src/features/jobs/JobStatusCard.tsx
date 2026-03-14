import React from 'react';
import { Card, Descriptions, Tag, Alert, Steps, Collapse, Typography, Button, Progress } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import type { Job, JobStage } from '@/types';
import { useRetryJobMutation } from '@/hooks/useJobs';

const { Panel } = Collapse;
const { Paragraph, Text } = Typography;

const stageColor: Record<JobStage, string> = {
  pending: 'default', downloading: 'processing', audio_extracted: 'processing',
  transcribing: 'processing', transcribed: 'processing', classifying: 'processing',
  classified: 'processing', detecting_services: 'processing', services_detected: 'processing',
  detecting_sermon: 'processing', sermon_detected: 'processing', exporting_sermon: 'processing',
  sermon_exported: 'processing', generating_highlights: 'processing',
  highlights_generated: 'processing', completed: 'success', failed: 'error',
};

const pipelineSteps = [
  { title: 'Download', stages: ['downloading', 'audio_extracted'] },
  { title: 'Transcribe', stages: ['transcribing', 'transcribed'] },
  { title: 'Classify', stages: ['classifying', 'classified'] },
  { title: 'Detect', stages: ['detecting_services', 'services_detected', 'detecting_sermon', 'sermon_detected'] },
  { title: 'Export', stages: ['exporting_sermon', 'sermon_exported'] },
  { title: 'Highlights', stages: ['generating_highlights', 'highlights_generated', 'completed'] },
];

function getCurrentStep(stage: JobStage): number {
  for (let i = 0; i < pipelineSteps.length; i++) {
    if (pipelineSteps[i].stages.includes(stage)) return i;
  }
  return stage === 'completed' ? pipelineSteps.length : 0;
}

function formatDate(d: string) {
  return new Date(d).toLocaleString();
}

function formatSeconds(s: number) {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  return h > 0 ? `${h}h ${m}m ${sec}s` : `${m}m ${sec}s`;
}

const JobStatusCard: React.FC<{ job: Job }> = ({ job }) => {
  const stepStatus = job.stage === 'failed' ? 'error' : job.stage === 'completed' ? 'finish' : 'process';
  const retryMutation = useRetryJobMutation();

  const [errorMessage, ...tracebackLines] = job.error_message?.split('\n\n') ?? [];
  const traceback = tracebackLines.join('\n\n');

  return (
    <Card 
      title={job.title ?? 'Processing…'} 
      style={{ marginBottom: 16 }}
      extra={job.stage === 'failed' && (
        <Button 
          type="primary" 
          danger 
          size="small" 
          icon={<ReloadOutlined />} 
          onClick={() => retryMutation.mutate(job.id)}
          loading={retryMutation.isPending}
        >
          Retry
        </Button>
      )}
    >
      {job.error_message && (
        <div style={{ marginBottom: 16 }}>
          <Alert
            type="error"
            message="Job Failed"
            description={
              <div style={{ marginTop: 8 }}>
                <Paragraph strong>{errorMessage}</Paragraph>
                {traceback && (
                  <Collapse ghost size="small">
                    <Panel header="Show Traceback" key="1">
                      <pre style={{ 
                        fontSize: '11px', 
                        backgroundColor: '#fff1f0', 
                        padding: '8px', 
                        borderRadius: '4px',
                        overflowX: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all'
                      }}>
                        {traceback}
                      </pre>
                    </Panel>
                  </Collapse>
                )}
              </div>
            }
          />
        </div>
      )}
      <Steps
        current={getCurrentStep(job.stage)}
        status={stepStatus}
        items={pipelineSteps.map((s) => ({ title: s.title }))}
        style={{ marginBottom: 16 }}
        size="small"
      />
      <Descriptions bordered size="small" column={2}>
        <Descriptions.Item label="Stage">
          <Tag color={stageColor[job.stage]}>{job.stage.replace(/_/g, ' ')}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Created">{formatDate(job.created_at)}</Descriptions.Item>
        {job.duration_seconds != null && (
          <Descriptions.Item label="Duration">{formatSeconds(job.duration_seconds)}</Descriptions.Item>
        )}
        <Descriptions.Item label="URL">
          <a href={job.youtube_url} target="_blank" rel="noreferrer">YouTube</a>
        </Descriptions.Item>
      </Descriptions>
      {job.progress !== undefined && job.stage !== 'completed' && job.stage !== 'failed' && (
        <div style={{ marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: '12px', marginBottom: 4, display: 'block' }}>
            Overall Progress
          </Text>
          <Progress percent={Math.round(job.progress)} status="active" />
        </div>
      )}
    </Card>
  );
};

export default JobStatusCard;
