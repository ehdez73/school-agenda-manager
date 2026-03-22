import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import SubjectList from '../SubjectList';

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

describe('SubjectList – section layout structure', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders a top-level <section> element as section root', () => {
    render(<SubjectList />);
    expect(document.querySelector('section.section-layout')).toBeInTheDocument();
  });

  it('renders a single <h2> with the section title', () => {
    render(<SubjectList />);
    const headings = screen.getAllByRole('heading', { level: 2 });
    expect(headings.length).toBe(1);
  });

  it('renders a <header> element wrapping the heading', () => {
    render(<SubjectList />);
    const header = document.querySelector('header.section-layout__header');
    expect(header).toBeInTheDocument();
    expect(header.querySelector('h2')).toBeInTheDocument();
  });

  it('renders the actions slot inside the header', () => {
    render(<SubjectList />);
    expect(document.querySelector('.section-layout__actions')).toBeInTheDocument();
  });

  it('renders the content zone inside section-layout__content', () => {
    render(<SubjectList />);
    expect(document.querySelector('.section-layout__content')).toBeInTheDocument();
  });
});
