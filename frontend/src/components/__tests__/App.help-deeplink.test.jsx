import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import App from '../../App';

vi.mock('../../components/CourseList', () => ({ default: () => <div>courses</div> }));
vi.mock('../../components/SubjectList', () => ({ default: () => <div>subjects</div> }));
vi.mock('../../components/TeacherList', () => ({ default: () => <div>teachers</div> }));
vi.mock('../../components/ConfigForm', () => ({ default: () => <div>config</div> }));
vi.mock('../../components/MarkdownTimetable', () => ({ default: () => <div>timetable</div> }));
vi.mock('../../components/LanguageSelector', () => ({ default: () => <div>language</div> }));
vi.mock('../../components/HelpSection', () => ({
  default: () => <div data-testid="help-section-mock">help section rendered</div>,
}));

vi.mock('../../i18n', () => ({
  t: key => key,
  setLocale: vi.fn(),
}));

describe('App help deep link behavior', () => {
  beforeEach(() => {
    localStorage.clear();
    window.location.hash = '#10-buenas-practicas-de-gestion';
  });

  it('opens help page automatically when app loads with hash', async () => {
    render(<App />);
    expect(await screen.findByTestId('help-section-mock')).toBeInTheDocument();
  });

  it('clears the help hash when navigating to another page', async () => {
    render(<App />);

    expect(await screen.findByTestId('help-section-mock')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'nav.courses' }));

    await waitFor(() => {
      expect(screen.getByText('courses')).toBeInTheDocument();
      expect(window.location.hash).toBe('');
    });
  });
});
