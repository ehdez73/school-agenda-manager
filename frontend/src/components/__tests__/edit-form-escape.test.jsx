import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';

import CourseForm from '../CourseForm';
import SubjectForm from '../SubjectForm';
import SubjectGroupForm from '../SubjectGroupForm';
import TeacherForm from '../TeacherForm';

vi.mock('../../i18n', () => ({
  t: key => key,
}));

vi.mock('../AutocompleteSelect', () => ({
  default: () => <div data-testid="autocomplete-select" />,
}));

vi.mock('../PreferencesGrid', () => ({
  default: () => <div data-testid="preferences-grid" />,
}));

const baseCourseForm = {
  form: { name: '', num_lines: 1 },
  setForm: vi.fn(),
  editingId: null,
  onSubmit: vi.fn(),
  onDelete: vi.fn(),
};

const baseSubjectForm = {
  form: {
    id: '',
    name: '',
    course_id: '1',
    weekly_hours: 2,
    max_hours_per_day: 1,
    consecutive_hours: true,
    linked_subject_id: '',
    included_lines: null,
  },
  setForm: vi.fn(),
  courses: [{ id: '1', name: 'Course 1', num_lines: 1 }],
  subjects: [],
  lockedHours: false,
  editingId: null,
  formError: '',
  onSubmit: vi.fn(),
  onDelete: vi.fn(),
  daysPerWeek: 5,
};

const baseSubjectGroupForm = {
  form: { name: '', subjects: [], included_lines: null },
  setForm: vi.fn(),
  subjects: [],
  formError: '',
  onSubmit: vi.fn(),
  onDelete: vi.fn(),
  courses: [{ id: '1', name: 'Course 1', num_lines: 1 }],
};

const baseTeacherForm = {
  form: { name: '', subjects: [], max_hours_week: 1, preferences: {}, tutor_group: null },
  setForm: vi.fn(),
  subjects: [],
  classesPerDay: 5,
  onSubmit: vi.fn(),
  onDelete: vi.fn(),
  groups: [],
};

describe('edit forms close on Escape', () => {
  it.each([
    ['CourseForm', CourseForm, baseCourseForm],
    ['SubjectForm', SubjectForm, baseSubjectForm],
    ['SubjectGroupForm', SubjectGroupForm, baseSubjectGroupForm],
    ['TeacherForm', TeacherForm, baseTeacherForm],
  ])('calls onCancel for %s when Escape is pressed', (_, Component, props) => {
    const onCancel = vi.fn();

    render(<Component {...props} onCancel={onCancel} />);

    fireEvent.keyDown(window, { key: 'Escape' });

    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});