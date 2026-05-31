import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import HelpSection from '../HelpSection';

const { apiMock } = vi.hoisted(() => ({
  apiMock: {
    get: vi.fn(),
  },
}));

vi.mock('../../lib/api', () => ({
  default: apiMock,
}));

vi.mock('../../i18n', () => ({
  t: key => key,
}));

describe('HelpSection TOC links', () => {
  const markdown = [
    '# User Guide',
    '',
    '## First Section',
    'Content',
    '',
    '### Subsection A',
    'Content',
    '',
    '## Second Section',
    'Content',
    '',
    '### Subsection B',
  ].join('\n');

  beforeEach(() => {
    vi.clearAllMocks();
    apiMock.get.mockResolvedValue(markdown);
    window.location.hash = '';
  });

  it('renders toc links whose targets exist as heading ids', async () => {
    render(<HelpSection locale="en" />);

    await screen.findByRole('heading', { name: 'User Guide' });

    const tocNav = screen.getByLabelText('help.toc_title');
    const links = tocNav.querySelectorAll('a.help-section__toc-link');
    expect(links.length).toBeGreaterThan(0);

    for (const link of links) {
      const href = link.getAttribute('href');
      expect(href).toBeTruthy();
      expect(href.startsWith('#')).toBe(true);

      const target = document.querySelector(href);
      expect(target).toBeTruthy();
    }
  });

  it('starts expanded and scroll links work on first click', async () => {
    render(<HelpSection locale="en" />);

    await screen.findByRole('heading', { name: 'User Guide' });

    const subsectionLink = await screen.findByRole('link', { name: 'Subsection A' });
    expect(subsectionLink).toBeInTheDocument();

    fireEvent.click(subsectionLink);
    await waitFor(() => {
      expect(window.location.hash).toBe('#section-3');
    });
  });

  it('scrolls inside app content using container-relative offsets', async () => {
    render(
      <div className="app__content">
        <HelpSection locale="en" />
      </div>
    );

    await screen.findByRole('heading', { name: 'User Guide' });

    const content = document.querySelector('.app__content');
    expect(content).toBeTruthy();

    const target = document.getElementById('section-3');
    expect(target).toBeTruthy();

    Object.defineProperty(content, 'scrollTop', {
      value: 200,
      writable: true,
      configurable: true,
    });

    Object.defineProperty(content, 'getBoundingClientRect', {
      value: () => ({
        top: 300,
        left: 0,
        bottom: 900,
        right: 1000,
        width: 1000,
        height: 600,
        x: 0,
        y: 300,
        toJSON: () => ({}),
      }),
      configurable: true,
    });

    Object.defineProperty(target, 'getBoundingClientRect', {
      value: () => ({
        top: 350,
        left: 0,
        bottom: 370,
        right: 1000,
        width: 1000,
        height: 20,
        x: 0,
        y: 350,
        toJSON: () => ({}),
      }),
      configurable: true,
    });

    const scrollToMock = vi.fn();
    Object.defineProperty(content, 'scrollTo', {
      value: scrollToMock,
      configurable: true,
    });

    const subsectionLink = await screen.findByRole('link', { name: 'Subsection A' });
    fireEvent.click(subsectionLink);

    await waitFor(() => {
      expect(scrollToMock).toHaveBeenCalledWith(expect.objectContaining({ top: 238 }));
      expect(window.location.hash).toBe('#section-3');
    });
  });

  it('resolves hash targets using normalized ids when hash has punctuation differences', async () => {
    window.location.hash = '#10.-buenas-practicas-de-gestion';

    const punctuationMarkdown = [
      '# User Guide',
      '',
      '## 10. Buenas practicas de gestion',
      'Content',
    ].join('\n');

    apiMock.get.mockResolvedValue(punctuationMarkdown);

    render(<HelpSection locale="en" />);

    await waitFor(() => {
      const target = document.getElementById('section-2');
      expect(target).toBeInTheDocument();
      expect(window.location.hash).toBe('#section-2');
    });
  });

  it('normalizes a legacy hash from the other language to the canonical help id', async () => {
    window.location.hash = '#curso';

    const englishMarkdown = [
      '# User Guide',
      '',
      '## Course',
      'Content',
    ].join('\n');

    const spanishMarkdown = [
      '# Guia de Usuario',
      '',
      '## Curso',
      'Content',
    ].join('\n');

    apiMock.get
      .mockResolvedValueOnce(englishMarkdown)
      .mockResolvedValueOnce(spanishMarkdown);

    render(<HelpSection locale="en" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Course' })).toBeInTheDocument();
      expect(window.location.hash).toBe('#section-2');
    });
  });

  it('keeps the same canonical hash when switching locale', async () => {
    window.location.hash = '#section-2';

    const englishMarkdown = [
      '# User Guide',
      '',
      '## Course',
      'Content',
    ].join('\n');

    const spanishMarkdown = [
      '# Guia de Usuario',
      '',
      '## Curso',
      'Content',
    ].join('\n');

    apiMock.get.mockImplementation(url => {
      if (String(url).includes('/api/docs/es')) return Promise.resolve(spanishMarkdown);
      if (String(url).includes('/api/docs/en')) return Promise.resolve(englishMarkdown);
      return Promise.resolve('');
    });

    const { rerender } = render(<HelpSection locale="es" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Curso' })).toBeInTheDocument();
    });

    rerender(<HelpSection locale="en" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Course' })).toBeInTheDocument();
      expect(window.location.hash).toBe('#section-2');
    });
  });

  it('keeps section hash stable when switching locale on numbered headings', async () => {
    window.location.hash = '#section-2';

    const englishMarkdown = [
      '# User Guide',
      '',
      '## Error 2: A subject does not appear with expected hours',
      'Content',
    ].join('\n');

    const spanishMarkdown = [
      '# Guia de Usuario',
      '',
      '## Error 2: Una asignatura no aparece con horas esperadas',
      'Contenido',
    ].join('\n');

    apiMock.get.mockImplementation(url => {
      if (String(url).includes('/api/docs/es')) return Promise.resolve(spanishMarkdown);
      if (String(url).includes('/api/docs/en')) return Promise.resolve(englishMarkdown);
      return Promise.resolve('');
    });

    const { rerender } = render(<HelpSection locale="en" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error 2: A subject does not appear with expected hours' })).toBeInTheDocument();
    });

    rerender(<HelpSection locale="es" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Error 2: Una asignatura no aparece con horas esperadas' })).toBeInTheDocument();
      expect(window.location.hash).toBe('#section-2');
    });
  });

  it('clears non-help hashes when loading help', async () => {
    window.location.hash = '#curso';

    render(<HelpSection locale="es" />);

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'User Guide' })).toBeInTheDocument();
      expect(window.location.hash).toBe('');
    });
  });

  it('rewrites relative image sources to the docs assets endpoint', async () => {
    const imageMarkdown = [
      '# User Guide',
      '',
      '![Screenshot](assets/screenshots/help.png)',
    ].join('\n');

    apiMock.get.mockResolvedValue(imageMarkdown);

    render(<HelpSection locale="en" />);

    const image = await screen.findByRole('img', { name: 'Screenshot' });
    expect(image.getAttribute('src')).toBe('/api/api/docs/assets/screenshots/help.png');
  });
});
