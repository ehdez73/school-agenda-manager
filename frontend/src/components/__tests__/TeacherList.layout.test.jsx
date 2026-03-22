import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import TeacherList from '../TeacherList';

vi.mock('../../lib/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue([]),
    post: vi.fn().mockResolvedValue({}),
    put: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock('../../i18n', () => ({
  t: (key) => key,
}));

describe('TeacherList – section layout structure', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders a top-level <section> element as section root', () => {
    render(<TeacherList />);
    expect(document.querySelector('section.section-layout')).toBeInTheDocument();
  });

  it('renders a single <h2> with the section title', () => {
    render(<TeacherList />);
    const headings = screen.getAllByRole('heading', { level: 2 });
    expect(headings.length).toBe(1);
  });

  it('renders a <header> element wrapping the heading', () => {
    render(<TeacherList />);
    const header = document.querySelector('header.section-layout__header');
    expect(header).toBeInTheDocument();
    expect(header.querySelector('h2')).toBeInTheDocument();
  });

  it('renders the actions slot inside the header', () => {
    render(<TeacherList />);
    expect(document.querySelector('.section-layout__actions')).toBeInTheDocument();
  });

  it('renders the content zone inside section-layout__content', () => {
    render(<TeacherList />);
    expect(document.querySelector('.section-layout__content')).toBeInTheDocument();
  });
});
