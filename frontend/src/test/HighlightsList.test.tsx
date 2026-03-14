import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HighlightsList from '@/features/highlights/HighlightsList';
import type { HighlightClip } from '@/types';

// Mock the hook
vi.mock('@/hooks/useJobs', () => ({
  useAssetsQuery: vi.fn().mockReturnValue({ data: { assets: [] } }),
}));

const highlights: HighlightClip[] = [
  {
    id: 1,
    start_seconds: 100,
    end_seconds: 145,
    score: 0.85,
    category: 'sermon',
    title: 'Faith over fear',
    hook_text: 'Fear is overcome by faith',
    transcript: 'When we trust God, fear has no place...',
    reasons: ['hook strength', 'emotional intensity'],
    status: 'pending',
  },
  {
    id: 2,
    start_seconds: 200,
    end_seconds: 260,
    score: 0.72,
    category: 'sermon',
    title: 'Grace for today',
    hook_text: 'His grace is new every morning',
    transcript: 'Every morning brings a fresh opportunity...',
    reasons: ['memorable phrasing'],
    status: 'approved',
  },
];

describe('HighlightsList', () => {
  it('renders all highlight titles', () => {
    render(<HighlightsList jobId={1} highlights={highlights} />);
    expect(screen.getByText('Faith over fear')).toBeInTheDocument();
    expect(screen.getByText('Grace for today')).toBeInTheDocument();
  });

  it('renders score progress bars', () => {
    render(<HighlightsList jobId={1} highlights={highlights} />);
    expect(screen.getByText('Score: 85%')).toBeInTheDocument();
    expect(screen.getByText('Score: 72%')).toBeInTheDocument();
  });

  it('shows approve and reject buttons only for pending highlights', () => {
    render(<HighlightsList jobId={1} highlights={highlights} />);
    expect(screen.getAllByRole('button', { name: /approve/i })).toHaveLength(1);
    expect(screen.getAllByRole('button', { name: /reject/i })).toHaveLength(1);
  });

  it('calls onApprove with the highlight id when Approve is clicked', async () => {
    const onApprove = vi.fn();
    render(<HighlightsList jobId={1} highlights={highlights} onApprove={onApprove} />);
    await userEvent.click(screen.getByRole('button', { name: /approve/i }));
    expect(onApprove).toHaveBeenCalledWith(1);
  });

  it('calls onReject with the highlight id when Reject is clicked', async () => {
    const onReject = vi.fn();
    render(<HighlightsList jobId={1} highlights={highlights} onReject={onReject} />);
    await userEvent.click(screen.getByRole('button', { name: /reject/i }));
    expect(onReject).toHaveBeenCalledWith(1);
  });

  it('renders a Render button for approved highlights', () => {
    render(<HighlightsList jobId={1} highlights={highlights} />);
    expect(screen.getByRole('button', { name: /render/i })).toBeInTheDocument();
  });

  it('calls onRender with the highlight id when Render is clicked', async () => {
    const onRender = vi.fn();
    render(<HighlightsList jobId={1} highlights={highlights} onRender={onRender} />);
    await userEvent.click(screen.getByRole('button', { name: /render/i }));
    expect(onRender).toHaveBeenCalledWith(2);
  });

  it('renders hook text for each highlight', () => {
    render(<HighlightsList jobId={1} highlights={highlights} />);
    expect(screen.getByText(/"Fear is overcome by faith"/)).toBeInTheDocument();
    expect(screen.getByText(/"His grace is new every morning"/)).toBeInTheDocument();
  });

  it('renders details button for each highlight', () => {
    render(<HighlightsList jobId={1} highlights={highlights} />);
    expect(screen.getAllByRole('button', { name: /details/i })).toHaveLength(2);
  });
});
