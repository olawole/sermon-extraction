import React from 'react';
import { Typography, List, Tag, Card, Space, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import JobCreateForm from '@/features/jobs/JobCreateForm';
import LoadingState from '@/components/common/LoadingState';
import ErrorState from '@/components/common/ErrorState';
import EmptyState from '@/components/common/EmptyState';
import { useJobsQuery } from '@/hooks/useJobs';
import type { Job, JobStage } from '@/types';

const { Title } = Typography;

const stageColor: Record<JobStage, string> = {
  pending: 'default', downloading: 'processing', audio_extracted: 'processing',
  transcribing: 'processing', transcribed: 'processing', classifying: 'processing',
  classified: 'processing', detecting_services: 'processing', services_detected: 'processing',
  detecting_sermon: 'processing', sermon_detected: 'processing', exporting_sermon: 'processing',
  sermon_exported: 'processing', generating_highlights: 'processing',
  highlights_generated: 'processing', completed: 'success', failed: 'error',
};

const PageWrapper = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const JobSubmissionPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: jobs, isLoading, isError } = useJobsQuery();

  return (
    <PageWrapper>
      <Title level={3} style={{ marginBottom: 24 }}>
        <PlusOutlined style={{ marginRight: 8 }} />
        New Extraction Job
      </Title>

      <JobCreateForm />

      <Title level={4} style={{ marginTop: 40, marginBottom: 16 }}>
        Recent Jobs
      </Title>

      {isLoading && <LoadingState tip="Loading jobs…" />}
      {isError && <ErrorState message="Failed to load jobs." />}
      {!isLoading && !isError && (!jobs || jobs.length === 0) && (
        <EmptyState description="No jobs yet. Submit a YouTube URL above to get started." />
      )}
      {jobs && jobs.length > 0 && (
        <Card>
          <List
            dataSource={jobs}
            renderItem={(job: Job) => (
              <List.Item
                key={job.id}
                actions={[
                  <Button
                    key="view"
                    type="link"
                    onClick={() => navigate(`/jobs/${job.id}`)}
                  >
                    View
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <span>{job.title ?? job.youtube_url}</span>
                      <Tag color={stageColor[job.stage]}>
                        {job.stage.replace(/_/g, ' ')}
                      </Tag>
                    </Space>
                  }
                  description={new Date(job.created_at).toLocaleString()}
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </PageWrapper>
  );
};

export default JobSubmissionPage;
