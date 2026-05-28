import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import CourseList from '../CourseList';
import SubjectList from '../SubjectList';
import SubjectGroupList from '../SubjectGroupList';
import TeacherList from '../TeacherList';

const { apiMock } = vi.hoisted(() => ({
  apiMock: {
    get: vi.fn().mockResolvedValue([]),
    post: vi.fn().mockResolvedValue({}),
    put: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
    del: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock('../../lib/api', () => ({
  default: apiMock,
}));

vi.mock('../../i18n', () => ({
  t: key => key,
}));

describe('Lists regression guard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMock.get.mockResolvedValue([]);
  });

  it('keeps course list add flow entrypoint visible', () => {
    render(<CourseList />);
    expect(screen.getByRole('button', { name: /courses\.add/i })).toBeInTheDocument();
  });

  it('keeps subject list filters and add action visible', () => {
    render(<SubjectList />);
    expect(screen.getByRole('button', { name: /subjects\.add/i })).toBeInTheDocument();
    expect(document.querySelector('.search-bar')).toBeInTheDocument();
  });

  it('keeps subject group list add action visible', () => {
    render(<SubjectGroupList />);
    expect(screen.getByRole('button', { name: /subject_groups\.add/i })).toBeInTheDocument();
  });

  it('keeps teacher list add action and filters visible', () => {
    render(<TeacherList />);
    expect(screen.getByRole('button', { name: /teachers\.add/i })).toBeInTheDocument();
    expect(document.querySelector('.search-bar')).toBeInTheDocument();
  });
});
