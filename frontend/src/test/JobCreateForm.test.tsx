import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import JobCreateForm from '@/features/jobs/JobCreateForm';
import * as api from '@/services/api';
import type { Job } from '@/types';

vi.mock('@/services/api');

const mockJob: Job = {
  id: 1,
  youtube_url: 'https://www.youtube.com/watch?v=abc123',
  title: null,
  duration_seconds: null,
  stage: 'pending',
  error_message: null,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

function renderForm() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <JobCreateForm />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('JobCreateForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the YouTube URL input and submit button', () => {
    renderForm();
    expect(screen.getByPlaceholderText(/youtube\.com/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start extraction/i })).toBeInTheDocument();
  });

  it('shows validation error when submitting empty form', async () => {
    renderForm();
    const button = screen.getByRole('button', { name: /start extraction/i });
    await userEvent.click(button);
    await waitFor(() => {
      expect(screen.getByText(/please enter a youtube url/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid URL', async () => {
    renderForm();
    const input = screen.getByPlaceholderText(/youtube\.com/i);
    await userEvent.type(input, 'https://vimeo.com/123');
    const button = screen.getByRole('button', { name: /start extraction/i });
    await userEvent.click(button);
    await waitFor(() => {
      expect(screen.getByText(/must be a valid youtube url/i)).toBeInTheDocument();
    });
  });

  it('calls createJob with the URL on valid submission', async () => {
    vi.mocked(api.createJob).mockResolvedValue(mockJob);
    renderForm();
    const input = screen.getByPlaceholderText(/youtube\.com/i);
    await userEvent.type(input, 'https://www.youtube.com/watch?v=abc123');
    const button = screen.getByRole('button', { name: /start extraction/i });
    await userEvent.click(button);
    await waitFor(() => {
      expect(api.createJob).toHaveBeenCalledWith('https://www.youtube.com/watch?v=abc123');
    });
  });
});
