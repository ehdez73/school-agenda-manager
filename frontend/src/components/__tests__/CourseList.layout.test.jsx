import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import CourseList from '../CourseList';

// Mock the api module to prevent real HTTP calls
vi.mock('../../lib/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue([]),
    post: vi.fn().mockResolvedValue({}),
    put: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
  },
}));

// Mock i18n
vi.mock('../../i18n', () => ({
  t: (key) => key,
}));

describe('CourseList – section layout structure', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders a top-level <section> element as section root', () => {
    render(<CourseList />);
    expect(document.querySelector('section.section-layout')).toBeInTheDocument();
  });

  it('renders a single <h2> with the section title', () => {
    render(<CourseList />);
    const headings = screen.getAllByRole('heading', { level: 2 });
    expect(headings.length).toBe(1);
  });

  it('renders a <header> element wrapping the heading', () => {
    render(<CourseList />);
    const header = document.querySelector('header.section-layout__header');
    expect(header).toBeInTheDocument();
    expect(header.querySelector('h2')).toBeInTheDocument();
  });

  it('renders the actions slot inside the header', () => {
    render(<CourseList />);
    const actions = document.querySelector('.section-layout__actions');
    expect(actions).toBeInTheDocument();
  });

  it('renders the content zone inside section-layout__content', () => {
    render(<CourseList />);
    const content = document.querySelector('.section-layout__content');
    expect(content).toBeInTheDocument();
  });
});
