import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Tabs, Button, Space, Popconfirm } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import styled from 'styled-components';

import JobStatusCard from '@/features/jobs/JobStatusCard';
import TranscriptViewer from '@/features/transcript/TranscriptViewer';
import SegmentsTable from '@/features/segments/SegmentsTable';
import ServiceSummaryCard from '@/features/segments/ServiceSummaryCard';
import SermonSummaryCard from '@/features/segments/SermonSummaryCard';
import TimelineView from '@/features/segments/TimelineView';
import HighlightsList from '@/features/highlights/HighlightsList';
import AssetListPanel from '@/features/assets/AssetListPanel';
import LoadingState from '@/components/common/LoadingState';
import ErrorState from '@/components/common/ErrorState';
import EmptyState from '@/components/common/EmptyState';

import {
  useJobQuery,
  useTranscriptQuery,
  useSegmentsQuery,
  useHighlightsQuery,
  useAssetsQuery,
  useApproveHighlightMutation,
  useRejectHighlightMutation,
  useRenderHighlightMutation,
  useRenderAllHighlightsMutation,
  useRetryJobMutation,
  useDeleteJobMutation,
} from '@/hooks/useJobs';

const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const JobDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const jobId = Number(id);

  const { data: job, isLoading: jobLoading, isError: jobError } = useJobQuery(jobId);
  const { data: transcript } = useTranscriptQuery(jobId);
  const { data: segments } = useSegmentsQuery(jobId);
  const { data: highlights } = useHighlightsQuery(jobId);
  const { data: assets } = useAssetsQuery(jobId);
  const approveMutation = useApproveHighlightMutation(jobId);
  const rejectMutation = useRejectHighlightMutation(jobId);
  const renderMutation = useRenderHighlightMutation(jobId);
  const renderAllMutation = useRenderAllHighlightsMutation(jobId);
  const retryMutation = useRetryJobMutation();
  const deleteMutation = useDeleteJobMutation();

  if (jobLoading) return <LoadingState tip="Loading job…" />;
  if (jobError || !job) return <ErrorState message="Failed to load job." />;

  const tabItems = [
    {
      key: 'transcript',
      label: 'Transcript',
      children: transcript?.chunks?.length ? (
        <TranscriptViewer chunks={transcript.chunks} />
      ) : (
        <EmptyState description="Transcript not yet available." />
      ),
    },
    {
      key: 'segments',
      label: 'Segments',
      children: segments ? (
        <Space direction="vertical" style={{ width: '100%' }}>
          {job.duration_seconds && (
            <TimelineView
              jobId={jobId}
              totalDuration={job.duration_seconds}
              sectionSegments={segments.section_segments}
              serviceSegments={segments.service_segments}
              sermonSegment={segments.sermon_segment}
              highlights={highlights?.highlights}
            />
          )}
          {segments.service_segments?.length > 0 && (
            <ServiceSummaryCard services={segments.service_segments} />
          )}
          {segments.sermon_segment && (
            <SermonSummaryCard sermon={segments.sermon_segment} />
          )}
          {segments.section_segments?.length > 0 ? (
            <SegmentsTable segments={segments.section_segments} />
          ) : (
            <EmptyState description="Section segments not yet available." />
          )}
        </Space>
      ) : (
        <EmptyState description="Segments not yet available." />
      ),
    },
    {
      key: 'highlights',
      label: 'Highlights',
      children: highlights?.highlights?.length ? (
        <>
          {highlights.highlights.some((h) => h.status === 'approved') && (
            <Space style={{ marginBottom: 12 }}>
              <Button
                type="primary"
                loading={renderAllMutation.isPending}
                onClick={() => renderAllMutation.mutate()}
              >
                Render All Approved
              </Button>
            </Space>
          )}
          <HighlightsList
            jobId={jobId}
            highlights={highlights.highlights}
            onApprove={(hId) => approveMutation.mutate(hId)}
            onReject={(hId) => rejectMutation.mutate(hId)}
            onRender={(hId) => renderMutation.mutate(hId)}
          />
        </>
      ) : (
        <EmptyState description="Highlights not yet available." />
      ),
    },
    {
      key: 'assets',
      label: 'Assets',
      children: assets?.assets?.length ? (
        <AssetListPanel assets={assets.assets} />
      ) : (
        <EmptyState description="Assets not yet available." />
      ),
    },
  ];

  return (
    <PageWrapper>
      <Space style={{ marginBottom: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/')}
        >
          Back to Jobs
        </Button>
        {job.stage === 'failed' && (
          <Button
            type="primary"
            loading={retryMutation.isPending}
            onClick={() => retryMutation.mutate(jobId)}
          >
            Retry
          </Button>
        )}
        <Popconfirm
          title="Delete this job?"
          description="This action cannot be undone."
          onConfirm={() => deleteMutation.mutate(jobId, { onSuccess: () => navigate('/') })}
          okText="Delete"
          okButtonProps={{ danger: true }}
          cancelText="Cancel"
        >
          <Button danger loading={deleteMutation.isPending}>
            Delete
          </Button>
        </Popconfirm>
      </Space>

      <JobStatusCard job={job} />

      <Tabs defaultActiveKey="transcript" items={tabItems} />
    </PageWrapper>
  );
};

export default JobDetailsPage;
