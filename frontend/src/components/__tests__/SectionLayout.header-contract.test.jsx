import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderSection } from '../../test/layoutFixtures';

describe('SectionLayout – header semantics contract (C-2)', () => {
  it('renders exactly one <h2> element', () => {
    renderSection({ title: 'My Section' });
    const headings = document.querySelectorAll('h2');
    expect(headings.length).toBe(1);
  });

  it('h2 contains the title text', () => {
    renderSection({ title: 'Subjects' });
    expect(screen.getByRole('heading', { level: 2, name: 'Subjects' })).toBeInTheDocument();
  });

  it('h2 is inside the <header> element', () => {
    renderSection({ title: 'Courses' });
    const header = document.querySelector('header.section-layout__header');
    expect(header).toBeInTheDocument();
    expect(header.querySelector('h2')).toBeInTheDocument();
  });

  it('renders a description when provided', () => {
    renderSection({ title: 'My Section', description: 'A helpful description' });
    expect(screen.getByText('A helpful description')).toBeInTheDocument();
  });

  it('does not render a description element when not provided', () => {
    renderSection({ title: 'My Section' });
    expect(document.querySelector('.section-layout__description')).not.toBeInTheDocument();
  });

  it('title has no raw text siblings at the heading level', () => {
    renderSection({ title: 'Clean Heading' });
    const heading = screen.getByRole('heading', { level: 2 });
    const headingRow = heading.parentElement;
    // Heading row should only contain the h2 and optionally the actions div
    const textNodes = Array.from(headingRow.childNodes).filter(
      n => n.nodeType === Node.TEXT_NODE && n.textContent.trim().length > 0
    );
    expect(textNodes.length).toBe(0);
  });
});
