import React from 'react';
import { Form, Input, Button, Card } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useCreateJobMutation } from '@/hooks/useJobs';

const JobCreateForm: React.FC = () => {
  const navigate = useNavigate();
  const mutation = useCreateJobMutation();
  const [form] = Form.useForm();

  const onFinish = async ({ youtube_url }: { youtube_url: string }) => {
    const job = await mutation.mutateAsync(youtube_url);
    navigate(`/jobs/${job.id}`);
  };

  return (
    <Card title="New Extraction Job" style={{ maxWidth: 600, margin: '0 auto' }}>
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item
          label="YouTube URL"
          name="youtube_url"
          rules={[
            { required: true, message: 'Please enter a YouTube URL' },
            {
              pattern: /^https?:\/\/(www\.)?(youtube\.com\/watch|youtu\.be\/)/,
              message: 'Must be a valid YouTube URL',
            },
          ]}
        >
          <Input placeholder="https://www.youtube.com/watch?v=..." size="large" />
        </Form.Item>
        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            loading={mutation.isPending}
            block
          >
            Start Extraction
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default JobCreateForm;
