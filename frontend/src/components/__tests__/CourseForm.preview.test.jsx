import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import CourseForm from '../CourseForm';

vi.mock('../../i18n', () => ({
  t: key => key,
}));

const baseProps = {
  setForm: vi.fn(),
  editingId: null,
  onSubmit: vi.fn(),
  onCancel: vi.fn(),
};

describe('CourseForm group preview', () => {
  it('shows groups preview from course name and number of lines', () => {
    render(
      <CourseForm
        {...baseProps}
        form={{ name: '1º', num_lines: 2 }}
      />
    );

    expect(screen.getByText('1ºA, 1ºB')).toBeInTheDocument();
  });

  it('shows placeholder when preview data is incomplete', () => {
    render(
      <CourseForm
        {...baseProps}
        form={{ name: '', num_lines: 2 }}
      />
    );

    expect(screen.getByText('-')).toBeInTheDocument();
  });
});