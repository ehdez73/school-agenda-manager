import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

import MarkdownTimetable from '../MarkdownTimetable';

const { apiMock } = vi.hoisted(() => ({
  apiMock: {
    get: vi.fn(),
    post: vi.fn().mockResolvedValue({}),
    del: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock('../../lib/api', () => ({
  default: apiMock,
}));

vi.mock('../../i18n', () => ({
  t: key => key,
}));

describe('MarkdownTimetable cell color behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('paints full cell when all subject entries share the same color', async () => {
    apiMock.get.mockImplementation((path) => {
      if (path === '/api/timetable/status/current') return Promise.resolve({ status: 'idle' });
      if (path === '/api/timetable') {
        return Promise.resolve(
          [
            '## timetable.by_course',
            '| Hour | Monday |',
            '|---|---|',
            '| 9:00 | <span class="tt-subject-entry" style="background-color: #ffaa00;">REL (Ana)</span> <br><span class="tt-subject-entry" style="background-color: #ffaa00;">VAL (Luis)</span> |',
          ].join('\n')
        );
      }
      return Promise.resolve({});
    });

    render(<MarkdownTimetable />);

    const rel = await screen.findByText('REL (Ana)');
    const td = rel.closest('td');
    expect(td).toBeTruthy();

    await waitFor(() => {
      expect(td.getAttribute('style') || '').toContain('background-color: rgb(255, 170, 0)');
    });

    const relEntry = rel.closest('.tt-subject-entry');
    expect((relEntry?.getAttribute('style')) || '').not.toContain('background-color');
  });

  it('does not paint full cell when subject entries have different colors', async () => {
    apiMock.get.mockImplementation((path) => {
      if (path === '/api/timetable/status/current') return Promise.resolve({ status: 'idle' });
      if (path === '/api/timetable') {
        return Promise.resolve(
          [
            '## timetable.by_course',
            '| Hour | Monday |',
            '|---|---|',
            '| 10:00 | <span class="tt-subject-entry" style="background-color: #111111;">REL (Ana)</span> <br><span class="tt-subject-entry" style="background-color: #222222;">VAL (Luis)</span> |',
          ].join('\n')
        );
      }
      return Promise.resolve({});
    });

    render(<MarkdownTimetable />);

    const rel = await screen.findByText('REL (Ana)');
    const td = rel.closest('td');
    expect(td).toBeTruthy();

    await waitFor(() => {
      expect((td.getAttribute('style')) || '').not.toContain('background-color');
    });
  });
});
