import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

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

  it('renders independent multi-select controls for course and teacher timetables', async () => {
    apiMock.get.mockImplementation((path) => {
      if (path === '/api/timetable/status/current') return Promise.resolve({ status: 'idle' });
      if (path === '/api/timetable') {
        return Promise.resolve(
          [
            '## By course',
            '### Course: 1A',
            '| Hour | Monday |',
            '|---|---|',
            '| 9:00 | MATH (Ana) |',
            '',
            '### Course: 1B',
            '| Hour | Monday |',
            '|---|---|',
            '| 9:00 | SCI (Luis) |',
            '',
            '## By teacher',
            '### Ana',
            'Assigned: 1/10',
            '| Hour | Monday |',
            '|---|---|',
            '| 9:00 | 1A: MATH |',
            '',
            '### Luis',
            'Assigned: 1/10',
            '| Hour | Monday |',
            '|---|---|',
            '| 9:00 | 1B: SCI |',
          ].join('\n')
        );
      }
      return Promise.resolve({});
    });

    render(<MarkdownTimetable />);

    const searchInputs = await screen.findAllByRole('searchbox');
    expect(searchInputs).toHaveLength(2);

    expect(await screen.findByText('MATH (Ana)')).toBeInTheDocument();
    expect(screen.getByText('SCI (Luis)')).toBeInTheDocument();
    expect(screen.getByText('1A: MATH')).toBeInTheDocument();
    expect(screen.getByText('1B: SCI')).toBeInTheDocument();

    fireEvent.focus(searchInputs[0]);
    fireEvent.change(searchInputs[0], { target: { value: 'Course: 1B' } });
    fireEvent.click(await screen.findByLabelText('Course: 1B'));
    expect(screen.queryByText('SCI (Luis)')).not.toBeInTheDocument();
    expect(screen.getByText('MATH (Ana)')).toBeInTheDocument();
    expect(screen.getByText('1B: SCI')).toBeInTheDocument();

    fireEvent.focus(searchInputs[1]);
    fireEvent.change(searchInputs[1], { target: { value: 'Luis' } });
    fireEvent.click(await screen.findByLabelText('Luis'));
    expect(screen.getByText('1B: SCI')).toBeInTheDocument();
  });

  it('supports all option and renders multiple selected timetables in sequence', async () => {
    const courseBlocks = Array.from({ length: 9 }, (_, i) => {
      const n = i + 1;
      return [
        `### Course: ${n}A`,
        '| Hour | Monday |',
        '|---|---|',
        `| 9:00 | SUB${n} (Teacher ${n}) |`,
        '',
      ].join('\n');
    }).join('\n');

    const teacherBlocks = Array.from({ length: 9 }, (_, i) => {
      const n = i + 1;
      return [
        `### Teacher ${n}`,
        'Assigned: 1/10',
        '| Hour | Monday |',
        '|---|---|',
        `| 9:00 | ${n}A: SUB${n} |`,
        '',
      ].join('\n');
    }).join('\n');

    apiMock.get.mockImplementation((path) => {
      if (path === '/api/timetable/status/current') return Promise.resolve({ status: 'idle' });
      if (path === '/api/timetable') {
        return Promise.resolve(
          [
            '## By course',
            courseBlocks,
            '## By teacher',
            teacherBlocks,
          ].join('\n')
        );
      }
      return Promise.resolve({});
    });

    render(<MarkdownTimetable />);

    const searchInputs = await screen.findAllByRole('searchbox');
    expect(searchInputs).toHaveLength(2);

    expect(await screen.findByText('SUB1 (Teacher 1)')).toBeInTheDocument();
    expect(screen.getByText('SUB9 (Teacher 9)')).toBeInTheDocument();

    fireEvent.focus(searchInputs[0]);
    fireEvent.change(searchInputs[0], { target: { value: 'Course: 9A' } });
    fireEvent.click(screen.getByLabelText('common.all_courses'));
    expect(screen.queryByText('SUB1 (Teacher 1)')).not.toBeInTheDocument();
    expect(screen.queryByText('SUB9 (Teacher 9)')).not.toBeInTheDocument();

    expect(screen.getByText('1A: SUB1')).toBeInTheDocument();
    expect(screen.getByText('9A: SUB9')).toBeInTheDocument();

    fireEvent.focus(searchInputs[1]);
    fireEvent.change(searchInputs[1], { target: { value: 'Teacher 9' } });
    fireEvent.click(screen.getByLabelText('common.all_teachers'));
    expect(screen.queryByText('1A: SUB1')).not.toBeInTheDocument();
    expect(screen.queryByText('9A: SUB9')).not.toBeInTheDocument();
  });

  it('shows no timetable panel when all options are deselected from default all-selected state', async () => {
    apiMock.get.mockImplementation((path) => {
      if (path === '/api/timetable/status/current') return Promise.resolve({ status: 'idle' });
      if (path === '/api/timetable') {
        return Promise.resolve(
          [
            '## By course',
            '### Course: 1A',
            '| Hour | Monday |',
            '|---|---|',
            '| 9:00 | MATH (Ana) |',
            '',
            '## By teacher',
            '### Ana',
            'Assigned: 1/10',
            '| Hour | Monday |',
            '|---|---|',
            '| 9:00 | 1A: MATH |',
          ].join('\n')
        );
      }
      return Promise.resolve({});
    });

    render(<MarkdownTimetable />);

    const searchInputs = await screen.findAllByRole('searchbox');
    expect(searchInputs).toHaveLength(2);
    expect(await screen.findByText('MATH (Ana)')).toBeInTheDocument();
    expect(screen.getByText('1A: MATH')).toBeInTheDocument();

    fireEvent.focus(searchInputs[0]);
    fireEvent.change(searchInputs[0], { target: { value: 'Course: 1A' } });
    fireEvent.click(await screen.findByRole('checkbox', { name: 'Course: 1A' }));
    fireEvent.focus(searchInputs[1]);
    fireEvent.change(searchInputs[1], { target: { value: 'Ana' } });
    fireEvent.click(await screen.findByRole('checkbox', { name: 'Ana' }));

    expect(screen.queryByText('MATH (Ana)')).not.toBeInTheDocument();
    expect(screen.queryByText('1A: MATH')).not.toBeInTheDocument();
    expect(screen.getAllByText('No timetables selected')).toHaveLength(2);
  });
});
